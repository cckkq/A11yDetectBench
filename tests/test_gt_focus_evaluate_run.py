import asyncio
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import AsyncMock, patch

from agent.gt_focus.evaluate_run import _apply_known_page_preconditions, evaluate_response_against_rule, evaluate_run_dir, eval_auth_state_path_for_run, issue_type_matches, normalize_issues


class FakeFocusLocator:
    def __init__(self, selector: str, page: 'FakeFocusPage'):
        self.selector = selector
        self.page = page

    @property
    def first(self):
        return self

    def nth(self, index):
        return self

    async def count(self):
        return 1 if self.selector in self.page.visible_selectors else 0

    async def is_visible(self, timeout=1000):
        return self.selector in self.page.visible_selectors

    async def scroll_into_view_if_needed(self, timeout=2000):
        return None

    async def click(self, timeout=5000):
        self.page.clicked.append(self.selector)
        self.page.handle_click(self.selector)

    async def fill(self, value, timeout=5000):
        self.page.filled.append((self.selector, value))
        self.page.field_values[self.selector] = value

    async def focus(self, timeout=5000):
        self.page.focused.append(self.selector)


class FakeFocusPage:
    def __init__(self):
        self.visible_selectors = {'button:has-text("Filters")'}
        self.clicked = []
        self.focused = []
        self.filled = []
        self.field_values = {}

    def handle_click(self, selector):
        if selector in {'button:has-text("Filters")', 'button[data-action="grid-filter-expand"]', '.admin__data-grid-header button.action-default:has-text("Filters")'}:
            self.visible_selectors.add('#notificationGrid_massaction-mass-select')
            self.visible_selectors.add('input[name="created_at[from]"]')
            self.visible_selectors.add('input[name="created_at[to]"]')
            self.visible_selectors.add('button[data-action="grid-filter-apply"]')
        if selector == 'button[data-action="grid-filter-apply"]':
            if self.field_values.get('input[name="created_at[from]"]'):
                self.visible_selectors.add('.admin__data-grid-filters-current button.action-remove')

    def locator(self, selector):
        return FakeFocusLocator(selector, self)

    async def wait_for_timeout(self, ms):
        return None

    async def wait_for_function(self, script, arg=None, timeout=0):
        return None

    async def evaluate(self, script, arg=None):
        if isinstance(arg, str):
            return arg in self.visible_selectors
        groups = arg if isinstance(arg, list) else []
        return all(any(selector in self.visible_selectors for selector in group) for group in groups)


def write_minimal_focus_run_dir(root: Path) -> Path:
    run_dir = root / 'run'
    run_dir.mkdir(parents=True)
    stale_auth_path = run_dir / 'stale_agent_auth.storage_state.json'
    stale_auth_path.write_text('{}\n', encoding='utf-8')
    (run_dir / 'task.snapshot.yaml').write_text(
        '\n'.join(
            [
                'task_id: gitlab.gl01.f21t3.test.verify.level1.v1',
                'instance_id: gitlab.gl01.f21t3.test',
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
                'task_id: gitlab.gl01.f21t3.test.verify.level1.v1',
                'instance_id: gitlab.gl01.f21t3.test',
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
                '    issue_family: visible_focus',
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
                'target': 'keyboard focused button',
                'issue_type': 'visible_focus',
                'observed_behavior': 'no visible focus indicator',
                'evidence': 'Tab reached the button without a visible ring',
            }
        )
        + '\n',
        encoding='utf-8',
    )
    (run_dir / 'meta.json').write_text(json.dumps({'auth_state_file': str(stale_auth_path)}) + '\n', encoding='utf-8')
    return run_dir


def l1_rule(family='visible_focus', verdict='issue_found', present=True):
    return {
        'task_level': 'level1',
        'gold': {
            'expected_verdict': verdict,
            'issue_present': present,
            'target': {'selector': 'button.gold'},
            'criterion': {'issue_family': family},
        },
    }


