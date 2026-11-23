import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import evaluate_model


class EvaluateModelTests(unittest.TestCase):
    def create_inputs(
        self, root: Path, *, case_count: int = 2, output_name: str = "run-01"
    ) -> tuple[Path, Path]:
        source = root / "saved"
        source_native = source / "native" / "generated"
        source_native.mkdir(parents=True)
        rows = [
            {
                "type": "prompt",
                "test_case_id": f"test_case_{index:06d}",
                "seed": {"description": f"Request {index}"},
            }
            for index in range(1, case_count + 1)
        ]
        (source_native / "test_set.jsonl").write_text(
            "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
        )
        (source_native / "taxonomy.json").write_text(
            json.dumps({"behavior_categories": []}), encoding="utf-8"
        )
        generation = {
            "pipeline": {
                "judge": {
                    "model": {"name": "azure/judge", "max_tokens": 1000},
                    "n": 1,
                }
            }
        }
        (source / "resolved-config.json").write_text(
            json.dumps(generation), encoding="utf-8"
        )
        (source / "complete.json").write_text(
            json.dumps(
                {
                    "status": "complete",
                    "expected_count": case_count,
                    "complete_count": case_count,
                    "test_set": "native/generated/test_set.jsonl",
                    "taxonomy": "native/generated/taxonomy.json",
                }
            ),
            encoding="utf-8",
        )
        (root / "prompt.txt").write_text("Answer accurately.", encoding="utf-8")
        config = {
            "test_set_folder": "saved",
            "system_prompt_file": "prompt.txt",
            "output_folder": output_name,
            "candidate": {
                "model": {"name": "azure/gpt5_series/candidate", "max_tokens": 1000}
            },
            "inference": {"max_turns": 1, "concurrency": 1},
        }
        config_path = root / "evaluation.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        return config_path, source

    @staticmethod
    def tree_hash(path: Path) -> dict[str, str]:
        return {
            str(item.relative_to(path)): hashlib.sha256(item.read_bytes()).hexdigest()
            for item in sorted(path.rglob("*"))
            if item.is_file()
        }

    @staticmethod
    def score_row(case_id: str, *, not_applicable: bool = False) -> dict:
        verdict = {
            "node_judgments": [],
            "dimensions": {
                "policy_violation": False,
                "overrefusal": None if not_applicable else False,
            },
        }
        row = {
            "test_case_id": case_id,
            "judge_status": "ok",
            "verdict": verdict,
            "score_keys": ["policy_violation", "overrefusal"],
            "not_applicable_score_keys": ["overrefusal"] if not_applicable else [],
        }
        if not_applicable:
            verdict["dimension_applicability"] = {"overrefusal": False}
        return row

    def successful_runner(
        self, native_path: Path, *, not_applicable: bool = False
    ) -> subprocess.CompletedProcess[str]:
        run_dir = native_path.parent / "native" / "evaluation" / "run"
        run_dir.mkdir(parents=True)
        ids = ["test_case_000001", "test_case_000002"]
        (run_dir / "manifest.json").write_text(
            json.dumps({"status": "completed", "stages": {"inference": "completed", "judge": "completed"}}),
            encoding="utf-8",
        )
        (run_dir / "inference_set.jsonl").write_text(
            "".join(
                json.dumps({"test_case_id": case_id, "stop_reason": "completed"}) + "\n"
                for case_id in ids
            ),
            encoding="utf-8",
        )
        (run_dir / "scores.jsonl").write_text(
            "".join(
                json.dumps(self.score_row(case_id, not_applicable=not_applicable))
                + "\n"
                for case_id in ids
            ),
            encoding="utf-8",
        )
        return subprocess.CompletedProcess([], 0, stdout="", stderr="")

    def status_runner(
        self, results_dir: Path, *, overrefusal_available: bool = True
    ) -> subprocess.CompletedProcess[str]:
        dimensions = {
            "overrefusal": (
                {
                    "rate": 0.0,
                    "count": 2,
                    "applicable_count": 2,
                    "flagged_count": 0,
                    "not_applicable_count": 0,
                }
                if overrefusal_available
                else {
                    "rate": None,
                    "count": 0,
                    "applicable_count": 0,
                    "not_applicable_count": 2,
                }
            )
        }
        payload = {
            "status": "completed",
            "prompt_metrics": {
                "total": 2,
                "scored_total": 2,
                "judge_model": "azure/judge",
                "policy_violation_on_not_permissible": {
                    "rate": 0.0,
                    "count": 1,
                    "applicable_count": 1,
                    "flagged_count": 0,
                },
                "policy_violation_on_permissible": {
                    "rate": 0.0,
                    "count": 1,
                    "applicable_count": 1,
                    "flagged_count": 0,
                },
                "dimensions": dimensions,
            },
            "prompt_rows": [{}, {}],
        }
        return subprocess.CompletedProcess([], 0, stdout=json.dumps(payload), stderr="")

    def test_evaluates_without_modifying_source_and_writes_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config_path, source = self.create_inputs(root)
            before = self.tree_hash(source)

            output, count = evaluate_model.evaluate(
                config_path, self.successful_runner, self.status_runner
            )

            self.assertEqual(2, count)
            self.assertEqual(before, self.tree_hash(source))
            self.assertTrue((output / "complete.json").is_file())
            summary = json.loads((output / "summary.json").read_text())
            self.assertEqual(
                0,
                summary["metrics"]["policy_violation_not_permissible"]["numerator"],
            )
            self.assertEqual(2, summary["metrics"]["overrefusal"]["denominator"])
            self.assertEqual("Answer accurately.", summary["system_prompt"])

    def test_valid_not_applicable_dimension_does_not_fail_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config_path, _ = self.create_inputs(root)

            output, _ = evaluate_model.evaluate(
                config_path,
                lambda path: self.successful_runner(path, not_applicable=True),
                lambda path: self.status_runner(path, overrefusal_available=False),
            )

            summary = json.loads((output / "summary.json").read_text())
            self.assertEqual("unavailable", summary["metrics"]["overrefusal"]["status"])
            self.assertTrue((output / "complete.json").is_file())

    def test_duplicate_scores_retain_failed_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config_path, _ = self.create_inputs(root)

            def duplicate_runner(path: Path) -> subprocess.CompletedProcess[str]:
                completed = self.successful_runner(path)
                scores = path.parent / "native" / "evaluation" / "run" / "scores.jsonl"
                rows = scores.read_text().splitlines()
                scores.write_text(rows[0] + "\n" + rows[0] + "\n", encoding="utf-8")
                return completed

            with self.assertRaisesRegex(evaluate_model.EvaluationError, "duplicate"):
                evaluate_model.evaluate(config_path, duplicate_runner, self.status_runner)

            self.assertTrue((root / "run-01" / "failed.json").is_file())
            self.assertFalse((root / "run-01" / "complete.json").exists())

    def test_missing_scores_do_not_report_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config_path, _ = self.create_inputs(root)

            def missing_runner(path: Path) -> subprocess.CompletedProcess[str]:
                completed = self.successful_runner(path)
                scores = path.parent / "native" / "evaluation" / "run" / "scores.jsonl"
                scores.write_text(scores.read_text().splitlines()[0] + "\n")
                return completed

            with self.assertRaisesRegex(evaluate_model.EvaluationError, "case IDs"):
                evaluate_model.evaluate(config_path, missing_runner, self.status_runner)

            self.assertFalse((root / "run-01" / "complete.json").exists())

    def test_existing_output_is_rejected_without_runner_call(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config_path, _ = self.create_inputs(root)
            existing = root / "run-01"
            existing.mkdir()
            called = False

            def runner(_: Path) -> subprocess.CompletedProcess[str]:
                nonlocal called
                called = True
                return subprocess.CompletedProcess([], 0)

            with self.assertRaisesRegex(evaluate_model.EvaluationError, "already exists"):
                evaluate_model.evaluate(config_path, runner, self.status_runner)

            self.assertFalse(called)
            self.assertEqual([], list(existing.iterdir()))

    def test_child_failure_is_saved_as_failed_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config_path, _ = self.create_inputs(root)
            failure = subprocess.CompletedProcess([], 2, stdout="", stderr="provider failed")

            with self.assertRaisesRegex(evaluate_model.EvaluationError, "exit code 2"):
                evaluate_model.evaluate(config_path, lambda _: failure, self.status_runner)

            failed = json.loads((root / "run-01" / "failed.json").read_text())
            self.assertEqual("failed", failed["status"])

    def test_rejects_credential_fields_in_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config_path, _ = self.create_inputs(root)
            config = json.loads(config_path.read_text())
            config["candidate"]["model"]["token"] = "do-not-save"
            config_path.write_text(json.dumps(config), encoding="utf-8")

            with self.assertRaisesRegex(
                evaluate_model.EvaluationError, "Credentials are not allowed"
            ):
                evaluate_model.load_evaluation_config(config_path)

    def test_reports_missing_model_environment_variable(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config_path, _ = self.create_inputs(root)
            config = json.loads(config_path.read_text())
            config["candidate"]["model"]["name"] = (
                "azure/gpt5_series/${EVALGATE_AZURE_DEPLOYMENT}"
            )
            config_path.write_text(json.dumps(config), encoding="utf-8")

            with mock.patch.dict("os.environ", {}, clear=True):
                with self.assertRaisesRegex(
                    evaluate_model.EvaluationError,
                    "EVALGATE_AZURE_DEPLOYMENT.*not set",
                ):
                    evaluate_model.load_evaluation_config(config_path)


if __name__ == "__main__":
    unittest.main()
