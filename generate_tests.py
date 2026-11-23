"""Generate one reusable ASSERT test set from a JSON configuration."""

from __future__ import annotations

import argparse
import copy
from importlib.metadata import PackageNotFoundError, version
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any, Callable

import yaml
from dotenv import load_dotenv


ASSERT_VERSION = "0.3.0"
_CREDENTIAL_KEYS = {
    "api_key",
    "apikey",
    "credential",
    "credentials",
    "password",
    "secret",
    "token",
}


class GenerationError(Exception):
    """A clear, expected generation failure."""


_MODEL_ENV_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def _resolve_model_env(value: str, path: str) -> str:
    missing: list[str] = []

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        resolved = os.environ.get(name)
        if resolved is None or not resolved.strip():
            missing.append(name)
            return match.group(0)
        return resolved

    resolved = _MODEL_ENV_PATTERN.sub(replace, value)
    if missing:
        raise GenerationError(
            f"Environment variable {', '.join(sorted(set(missing)))} "
            f"required by {path} is not set"
        )
    return resolved


def _resolve_model_names(value: Any, path: str = "config") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key == "name" and isinstance(child, str) and "model" in path.split("."):
                value[key] = _resolve_model_env(child, child_path)
            else:
                _resolve_model_names(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _resolve_model_names(child, f"{path}[{index}]")


def _load_environment(config_path: Path) -> None:
    for parent in config_path.resolve().parents:
        env_path = parent / ".env"
        if env_path.is_file():
            load_dotenv(env_path, override=False)
            return


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _resolve_text(
    config: dict[str, Any],
    config_dir: Path,
    inline_key: str,
    file_key: str,
) -> str:
    inline = config.get(inline_key)
    file_value = config.get(file_key)
    if inline is not None and file_value is not None:
        raise GenerationError(f"Specify only one of {inline_key!r} or {file_key!r}")
    if file_value is not None:
        if not isinstance(file_value, str) or not file_value.strip():
            raise GenerationError(f"{file_key} must be a non-empty path")
        path = (config_dir / file_value).resolve()
        if not path.is_file():
            raise GenerationError(f"Referenced {file_key} does not exist: {path}")
        text = path.read_text(encoding="utf-8")
    else:
        if not isinstance(inline, str):
            raise GenerationError(f"{inline_key} must be text")
        text = inline
    if not text.strip():
        raise GenerationError(f"{inline_key} must not be empty")
    return text


def _reject_credential_fields(value: Any, path: str = "config") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = key.lower()
            if lowered in _CREDENTIAL_KEYS or lowered.endswith(("_api_key", "_secret")):
                raise GenerationError(f"Credentials are not allowed in {path}.{key}")
            _reject_credential_fields(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_credential_fields(child, f"{path}[{index}]")


def load_generation_config(config_path: Path) -> tuple[dict[str, Any], Path]:
    _load_environment(config_path)
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise GenerationError(f"Config file does not exist: {config_path}") from None
    except json.JSONDecodeError as exc:
        raise GenerationError(f"Invalid JSON in {config_path}: {exc.msg}") from exc
    if not isinstance(raw, dict):
        raise GenerationError("The config must contain a JSON object")

    _reject_credential_fields(raw)
    config_dir = config_path.resolve().parent
    config = copy.deepcopy(raw)
    _resolve_model_names(config)

    output_value = config.pop("output_folder", None)
    if not isinstance(output_value, str) or not output_value.strip():
        raise GenerationError("output_folder must be a non-empty path")
    output_folder = (config_dir / output_value).resolve()

    behavior = config.get("behavior")
    if not isinstance(behavior, dict):
        raise GenerationError("behavior must be an object")
    behavior_file = config.pop("behavior_file", None)
    if behavior_file is not None:
        if "description" in behavior:
            raise GenerationError("Specify only one of behavior.description or behavior_file")
        behavior_input = dict(config, behavior_file=behavior_file)
        behavior["description"] = _resolve_text(
            behavior_input,
            config_dir,
            "behavior_description",
            "behavior_file",
        )

    context_file = config.pop("context_file", None)
    if context_file is not None:
        if "context" in config:
            raise GenerationError("Specify only one of context or context_file")
        config["context"] = _resolve_text(
            {"context_file": context_file},
            config_dir,
            "context",
            "context_file",
        )
    elif not isinstance(config.get("context"), str) or not config["context"].strip():
        raise GenerationError("context must be non-empty text or use context_file")

    if not isinstance(behavior.get("name"), str) or not behavior["name"].strip():
        raise GenerationError("behavior.name must be non-empty text")
    if not isinstance(behavior.get("description"), str) or not behavior["description"].strip():
        raise GenerationError("behavior.description must be non-empty text or use behavior_file")

    pipeline = config.get("pipeline")
    if not isinstance(pipeline, dict):
        raise GenerationError("pipeline must be an object")
    if not isinstance(pipeline.get("systematize"), dict):
        raise GenerationError("pipeline.systematize must be configured")
    test_set = pipeline.get("test_set")
    prompt = test_set.get("prompt") if isinstance(test_set, dict) else None
    sample_size = prompt.get("sample_size") if isinstance(prompt, dict) else None
    if (
        not isinstance(sample_size, int)
        or isinstance(sample_size, bool)
        or sample_size <= 0
    ):
        raise GenerationError("pipeline.test_set.prompt.sample_size must be a positive integer")
    if not isinstance(test_set, dict) or "scenario" in test_set:
        raise GenerationError("Only prompt-only test-set generation is supported")
    if "judge" not in pipeline or not isinstance(pipeline["judge"], dict):
        raise GenerationError("pipeline.judge must be configured")

    config["assert_version"] = ASSERT_VERSION
    config["output_folder"] = str(output_folder)
    return config, output_folder


def _assert_executable() -> Path:
    try:
        installed_version = version("assert-ai")
    except PackageNotFoundError:
        raise GenerationError("assert-ai==0.3.0 is not installed") from None
    if installed_version != ASSERT_VERSION:
        raise GenerationError(
            f"Expected assert-ai=={ASSERT_VERSION}, found {installed_version}"
        )
    name = "assert-ai.exe" if os.name == "nt" else "assert-ai"
    executable = Path(sys.executable).resolve().parent / name
    if not executable.is_file():
        raise GenerationError(f"ASSERT executable not found beside Python: {executable}")
    return executable


def run_assert(native_config: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            str(_assert_executable()),
            "run",
            "--config",
            str(native_config),
            "--strict",
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def _native_config(config: dict[str, Any], output_folder: Path) -> dict[str, Any]:
    native = {
        "suite": "generated",
        "behavior": copy.deepcopy(config["behavior"]),
        "context": config["context"],
        "artifacts_root": str(output_folder / "native"),
        "results_dir": str(output_folder / "native"),
        "pipeline": {
            "systematize": copy.deepcopy(config["pipeline"]["systematize"]),
            "test_set": copy.deepcopy(config["pipeline"]["test_set"]),
        },
    }
    return native


def _validate_test_set(path: Path, expected_count: int) -> list[dict[str, Any]]:
    if not path.is_file():
        raise GenerationError(f"ASSERT did not create test_set.jsonl at {path}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise GenerationError(
                f"ASSERT wrote invalid JSON in test_set.jsonl line {line_number}: {exc.msg}"
            ) from exc
        if not isinstance(row, dict):
            raise GenerationError(f"Test case at line {line_number} is not an object")
        rows.append(row)

    if len(rows) != expected_count:
        raise GenerationError(
            f"ASSERT generated {len(rows)}/{expected_count} complete test cases"
        )
    ids = [row.get("test_case_id") for row in rows]
    if any(not isinstance(case_id, str) or not case_id.strip() for case_id in ids):
        raise GenerationError("Every generated test case must have a non-empty test_case_id")
    if len(set(ids)) != len(ids):
        raise GenerationError("Generated test case IDs are not unique")
    for index, row in enumerate(rows, 1):
        if row.get("type") != "prompt":
            raise GenerationError(f"Test case {index} is not a single-turn prompt")
        seed = row.get("seed")
        if not isinstance(seed, dict) or not isinstance(seed.get("description"), str):
            raise GenerationError(f"Test case {index} has no request description")
    return rows


def generate(
    config_path: Path,
    runner: Callable[[Path], subprocess.CompletedProcess[str]] = run_assert,
) -> tuple[Path, int]:
    config, output_folder = load_generation_config(config_path)
    if output_folder.exists():
        raise GenerationError(f"Output destination already exists: {output_folder}")

    output_folder.mkdir(parents=True)
    try:
        _write_json(output_folder / "resolved-config.json", config)
        native_path = output_folder / "assert-generation.yaml"
        native_path.write_text(
            yaml.safe_dump(_native_config(config, output_folder), sort_keys=False),
            encoding="utf-8",
        )

        completed = runner(native_path)
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "").strip().splitlines()
            suffix = f": {' | '.join(detail[-12:])}" if detail else ""
            raise GenerationError(
                f"ASSERT generation failed with exit code {completed.returncode}{suffix}"
            )

        expected_count = config["pipeline"]["test_set"]["prompt"]["sample_size"]
        test_set_path = (
            output_folder / "native" / "generated" / "test_set.jsonl"
        )
        rows = _validate_test_set(test_set_path, expected_count)
        taxonomy_path = output_folder / "native" / "generated" / "taxonomy.json"
        if not taxonomy_path.is_file():
            raise GenerationError(f"ASSERT did not create taxonomy.json at {taxonomy_path}")
        _write_json(
            output_folder / "complete.json",
            {
                "status": "complete",
                "assert_version": ASSERT_VERSION,
                "expected_count": expected_count,
                "complete_count": len(rows),
                "test_set": "native/generated/test_set.jsonl",
                "taxonomy": "native/generated/taxonomy.json",
            },
        )
        return output_folder, len(rows)
    except Exception as original:
        try:
            shutil.rmtree(output_folder)
        except OSError as cleanup_error:
            raise GenerationError(
                f"{original}; cleanup failed for {output_folder}: {cleanup_error}"
            ) from original
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a reusable ASSERT test set")
    parser.add_argument("--config", required=True, type=Path, help="Path to JSON config")
    args = parser.parse_args()
    try:
        output_folder, count = generate(args.config)
    except (GenerationError, OSError) as exc:
        print(f"Generation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Generated {count} test cases in {output_folder}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
