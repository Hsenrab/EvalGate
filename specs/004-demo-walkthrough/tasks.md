---
description: "Proportionate task list for demo walkthrough"
---

# Tasks: Demo Walkthrough

**Input**: [spec.md](spec.md) and [plan.md](plan.md)

**Scope**: Tracked non-sensitive end-to-end demo inputs and a README walkthrough.
No runtime code, new dependencies, live-output commits, or automated provider
tests.

## Tasks

- [X] T001 Add non-sensitive behavior/context, neutral and training-only biased prompts, generation config, and two evaluation configs under `examples/end-to-end/`.
- [X] T002 Add the complete generate-review-evaluate-compare walkthrough, credential placeholders, output locations, cost warning, and applicability caveat to `README.md`.
- [X] T003 Validate tracked JSON with the existing loaders, run `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`, and scan `examples/end-to-end/` for secrets and absolute machine paths.
- [X] T004 Perform the bounded manual live 10-case workflow only when explicitly invoked, record immutability and evidence locations in `specs/004-demo-walkthrough/plan.md`, and keep generated outputs out of Git.

## Validation

Offline validation must make no provider calls. Live acceptance is separate,
bounded, and reported without committing generated output.
