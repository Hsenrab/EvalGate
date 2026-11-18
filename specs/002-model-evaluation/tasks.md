---
description: "Proportionate task list for model evaluation"
---

# Tasks: Model Evaluation

**Input**: [spec.md](spec.md) and [plan.md](plan.md)

**Scope**: One config-driven evaluation script using ASSERT inference and judge
stages against saved feature-1 tests. Excludes run comparison, UI, thresholds,
custom retry infrastructure, and automated live-model tests.

## Tasks

- [X] T001 Confirm the pinned ASSERT CLI accepts inference-plus-judge YAML with explicit copied `test_set_path` and `taxonomy_path`, then record the final config/output assumptions in `specs/002-model-evaluation/plan.md`.
- [X] T002 Implement config loading, credential rejection, config-relative paths, source-artifact validation, immutable input copying, ASSERT invocation, failed-run status, final result validation, metrics summary, and completion writing in `evaluate_model.py`.
- [X] T003 Add focused offline tests for successful reuse, source immutability, retained failed runs, duplicate/missing/invalid results, valid not-applicable judgments, unavailable metrics, and existing-output rejection in `tests/test_evaluate_model.py`.
- [X] T004 Document the evaluation config, command, saved artifacts, failure behavior, and metric labels in `README.md`, adding a non-sensitive `examples/` config only if it makes the workflow runnable without local files.
- [X] T005 Run the focused offline suite with `.\.venv\Scripts\python.exe -m unittest tests.test_generate_tests tests.test_evaluate_model -v`; validate a bounded live 10-case run separately only when explicitly invoked, confirming the source test folder remains unchanged.

## Validation

Offline tests must cover the meaningful success and failure boundaries without
provider calls. A successful live check is reported separately and is not
required for task completion unless explicitly invoked.
