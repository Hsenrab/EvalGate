---
description: "Proportionate task list for lightweight results viewer"
---

# Tasks: Lightweight Results Viewer

**Input**: [spec.md](spec.md) and [plan.md](plan.md)

**Scope**: One self-contained local HTML viewer for saved run summaries and
comparisons. Excludes a backend, build system, uploads, persistence, winner
selection, and arbitrary filesystem scanning.

## Tasks

- [X] T001 Add exact system-prompt text to future summaries in `evaluate_model.py` and a focused assertion in `tests/test_evaluate_model.py` while preserving compatibility with older summaries.
- [X] T002 Create `results-viewer.html` with inline Clawpilot-themed CSS/JavaScript, local multi-file selection, strict summary/comparison validation, run cards, metric tables, unavailable states, changed-case references, denominator warnings, errors, and no network/storage APIs.
- [X] T003 Document opening `results-viewer.html`, selecting supported JSON files, local browser limitations, evidence-reference behavior, and no-upload/no-network guarantees in `README.md`.
- [X] T004 Run `.\.venv\Scripts\python.exe -m unittest tests.test_evaluate_model -v`, load representative summary/comparison plus malformed and unavailable fixtures in the viewer, and statically confirm `results-viewer.html` has no external resources or network/storage APIs.

## Validation

Automated tests are provider-free. Viewer acceptance uses local saved artifacts
and fixtures only; it must never upload or fetch selected evidence.
