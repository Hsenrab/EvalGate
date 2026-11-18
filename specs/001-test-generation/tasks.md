---
description: "Proportionate task list for test generation"
---

# Tasks: Test Generation

**Input**: [spec.md](spec.md), [plan.md](plan.md), and [research.md](research.md)

**Scope**: One config-driven ASSERT generation wrapper. Excludes evaluation,
comparison, UI, and custom authentication, retry, logging, or recovery systems.

## Tasks

- [X] T001 Pin `assert-ai==0.3.0` in `requirements.txt`; confirm the installed version and `assert-ai run --help` support `--config` and `--strict`.
- [X] T002 Implement config loading, config-relative text references, basic input validation, native YAML generation, resolved-input saving, existing-output rejection, and one `--strict` ASSERT CLI invocation in `generate_tests.py`.
- [X] T003 Add exact-count/unique-ID validation and write `complete.json` last; preserve native ASSERT artifacts and return a useful nonzero error without a completion marker on incomplete output in `generate_tests.py`.
- [X] T004 Add focused offline tests for success, config-relative paths, existing output, short output despite child success, and one child failure in `tests/test_generate_tests.py`.
- [X] T005 Add local credential, input, and output exclusions in `.gitignore`.
- [X] T006 Document installation, JSON configuration, environment credentials, the generation command, manual review, call/cost limits, and common errors in `README.md`.
- [X] T007 Run the focused tests and CLI smoke check, then record the results in `specs/001-test-generation/research.md`.
- [X] T008 Only with explicit approval, run one bounded 10-case generation with non-sensitive inputs and record the manual acceptance result in `README.md`. **Verified:** GPT-5.4 generation succeeded with `azure/gpt5_series/assert-intermediate`; the wrapper validated exactly 10 cases and wrote `complete.json`.

## Validation

Automated validation makes no provider calls. A live run requires explicit
approval and is reported separately from local test evidence.
