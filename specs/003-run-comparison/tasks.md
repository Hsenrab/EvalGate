---
description: "Proportionate task list for run comparison"
---

# Tasks: Run Comparison

**Input**: [spec.md](spec.md) and [plan.md](plan.md)

**Scope**: One offline script comparing two complete Feature 2 runs. Excludes
provider calls, partial comparisons, statistical claims, and winner selection.

## Tasks

- [X] T001 Implement saved-run loading, compatibility checks, complete-result validation, metric differences, case matching, evidence references, output-file protection, and console reporting in `compare_runs.py`.
- [X] T002 Add focused offline tests for correct differences, changed cases, unavailable metrics, incompatibility, incomplete/invalid evidence, and existing output rejection in `tests/test_compare_runs.py`.
- [X] T003 Document the comparison command, output shape, compatibility requirements, and no-model-call boundary in `README.md`.
- [X] T004 Run the focused validation with `.\.venv\Scripts\python.exe -m unittest tests.test_evaluate_model tests.test_compare_runs -v`.

## Validation

All validation is local and makes no model calls. The two runs must remain
unchanged and an invalid or incompatible pair must produce no comparison output.
