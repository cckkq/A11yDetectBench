import asyncio
import json
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import AsyncMock, patch


from agent.gt_errors.evaluate_run import (
    _apply_known_page_preconditions,
    evaluate_response_against_rule,
    evaluate_run_dir,
    eval_auth_state_path_for_run,
    issue_type_matches,
    normalize_issues,
)


GITLAB_CI_EDITOR_URL = 'http://localhost:8023/byteblaze/dotfiles/-/ci/editor?branch_name=main'
GITLAB_CI_CONFIGURE_SELECTOR = 'button[data-qa-selector={0}create_new_ci_button{0}]'.format(chr(34))
GITLAB_GL70_MONACO_SELECTOR = '.monaco-editor textarea.inputarea[role={0}textbox{0}]'.format(chr(34))


class FakeLocator:
    def __init__(self, page, selector):
        self.page = page
        self.selector = selector
        self.first = self

    async def count(self):
        return self.page.locator_count

    async def click(self, timeout):
        self.page.clicks.append({'selector': self.selector, 'timeout': timeout})


class FakePage:
    def __init__(self, *, gold_present=False, locator_count=1):
        self.gold_present = gold_present
        self.locator_count = locator_count
        self.evaluate_calls = []
        self.locator_calls = []
        self.clicks = []
        self.wait_load_states = []
        self.wait_functions = []

    async def evaluate(self, script, groups):
        self.evaluate_calls.append({'script': script, 'groups': groups})
        return self.gold_present

    def locator(self, selector):
        self.locator_calls.append(selector)
        return FakeLocator(self, selector)

    async def wait_for_load_state(self, state, timeout):
        self.wait_load_states.append({'state': state, 'timeout': timeout})

    async def wait_for_function(self, script, groups, timeout):
        self.wait_functions.append({'script': script, 'groups': groups, 'timeout': timeout})


def write_minimal_run_dir(root: Path) -> Path:
    run_dir = root / 'run'
    run_dir.mkdir(parents=True)
    stale_auth_path = run_dir / 'stale_agent_auth.storage_state.json'
    stale_auth_path.write_text('{}\n', encoding='utf-8')

    (run_dir / 'task.snapshot.yaml').write_text(
        '\n'.join(
            [
                'task_id: gitlab.gl11.e2.test.verify.level1.v1',
                'instance_id: gitlab.gl11.e2.test',
                'start_url: http://localhost:8023/-/profile',
                'auth_state_file: agent/gt/auth/gitlab.storage_state.json',
                '',
            ]
        ),
        encoding='utf-8',
    )
    (run_dir / 'evaluate-rule.snapshot.yaml').write_text(
        '\n'.join(
            [
                'task_id: gitlab.gl11.e2.test.verify.level1.v1',
                'instance_id: gitlab.gl11.e2.test',
                'task_level: level1',
                'page:',
                '  site: gitlab',
                '  start_url: http://localhost:8023/-/profile',
                'gold:',
                '  issue_present: true',
                '  expected_verdict: issue_found',
                '  target:',
                '    selector: input.gold',
                '  criterion:',
                '    issue_family: error_suggestion',
                '',
            ]
        ),
        encoding='utf-8',
    )
    (run_dir / 'final-response.json').write_text(
        json.dumps(
            {
                'verdict': 'issue_found',
                'selector': 'input.agent',
                'target': 'the input',
                'issue_type': 'error_suggestion',
                'observed_behavior': 'invalid value lacks guidance',
                'evidence': 'validation message lacks expected format',
            }
        )
        + '\n',
        encoding='utf-8',
    )
    (run_dir / 'meta.json').write_text(
        json.dumps({'auth_state_file': str(stale_auth_path)}) + '\n',
        encoding='utf-8',
    )
    return run_dir


def single_rule(issue_family='error_suggestion', expected_verdict='issue_found', issue_present=True):
    return {
        'task_level': 'level1',
        'gold': {
            'expected_verdict': expected_verdict,
            'issue_present': issue_present,
            'target': {'selector': 'input.gold'},
            'criterion': {'issue_family': issue_family},
        },
    }


