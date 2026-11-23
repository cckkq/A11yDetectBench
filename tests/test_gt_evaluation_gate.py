import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from agent.gt.evaluation_gate import audit_roots


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


class EvaluationGateTest(unittest.TestCase):
    def test_gate_ignores_tmp_logs_and_fails_official_evaluator_errors(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_json(root / "_logs" / "tmp_corrected_eval" / "evaluation.json", {"evaluator_error": True})
            official = root / "official"
            write_json(official / "evaluation.json", {"task_id": "ok", "instance_id": "ok", "expected_verdict": "no_issue_found", "overall_pass": True})
            write_json(official / "task.snapshot.yaml", {"task_id": "ok"})
            write_json(official / "evaluate-rule.snapshot.yaml", {"task_id": "ok"})
            write_json(official / "final-response.json", {"verdict": "no_issue_found"})
            bad = root / "bad"
            write_json(
                bad / "evaluation.json",
                {
                    "task_id": "bad",
                    "instance_id": "bad",
                    "expected_verdict": "issue_found",
                    "overall_pass": False,
                    "evaluator_error": True,
                    "gold_resolution_errors": [{"reason": "no_gold_elements"}],
                },
            )
            write_json(bad / "task.snapshot.yaml", {"task_id": "bad"})
            write_json(bad / "evaluate-rule.snapshot.yaml", {"task_id": "bad"})
            write_json(bad / "final-response.json", {"verdict": "issue_found"})

            result = audit_roots("ERROR", [root])

            self.assertEqual(result.evals, 2)
            self.assertEqual(len(result.hard_failures), 1)
            self.assertEqual(result.hard_failures[0].task_id, "bad")
            self.assertIn("evaluator_error", result.hard_failures[0].hard_failures)
            self.assertIn("gold_resolution", result.hard_failures[0].hard_failures)

    def test_gate_flags_evaluation_json_without_official_run_artifacts(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_json(root / "loose" / "evaluation.json", {"task_id": "loose", "instance_id": "loose", "expected_verdict": "no_issue_found", "overall_pass": True})

            result = audit_roots("LINKS", [root])

            self.assertEqual(result.evals, 1)
            self.assertEqual(len(result.hard_failures), 1)
            self.assertIn("missing_run_artifacts", result.hard_failures[0].hard_failures[0])

    def test_gate_flags_run_directory_without_evaluation_json(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            run_dir = root / "task" / "run-1"
            write_json(run_dir / "task.snapshot.yaml", {"task_id": "missing-eval"})
            write_json(run_dir / "evaluate-rule.snapshot.yaml", {"task_id": "missing-eval"})
            write_json(run_dir / "final-response.json", {"verdict": "issue_found"})

            result = audit_roots("ERROR", [root])

            self.assertEqual(result.evals, 0)
            self.assertEqual(len(result.hard_failures), 1)
            self.assertIn("missing_evaluation_json", result.hard_failures[0].hard_failures)

    def test_gate_flags_login_redirect_for_issue_task(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_json(
                root / "run" / "evaluation.json",
                {
                    "task_id": "auth-bug",
                    "instance_id": "auth-bug",
                    "expected_verdict": "issue_found",
                    "overall_pass": False,
                    "page": {"start_url": "http://localhost/admin/page", "final_url": "http://localhost/admin/auth/login/", "http_status": 200},
                },
            )
            write_json(root / "run" / "task.snapshot.yaml", {"task_id": "auth-bug"})
            write_json(root / "run" / "evaluate-rule.snapshot.yaml", {"task_id": "auth-bug"})
            write_json(root / "run" / "final-response.json", {"verdict": "issue_found"})

            result = audit_roots("FOCUS", [root])

            self.assertEqual(result.evals, 1)
            self.assertEqual(len(result.hard_failures), 1)
            self.assertIn("auth_or_http_for_issue_task", result.hard_failures[0].hard_failures)


if __name__ == "__main__":
    unittest.main()
