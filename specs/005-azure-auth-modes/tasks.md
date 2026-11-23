---
description: "Proportionate task list for Azure auth modes"
---

# Tasks: Azure Authentication Modes

**Input**: [spec.md](spec.md) and [plan.md](plan.md)

**Scope**: Reuse ASSERT 0.3.0's existing API-key, explicit Entra, and
`DefaultAzureCredential` fallback behavior. Excludes custom credential code,
login flows, credential storage, and provider-specific adapters.

## Tasks

- [X] T001 Document API-key mode, explicit Entra mode, automatic `DefaultAzureCredential` fallback, precedence, ignored `.env` use, and common credential troubleshooting in `README.md`.
- [X] T002 Verify existing credential-field tests cover generation and evaluation configs; add only the minimum focused rejection tests in `tests/test_generate_tests.py` and `tests/test_evaluate_model.py` if coverage is missing.
- [X] T003 Run the provider-free validation with `.\.venv\Scripts\python.exe -m unittest tests.test_generate_tests tests.test_evaluate_model -v` and confirm the unchanged CLI/config path in `generate_tests.py` and `evaluate_model.py`.
- [X] T004 Record bounded manual smoke evidence for any auth modes actually run in `specs/005-azure-auth-modes/plan.md`, explicitly disclose unverified modes, and keep credentials and outputs out of Git.

## Validation

Automated tests must remain provider-free. Live smoke checks are optional,
bounded, and reported separately; no successful claim is made for an unrun
authentication mode.
