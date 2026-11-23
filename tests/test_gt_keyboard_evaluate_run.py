import asyncio
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import AsyncMock, patch


from agent.gt_keyboard.evaluate_run import evaluate_response_against_rule, evaluate_run_dir, eval_auth_state_path_for_run, issue_type_matches, normalize_issues


def write_minimal_keyboard_run_dir(root: Path) -> Path:
    run_dir = root / 'run'
    run_dir.mkdir(parents=True)
    stale_auth_path = run_dir / 'stale_agent_auth.storage_state.json'
    stale_auth_path.write_text('{}\n', encoding='utf-8')
    (run_dir / 'task.snapshot.yaml').write_text(
        '\n'.join(
            [
                'task_id: gitlab.gl01.keyboard.test.verify.level1.v1',
                'instance_id: gitlab.gl01.keyboard.test',
                'start_url: http://localhost:8023/dashboard/projects',
                'auth_state_file: agent/gt/auth/gitlab.storage_state.json',
                '',
            ]
        ),
        encoding='utf-8',
    )
    (run_dir / 'evaluate-rule.snapshot.yaml').write_text(
        '\n'.join(
            [
                'task_id: gitlab.gl01.keyboard.test.verify.level1.v1',
                'instance_id: gitlab.gl01.keyboard.test',
                'task_level: level1',
                'page:',
                '  site: gitlab',
                '  start_url: http://localhost:8023/dashboard/projects',
                'gold:',
                '  issue_present: true',
                '  expected_verdict: issue_found',
                '  target:',
                '    selector: button.gold',
                '  criterion:',
                '    issue_family: keyboard_nonreachable',
                '',
            ]
        ),
        encoding='utf-8',
    )
    (run_dir / 'final-response.json').write_text(
        json.dumps(
            {
                'verdict': 'issue_found',
                'selector': 'button.agent',
                'target': 'keyboard target',
                'issue_type': 'keyboard_nonreachable',
                'observed_behavior': 'target cannot be reached by Tab',
                'evidence': 'Tab sequence skips the target',
            }
        )
        + '\n',
        encoding='utf-8',
    )
    (run_dir / 'meta.json').write_text(json.dumps({'auth_state_file': str(stale_auth_path)}) + '\n', encoding='utf-8')
    return run_dir


def single_rule(issue_family='keyboard_nonreachable', expected_verdict='issue_found', issue_present=True):
    return {
        'task_level': 'level1',
        'gold': {
            'expected_verdict': expected_verdict,
            'issue_present': issue_present,
            'target': {'selector': 'button.gold'},
            'criterion': {'issue_family': issue_family},
        },
    }


