"""Evaluate one model against a saved ASSERT test set."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable

import yaml

from generate_tests import (
    ASSERT_VERSION,
    GenerationError,
    _assert_executable,
    _reject_credential_fields,
    _load_environment,
    _resolve_model_names,
    _validate_test_set,
)


class EvaluationError(Exception):
    """A clear, expected evaluation failure."""


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _load_json(path: Path, description: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise EvaluationError(f"Missing {description}: {path}") from None
    except json.JSONDecodeError as exc:
        raise EvaluationError(
            f"Invalid JSON in {description} {path}: {exc.msg}"
        ) from exc
    if not isinstance(value, dict):
        raise EvaluationError(f"{description.capitalize()} must be a JSON object: {path}")
    return value


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _positive_int(value: Any, field: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise EvaluationError(f"{field} must be a positive integer")
    return value


def load_evaluation_config(config_path: Path) -> tuple[dict[str, Any], Path, Path, str]:
    _load_environment(config_path)
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise EvaluationError(f"Config file does not exist: {config_path}") from None
    except json.JSONDecodeError as exc:
        raise EvaluationError(f"Invalid JSON in {config_path}: {exc.msg}") from exc
    if not isinstance(raw, dict):
        raise EvaluationError("The config must contain a JSON object")

    try:
        _reject_credential_fields(raw)
    except GenerationError as exc:
        raise EvaluationError(str(exc)) from exc

    config_dir = config_path.resolve().parent
    config = copy.deepcopy(raw)
    try:
        _resolve_model_names(config)
    except GenerationError as exc:
        raise EvaluationError(str(exc)) from exc

    test_set_value = config.pop("test_set_folder", None)
    if not isinstance(test_set_value, str) or not test_set_value.strip():
        raise EvaluationError("test_set_folder must be a non-empty path")
    test_set_folder = (config_dir / test_set_value).resolve()
    if not test_set_folder.is_dir():
        raise EvaluationError(f"Test-set folder does not exist: {test_set_folder}")

    prompt_value = config.pop("system_prompt_file", None)
    if not isinstance(prompt_value, str) or not prompt_value.strip():
        raise EvaluationError("system_prompt_file must be a non-empty path")
    prompt_path = (config_dir / prompt_value).resolve()
    if not prompt_path.is_file():
        raise EvaluationError(f"System prompt file does not exist: {prompt_path}")
    system_prompt = prompt_path.read_text(encoding="utf-8")
    if not system_prompt.strip():
        raise EvaluationError(f"System prompt file is empty: {prompt_path}")

    output_value = config.pop("output_folder", None)
    if not isinstance(output_value, str) or not output_value.strip():
        raise EvaluationError("output_folder must be a non-empty path")
    output_folder = (config_dir / output_value).resolve()

    candidate = config.pop("candidate", None)
    if not isinstance(candidate, dict) or not isinstance(candidate.get("model"), dict):
        raise EvaluationError("candidate.model must be configured")
    model_name = candidate["model"].get("name")
    if not isinstance(model_name, str) or not model_name.strip():
        raise EvaluationError("candidate.model.name must be non-empty text")

    inference = config.pop("inference", {})
    if not isinstance(inference, dict):
        raise EvaluationError("inference must be an object")
    allowed_inference = {
        "max_turns",
        "max_tool_calls",
        "tool_timeout_s",
        "startup_timeout_s",
        "concurrency",
    }
    unknown = sorted(set(inference) - allowed_inference)
    if unknown:
        raise EvaluationError(f"Unsupported inference setting(s): {', '.join(unknown)}")
    for key in ("max_turns", "max_tool_calls", "concurrency"):
        _positive_int(inference.get(key), f"inference.{key}")
    for key in ("tool_timeout_s", "startup_timeout_s"):
        value = inference.get(key)
        if value is not None and (
            not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0
        ):
            raise EvaluationError(f"inference.{key} must be a positive number")
    if config:
        raise EvaluationError(f"Unsupported config field(s): {', '.join(sorted(config))}")

    resolved = {
        "test_set_folder": str(test_set_folder),
        "system_prompt_file": str(prompt_path),
        "system_prompt": system_prompt,
        "output_folder": str(output_folder),
        "candidate": candidate,
        "inference": inference,
        "assert_version": ASSERT_VERSION,
    }
    return resolved, test_set_folder, output_folder, system_prompt


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


def run_assert_status(results_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            str(_assert_executable()),
            "results",
            "status",
            "evaluation",
            "run",
            "--results-dir",
            str(results_dir),
            "--json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def _native_config(
    config: dict[str, Any],
    output_folder: Path,
    test_set_path: Path,
    taxonomy_path: Path,
    system_prompt: str,
    judge: dict[str, Any],
) -> dict[str, Any]:
    inference = copy.deepcopy(config["inference"])
    inference.update(
        {
            "target": {
                "model": copy.deepcopy(config["candidate"]["model"]),
                "system_prompt": system_prompt,
            },
            "test_set_path": str(test_set_path),
            "strict": True,
        }
    )
    native_judge = copy.deepcopy(judge)
    native_judge.update(
        {
            "taxonomy_path": str(taxonomy_path),
        }
    )
    return {
        "suite": "evaluation",
        "run": "run",
        "artifacts_root": str(output_folder / "native"),
        "results_dir": str(output_folder / "native"),
        "pipeline": {
            "inference": inference,
            "judge": native_judge,
        },
    }


def _read_jsonl(path: Path, description: str) -> list[dict[str, Any]]:
    if not path.is_file():
        raise EvaluationError(f"Missing {description}: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EvaluationError(
                f"Invalid JSON in {description} line {line_number}: {exc.msg}"
            ) from exc
        if not isinstance(row, dict):
            raise EvaluationError(f"{description.capitalize()} line {line_number} is not an object")
        rows.append(row)
    return rows


def _validate_unique_ids(
    rows: list[dict[str, Any]], expected_ids: set[str], description: str
) -> None:
    ids = [row.get("test_case_id") for row in rows]
    if any(not isinstance(case_id, str) or not case_id.strip() for case_id in ids):
        raise EvaluationError(f"Every {description} row must have a test_case_id")
    if len(ids) != len(set(ids)):
        raise EvaluationError(f"{description.capitalize()} contains duplicate test_case_id values")
    if set(ids) != expected_ids:
        raise EvaluationError(
            f"{description.capitalize()} case IDs do not match the saved test set"
        )


def _validate_scores(path: Path, expected_ids: set[str]) -> list[dict[str, Any]]:
    rows = _read_jsonl(path, "scores")
    _validate_unique_ids(rows, expected_ids, "scores")
    for row in rows:
        case_id = row["test_case_id"]
        if row.get("judge_status") != "ok":
            raise EvaluationError(f"Case {case_id} does not have a successful judgment")
        verdict = row.get("verdict")
        if not isinstance(verdict, dict):
            raise EvaluationError(f"Case {case_id} has no judgment object")
        if not isinstance(verdict.get("node_judgments"), list):
            raise EvaluationError(f"Case {case_id} judgment has no node judgments")
        dimensions = verdict.get("dimensions")
        if not isinstance(dimensions, dict):
            raise EvaluationError(f"Case {case_id} judgment has no dimensions")
        score_keys = row.get("score_keys")
        if not isinstance(score_keys, list) or not score_keys:
            raise EvaluationError(f"Case {case_id} judgment has no score keys")
        applicability = verdict.get("dimension_applicability")
        dimension_scales = row.get("dimension_scales")
        allowed_na = {
            key
            for key in row.get("not_applicable_score_keys", [])
            if isinstance(key, str)
        } if isinstance(row.get("not_applicable_score_keys", []), list) else set()
        for key in score_keys:
            if not isinstance(key, str) or key not in dimensions:
                raise EvaluationError(f"Case {case_id} judgment has invalid score key")
            value = dimensions[key]
            valid_na = (
                key in allowed_na
                and value is None
                and isinstance(applicability, dict)
                and applicability.get(key) is False
            )
            valid_scale = False
            if isinstance(dimension_scales, dict):
                scale = dimension_scales.get(key)
                scale_values = scale.get("values") if isinstance(scale, dict) else None
                if isinstance(scale_values, list):
                    valid_scale = any(
                        isinstance(entry, dict)
                        and entry.get("value") == value
                        and type(entry.get("value")) is type(value)
                        for entry in scale_values
                    )
            if not isinstance(value, bool) and not valid_na and not valid_scale:
                raise EvaluationError(
                    f"Case {case_id} judgment dimension {key} is invalid"
                )
    return rows


def _metric(summary: Any) -> dict[str, Any]:
    if not isinstance(summary, dict):
        return {"status": "unavailable"}
    denominator = summary.get("applicable_count", summary.get("count"))
    numerator = summary.get("flagged_count")
    rate = summary.get("rate")
    if (
        not isinstance(denominator, int)
        or isinstance(denominator, bool)
        or denominator <= 0
        or not isinstance(numerator, int)
        or isinstance(numerator, bool)
        or not isinstance(rate, (int, float))
        or isinstance(rate, bool)
    ):
        return {"status": "unavailable"}
    return {
        "status": "available",
        "numerator": numerator,
        "denominator": denominator,
        "rate": rate,
    }


def _build_summary(
    status_payload: dict[str, Any],
    config: dict[str, Any],
    expected_count: int,
    prompt_hash: str,
    source_hashes: dict[str, str],
) -> dict[str, Any]:
    prompt_metrics = status_payload.get("prompt_metrics")
    if not isinstance(prompt_metrics, dict):
        prompt_metrics = {}
    dimensions = prompt_metrics.get("dimensions")
    dimensions = dimensions if isinstance(dimensions, dict) else {}
    return {
        "status": "complete",
        "assert_version": ASSERT_VERSION,
        "expected_count": expected_count,
        "scored_count": len(status_payload.get("prompt_rows") or []),
        "candidate_model": config["candidate"]["model"],
        "system_prompt": config["system_prompt"],
        "system_prompt_sha256": prompt_hash,
        "judge_model": prompt_metrics.get("judge_model"),
        "source_sha256": source_hashes,
        "metrics": {
            "policy_violation_not_permissible": _metric(
                prompt_metrics.get("policy_violation_on_not_permissible")
            ),
            "policy_violation_permissible": _metric(
                prompt_metrics.get("policy_violation_on_permissible")
            ),
            "overrefusal": _metric(dimensions.get("overrefusal")),
        },
    }


def _failure_detail(completed: subprocess.CompletedProcess[str]) -> str:
    detail = (completed.stderr or completed.stdout or "").strip().splitlines()
    return f": {' | '.join(detail[-12:])}" if detail else ""


def _prepare_output(
    output_folder: Path,
    config: dict[str, Any],
    test_set_folder: Path,
    test_set_path: Path,
    taxonomy_path: Path,
    system_prompt: str,
    judge: dict[str, Any],
) -> tuple[Path, Path, str]:
    _write_json(output_folder / "resolved-config.json", config)
    inputs = output_folder / "inputs"
    inputs.mkdir()
    copied_test_set = inputs / "test_set.jsonl"
    copied_taxonomy = inputs / "taxonomy.json"
    copied_test_set.write_bytes(test_set_path.read_bytes())
    copied_taxonomy.write_bytes(taxonomy_path.read_bytes())
    (inputs / "resolved-config.json").write_bytes(
        (test_set_folder / "resolved-config.json").read_bytes()
    )
    (inputs / "complete.json").write_bytes(
        (test_set_folder / "complete.json").read_bytes()
    )
    prompt_path = inputs / "system-prompt.txt"
    prompt_path.write_text(system_prompt, encoding="utf-8")

    suite_dir = output_folder / "native" / "evaluation"
    suite_dir.mkdir(parents=True)
    (suite_dir / "taxonomy.json").write_bytes(copied_taxonomy.read_bytes())
    native_path = output_folder / "assert-evaluation.yaml"
    native_path.write_text(
        yaml.safe_dump(
            _native_config(
                config,
                output_folder,
                copied_test_set,
                copied_taxonomy,
                system_prompt,
                judge,
            ),
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return native_path, suite_dir, _hash_file(prompt_path)


def evaluate(
    config_path: Path,
    runner: Callable[[Path], subprocess.CompletedProcess[str]] = run_assert,
    status_runner: Callable[[Path], subprocess.CompletedProcess[str]] = run_assert_status,
) -> tuple[Path, int]:
    config, test_set_folder, output_folder, system_prompt = load_evaluation_config(
        config_path
    )
    if output_folder.exists():
        raise EvaluationError(f"Output destination already exists: {output_folder}")

    completion = _load_json(test_set_folder / "complete.json", "test-set completion")
    if completion.get("status") != "complete":
        raise EvaluationError("Saved test set is not complete")
    expected_count = completion.get("complete_count", completion.get("expected_count"))
    if completion.get("expected_count") != expected_count:
        raise EvaluationError("Saved test-set completion counts do not match")
    if (
        not isinstance(expected_count, int)
        or isinstance(expected_count, bool)
        or expected_count <= 0
    ):
        raise EvaluationError("Saved test-set completion has an invalid case count")

    resolved_generation = _load_json(
        test_set_folder / "resolved-config.json", "resolved generation config"
    )
    source_assert_version = resolved_generation.get("assert_version")
    if source_assert_version is not None and source_assert_version != ASSERT_VERSION:
        raise EvaluationError(
            f"Saved test set used assert-ai {source_assert_version}, expected {ASSERT_VERSION}"
        )
    try:
        _reject_credential_fields(resolved_generation)
    except GenerationError as exc:
        raise EvaluationError(
            f"Saved generation config cannot be reused: {exc}"
        ) from exc
    pipeline = resolved_generation.get("pipeline")
    if not isinstance(pipeline, dict) or not isinstance(pipeline.get("judge"), dict):
        raise EvaluationError("Saved generation config has no judge settings")
    judge = pipeline["judge"]

    test_set_relative = completion.get("test_set")
    taxonomy_relative = completion.get("taxonomy")
    test_set_path = (
        (test_set_folder / test_set_relative).resolve()
        if isinstance(test_set_relative, str)
        else test_set_folder
    )
    taxonomy_path = (
        (test_set_folder / taxonomy_relative).resolve()
        if isinstance(taxonomy_relative, str)
        else test_set_folder
    )
    try:
        test_set_path.relative_to(test_set_folder.resolve())
        taxonomy_path.relative_to(test_set_folder.resolve())
    except ValueError:
        raise EvaluationError("Saved artifact paths must stay within the test-set folder") from None
    if not isinstance(test_set_relative, str) or not test_set_path.is_file():
        raise EvaluationError(f"Saved test set is missing: {test_set_path}")
    if not isinstance(taxonomy_relative, str) or not taxonomy_path.is_file():
        raise EvaluationError(f"Saved taxonomy is missing: {taxonomy_path}")
    try:
        test_rows = _validate_test_set(test_set_path, expected_count)
    except GenerationError as exc:
        raise EvaluationError(str(exc)) from exc
    expected_ids = {str(row["test_case_id"]) for row in test_rows}
    _load_json(taxonomy_path, "taxonomy")

    source_paths = {
        "complete.json": test_set_folder / "complete.json",
        "resolved-config.json": test_set_folder / "resolved-config.json",
        "test_set.jsonl": test_set_path,
        "taxonomy.json": taxonomy_path,
    }
    source_hashes = {name: _hash_file(path) for name, path in source_paths.items()}

    output_folder.mkdir(parents=True)
    try:
        native_path, suite_dir, prompt_hash = _prepare_output(
            output_folder,
            config,
            test_set_folder,
            test_set_path,
            taxonomy_path,
            system_prompt,
            judge,
        )
        completed = runner(native_path)
        if completed.returncode != 0:
            raise EvaluationError(
                f"ASSERT evaluation failed with exit code {completed.returncode}"
                f"{_failure_detail(completed)}"
            )

        run_dir = suite_dir / "run"
        manifest = _load_json(run_dir / "manifest.json", "run manifest")
        if manifest.get("status") != "completed":
            raise EvaluationError(f"ASSERT run status is not completed: {manifest.get('status')}")
        inference_rows = _read_jsonl(run_dir / "inference_set.jsonl", "inference results")
        _validate_unique_ids(inference_rows, expected_ids, "inference results")
        _validate_scores(run_dir / "scores.jsonl", expected_ids)

        for name, path in source_paths.items():
            if _hash_file(path) != source_hashes[name]:
                raise EvaluationError(f"Source test artifact changed during evaluation: {path}")

        status_completed = status_runner(output_folder / "native")
        if status_completed.returncode != 0:
            raise EvaluationError(
                f"ASSERT status failed with exit code {status_completed.returncode}"
                f"{_failure_detail(status_completed)}"
            )
        try:
            status_payload = json.loads(status_completed.stdout)
        except json.JSONDecodeError as exc:
            raise EvaluationError(f"ASSERT status returned invalid JSON: {exc.msg}") from exc
        if not isinstance(status_payload, dict):
            raise EvaluationError("ASSERT status did not return an object")
        prompt_metrics = status_payload.get("prompt_metrics")
        if not isinstance(prompt_metrics, dict) or prompt_metrics.get("scored_total") != expected_count:
            raise EvaluationError(
                f"ASSERT scored {prompt_metrics.get('scored_total') if isinstance(prompt_metrics, dict) else 0}/{expected_count} cases"
            )

        summary = _build_summary(
            status_payload,
            config,
            expected_count,
            prompt_hash,
            source_hashes,
        )
        _write_json(output_folder / "summary.json", summary)
        _write_json(
            output_folder / "complete.json",
            {
                "status": "complete",
                "assert_version": ASSERT_VERSION,
                "expected_count": expected_count,
                "scored_count": expected_count,
                "summary": "summary.json",
            },
        )
        return output_folder, expected_count
    except Exception as exc:
        _write_json(
            output_folder / "failed.json",
            {
                "status": "failed",
                "assert_version": ASSERT_VERSION,
                "error": str(exc),
            },
        )
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate a model against saved tests")
    parser.add_argument("--config", required=True, type=Path, help="Path to JSON config")
    args = parser.parse_args()
    try:
        output_folder, count = evaluate(args.config)
    except (EvaluationError, OSError) as exc:
        print(f"Evaluation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Evaluated {count} test cases in {output_folder}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
