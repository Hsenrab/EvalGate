import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import generate_tests


class GenerateTestsTests(unittest.TestCase):
    def config(self, root: Path, output_name: str = "output") -> Path:
        (root / "behavior.txt").write_text("Test support requests.", encoding="utf-8")
        (root / "context.txt").write_text("A support assistant.", encoding="utf-8")
        config = {
            "behavior": {"name": "support_scope"},
            "behavior_file": "behavior.txt",
            "context_file": "context.txt",
            "output_folder": output_name,
            "pipeline": {
                "systematize": {
                    "model": {"name": "openai/generation", "max_tokens": 1000},
                    "web_search": False,
                },
                "test_set": {
                    "prompt": {
                        "sample_size": 10,
                        "model": {"name": "openai/generation", "max_tokens": 1000},
                    }
                },
                "judge": {
                    "model": {"name": "openai/judge", "max_tokens": 1000},
                    "n": 1,
                },
            },
        }
        path = root / "config.json"
        path.write_text(json.dumps(config), encoding="utf-8")
        return path

    @staticmethod
    def success_runner(config_path: Path) -> subprocess.CompletedProcess[str]:
        native = config_path.parent / "native" / "generated"
        native.mkdir(parents=True)
        rows = [
            {
                "type": "prompt",
                "test_case_id": f"test_case_{index:06d}",
                "seed": {"description": f"Request {index}"},
            }
            for index in range(1, 11)
        ]
        (native / "test_set.jsonl").write_text(
            "".join(json.dumps(row) + "\n" for row in rows),
            encoding="utf-8",
        )
        (native / "taxonomy.json").write_text("{}", encoding="utf-8")
        return subprocess.CompletedProcess([], 0)

    def test_generates_complete_saved_set_from_config_relative_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "configs"
            root.mkdir()
            config_path = self.config(root)

            output, count = generate_tests.generate(config_path, self.success_runner)

            self.assertEqual(10, count)
            self.assertTrue((output / "complete.json").is_file())
            resolved = json.loads((output / "resolved-config.json").read_text())
            self.assertEqual("Test support requests.", resolved["behavior"]["description"])
            self.assertEqual("A support assistant.", resolved["context"])
            self.assertIn("assert-generation.yaml", {p.name for p in output.iterdir()})

    def test_rejects_existing_output_without_calling_assert(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config_path = self.config(root)
            existing = root / "output"
            existing.mkdir()
            runner = mock.Mock()

            with self.assertRaises(generate_tests.GenerationError):
                generate_tests.generate(config_path, runner)

            runner.assert_not_called()
            self.assertTrue(existing.is_dir())

    def test_rejects_short_output_even_when_child_succeeds(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config_path = self.config(root)

            def short_runner(config_path: Path) -> subprocess.CompletedProcess[str]:
                native = config_path.parent / "native" / "generated"
                native.mkdir(parents=True)
                (native / "test_set.jsonl").write_text(
                    json.dumps(
                        {
                            "type": "prompt",
                            "test_case_id": "test_case_000001",
                            "seed": {"description": "One request"},
                        }
                    )
                    + "\n",
                    encoding="utf-8",
                )
                return subprocess.CompletedProcess([], 0)

            with self.assertRaisesRegex(
                generate_tests.GenerationError, r"1/10 complete"
            ):
                generate_tests.generate(config_path, short_runner)

            self.assertFalse((root / "output").exists())

    def test_child_failure_is_nonzero_and_cleans_owned_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config_path = self.config(root)
            failure = subprocess.CompletedProcess(
                [], 2, stdout="", stderr="provider detail"
            )

            with self.assertRaisesRegex(
                generate_tests.GenerationError, "exit code 2"
            ):
                generate_tests.generate(config_path, lambda _: failure)

            self.assertFalse((root / "output").exists())

    def test_rejects_credential_fields_in_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config_path = self.config(root)
            config = json.loads(config_path.read_text())
            config["AZURE_API_KEY"] = "do-not-save"
            config_path.write_text(json.dumps(config), encoding="utf-8")

            with self.assertRaisesRegex(
                generate_tests.GenerationError, "Credentials are not allowed"
            ):
                generate_tests.load_generation_config(config_path)


if __name__ == "__main__":
    unittest.main()