class KeyboardEvaluateRunUnitTest(unittest.TestCase):
    def test_evaluate_run_refreshes_and_probes_auth_before_scoring_auth_required_task(self):
        with TemporaryDirectory() as tmp:
            run_dir = write_minimal_keyboard_run_dir(Path(tmp))
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
                        'gold': {'button.gold': ['same-node']},
                        'agent': {'button.agent': ['same-node']},
                    },
                    'selector_errors': [],
                }

            with patch('agent.gt_keyboard.evaluate_run.refresh_eval_auth_state', side_effect=fake_refresh) as refresh, patch(
                'agent.gt_keyboard.evaluate_run.probe_eval_auth_state', new=AsyncMock(return_value=(True, 'ok'))
            ) as probe, patch('agent.gt_keyboard.evaluate_run.resolve_selectors_on_page', side_effect=fake_resolve) as resolve:
                result = asyncio.run(evaluate_run_dir(run_dir))

            refresh.assert_awaited_once()
            probe.assert_awaited_once_with('gitlab', eval_auth_path)
            resolve.assert_awaited_once()
            self.assertEqual(result['storage_state_file'], str(eval_auth_path))
            self.assertEqual(result['auth']['mode'], 'fresh')
            self.assertTrue(result['auth']['probe_ok'])
            self.assertTrue(result['overall_pass'])

    def test_evaluate_run_refreshes_fresh_auth_outside_run_dir(self):
        with TemporaryDirectory() as tmp:
            run_dir = write_minimal_keyboard_run_dir(Path(tmp))
            seen_auth_path: Path | None = None

            async def fake_refresh(site, output_path, headless=True):
                nonlocal seen_auth_path
                seen_auth_path = output_path
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text('{}\n', encoding='utf-8')
                return output_path

            async def fake_resolve(**kwargs):
                self.assertEqual(kwargs['storage_state_path'], seen_auth_path)
                return {
                    'start_url': kwargs['start_url'],
                    'final_url': kwargs['start_url'],
                    'http_status': 200,
                    'precondition_actions': [],
                    'selector_resolutions': {
                        'gold': {'button.gold': ['same-node']},
                        'agent': {'button.agent': ['same-node']},
                    },
                    'selector_errors': [],
                }

            with patch('agent.gt_keyboard.evaluate_run.refresh_eval_auth_state', side_effect=fake_refresh), patch(
                'agent.gt_keyboard.evaluate_run.probe_eval_auth_state', new=AsyncMock(return_value=(True, 'ok'))
            ), patch('agent.gt_keyboard.evaluate_run.resolve_selectors_on_page', side_effect=fake_resolve):
                result = asyncio.run(evaluate_run_dir(run_dir))

            self.assertIsNotNone(seen_auth_path)
            assert seen_auth_path is not None
            self.assertNotEqual(seen_auth_path.parent, run_dir)
            self.assertIn('eval_auth', seen_auth_path.parts)
            self.assertEqual(result['storage_state_file'], str(seen_auth_path))

    def test_evaluate_run_reports_auth_probe_error_without_scoring(self):
        with TemporaryDirectory() as tmp:
            run_dir = write_minimal_keyboard_run_dir(Path(tmp))
            eval_auth_path = eval_auth_state_path_for_run(run_dir, 'gitlab')

            async def fake_refresh(site, output_path, headless=True):
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text('{}\n', encoding='utf-8')
                return output_path

            with patch('agent.gt_keyboard.evaluate_run.refresh_eval_auth_state', side_effect=fake_refresh), patch(
                'agent.gt_keyboard.evaluate_run.probe_eval_auth_state', new=AsyncMock(return_value=(False, 'redirected to login'))
            ), patch('agent.gt_keyboard.evaluate_run.resolve_selectors_on_page', new=AsyncMock()) as resolve:
                result = asyncio.run(evaluate_run_dir(run_dir))

            resolve.assert_not_awaited()
            self.assertFalse(result['overall_pass'])
            self.assertTrue(result['evaluator_error'])
            self.assertEqual(result['error_type'], 'auth_probe')
            self.assertEqual(result['storage_state_file'], str(eval_auth_path))
            self.assertEqual(result['auth']['probe_reason'], 'redirected to login')

    def test_evaluate_run_records_response_format_error_as_agent_fail(self):
        with TemporaryDirectory() as tmp:
            run_dir = write_minimal_keyboard_run_dir(Path(tmp))
            (run_dir / 'final-response.json').write_text('{"raw": ""}\n', encoding='utf-8')

            with patch('agent.gt_keyboard.evaluate_run.refresh_eval_auth_state', new=AsyncMock()) as refresh, patch(
                'agent.gt_keyboard.evaluate_run.probe_eval_auth_state', new=AsyncMock()
            ) as probe, patch('agent.gt_keyboard.evaluate_run.resolve_selectors_on_page', new=AsyncMock()) as resolve:
                result = asyncio.run(evaluate_run_dir(run_dir))

            refresh.assert_not_awaited()
            probe.assert_not_awaited()
            resolve.assert_not_awaited()
            self.assertFalse(result['overall_pass'])
            self.assertFalse(result['evaluator_error'])
            self.assertEqual(result['error_type'], 'response_format_error')
            self.assertEqual(result['expected_verdict'], 'issue_found')
            self.assertEqual(result['observed_verdict'], '')

    def test_l1_issue_matches_gold_selector_and_family(self):
        response = {
            'verdict': 'issue_found',
            'selector': 'button.agent',
            'target': 'the keyboard target',
            'issue_type': 'keyboard_nonreachable',
            'observed_behavior': 'target cannot be reached by Tab',
            'evidence': 'Tab sequence skips the target',
        }
        result = evaluate_response_against_rule(
            response,
            single_rule(),
            {'gold': {'button.gold': ['e1']}, 'agent': {'button.agent': ['e1']}},
        )

        self.assertTrue(result['overall_pass'])
        self.assertTrue(result['verdict_match'])
        self.assertTrue(result['selector_match'])
        self.assertTrue(result['issue_type_match'])
        self.assertEqual(result['normalization_warnings'], [])

    def test_l1_rejects_multi_issue_shape(self):
        response = {
            'verdict': 'issue_found',
            'issues': [
                {'selector': 'button.agent', 'issue_type': 'keyboard_nonreachable', 'target': 'button'},
            ],
        }

        with self.assertRaisesRegex(ValueError, 'L1 Keyboard responses must use the single-issue output shape'):
            normalize_issues(response, single_rule())

    def test_pass_l1_no_issue_found_passes_but_issue_found_is_false_positive(self):
        rule = single_rule(issue_family='on_input', expected_verdict='no_issue_found', issue_present=False)

        clean = evaluate_response_against_rule(
            {'verdict': 'no_issue_found'},
            rule,
            {'gold': {'button.gold': ['e1']}, 'agent': {}},
        )
        self.assertTrue(clean['overall_pass'])

        false_positive = evaluate_response_against_rule(
            {
                'verdict': 'issue_found',
                'selector': 'button.agent',
                'target': 'the selector',
                'issue_type': 'on_input',
                'observed_behavior': 'old issue behavior',
                'evidence': 'old issue evidence',
            },
            rule,
            {'gold': {'button.gold': ['e1']}, 'agent': {'button.agent': ['e1']}},
        )

        self.assertFalse(false_positive['overall_pass'])
        self.assertFalse(false_positive['verdict_match'])

    def test_issues_found_verdict_is_normalized_with_warning(self):
        response = {
            'verdict': 'issues_found',
            'selector': 'button.agent',
            'target': 'button',
            'issue_type': 'WCAG 2.1.1 Keyboard',
            'observed_behavior': 'target cannot be reached by Tab',
            'evidence': 'Tab sequence skips the target',
        }

        issues = normalize_issues(response, single_rule())
        result = evaluate_response_against_rule(
            response,
            single_rule(),
            {'gold': {'button.gold': ['e1']}, 'agent': {'button.agent': ['e1']}},
        )

        self.assertEqual(len(issues), 1)
        self.assertTrue(result['overall_pass'])
        self.assertEqual(result['observed_verdict'], 'issue_found')
        self.assertEqual(result['normalization_warnings'], [{'field': 'verdict', 'from': 'issues_found', 'to': 'issue_found'}])

    def test_missing_gold_resolution_is_explicit_evaluator_error(self):
        response = {
            'verdict': 'issue_found',
            'selector': 'button.agent',
            'target': 'the keyboard target',
            'issue_type': 'keyboard_nonreachable',
            'observed_behavior': 'not reachable',
            'evidence': 'Tab skips it',
        }

        result = evaluate_response_against_rule(
            response,
            single_rule(),
            {'gold': {'button.gold': []}, 'agent': {'button.agent': ['e1']}},
        )

        self.assertFalse(result['overall_pass'])
        self.assertTrue(result['evaluator_error'])
        self.assertEqual(result['error_type'], 'gold_resolution')
        self.assertEqual(result['gold_resolution_errors'][0]['reason'], 'no_gold_elements')

    def test_issue_type_accepts_keyboard_aliases_without_cross_matching(self):
        self.assertTrue(issue_type_matches('WCAG 2.1.1 Keyboard', single_rule(issue_family='keyboard_nonreachable'))['match'])
        self.assertTrue(issue_type_matches('WCAG 3.2.2 On Input', single_rule(issue_family='on_input'))['match'])
        self.assertTrue(issue_type_matches('WCAG 2.1.4 Character Key Shortcuts', single_rule(issue_family='character_key_shortcuts'))['match'])
        self.assertTrue(issue_type_matches('WCAG 3.2.1 On Focus', single_rule(issue_family='on_focus'))['match'])
        trap = issue_type_matches('WCAG 2.1.2 No Keyboard Trap', single_rule(issue_family='keyboard_nonreachable'))
        self.assertTrue(trap['match'])
        self.assertEqual(trap['method'], 'keyboard_nonreachable_trap_subtype')

        cross = issue_type_matches('WCAG 3.2.2 On Input', single_rule(issue_family='keyboard_nonreachable'))
        self.assertFalse(cross['match'])
        self.assertEqual(cross['observed_family'], 'on_input')


if __name__ == '__main__':
    unittest.main()
