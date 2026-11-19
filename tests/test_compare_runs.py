import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import compare_runs


class CompareRunsTests(unittest.TestCase):
    def create_run(
        self,
        root: Path,
        name: str,
        *,
        first_rate: float = 0.0,
        changed: bool = False,
        unavailable: bool = False,
        test_marker: str = "same",
        judge_marker: str = "same",
    ) -> Path:
        run = root / name
        inputs = run / "inputs"
        native_run = run / "native" / "evaluation" / "run"
        inputs.mkdir(parents=True)
        native_run.mkdir(parents=True)
        test_set = (
            '{"type":"prompt","test_case_id":"case-1","seed":{"description":"one"}}\n'
            '{"type":"prompt","test_case_id":"case-2","seed":{"description":"two"}}\n'
        )
        if test_marker != "same":
            test_set = test_set.replace('"one"', f'"{test_marker}"')
        taxonomy = json.dumps(
            {"behavior_categories": [{"name": "safe", "permissible": True}]}
        )
        generation = {
            "behavior": {"name": "scope", "description": "Stay on scope."},
            "context": "A single-turn assistant.",
            "pipeline": {
                "judge": {
                    "model": {"name": "azure/judge", "max_tokens": 1000},
                    "n": 1,
                    "dimensions": judge_marker,
                }
            },
            "assert_version": "0.3.0",
        }
        (inputs / "test_set.jsonl").write_text(test_set, encoding="utf-8")
        (inputs / "taxonomy.json").write_text(taxonomy, encoding="utf-8")
        (inputs / "resolved-config.json").write_text(
            json.dumps(generation), encoding="utf-8"
        )
        (inputs / "complete.json").write_text(
            json.dumps({"status": "complete"}), encoding="utf-8"
        )
        resolved = {
            "candidate": {"model": {"name": f"azure/{name}", "max_tokens": 1000}},
            "system_prompt": f"Prompt for {name}.",
            "assert_version": "0.3.0",
        }
        (run / "resolved-config.json").write_text(
            json.dumps(resolved), encoding="utf-8"
        )
        (run / "complete.json").write_text(
            json.dumps(
                {
                    "status": "complete",
                    "assert_version": "0.3.0",
                    "expected_count": 2,
                    "scored_count": 2,
                }
            ),
            encoding="utf-8",
        )
        first_metric = {
            "status": "available",
            "numerator": round(first_rate * 2),
            "denominator": 2,
            "rate": first_rate,
        }
        overrefusal = {"status": "unavailable"} if unavailable else first_metric
        summary = {
            "status": "complete",
            "expected_count": 2,
            "scored_count": 2,
            "source_sha256": {
                "test_set.jsonl": self.sha(inputs / "test_set.jsonl"),
                "taxonomy.json": self.sha(inputs / "taxonomy.json"),
                "resolved-config.json": self.sha(inputs / "resolved-config.json"),
            },
            "metrics": {
                "policy_violation_not_permissible": first_metric,
                "policy_violation_permissible": first_metric,
                "overrefusal": overrefusal,
            },
        }
        (run / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
        (native_run / "manifest.json").write_text(
            json.dumps(
                {
                    "status": "completed",
                    "stages": {"inference": "completed", "judge": "completed"},
                }
            ),
            encoding="utf-8",
        )
        inference = [
            {"test_case_id": "case-1", "stop_reason": "completed"},
            {"test_case_id": "case-2", "stop_reason": "completed"},
        ]
        (native_run / "inference_set.jsonl").write_text(
            "".join(json.dumps(row) + "\n" for row in reversed(inference)),
            encoding="utf-8",
        )
        scores = []
        for case_id in ("case-1", "case-2"):
            dimensions = {
                "policy_violation": changed and case_id == "case-2",
                "overrefusal": False,
            }
            scores.append(
                {
                    "test_case_id": case_id,
                    "judge_status": "ok",
                    "score_keys": ["policy_violation", "overrefusal"],
                    "not_applicable_score_keys": [],
                    "verdict": {
                        "dimensions": dimensions,
                        "node_judgments": [],
                    },
                }
            )
        (native_run / "scores.jsonl").write_text(
            "".join(json.dumps(row) + "\n" for row in scores), encoding="utf-8"
        )
        return run

    @staticmethod
    def sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def test_compares_rates_and_changed_case_by_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = self.create_run(root, "first", first_rate=0.0)
            second = self.create_run(root, "second", first_rate=0.5, changed=True)
            output = root / "comparison.json"

            comparison = compare_runs.run(first, second, output)

            self.assertEqual(
                0.5,
                comparison["metrics"]["policy_violation_not_permissible"][
                    "second_minus_first"
                ],
            )
            self.assertEqual(1, comparison["cases"]["changed_count"])
            changed = comparison["cases"]["changed"][0]
            self.assertEqual("case-2", changed["test_case_id"])
            self.assertIn("case-2", changed["first"]["response_reference"])
            self.assertTrue(output.is_file())

    def test_unavailable_metric_omits_difference(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = self.create_run(root, "first", unavailable=True)
            second = self.create_run(root, "second", first_rate=0.5)

            comparison = compare_runs.compare(first, second)

            self.assertNotIn(
                "second_minus_first", comparison["metrics"]["overrefusal"]
            )

    def test_rejects_different_test_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = self.create_run(root, "first")
            second = self.create_run(root, "second", test_marker="different")

            with self.assertRaisesRegex(compare_runs.ComparisonError, "test-set content"):
                compare_runs.compare(first, second)

    def test_rejects_different_judge_settings(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = self.create_run(root, "first")
            second = self.create_run(root, "second", judge_marker="different")

            with self.assertRaisesRegex(
                compare_runs.ComparisonError, "judge/scoring"
            ):
                compare_runs.compare(first, second)

    def test_rejects_different_taxonomy(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = self.create_run(root, "first")
            second = self.create_run(root, "second")
            taxonomy = second / "inputs" / "taxonomy.json"
            taxonomy.write_text(
                json.dumps(
                    {
                        "behavior_categories": [
                            {"name": "different", "permissible": False}
                        ]
                    }
                ),
                encoding="utf-8",
            )
            summary_path = second / "summary.json"
            summary = json.loads(summary_path.read_text())
            summary["source_sha256"]["taxonomy.json"] = self.sha(taxonomy)
            summary_path.write_text(json.dumps(summary), encoding="utf-8")

            with self.assertRaisesRegex(
                compare_runs.ComparisonError, "taxonomy content"
            ):
                compare_runs.compare(first, second)

    def test_rejects_duplicate_scores_without_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = self.create_run(root, "first")
            second = self.create_run(root, "second")
            scores = second / "native" / "evaluation" / "run" / "scores.jsonl"
            first_line = scores.read_text().splitlines()[0]
            scores.write_text(first_line + "\n" + first_line + "\n", encoding="utf-8")
            output = root / "comparison.json"

            with self.assertRaisesRegex(compare_runs.ComparisonError, "duplicate"):
                compare_runs.run(first, second, output)

            self.assertFalse(output.exists())

    def test_rejects_incomplete_manifest_without_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = self.create_run(root, "first")
            second = self.create_run(root, "second")
            manifest = second / "native" / "evaluation" / "run" / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "status": "failed",
                        "stages": {"inference": "completed", "judge": "failed"},
                    }
                ),
                encoding="utf-8",
            )
            output = root / "comparison.json"

            with self.assertRaisesRegex(compare_runs.ComparisonError, "not completed"):
                compare_runs.run(first, second, output)

            self.assertFalse(output.exists())

    def test_existing_output_is_rejected_without_modifying_runs(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = self.create_run(root, "first")
            second = self.create_run(root, "second")
            before = [
                self.sha(path)
                for path in sorted(root.rglob("*"))
                if path.is_file()
            ]
            output = root / "comparison.json"
            output.write_text("existing", encoding="utf-8")

            with self.assertRaisesRegex(compare_runs.ComparisonError, "already exists"):
                compare_runs.run(first, second, output)

            self.assertEqual("existing", output.read_text())
            after = [
                self.sha(path)
                for path in sorted(root.rglob("*"))
                if path.is_file() and path != output
            ]
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
