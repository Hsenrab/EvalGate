"""Compare two complete evaluation runs without making model calls."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from evaluate_model import EvaluationError, _validate_scores


METRIC_NAMES = (
    "policy_violation_not_permissible",
    "policy_violation_permissible",
    "overrefusal",
)


class ComparisonError(Exception):
    """A clear, expected comparison failure."""


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _load_json(path: Path, description: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ComparisonError(f"Missing {description}: {path}") from None
    except json.JSONDecodeError as exc:
        raise ComparisonError(
            f"Invalid JSON in {description} {path}: {exc.msg}"
        ) from exc
    if not isinstance(value, dict):
        raise ComparisonError(f"{description.capitalize()} must be a JSON object: {path}")
    return value


def _read_jsonl(path: Path, description: str) -> list[dict[str, Any]]:
    if not path.is_file():
        raise ComparisonError(f"Missing {description}: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ComparisonError(
                f"Invalid JSON in {description} line {line_number}: {exc.msg}"
            ) from exc
        if not isinstance(row, dict):
            raise ComparisonError(
                f"{description.capitalize()} line {line_number} is not an object"
            )
        rows.append(row)
    return rows


def _index_rows(
    rows: list[dict[str, Any]], expected_count: int, description: str
) -> dict[str, dict[str, Any]]:
    if len(rows) != expected_count:
        raise ComparisonError(
            f"{description.capitalize()} has {len(rows)}/{expected_count} rows"
        )
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        case_id = row.get("test_case_id")
        if not isinstance(case_id, str) or not case_id.strip():
            raise ComparisonError(f"Every {description} row must have a test_case_id")
        if case_id in indexed:
            raise ComparisonError(
                f"{description.capitalize()} contains duplicate test_case_id {case_id}"
            )
        indexed[case_id] = row
    return indexed


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve_input(path: Path, description: str) -> Path:
    if not path.is_file():
        raise ComparisonError(f"Missing {description}: {path}")
    return path


def _load_run(path: Path) -> dict[str, Any]:
    run_path = path.resolve()
    if not run_path.is_dir():
        raise ComparisonError(f"Evaluation run folder does not exist: {run_path}")

    completion = _load_json(run_path / "complete.json", "run completion")
    if completion.get("status") != "complete":
        raise ComparisonError(f"Run is not complete: {run_path}")
    expected_count = completion.get("expected_count")
    scored_count = completion.get("scored_count")
    if (
        not isinstance(expected_count, int)
        or isinstance(expected_count, bool)
        or expected_count <= 0
        or scored_count != expected_count
    ):
        raise ComparisonError(f"Run completion counts are invalid: {run_path}")

    summary = _load_json(run_path / "summary.json", "run summary")
    if summary.get("status") != "complete":
        raise ComparisonError(f"Run summary is not complete: {run_path}")
    if (
        summary.get("expected_count") != expected_count
        or summary.get("scored_count") != expected_count
    ):
        raise ComparisonError(f"Run summary counts do not match completion: {run_path}")
    metrics = summary.get("metrics")
    if not isinstance(metrics, dict):
        raise ComparisonError(f"Run summary has no metrics: {run_path}")
    for metric_name in METRIC_NAMES:
        metric = metrics.get(metric_name)
        if not isinstance(metric, dict) or metric.get("status") not in {
            "available",
            "unavailable",
        }:
            raise ComparisonError(f"Run summary has invalid {metric_name}: {run_path}")
        if metric["status"] == "available":
            numerator = metric.get("numerator")
            denominator = metric.get("denominator")
            rate = metric.get("rate")
            if (
                not isinstance(numerator, int)
                or isinstance(numerator, bool)
                or not isinstance(denominator, int)
                or isinstance(denominator, bool)
                or denominator <= 0
                or not 0 <= numerator <= denominator
                or not isinstance(rate, (int, float))
                or isinstance(rate, bool)
            ):
                raise ComparisonError(f"Run summary has invalid {metric_name}: {run_path}")

    resolved = _load_json(run_path / "resolved-config.json", "resolved run config")
    candidate = resolved.get("candidate")
    if (
        not isinstance(candidate, dict)
        or not isinstance(candidate.get("model"), dict)
        or not isinstance(resolved.get("system_prompt"), str)
    ):
        raise ComparisonError(f"Run config has no candidate model or system prompt: {run_path}")

    inputs = run_path / "inputs"
    test_set_path = _resolve_input(inputs / "test_set.jsonl", "copied test set")
    taxonomy_path = _resolve_input(inputs / "taxonomy.json", "copied taxonomy")
    generation_path = _resolve_input(
        inputs / "resolved-config.json", "copied generation config"
    )
    generation = _load_json(generation_path, "copied generation config")
    source_hashes = summary.get("source_sha256")
    if not isinstance(source_hashes, dict):
        raise ComparisonError(f"Run summary has no source hashes: {run_path}")
    hash_paths = {
        "test_set.jsonl": test_set_path,
        "taxonomy.json": taxonomy_path,
        "resolved-config.json": generation_path,
    }
    for key, artifact_path in hash_paths.items():
        if source_hashes.get(key) != _hash_file(artifact_path):
            raise ComparisonError(
                f"Copied {key} does not match the saved source hash: {run_path}"
            )

    manifest = _load_json(
        run_path / "native" / "evaluation" / "run" / "manifest.json",
        "run manifest",
    )
    if manifest.get("status") != "completed":
        raise ComparisonError(f"ASSERT run manifest is not completed: {run_path}")
    stages = manifest.get("stages")
    if not isinstance(stages, dict) or stages.get("inference") != "completed" or stages.get("judge") != "completed":
        raise ComparisonError(f"ASSERT inference or judge stage is incomplete: {run_path}")

    inference_path = (
        run_path / "native" / "evaluation" / "run" / "inference_set.jsonl"
    )
    scores_path = run_path / "native" / "evaluation" / "run" / "scores.jsonl"
    inference_rows = _read_jsonl(inference_path, "inference results")
    inference_by_id = _index_rows(inference_rows, expected_count, "inference results")
    try:
        score_rows = _validate_scores(scores_path, set(inference_by_id))
    except (EvaluationError, OSError) as exc:
        raise ComparisonError(str(exc)) from exc
    scores_by_id = _index_rows(score_rows, expected_count, "scores")
    if set(scores_by_id) != set(inference_by_id):
        raise ComparisonError(f"Inference and score case IDs differ: {run_path}")

    return {
        "path": run_path,
        "completion": completion,
        "summary": summary,
        "resolved": resolved,
        "generation": generation,
        "test_set_path": test_set_path,
        "taxonomy_path": taxonomy_path,
        "inference_path": inference_path,
        "scores_path": scores_path,
        "scores": scores_by_id,
        "expected_count": expected_count,
    }


def _compatibility(first: dict[str, Any], second: dict[str, Any]) -> None:
    if first["test_set_path"].read_bytes() != second["test_set_path"].read_bytes():
        raise ComparisonError("Runs used different test-set content")
    if first["taxonomy_path"].read_bytes() != second["taxonomy_path"].read_bytes():
        raise ComparisonError("Runs used different taxonomy content")

    first_generation = first["generation"]
    second_generation = second["generation"]
    for key in ("behavior", "context"):
        if first_generation.get(key) != second_generation.get(key):
            raise ComparisonError(f"Runs used different generation {key}")
    first_pipeline = first_generation.get("pipeline")
    second_pipeline = second_generation.get("pipeline")
    if not isinstance(first_pipeline, dict) or not isinstance(second_pipeline, dict):
        raise ComparisonError("Saved generation configuration has no pipeline")
    if first_pipeline.get("judge") != second_pipeline.get("judge"):
        raise ComparisonError("Runs used different judge/scoring settings")

    if first["completion"].get("assert_version") != second["completion"].get("assert_version"):
        raise ComparisonError("Runs used different ASSERT versions")
    if set(first["scores"]) != set(second["scores"]):
        raise ComparisonError("Runs have different expected case IDs")


def _metric_comparison(first: Any, second: Any) -> dict[str, Any]:
    result = {
        "first": first if isinstance(first, dict) else {"status": "unavailable"},
        "second": second if isinstance(second, dict) else {"status": "unavailable"},
    }
    first_rate = first.get("rate") if isinstance(first, dict) else None
    second_rate = second.get("rate") if isinstance(second, dict) else None
    if (
        isinstance(first_rate, (int, float))
        and not isinstance(first_rate, bool)
        and isinstance(second_rate, (int, float))
        and not isinstance(second_rate, bool)
        and first.get("status") == "available"
        and second.get("status") == "available"
    ):
        result["second_minus_first"] = second_rate - first_rate
    return result


def _verdict_view(row: dict[str, Any]) -> dict[str, Any]:
    verdict = row["verdict"]
    return {
        "dimensions": verdict.get("dimensions"),
        "dimension_applicability": verdict.get("dimension_applicability", {}),
    }


def _evidence_ref(run: dict[str, Any], case_id: str, kind: str) -> str:
    path = run["inference_path"] if kind == "response" else run["scores_path"]
    return f"{path}#test_case_id={case_id}"


def _changed_cases(first: dict[str, Any], second: dict[str, Any]) -> list[dict[str, Any]]:
    changed: list[dict[str, Any]] = []
    for case_id in sorted(first["scores"]):
        first_score = first["scores"][case_id]
        second_score = second["scores"][case_id]
        first_view = _verdict_view(first_score)
        second_view = _verdict_view(second_score)
        if first_view == second_view:
            continue
        changed.append(
            {
                "test_case_id": case_id,
                "first": {
                    "judgment": first_view,
                    "response_reference": _evidence_ref(first, case_id, "response"),
                    "judgment_reference": _evidence_ref(first, case_id, "judgment"),
                },
                "second": {
                    "judgment": second_view,
                    "response_reference": _evidence_ref(second, case_id, "response"),
                    "judgment_reference": _evidence_ref(second, case_id, "judgment"),
                },
            }
        )
    return changed


def compare(first_folder: Path, second_folder: Path) -> dict[str, Any]:
    first = _load_run(first_folder)
    second = _load_run(second_folder)
    _compatibility(first, second)

    first_metrics = first["summary"]["metrics"]
    second_metrics = second["summary"]["metrics"]
    metrics = {
        name: _metric_comparison(first_metrics.get(name), second_metrics.get(name))
        for name in METRIC_NAMES
    }
    changed = _changed_cases(first, second)
    return {
        "status": "complete",
        "assert_version": first["completion"]["assert_version"],
        "difference_direction": "second_minus_first",
        "first": {
            "run_folder": str(first["path"]),
            "candidate_model": first["resolved"]["candidate"]["model"],
            "system_prompt": first["resolved"]["system_prompt"],
            "expected_count": first["expected_count"],
            "scored_count": first["summary"]["scored_count"],
        },
        "second": {
            "run_folder": str(second["path"]),
            "candidate_model": second["resolved"]["candidate"]["model"],
            "system_prompt": second["resolved"]["system_prompt"],
            "expected_count": second["expected_count"],
            "scored_count": second["summary"]["scored_count"],
        },
        "metrics": metrics,
        "cases": {
            "expected_count": first["expected_count"],
            "unchanged_count": first["expected_count"] - len(changed),
            "changed_count": len(changed),
            "changed": changed,
        },
    }


def run(first_folder: Path, second_folder: Path, output_path: Path) -> dict[str, Any]:
    output = output_path.resolve()
    if output.exists():
        raise ComparisonError(f"Comparison output already exists: {output}")
    comparison = compare(first_folder, second_folder)
    output.parent.mkdir(parents=True, exist_ok=True)
    _write_json(output, comparison)
    return comparison


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare two saved evaluation runs")
    parser.add_argument("first_run", type=Path, help="First completed run folder")
    parser.add_argument("second_run", type=Path, help="Second completed run folder")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("comparison.json"),
        help="New comparison JSON destination (default: comparison.json)",
    )
    args = parser.parse_args()
    try:
        result = run(args.first_run, args.second_run, args.output)
    except (ComparisonError, OSError) as exc:
        print(f"Comparison failed: {exc}", file=sys.stderr)
        return 1

    print(
        f"Compared {result['cases']['expected_count']} cases: "
        f"{result['cases']['changed_count']} changed, "
        f"{result['cases']['unchanged_count']} unchanged"
    )
    for metric_name, metric in result["metrics"].items():
        difference = metric.get("second_minus_first")
        rendered = "unavailable" if difference is None else f"{difference:+.6f}"
        print(f"{metric_name}: {rendered} (second minus first)")
    print(f"Saved comparison to {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
