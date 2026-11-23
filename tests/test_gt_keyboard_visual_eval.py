import unittest

from agent.gt_keyboard.tmp_visualize_keyboard_eval import _agent_items, _gold_items, _missing_items


def base_rule(issue_present=True):
    return {
        'gold': {
            'issue_present': issue_present,
            'expected_verdict': 'issue_found' if issue_present else 'no_issue_found',
            'target': {'selector': 'button.gold'},
            'criterion': {'issue_family': 'on_input'},
        }
    }


class KeyboardVisualEvalTest(unittest.TestCase):
    def test_visual_items_mark_l1_match(self):
        rule = base_rule()
        evaluation = {
            'matched_issue_index': 0,
            'expected_count': 1,
            'matched_count': 1,
            'issue_results': [
                {
                    'index': 0,
                    'selector_match': True,
                    'issue_type_match': True,
                    'issue_pass': True,
                }
            ],
        }
        response = {
            'verdict': 'issue_found',
            'selector': 'button.agent',
            'target': 'target',
            'issue_type': 'on_input',
            'observed_behavior': 'behavior',
            'evidence': 'evidence',
        }

        self.assertIn('matched', _gold_items(rule, evaluation)[0]['label'])
        agent = _agent_items(response, rule, evaluation)
        self.assertEqual(agent[0]['selector'], 'button.agent')
        self.assertIn('match -> GT#0', agent[0]['label'])
        self.assertEqual(_missing_items(rule, evaluation), [])

    def test_visual_items_mark_wrong_target_and_missing_gt(self):
        rule = base_rule()
        evaluation = {
            'expected_count': 1,
            'matched_count': 0,
            'issue_results': [
                {
                    'index': 0,
                    'selector_match': False,
                    'issue_type_match': True,
                    'issue_pass': False,
                }
            ],
        }
        response = {
            'verdict': 'issue_found',
            'selector': 'button.other',
            'target': 'target',
            'issue_type': 'on_input',
            'observed_behavior': 'behavior',
            'evidence': 'evidence',
        }

        self.assertIn('missing', _gold_items(rule, evaluation)[0]['label'])
        self.assertIn('wrong_target', _agent_items(response, rule, evaluation)[0]['label'])
        missing = _missing_items(rule, evaluation)
        self.assertEqual(missing[0]['selector'], 'button.gold')
        self.assertEqual(missing[0]['style'], 'dashed')

    def test_visual_items_mark_issue_type_mismatch(self):
        rule = base_rule()
        evaluation = {
            'expected_count': 1,
            'matched_count': 0,
            'issue_results': [
                {
                    'index': 0,
                    'selector_match': True,
                    'issue_type_match': False,
                    'issue_pass': False,
                }
            ],
        }
        response = {
            'verdict': 'issue_found',
            'selector': 'button.gold',
            'target': 'target',
            'issue_type': 'keyboard_nonreachable',
            'observed_behavior': 'behavior',
            'evidence': 'evidence',
        }

        self.assertIn('type_mismatch', _agent_items(response, rule, evaluation)[0]['label'])

    def test_clean_target_has_no_missing_overlay(self):
        rule = base_rule(issue_present=False)
        evaluation = {'expected_count': 0, 'matched_count': 0}

        self.assertIn('clean_target', _gold_items(rule, evaluation)[0]['label'])
        self.assertEqual(_missing_items(rule, evaluation), [])


if __name__ == '__main__':
    unittest.main()