class FocusEvaluateRunUnitTest(unittest.TestCase):
    def test_magento_filter_precondition_opens_grid_filter_controls_before_resolution(self):
        page = FakeFocusPage()
        rule = {'task_id': 'shopping_admin.pa02.f21t6a.grid_small_selectors_no_visible_focus.verify.level3.v1'}

        actions = asyncio.run(
            _apply_known_page_preconditions(
                page,
                {},
                rule,
                [['#notificationGrid_massaction-mass-select']],
                timeout_ms=5000,
            )
        )

        self.assertEqual(page.clicked, ['button:has-text("Filters")'])
        self.assertEqual(actions[0]['type'], 'click')
        self.assertEqual(actions[0]['reason'], 'open Magento Admin grid filters')

    def test_pa04_precondition_recreates_purchase_date_active_filter_before_resolution(self):
        page = FakeFocusPage()
        rule = {
            'task_id': 'shopping_admin.pa04.focus_assessment.verify.level3.v1',
            'gold': {
                'issues': [
                    {
                        'issue_id': 'shopping_admin.pa04.f21t6a.grid_small_selectors_no_visible_focus',
                        'target': {'selector': '.admin__data-grid-filters-current button.action-remove'},
                        'criterion': {'issue_family': 'visible_focus'},
                    }
                ]
            },
        }

        actions = asyncio.run(
            _apply_known_page_preconditions(
                page,
                {},
                rule,
                [['.admin__data-grid-filters-current button.action-remove']],
                timeout_ms=5000,
            )
        )

        self.assertIn('button:has-text("Filters")', page.clicked)
        self.assertIn(('input[name="created_at[from]"]', 'not-a-date'), page.filled)
        self.assertIn('button[data-action="grid-filter-apply"]', page.clicked)
        self.assertIn('.admin__data-grid-filters-current button.action-remove', page.visible_selectors)
        self.assertNotIn('precondition_unresolved', [action['type'] for action in actions])

    def test_evaluate_run_refreshes_and_probes_auth_before_scoring_auth_required_task(self):
        with TemporaryDirectory() as tmp:
            run_dir = write_minimal_focus_run_dir(Path(tmp))
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
                    'selector_resolutions': {
                        'gold': {'button.gold': ['same-node']},
                        'agent': {'button.agent': ['same-node']},
                    },
                    'selector_errors': [],
                }

            with patch('agent.gt_focus.evaluate_run.refresh_eval_auth_state', side_effect=fake_refresh) as refresh, patch(
                'agent.gt_focus.evaluate_run.probe_eval_auth_state', new=AsyncMock(return_value=(True, 'ok'))
            ) as probe, patch('agent.gt_focus.evaluate_run.resolve_selectors_on_page', side_effect=fake_resolve) as resolve:
                result = asyncio.run(evaluate_run_dir(run_dir))

            refresh.assert_awaited_once()
            probe.assert_awaited_once_with('gitlab', eval_auth_path)
            resolve.assert_awaited_once()
            self.assertEqual(result['storage_state_file'], str(eval_auth_path))
            self.assertEqual(result['auth']['mode'], 'fresh')
            self.assertTrue(result['auth']['probe_ok'])
            self.assertTrue(result['overall_pass'])

    def test_evaluate_run_reports_auth_probe_error_without_scoring(self):
        with TemporaryDirectory() as tmp:
            run_dir = write_minimal_focus_run_dir(Path(tmp))
            eval_auth_path = eval_auth_state_path_for_run(run_dir, 'gitlab')

            async def fake_refresh(site, output_path, headless=True):
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text('{}\n', encoding='utf-8')
                return output_path

            with patch('agent.gt_focus.evaluate_run.refresh_eval_auth_state', side_effect=fake_refresh), patch(
                'agent.gt_focus.evaluate_run.probe_eval_auth_state', new=AsyncMock(return_value=(False, 'redirected to login'))
            ), patch('agent.gt_focus.evaluate_run.resolve_selectors_on_page', new=AsyncMock()) as resolve:
                result = asyncio.run(evaluate_run_dir(run_dir))

            resolve.assert_not_awaited()
            self.assertFalse(result['overall_pass'])
            self.assertTrue(result['evaluator_error'])
            self.assertEqual(result['error_type'], 'auth_probe')
            self.assertEqual(result['storage_state_file'], str(eval_auth_path))
            self.assertEqual(result['auth']['probe_reason'], 'redirected to login')

    def test_l1_and_pass_l1_use_selector_family_and_verdict(self):
        positive = evaluate_response_against_rule(
            {
                'verdict': 'issue_found',
                'selector': 'button.agent',
                'target': 'keyboard focused button',
                'issue_type': 'visible_focus',
                'observed_behavior': 'no rendered focus indicator',
                'evidence': 'Tab reached the button without a visible ring',
            },
            l1_rule(),
            {'gold': {'button.gold': ['e1']}, 'agent': {'button.agent': ['e1']}},
        )
        self.assertTrue(positive['overall_pass'])
        self.assertTrue(positive['selector_match'])
        self.assertTrue(positive['issue_type_match'])

        pass_rule = l1_rule(verdict='no_issue_found', present=False)
        clean = evaluate_response_against_rule({'verdict': 'no_issue_found'}, pass_rule, {'gold': {'button.gold': ['e1']}, 'agent': {}})
        self.assertTrue(clean['overall_pass'])

        false_positive = evaluate_response_against_rule(
            {
                'verdict': 'issue_found',
                'selector': 'button.agent',
                'target': 'keyboard focused button',
                'issue_type': 'visible_focus',
                'observed_behavior': 'old positive behavior',
                'evidence': 'old positive evidence',
            },
            pass_rule,
            {'gold': {'button.gold': ['e1']}, 'agent': {'button.agent': ['e1']}},
        )
        self.assertFalse(false_positive['overall_pass'])
        self.assertFalse(false_positive['verdict_match'])

    def test_multi_gold_merge_counts_missing_and_extra_issues(self):
        rule = {
            'task_level': 'level3',
            'gold': {
                'expected_verdict': 'issue_found',
                'issues': [
                    {'issue_id': 'f1', 'target': {'selector': 'button.no-ring'}, 'criterion': {'issue_family': 'visible_focus'}},
                    {'issue_id': 'f5', 'target': {'selector': 'button.split'}, 'criterion': {'issue_family': 'revealing_content'}},
                ],
            },
        }
        response = {
            'verdict': 'issue_found',
            'issues': [
                {'selector': 'button.no-ring.agent', 'issue_type': 'visible_focus', 'target': 'button'},
                {'selector': 'a.extra', 'issue_type': 'visible_focus', 'target': 'extra'},
            ],
        }
        result = evaluate_response_against_rule(
            response,
            rule,
            {
                'gold': {'button.no-ring': ['vf'], 'button.split': ['rc']},
                'agent': {'button.no-ring.agent': ['vf'], 'a.extra': ['extra']},
            },
        )
        self.assertFalse(result['overall_pass'])
        self.assertEqual(result['matched_count'], 1)
        self.assertEqual(result['missing_gold'], ['f5'])
        self.assertEqual(result['extra_issues'], [1])
        self.assertEqual(result['recall'], 0.5)
        self.assertEqual(result['precision'], 0.5)

    def test_issues_found_alias_and_focus_family_aliases_are_conservative(self):
        response = {'verdict': 'issues_found', 'issues': [{'selector': 'button.agent', 'issue_type': 'F.1 Visible Focus', 'target': 'button'}]}
        rule = {'task_level': 'level2', 'gold': {'expected_verdict': 'issue_found', 'issues': [{'issue_id': 'f1', 'target': {'selector': 'button.gold'}, 'criterion': {'issue_family': 'visible_focus'}}]}}
        self.assertEqual(len(normalize_issues(response, rule)), 1)
        result = evaluate_response_against_rule(response, rule, {'gold': {'button.gold': ['e1']}, 'agent': {'button.agent': ['e1']}})
        self.assertTrue(result['overall_pass'])
        self.assertEqual(result['observed_verdict'], 'issue_found')
        self.assertEqual(result['normalization_warnings'], [{'field': 'verdict', 'from': 'issues_found', 'to': 'issue_found'}])

        self.assertTrue(issue_type_matches('WCAG 2.4.7 Focus Visible', l1_rule())['match'])
        self.assertTrue(issue_type_matches('F.5 Revealing Content', l1_rule(family='revealing_content'))['match'])
        self.assertTrue(issue_type_matches('F.2 Focus Order', l1_rule(family='focus_order'))['match'])
        self.assertTrue(issue_type_matches('F.3 Closing Content', l1_rule(family='closing_content'))['match'])
        self.assertTrue(issue_type_matches('F.4 Modal Dialogs', l1_rule(family='modal_dialogs'))['match'])
        self.assertTrue(issue_type_matches('WCAG 2.4.11 Focus Not Obscured', l1_rule(family='focus_not_obscured'))['match'])
        cross = issue_type_matches('F.5 Revealing Content', l1_rule(family='visible_focus'))
        self.assertFalse(cross['match'])
        self.assertEqual(cross['observed_family'], 'revealing_content')

    def test_missing_gold_resolution_is_explicit_evaluator_error(self):
        result = evaluate_response_against_rule(
            {'verdict': 'issue_found', 'selector': 'button.agent', 'target': 'button', 'issue_type': 'visible_focus'},
            l1_rule(),
            {'gold': {'button.gold': []}, 'agent': {'button.agent': ['e1']}},
        )
        self.assertFalse(result['overall_pass'])
        self.assertTrue(result['evaluator_error'])
        self.assertEqual(result['error_type'], 'gold_resolution')
        self.assertEqual(result['gold_resolution_errors'][0]['reason'], 'no_gold_elements')


if __name__ == '__main__':
    unittest.main()
