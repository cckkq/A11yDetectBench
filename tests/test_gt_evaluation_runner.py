import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from agent.gt.parallel_runner import append_status, load_completed_run_keys


class EvaluationRunnerStatusTest(unittest.TestCase):
    def test_shared_gt_package_no_longer_exposes_generic_runners(self):
        import agent.gt as gt_shared

        self.assertFalse(hasattr(gt_shared, "run_experiment"))
        self.assertFalse(hasattr(gt_shared, "run_experiment_parallel"))

    def test_task_id_for_run_prefers_task_yaml_identity(self):
        from agent.gt.evaluation_runner import task_id_for_run

        run = {
            "instance_id": "gitlab.gl11",
            "task_base": "gitlab.gl11.error_assessment",
            "task_variant": "verify.level3.v1",
            "task_id": "gitlab.gl11.e2.rule_violation_without_actionable_suggestion.verify.level3.v1",
        }

        self.assertEqual(
            task_id_for_run(run),
            "gitlab.gl11.e2.rule_violation_without_actionable_suggestion.verify.level3.v1",
        )

    def test_run_key_prefers_task_yaml_identity_for_resume(self):
        from agent.gt.parallel_runner import build_run_key

        run = {
            "instance_id": "gitlab.gl11",
            "task_base": "gitlab.gl11.error_assessment",
            "task_variant": "verify.level3.v1",
            "repeat_index": 2,
            "task_id": "gitlab.gl11.e2.rule_violation_without_actionable_suggestion.verify.level3.v1",
        }

        self.assertEqual(
            build_run_key(run),
            "gitlab.gl11.e2.rule_violation_without_actionable_suggestion.verify.level3.v1::repeat=2",
        )

    def test_resume_only_treats_official_evaluated_statuses_as_completed(self):
        with TemporaryDirectory() as temp_dir:
            status_path = Path(temp_dir) / "status.jsonl"
            append_status(status_path, {"run_key": "legacy-task-success", "status": "succeeded"})
            append_status(status_path, {"run_key": "agent-failed", "status": "failed"})
            append_status(status_path, {"run_key": "eval-precondition-bug", "status": "evaluator_error"})
            append_status(status_path, {"run_key": "clean-pass", "status": "evaluated_pass"})
            append_status(status_path, {"run_key": "clean-agent-miss", "status": "evaluated_fail"})

            self.assertEqual(load_completed_run_keys(status_path), {"clean-pass", "clean-agent-miss"})

    def test_evaluation_summary_distinguishes_agent_fail_from_evaluator_error(self):
        from agent.gt.evaluation_runner import summarize_evaluation_status

        with TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)
            evaluation_path = run_dir / "evaluation.json"

            evaluation_path.write_text(
                json.dumps(
                    {
                        "task_id": "agent-miss",
                        "instance_id": "agent-miss",
                        "expected_verdict": "issue_found",
                        "overall_pass": False,
                        "evaluator_error": False,
                    }
                ),
                encoding="utf-8",
            )
            summary = summarize_evaluation_status(run_dir, returncode=1)
            self.assertEqual(summary["status"], "evaluated_fail")
            self.assertFalse(summary["evaluator_error"])

            evaluation_path.write_text(
                json.dumps(
                    {
                        "overall_pass": False,
                        "evaluator_error": True,
                        "error_type": "gold_resolution",
                        "gold_resolution_errors": [{"reason": "no_gold_elements"}],
                    }
                ),
                encoding="utf-8",
            )
            summary = summarize_evaluation_status(run_dir, returncode=2)
            self.assertEqual(summary["status"], "evaluator_error")
            self.assertTrue(summary["evaluator_error"])
            self.assertEqual(summary["error_type"], "gold_resolution")
            self.assertEqual(summary["gold_resolution_error_count"], 1)

    def test_unexpected_evaluator_returncode_is_not_agent_fail(self):
        from agent.gt.evaluation_runner import summarize_evaluation_status

        with TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)
            (run_dir / "evaluation.json").write_text(
                json.dumps(
                    {
                        "task_id": "eval-crash",
                        "instance_id": "eval-crash",
                        "expected_verdict": "issue_found",
                        "overall_pass": False,
                        "evaluator_error": False,
                    }
                ),
                encoding="utf-8",
            )

            summary = summarize_evaluation_status(run_dir, returncode=3)

            self.assertEqual(summary["status"], "evaluator_error")
            self.assertTrue(summary["evaluator_error"])
            self.assertEqual(summary["error_type"], "unexpected_evaluator_returncode")

    def test_missing_core_evaluation_fields_are_evaluator_error(self):
        from agent.gt.evaluation_runner import summarize_evaluation_status

        with TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)
            (run_dir / "evaluation.json").write_text(
                json.dumps({"overall_pass": True, "evaluator_error": False}),
                encoding="utf-8",
            )

            summary = summarize_evaluation_status(run_dir, returncode=0)

            self.assertEqual(summary["status"], "evaluator_error")
            self.assertTrue(summary["evaluator_error"])
            self.assertEqual(summary["error_type"], "missing_core_evaluation_fields")
            self.assertEqual(summary["missing_core_fields"], ["task_id", "instance_id", "expected_verdict"])

    def test_gold_resolution_artifacts_are_evaluator_error_even_if_flag_is_missing(self):
        from agent.gt.evaluation_runner import summarize_evaluation_status

        with TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)
            (run_dir / "evaluation.json").write_text(
                json.dumps(
                    {
                        "task_id": "bad-gold",
                        "instance_id": "bad-gold",
                        "expected_verdict": "issue_found",
                        "overall_pass": False,
                        "evaluator_error": False,
                        "gold_resolution_errors": [{"reason": "no_gold_elements"}],
                    }
                ),
                encoding="utf-8",
            )

            summary = summarize_evaluation_status(run_dir, returncode=1)

            self.assertEqual(summary["status"], "evaluator_error")
            self.assertTrue(summary["evaluator_error"])
            self.assertEqual(summary["error_type"], "gold_resolution")

    def test_auth_redirect_for_issue_task_is_evaluator_error(self):
        from agent.gt.evaluation_runner import summarize_evaluation_status

        with TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)
            (run_dir / "evaluation.json").write_text(
                json.dumps(
                    {
                        "task_id": "auth-bug",
                        "instance_id": "auth-bug",
                        "expected_verdict": "issue_found",
                        "overall_pass": False,
                        "evaluator_error": False,
                        "page": {
                            "start_url": "http://localhost/admin/page",
                            "final_url": "http://localhost/admin/auth/login/",
                            "http_status": 200,
                        },
                    }
                ),
                encoding="utf-8",
            )

            summary = summarize_evaluation_status(run_dir, returncode=1)

            self.assertEqual(summary["status"], "evaluator_error")
            self.assertTrue(summary["evaluator_error"])
            self.assertEqual(summary["error_type"], "auth_or_http_for_issue_task")

    def test_gold_selector_error_is_not_agent_fail(self):
        from agent.gt.evaluation_runner import summarize_evaluation_status

        with TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)
            (run_dir / "evaluation.json").write_text(
                json.dumps(
                    {
                        "task_id": "bad-selector",
                        "instance_id": "bad-selector",
                        "expected_verdict": "issue_found",
                        "overall_pass": False,
                        "evaluator_error": False,
                        "selector_errors": [{"side": "gold", "selector": "#missing", "reason": "timeout"}],
                    }
                ),
                encoding="utf-8",
            )

            summary = summarize_evaluation_status(run_dir, returncode=1)

            self.assertEqual(summary["status"], "evaluator_error")
            self.assertEqual(summary["error_type"], "gold_selector_error")
            self.assertEqual(summary["gold_selector_error_count"], 1)

    def test_issue_task_with_empty_gold_selectors_is_not_agent_fail(self):
        from agent.gt.evaluation_runner import summarize_evaluation_status

        with TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)
            (run_dir / "evaluation.json").write_text(
                json.dumps(
                    {
                        "task_id": "empty-gold",
                        "instance_id": "empty-gold",
                        "expected_verdict": "issue_found",
                        "overall_pass": False,
                        "evaluator_error": False,
                        "gold_selectors": [],
                    }
                ),
                encoding="utf-8",
            )

            summary = summarize_evaluation_status(run_dir, returncode=1)

            self.assertEqual(summary["status"], "evaluator_error")
            self.assertEqual(summary["error_type"], "expected_issue_without_gold_selectors")


if __name__ == "__main__":
    unittest.main()
