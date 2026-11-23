import unittest

import asyncio
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import AsyncMock, patch

from agent.gt_links.evaluate_run import (
    _resolve_one_selector,
    compare_selector_sets,
    evaluate_run_dir,
    evaluate_response_against_rule,
    eval_auth_state_path_for_run,
    issue_type_matches,
    normalize_issues,
)


def write_minimal_links_run_dir(root: Path) -> Path:
    run_dir = root / 'run'
    run_dir.mkdir(parents=True)
    stale_auth_path = run_dir / 'stale_agent_auth.storage_state.json'
    stale_auth_path.write_text('{}\n', encoding='utf-8')
    (run_dir / 'task.snapshot.yaml').write_text(
        '\n'.join(
            [
                'task_id: gitlab.gl01.lf.test.verify.level1.v1',
                'instance_id: gitlab.gl01.lf.test',
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
                'task_id: gitlab.gl01.lf.test.verify.level1.v1',
                'instance_id: gitlab.gl01.lf.test',
                'task_level: level1',
                'page:',
                '  site: gitlab',
                '  start_url: http://localhost:8023/dashboard/projects',
                'gold:',
                '  issue_present: true',
                '  expected_verdict: issue_found',
                '  target:',
                '    selector: a.gold',
                '  criterion:',
                '    issue_family: link_function',
                '',
            ]
        ),
        encoding='utf-8',
    )
    (run_dir / 'final-response.json').write_text(
        json.dumps(
            {
                'verdict': 'issue_found',
                'selector': 'a.agent',
                'target': 'link target',
                'issue_type': 'link_function',
                'observed_behavior': 'link behaves like a widget without role',
                'evidence': 'activation opens menu in place',
            }
        )
        + '\n',
        encoding='utf-8',
    )
    (run_dir / 'meta.json').write_text(json.dumps({'auth_state_file': str(stale_auth_path)}) + '\n', encoding='utf-8')
    return run_dir


class _FakeSelectorPage:
    def __init__(self, responses):
        self.responses = list(responses)
        self.waits = []

    async def eval_on_selector_all(self, selector, script):
        response = self.responses.pop(0) if self.responses else []
        if isinstance(response, Exception):
            raise response
        return response

    async def wait_for_timeout(self, timeout_ms):
        self.waits.append(timeout_ms)
        await asyncio.sleep(timeout_ms / 1000)