class ErrorEvaluateRunUnitTest(unittest.TestCase):
    def test_script_execution_adds_project_root_to_import_path(self):
        project_root = Path(__file__).resolve().parents[1]
        script_path = project_root / 'agent' / 'gt_errors' / 'evaluate_run.py'
        original_path = list(sys.path)
        try:
            sys.path = [p for p in sys.path if p not in ('', str(project_root))]
            sys.path.insert(0, str(script_path.parent))
            runpy.run_path(str(script_path), run_name='gt_errors_eval_probe')
            self.assertIn(str(project_root), sys.path)
        finally:
            sys.path = original_path

    def test_gitlab_ci_editor_precondition_opens_monaco_editor_target_before_resolution(self):
        page = FakePage(gold_present=False, locator_count=1)

        actions = asyncio.run(
            _apply_known_page_preconditions(
                page,
                GITLAB_CI_EDITOR_URL,
                [[GITLAB_GL70_MONACO_SELECTOR]],
                timeout_ms=30_000,
            )
        )

        self.assertEqual(
            actions,
            [
                {
                    'type': 'click',
                    'selector': GITLAB_CI_CONFIGURE_SELECTOR,
                    'reason': 'open GitLab CI editor before resolving gold selectors',
                }
            ],
        )
        self.assertEqual(page.locator_calls, [GITLAB_CI_CONFIGURE_SELECTOR])
        self.assertEqual(page.clicks, [{'selector': GITLAB_CI_CONFIGURE_SELECTOR, 'timeout': 10_000}])
        self.assertEqual(page.wait_load_states, [{'state': 'networkidle', 'timeout': 8_000}])
        self.assertEqual(page.wait_functions[0]['groups'], [[GITLAB_GL70_MONACO_SELECTOR]])
        self.assertEqual(page.wait_functions[0]['timeout'], 12_000)

    def test_gitlab_ci_editor_precondition_does_not_click_for_unrelated_missing_gold(self):
        page = FakePage(gold_present=False, locator_count=1)

        actions = asyncio.run(
            _apply_known_page_preconditions(
                page,
                GITLAB_CI_EDITOR_URL,
                [['input[name=unrelated]']],
                timeout_ms=30_000,
            )
        )

        self.assertEqual(actions, [])
        self.assertEqual(page.locator_calls, [])
        self.assertEqual(page.clicks, [])

    def test_evaluate_run_refreshes_and_probes_auth_before_scoring_auth_required_task(self):
        with TemporaryDirectory() as tmp:
            run_dir = write_minimal_run_dir(Path(tmp))
            eval_auth_path = eval_auth_state_path_for_run(run_dir, 'gitlab')

            async def fake_refresh(site, output_path, headless=True):
                self.assertEqual(site, 'gitlab')
                self.assertEqual(output_path, eval_auth_path)
                self.assertTrue(headless)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text('{}\n', encoding='utf-8')
                return output_path

            async def fake_resolve(**kwargs):
                self.assertEqual(kwargs['storage_state_path'], eval_auth_path)
                return {
                    'start_url': kwargs['start_url'],
                    'final_url': kwargs['start_url'],
                    'http_status': 200,
                    'precondition_actions': [],
                    'selector_resolutions': {
                        'gold': {'input.gold': ['same-node']},
                        'agent': {'input.agent': ['same-node']},
                    },
                    'selector_errors': [],
                }

            with patch('agent.gt_errors.evaluate_run.refresh_eval_auth_state', side_effect=fake_refresh) as refresh, patch(
                'agent.gt_errors.evaluate_run.probe_eval_auth_state', new=AsyncMock(return_value=(True, 'ok'))
            ) as probe, patch('agent.gt_errors.evaluate_run.resolve_selectors_on_page', side_effect=fake_resolve) as resolve:
                result = asyncio.run(evaluate_run_dir(run_dir))

            refresh.assert_awaited_once()
            probe.assert_awaited_once_with('gitlab', eval_auth_path)
            resolve.assert_awaited_once()
            self.assertEqual(result['storage_state_file'], str(eval_auth_path))
            self.assertEqual(
                result['auth'],
                {
                    'mode': 'fresh',
                    'site': 'gitlab',
                    'storage_state_file': str(eval_auth_path),
                    'probe_ok': True,
                    'probe_reason': 'ok',
                },
            )
            self.assertTrue(result['overall_pass'])

    def test_evaluate_run_reports_auth_probe_error_without_scoring(self):
        with TemporaryDirectory() as tmp:
            run_dir = write_minimal_run_dir(Path(tmp))
            eval_auth_path = eval_auth_state_path_for_run(run_dir, 'gitlab')

            async def fake_refresh(site, output_path, headless=True):
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text('{}\n', encoding='utf-8')
                return output_path

            with patch('agent.gt_errors.evaluate_run.refresh_eval_auth_state', side_effect=fake_refresh), patch(
                'agent.gt_errors.evaluate_run.probe_eval_auth_state', new=AsyncMock(return_value=(False, 'redirected to login'))
            ), patch('agent.gt_errors.evaluate_run.resolve_selectors_on_page', new=AsyncMock()) as resolve:
                result = asyncio.run(evaluate_run_dir(run_dir))

            resolve.assert_not_awaited()
            self.assertFalse(result['overall_pass'])
            self.assertTrue(result['evaluator_error'])
            self.assertEqual(result['error_type'], 'auth_probe')
            self.assertEqual(result['storage_state_file'], str(eval_auth_path))
            self.assertEqual(result['auth']['mode'], 'fresh')
            self.assertEqual(result['auth']['site'], 'gitlab')
            self.assertFalse(result['auth']['probe_ok'])
            self.assertEqual(result['auth']['probe_reason'], 'redirected to login')

    def test_l1_issue_matches_gold_selector_and_family(self):
        response = {
            'verdict': 'issue_found',
            'selector': 'input.agent',
            'target': 'the input',
            'issue_type': 'error_suggestion',
            'observed_behavior': 'invalid value lacks guidance',
            'evidence': 'validation message lacks expected format',
        }
        result = evaluate_response_against_rule(
            response,
            single_rule(),
            {'gold': {'input.gold': ['e1']}, 'agent': {'input.agent': ['e1']}},
        )

        self.assertTrue(result['overall_pass'])
        self.assertTrue(result['verdict_match'])
        self.assertTrue(result['selector_match'])
        self.assertTrue(result['issue_type_match'])
        self.assertEqual(result['normalization_warnings'], [])

    def test_e4_message_node_selector_does_not_match_gold_target_selector(self):
        response = {
            'verdict': 'issue_found',
            'selector': 'p.gl-field-error',
            'target': 'the rendered error message',
            'issue_type': 'status_messages',
            'observed_behavior': 'message is not live',
            'evidence': 'message lacks aria-live',
        }
        result = evaluate_response_against_rule(
            response,
            single_rule(issue_family='status_messages'),
            {'gold': {'input.gold': ['target-input']}, 'agent': {'p.gl-field-error': ['message-node']}},
        )

        self.assertFalse(result['overall_pass'])
        self.assertFalse(result['selector_match'])
        self.assertEqual(result['issue_results'][0]['selector_relation'], 'mismatch')
        self.assertTrue(result['issue_results'][0]['issue_type_match'])

    def test_multi_gold_matches_each_error_issue_once(self):
        rule = {
            'task_level': 'level3',
            'gold': {
                'expected_verdict': 'issue_found',
                'issues': [
                    {
                        'issue_id': 'e1-source-url',
                        'target': {'selector': 'input.source-url'},
                        'criterion': {'issue_family': 'status_messages'},
                    },
                    {
                        'issue_id': 'e2-date-format',
                        'target': {'selector': 'input.date'},
                        'criterion': {'issue_family': 'error_suggestion'},
                    },
                ],
            },
        }
        response = {
            'verdict': 'issue_found',
            'issues': [
                {'selector': 'input.date.agent', 'issue_type': 'error_suggestion', 'target': 'date'},
                {'selector': 'input.source-url.agent', 'issue_type': 'status_messages', 'target': 'url'},
            ],
        }
        result = evaluate_response_against_rule(
            response,
            rule,
            {
                'gold': {'input.source-url': ['url'], 'input.date': ['date']},
                'agent': {'input.source-url.agent': ['url'], 'input.date.agent': ['date']},
            },
        )

        self.assertTrue(result['overall_pass'])
        self.assertEqual(result['expected_count'], 2)
        self.assertEqual(result['reported_count'], 2)
        self.assertEqual(result['matched_count'], 2)
        self.assertEqual(result['missing_gold'], [])
        self.assertEqual(result['extra_issues'], [])

    def test_multi_gold_extra_issue_fails_overall_and_reports_precision(self):
        rule = {
            'task_level': 'level2',
            'gold': {
                'expected_verdict': 'issue_found',
                'issues': [
                    {
                        'issue_id': 'e2-email',
                        'target': {'selector': 'input.email'},
                        'criterion': {'issue_family': 'error_suggestion'},
                    }
                ],
            },
        }
        response = {
            'verdict': 'issue_found',
            'issues': [
                {'selector': 'input.email.agent', 'issue_type': 'error_suggestion', 'target': 'email'},
                {'selector': 'input.other', 'issue_type': 'error_suggestion', 'target': 'other'},
            ],
        }
        result = evaluate_response_against_rule(
            response,
            rule,
            {
                'gold': {'input.email': ['email']},
                'agent': {'input.email.agent': ['email'], 'input.other': ['other']},
            },
        )

        self.assertFalse(result['overall_pass'])
        self.assertEqual(result['matched_count'], 1)
        self.assertEqual(result['extra_issues'], [1])
        self.assertEqual(result['recall'], 1.0)
        self.assertEqual(result['precision'], 0.5)

    def test_pass_l1_no_issue_found_passes_but_issue_found_is_false_positive(self):
        rule = single_rule(
            issue_family='error_identification',
            expected_verdict='no_issue_found',
            issue_present=False,
        )

        clean = evaluate_response_against_rule(
            {'verdict': 'no_issue_found'},
            rule,
            {'gold': {'input.gold': ['e1']}, 'agent': {}},
        )
        self.assertTrue(clean['overall_pass'])

        false_positive = evaluate_response_against_rule(
            {
                'verdict': 'issue_found',
                'selector': 'input.agent',
                'target': 'the input',
                'issue_type': 'error_identification',
                'observed_behavior': 'still reports old issue',
                'evidence': 'old issue evidence',
            },
            rule,
            {'gold': {'input.gold': ['e1']}, 'agent': {'input.agent': ['e1']}},
        )

        self.assertFalse(false_positive['overall_pass'])
        self.assertFalse(false_positive['verdict_match'])

    def test_issues_found_verdict_is_normalized_with_warning(self):
        response = {
            'verdict': 'issues_found',
            'issues': [
                {'selector': 'input.agent', 'issue_type': 'error_suggestion', 'target': 'input'},
            ],
        }
        rule = {
            'task_level': 'level2',
            'gold': {
                'expected_verdict': 'issue_found',
                'issues': [
                    {
                        'issue_id': 'e2-input',
                        'target': {'selector': 'input.gold'},
                        'criterion': {'issue_family': 'error_suggestion'},
                    }
                ],
            },
        }

        issues = normalize_issues(response, rule)
        result = evaluate_response_against_rule(
            response,
            rule,
            {'gold': {'input.gold': ['e1']}, 'agent': {'input.agent': ['e1']}},
        )

        self.assertEqual(len(issues), 1)
        self.assertTrue(result['overall_pass'])
        self.assertEqual(result['observed_verdict'], 'issue_found')
        self.assertEqual(
            result['normalization_warnings'],
            [{'field': 'verdict', 'from': 'issues_found', 'to': 'issue_found'}],
        )

    def test_missing_gold_resolution_is_explicit_evaluator_error(self):
        response = {
            'verdict': 'issue_found',
            'selector': 'input.agent',
            'target': 'the input',
            'issue_type': 'error_suggestion',
            'observed_behavior': 'invalid value lacks guidance',
            'evidence': 'validation message lacks expected format',
        }

        result = evaluate_response_against_rule(
            response,
            single_rule(),
            {'gold': {'input.gold': []}, 'agent': {'input.agent': ['e1']}},
        )

        self.assertFalse(result['overall_pass'])
        self.assertTrue(result['evaluator_error'])
        self.assertEqual(result['error_type'], 'gold_resolution')
        self.assertEqual(result['gold_resolution_errors'][0]['reason'], 'no_gold_elements')

    def test_issue_type_accepts_wcag_and_requirement_aliases(self):
        self.assertTrue(
            issue_type_matches(
                'WCAG 3.3.3 Error Suggestion (missing correction suggestion)',
                single_rule(issue_family='error_suggestion'),
            )['match']
        )
        self.assertTrue(
            issue_type_matches(
                'WCAG 4.1.3 Status Messages: validation message not programmatically determinable',
                single_rule(issue_family='status_messages'),
            )['match']
        )
        self.assertTrue(
            issue_type_matches(
                'E.1_input_error_not_programmatically_identified',
                single_rule(issue_family='error_identification'),
            )['match']
        )
        self.assertTrue(
            issue_type_matches(
                'WCAG 3.3.4 Error Prevention (Legal, Financial, Data)',
                single_rule(issue_family='error_prevention'),
            )['match']
        )
        self.assertTrue(
            issue_type_matches(
                'E.3 error prevention: missing confirmation before data deletion',
                single_rule(issue_family='error_prevention'),
            )['match']
        )

    def test_issue_type_alias_does_not_cross_match_error_families(self):
        result = issue_type_matches(
            'E.1_input_error_not_programmatically_identified',
            single_rule(issue_family='status_messages'),
        )

        self.assertFalse(result['match'])
        self.assertEqual(result['observed_family'], 'error_identification')

        e3_cross = issue_type_matches(
            'E.3 error prevention missing review step',
            single_rule(issue_family='error_suggestion'),
        )
        self.assertFalse(e3_cross['match'])
        self.assertEqual(e3_cross['observed_family'], 'error_prevention')


if __name__ == '__main__':
    unittest.main()