class LinksEvaluateRunUnitTest(unittest.TestCase):
    def test_evaluate_run_refreshes_and_probes_auth_before_scoring_auth_required_task(self):
        with TemporaryDirectory() as tmp:
            run_dir = write_minimal_links_run_dir(Path(tmp))
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
                        'gold': {'a.gold': ['same-node']},
                        'agent': {'a.agent': ['same-node']},
                    },
                    'selector_errors': [],
                }

            with patch('agent.gt_links.evaluate_run.refresh_eval_auth_state', side_effect=fake_refresh) as refresh, patch(
                'agent.gt_links.evaluate_run.probe_eval_auth_state', new=AsyncMock(return_value=(True, 'ok'))
            ) as probe, patch('agent.gt_links.evaluate_run.resolve_selectors_on_page', side_effect=fake_resolve) as resolve:
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
            run_dir = write_minimal_links_run_dir(Path(tmp))
            eval_auth_path = eval_auth_state_path_for_run(run_dir, 'gitlab')

            async def fake_refresh(site, output_path, headless=True):
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text('{}\n', encoding='utf-8')
                return output_path

            with patch('agent.gt_links.evaluate_run.refresh_eval_auth_state', side_effect=fake_refresh), patch(
                'agent.gt_links.evaluate_run.probe_eval_auth_state', new=AsyncMock(return_value=(False, 'redirected to login'))
            ), patch('agent.gt_links.evaluate_run.resolve_selectors_on_page', new=AsyncMock()) as resolve:
                result = asyncio.run(evaluate_run_dir(run_dir))

            resolve.assert_not_awaited()
            self.assertFalse(result['overall_pass'])
            self.assertTrue(result['evaluator_error'])
            self.assertEqual(result['error_type'], 'auth_probe')
            self.assertEqual(result['storage_state_file'], str(eval_auth_path))
            self.assertEqual(result['auth']['probe_reason'], 'redirected to login')

    def test_resolve_one_selector_waits_for_stable_nonempty_result(self):
        page = _FakeSelectorPage([
            [],
            ['e1'],
            [],
            ['e1', 'e2'],
            ['e1', 'e2'],
        ])

        ids, error = asyncio.run(
            _resolve_one_selector(
                page,
                'a.dynamic-grid-action',
                timeout_ms=2000,
                poll_ms=100,
                stable_ms=100,
            )
        )

        self.assertIsNone(error)
        self.assertEqual(ids, ['e1', 'e2'])
        self.assertGreaterEqual(len(page.waits), 4)

    def test_multi_gold_merge_matches_each_gold_issue_once_and_reports_metrics(self):
        rule = {
            'task_level': 'level3',
            'gold': {
                'expected_verdict': 'issue_found',
                'issues': [
                    {
                        'issue_id': 'gold-a',
                        'target': {'selector': 'a.gold-a'},
                        'criterion': {
                            'issue_family': 'link_function',
                            'assessment_requirement': 'L.1 Link Function',
                            'wcag': {'number': '4.1.2', 'name': 'Name, Role, Value'},
                        },
                    },
                    {
                        'issue_id': 'gold-b',
                        'target': {'selector': 'a.gold-b'},
                        'criterion': {
                            'issue_family': 'link_purpose',
                            'assessment_requirement': 'L.2 Link Purpose',
                            'wcag': {'number': '2.4.4', 'name': 'Link Purpose (In Context)'},
                        },
                    },
                ],
            },
        }
        response = {
            'verdict': 'issue_found',
            'issues': [
                {'selector': 'a.agent-b-subset', 'issue_type': 'link_purpose', 'target': 'b'},
                {'selector': 'a.agent-a', 'issue_type': 'link_function', 'target': 'a'},
            ],
        }
        selector_resolutions = {
            'gold': {'a.gold-a': ['e1'], 'a.gold-b': ['e2', 'e3']},
            'agent': {'a.agent-a': ['e1'], 'a.agent-b-subset': ['e2']},
        }

        result = evaluate_response_against_rule(response, rule, selector_resolutions)

        self.assertTrue(result['overall_pass'])
        self.assertEqual(result['expected_count'], 2)
        self.assertEqual(result['reported_count'], 2)
        self.assertEqual(result['matched_count'], 2)
        self.assertEqual(result['recall'], 1.0)
        self.assertEqual(result['precision'], 1.0)
        self.assertEqual(result['missing_gold'], [])
        self.assertEqual(result['extra_issues'], [])
        self.assertEqual(result['gold_issue_results'][1]['matched_issue_index'], 0)

    def test_multi_gold_merge_rejects_extra_issues_outside_gold_inventory(self):
        rule = {
            'task_level': 'level2',
            'gold': {
                'expected_verdict': 'issue_found',
                'issues': [
                    {
                        'issue_id': 'gold-a',
                        'target': {'selector': 'a.gold-a'},
                        'criterion': {
                            'issue_family': 'link_purpose',
                            'assessment_requirement': 'L.2 Link Purpose',
                            'wcag': {'number': '2.4.4', 'name': 'Link Purpose (In Context)'},
                        },
                    }
                ],
            },
        }
        response = {
            'verdict': 'issue_found',
            'issues': [
                {'selector': 'a.agent-a', 'issue_type': 'link_purpose', 'target': 'a'},
                {'selector': 'a.outside', 'issue_type': 'link_purpose', 'target': 'outside'},
            ],
        }
        selector_resolutions = {
            'gold': {'a.gold-a': ['e1']},
            'agent': {'a.agent-a': ['e1'], 'a.outside': ['e99']},
        }

        result = evaluate_response_against_rule(response, rule, selector_resolutions)

        self.assertFalse(result['overall_pass'])
        self.assertEqual(result['matched_count'], 1)
        self.assertEqual(result['reported_count'], 2)
        self.assertEqual(result['precision'], 0.5)
        self.assertEqual(result['recall'], 1.0)
        self.assertEqual(result['extra_issues'], [1])

    def test_multi_gold_metrics_deduplicate_agent_reports_for_same_gold_group(self):
        rule = {
            'task_level': 'level2',
            'gold': {
                'expected_verdict': 'issue_found',
                'issues': [
                    {
                        'issue_id': 'read-details-group',
                        'target': {'selector': 'a.read-details'},
                        'criterion': {
                            'issue_family': 'link_purpose',
                            'assessment_requirement': 'L.2 Link Purpose',
                            'wcag': {'number': '2.4.4', 'name': 'Link Purpose (In Context)'},
                        },
                    },
                    {
                        'issue_id': 'remove-group',
                        'target': {'selector': 'a.remove'},
                        'criterion': {
                            'issue_family': 'link_purpose',
                            'assessment_requirement': 'L.2 Link Purpose',
                            'wcag': {'number': '2.4.4', 'name': 'Link Purpose (In Context)'},
                        },
                    },
                ],
            },
        }
        response = {
            'verdict': 'issue_found',
            'issues': [
                {'selector': 'a.remove-first', 'issue_type': 'link_purpose', 'target': 'remove first row'},
                {'selector': 'a.remove-second', 'issue_type': 'link_purpose', 'target': 'remove second row'},
            ],
        }
        selector_resolutions = {
            'gold': {'a.read-details': ['e-read'], 'a.remove': ['e-remove-1', 'e-remove-2']},
            'agent': {'a.remove-first': ['e-remove-1'], 'a.remove-second': ['e-remove-2']},
        }

        result = evaluate_response_against_rule(response, rule, selector_resolutions)

        self.assertFalse(result['overall_pass'])
        self.assertEqual(result['expected_count'], 2)
        self.assertEqual(result['raw_reported_count'], 2)
        self.assertEqual(result['reported_count'], 1)
        self.assertEqual(result['matched_count'], 1)
        self.assertEqual(result['recall'], 0.5)
        self.assertEqual(result['precision'], 1.0)
        self.assertEqual(result['missing_gold'], ['read-details-group'])
        self.assertEqual(result['extra_issues'], [])
        self.assertEqual(result['duplicate_matched_issue_indices'], [1])

    def test_multi_gold_merge_reports_missing_gold_issues(self):
        rule = {
            'task_level': 'level3',
            'gold': {
                'expected_verdict': 'issue_found',
                'issues': [
                    {
                        'issue_id': 'gold-a',
                        'target': {'selector': 'a.gold-a'},
                        'criterion': {
                            'issue_family': 'link_function',
                            'assessment_requirement': 'L.1 Link Function',
                            'wcag': {'number': '4.1.2', 'name': 'Name, Role, Value'},
                        },
                    },
                    {
                        'issue_id': 'gold-b',
                        'target': {'selector': 'a.gold-b'},
                        'criterion': {
                            'issue_family': 'link_purpose',
                            'assessment_requirement': 'L.2 Link Purpose',
                            'wcag': {'number': '2.4.4', 'name': 'Link Purpose (In Context)'},
                        },
                    },
                ],
            },
        }
        response = {
            'verdict': 'issue_found',
            'issues': [{'selector': 'a.agent-a', 'issue_type': 'link_function', 'target': 'a'}],
        }
        selector_resolutions = {
            'gold': {'a.gold-a': ['e1'], 'a.gold-b': ['e2']},
            'agent': {'a.agent-a': ['e1']},
        }

        result = evaluate_response_against_rule(response, rule, selector_resolutions)

        self.assertFalse(result['overall_pass'])
        self.assertEqual(result['matched_count'], 1)
        self.assertEqual(result['recall'], 0.5)
        self.assertEqual(result['precision'], 1.0)
        self.assertEqual(result['missing_gold'], ['gold-b'])


    def test_multi_gold_element_expanded_counts_partial_group_coverage(self):
        rule = {
            'task_level': 'level2',
            'gold': {
                'expected_verdict': 'issue_found',
                'issues': [
                    {
                        'issue_id': 'admin-left-nav',
                        'target': {'selector': 'a.gold-nav'},
                        'criterion': {'issue_family': 'link_function'},
                    }
                ],
            },
        }
        response = {
            'verdict': 'issue_found',
            'issues': [{'selector': 'a.agent-sales', 'issue_type': 'link_function', 'target': 'Sales'}],
        }
        selector_resolutions = {
            'gold': {'a.gold-nav': ['e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8']},
            'agent': {'a.agent-sales': ['e1']},
        }

        result = evaluate_response_against_rule(response, rule, selector_resolutions)

        self.assertEqual(result['matched_count'], 1)
        expanded = result['element_expanded']
        self.assertEqual(expanded['expected_elements'], 8)
        self.assertEqual(expanded['matched_elements'], 1)
        self.assertEqual(expanded['reported_elements'], 1)
        self.assertEqual(expanded['extra_elements'], 0)
        self.assertEqual(expanded['recall'], 0.125)
        self.assertEqual(expanded['precision'], 1.0)
        self.assertEqual(expanded['per_gold_issue'][0]['matched_element_count'], 1)
        self.assertEqual(expanded['per_gold_issue'][0]['matched_agent_issue_indices'], [0])

    def test_multi_gold_element_expanded_partially_credits_mixed_selector(self):
        rule = {
            'task_level': 'level2',
            'gold': {
                'expected_verdict': 'issue_found',
                'issues': [
                    {
                        'issue_id': 'admin-left-nav',
                        'target': {'selector': 'a.gold-nav'},
                        'criterion': {'issue_family': 'link_function'},
                    }
                ],
            },
        }
        response = {
            'verdict': 'issue_found',
            'issues': [{'selector': 'a.agent-mixed', 'issue_type': 'link_function', 'target': 'mixed'}],
        }
        selector_resolutions = {
            'gold': {'a.gold-nav': ['e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8']},
            'agent': {'a.agent-mixed': ['e1', 'e2', 'e3', 'x1', 'x2']},
        }

        result = evaluate_response_against_rule(response, rule, selector_resolutions)

        self.assertEqual(result['matched_count'], 0)
        self.assertEqual(result['extra_issues'], [0])
        expanded = result['element_expanded']
        self.assertEqual(expanded['expected_elements'], 8)
        self.assertEqual(expanded['matched_elements'], 3)
        self.assertEqual(expanded['reported_elements'], 5)
        self.assertEqual(expanded['extra_elements'], 2)
        self.assertEqual(expanded['recall'], 0.375)
        self.assertEqual(expanded['precision'], 0.6)

    def test_multi_gold_element_expanded_deduplicates_repeated_elements_and_counts_unresolved(self):
        rule = {
            'task_level': 'level2',
            'gold': {
                'expected_verdict': 'issue_found',
                'issues': [
                    {
                        'issue_id': 'admin-left-nav',
                        'target': {'selector': 'a.gold-nav'},
                        'criterion': {'issue_family': 'link_function'},
                    }
                ],
            },
        }
        response = {
            'verdict': 'issue_found',
            'issues': [
                {'selector': 'a.agent-sales', 'issue_type': 'link_function', 'target': 'Sales'},
                {'selector': 'a.agent-sales-again', 'issue_type': 'link_function', 'target': 'Sales again'},
                {'selector': 'a.agent-unresolved', 'issue_type': 'link_function', 'target': 'Unresolved'},
            ],
        }
        selector_resolutions = {
            'gold': {'a.gold-nav': ['e1', 'e2']},
            'agent': {'a.agent-sales': ['e1'], 'a.agent-sales-again': ['e1'], 'a.agent-unresolved': []},
        }

        result = evaluate_response_against_rule(response, rule, selector_resolutions)

        self.assertEqual(result['matched_count'], 1)
        self.assertEqual(result['duplicate_matched_issue_indices'], [1])
        self.assertEqual(result['extra_issues'], [2])
        expanded = result['element_expanded']
        self.assertEqual(expanded['expected_elements'], 2)
        self.assertEqual(expanded['matched_elements'], 1)
        self.assertEqual(expanded['reported_elements'], 2)
        self.assertEqual(expanded['reported_elements_distinct'], 2)
        self.assertEqual(expanded['reported_elements_raw'], 3)
        self.assertEqual(expanded['extra_elements'], 1)
        self.assertEqual(expanded['duplicate_reported_elements'], 1)
        self.assertEqual(expanded['unresolved_reported_issues'], 1)
        self.assertEqual(expanded['unresolved_reported_units'], 1)
        self.assertEqual(expanded['recall'], 0.5)
        self.assertEqual(expanded['precision'], 0.5)

    def test_selector_set_accepts_exact_match(self):
        result = compare_selector_sets(gold=["a#one", "a#two"], agent=["a#one", "a#two"])

        self.assertTrue(result["match"])
        self.assertEqual(result["missing_gold"], [])
        self.assertEqual(result["extra_agent"], [])

    def test_selector_set_accepts_agent_subset_of_gold(self):
        result = compare_selector_sets(gold=["a#one", "a#two", "a#three"], agent=["a#two"])

        self.assertTrue(result["match"])
        self.assertEqual(result["extra_agent"], [])

    def test_selector_set_rejects_agent_outside_gold(self):
        result = compare_selector_sets(gold=["a#one", "a#two"], agent=["a#one", "a#outside"])

        self.assertFalse(result["match"])
        self.assertEqual(result["extra_agent"], ["a#outside"])

    def test_issue_type_matches_canonical_family_only(self):
        rule = {
            "gold": {
                "issue_type": ["WCAG 2.4.4 Link Purpose (In Context)"],
                "criterion": {
                    "issue_family": "link_purpose",
                    "assessment_requirement": "L.2 Link Purpose",
                    "wcag": {"number": "2.4.4", "name": "Link Purpose (In Context)"},
                },
            }
        }

        result = issue_type_matches("link_purpose", rule)

        self.assertTrue(result["match"])
        self.assertEqual(result["method"], "issue_family")

    def test_issue_type_rejects_wcag_requirement_and_prose_text(self):
        rule = {
            "gold": {
                "issue_type": ["WCAG 2.4.4 Link Purpose (In Context)"],
                "criterion": {
                    "issue_family": "link_purpose",
                    "assessment_requirement": "L.2 Link Purpose",
                    "wcag": {"number": "2.4.4", "name": "Link Purpose (In Context)"},
                },
            }
        }

        self.assertFalse(issue_type_matches("WCAG 2.4.4", rule)["match"])
        self.assertFalse(issue_type_matches("L.2 Link Purpose", rule)["match"])
        self.assertFalse(issue_type_matches("This is a link purpose failure", rule)["match"])

    def test_issue_type_rejects_unrelated_family(self):
        rule = {
            "gold": {
                "issue_type": ["WCAG 2.4.4 Link Purpose (In Context)"],
                "criterion": {
                    "issue_family": "link_purpose",
                    "assessment_requirement": "L.2 Link Purpose",
                    "wcag": {"number": "2.4.4", "name": "Link Purpose (In Context)"},
                },
            }
        }

        self.assertFalse(issue_type_matches("link_function", rule)["match"])

    def test_issue_type_ignores_removed_canonical_agent_fields(self):
        rule = {
            "gold": {
                "criterion": {
                    "issue_family": "link_purpose",
                    "assessment_requirement": "L.2 Link Purpose",
                    "wcag": {"number": "2.4.4", "name": "Link Purpose (In Context)"},
                },
            }
        }
        issue = {
            "issue_family": "link_function",
            "wcag_number": "4.1.2",
            "assessment_requirement": "L.1 Link Function",
            "issue_type": "link_purpose",
        }

        result = issue_type_matches(issue, rule)

        self.assertTrue(result["match"])
        self.assertEqual(result["method"], "issue_family")

    def test_issue_type_uses_only_issue_type_when_legacy_fields_conflict(self):
        rule = {
            "gold": {
                "criterion": {
                    "issue_family": "link_purpose",
                    "assessment_requirement": "L.2 Link Purpose",
                    "wcag": {"number": "2.4.4", "name": "Link Purpose (In Context)"},
                },
            }
        }
        issue = {
            "issue_family": "link_function",
            "wcag_number": "4.1.2",
            "assessment_requirement": "L.1 Link Function",
            "issue_type": "link_purpose",
        }

        result = issue_type_matches(issue, rule)

        self.assertTrue(result["match"])
        self.assertEqual(result["method"], "issue_family")

    def test_normalize_issues_supports_l1_and_multiissue_outputs(self):
        l1 = {"verdict": "issue_found", "selector": "a#one", "target": "one", "issue_type": "link_purpose"}
        l2 = {"verdict": "issue_found", "issues": [{"selector": "a#two", "target": "two", "issue_type": "link_purpose"}]}

        self.assertEqual(normalize_issues(l1), [l1])
        self.assertEqual(normalize_issues(l2), l2["issues"])

    def test_normalize_issues_rejects_unsupported_top_level_fields(self):
        with self.assertRaisesRegex(ValueError, "unsupported fields.*findings"):
            normalize_issues({"verdict": "confirmed", "findings": []})

    def test_normalize_issues_rejects_unsupported_issue_fields(self):
        response = {
            "verdict": "issue_found",
            "issues": [
                {
                    "selector": "a#one",
                    "target": "one",
                    "issue_type": "link_purpose",
                    "finding_id": "legacy",
                }
            ],
        }
        with self.assertRaisesRegex(ValueError, "unsupported fields.*finding_id"):
            normalize_issues(response, {"task_level": "level2"})

    def test_no_issue_found_cannot_carry_reported_issues(self):
        response = {"verdict": "no_issue_found", "issues": [{"selector": "a#one"}]}
        with self.assertRaisesRegex(ValueError, "must not contain reported issues"):
            normalize_issues(response, {"task_level": "level2"})

    def test_single_gold_l2_passes_when_any_issue_matches(self):
        rule = {
            "task_level": "level2",
            "gold": {
                "expected_verdict": "issue_found",
                "issue_type": ["WCAG 2.4.4 Link Purpose (In Context)"],
                "target": {"selector": "a#gold"},
                "criterion": {
                    "issue_family": "link_purpose",
                    "assessment_requirement": "L.2 Link Purpose",
                    "wcag": {"number": "2.4.4", "name": "Link Purpose (In Context)"},
                },
            },
        }
        response = {
            "verdict": "issue_found",
            "issues": [
                {"selector": "a#other", "issue_type": "link_purpose", "target": "other"},
                {"selector": "a#gold", "issue_type": "link_purpose", "target": "gold"},
            ],
        }
        selector_resolutions = {
            "gold": {"a#gold": ["e1"]},
            "agent": {"a#other": ["e2"], "a#gold": ["e1"]},
        }

        result = evaluate_response_against_rule(response, rule, selector_resolutions)

        self.assertTrue(result["overall_pass"])
        self.assertEqual(result["matched_issue_index"], 1)

    def test_single_gold_l2_fails_when_no_issue_matches_gold_selector(self):
        rule = {
            "task_level": "level2",
            "gold": {
                "expected_verdict": "issue_found",
                "issue_type": ["WCAG 2.4.4 Link Purpose (In Context)"],
                "target": {"selector": "a#gold"},
                "criterion": {
                    "issue_family": "link_purpose",
                    "assessment_requirement": "L.2 Link Purpose",
                    "wcag": {"number": "2.4.4", "name": "Link Purpose (In Context)"},
                },
            },
        }
        response = {
            "verdict": "issue_found",
            "issues": [{"selector": "a#other", "issue_type": "link_purpose", "target": "other"}],
        }
        selector_resolutions = {
            "gold": {"a#gold": ["e1"]},
            "agent": {"a#other": ["e2"]},
        }

        result = evaluate_response_against_rule(response, rule, selector_resolutions)

        self.assertFalse(result["overall_pass"])
        self.assertFalse(result["selector_match"])


    def test_single_gold_issue_present_reports_evaluator_error_when_gold_selector_unresolved(self):
        rule = {
            'task_level': 'level1',
            'gold': {
                'issue_present': True,
                'expected_verdict': 'issue_found',
                'target': {'selector': 'a#gold'},
                'criterion': {'issue_family': 'link_purpose'},
            },
        }
        response = {
            'verdict': 'issue_found',
            'selector': 'a#gold',
            'issue_type': 'link_purpose',
            'target': 'gold',
        }
        selector_resolutions = {
            'gold': {'a#gold': []},
            'agent': {'a#gold': ['e1']},
        }

        result = evaluate_response_against_rule(response, rule, selector_resolutions)

        self.assertTrue(result['evaluator_error'])
        self.assertEqual(result['error_type'], 'gold_resolution')
        self.assertFalse(result['overall_pass'])
        self.assertEqual(result['gold_resolution_errors'][0]['selectors'], ['a#gold'])

    def test_multi_gold_issue_present_reports_evaluator_error_for_unresolved_gold_issue(self):
        rule = {
            'task_level': 'level3',
            'gold': {
                'issue_present': True,
                'expected_verdict': 'issue_found',
                'issues': [
                    {
                        'issue_id': 'resolved',
                        'target': {'selector': 'a#resolved'},
                        'criterion': {'issue_family': 'link_purpose'},
                    },
                    {
                        'issue_id': 'missing',
                        'target': {'selector': 'a#missing'},
                        'criterion': {'issue_family': 'link_purpose'},
                    },
                ],
            },
        }
        response = {
            'verdict': 'issue_found',
            'issues': [{'selector': 'a#resolved', 'issue_type': 'link_purpose', 'target': 'resolved'}],
        }
        selector_resolutions = {
            'gold': {'a#resolved': ['e1'], 'a#missing': []},
            'agent': {'a#resolved': ['e1']},
        }

        result = evaluate_response_against_rule(response, rule, selector_resolutions)

        self.assertTrue(result['evaluator_error'])
        self.assertEqual(result['error_type'], 'gold_resolution')
        self.assertFalse(result['overall_pass'])
        self.assertEqual(result['gold_resolution_errors'][0]['issue_id'], 'missing')


if __name__ == "__main__":
    unittest.main()


