# Implementation Plan: Demo Walkthrough

**Branch**: `004-demo-walkthrough` | **Date**: 2026-11-19 | **Spec**: [spec.md](spec.md)

## Summary

Add one tracked `examples/end-to-end/` input bundle and a short README
walkthrough that exercises the existing generate, evaluate, and compare scripts.
No runtime code or new dependency is needed.

## Technical Context

- **Runtime and dependencies**: Existing Python 3.11+ project, pinned ASSERT
  dependency, and the three existing scripts. No package change.
- **Tracked inputs**:
  - Non-sensitive `behavior.txt` and `context.txt`.
  - `generation.json` requesting 10 cases with placeholder GPT-5/Azure
    deployment names.
  - A neutral and a training-only gender-bias system-prompt file.
  - Two evaluation JSON files referencing the same generated test set and
    differing only in prompt/output folder.
- **Generated outputs**: One test set, two run folders, and one comparison file
  under `outputs/`, which remains ignored and is never committed.
- **Path handling**: Example config paths are relative to each config location.
  The walkthrough tells users to edit output names rather than overwrite.
- **Execution boundary**: Reuse `generate_tests.py`, `evaluate_model.py`, and
  `compare_runs.py` without changing their behavior. The walkthrough is the
  only new user-facing integration.

## Constitution Check

- **Compose rather than rebuild**: passes; this feature supplies examples and
  documentation around existing commands.
- **Evidence validity**: passes by requiring manual review of generated coverage
  and explicit completion/summaries before the next step.
- **Immutable traceability**: passes by using new output folders and explaining
  that generation/evaluation comparison never overwrites prior evidence.
- **Data protection**: passes with non-sensitive tracked inputs, placeholders,
  environment-only credentials, and ignored outputs.
- **Simple and tested**: passes with a small example bundle and manual
  end-to-end acceptance rather than new automation.

## Implementation

1. Add `examples/end-to-end/` with `behavior.txt`, `context.txt`,
   `system-prompt-neutral.txt`, `system-prompt-biased-training.txt`,
   `generation.json`, `evaluation-neutral.json`, and
   `evaluation-biased-training.json`.
2. Keep all model names as explicit replacement placeholders. Keep the GPT-5
   routing prefix documented where Azure users need it, without embedding a
   real deployment.
3. Point both evaluation configs at the same generated test set and retain the
   same judge/scoring settings from generation. Only the system-prompt file and
   output folder differ.
4. Add a concise end-to-end section to `README.md` covering installation,
   environment variables, replacing deployment placeholders, output naming,
   generating 10 cases, reviewing permitted/prohibited taxonomy coverage,
   running both evaluations, comparing, and locating key files.
5. Document that generated outputs are local, live calls have usage cost, a
   completed generation is not automatic approval, and rate differences with
   changed denominators need case-level interpretation.
6. Perform a bounded manual acceptance run using local non-placeholder model
   settings only, without copying live outputs into Git. Record in
   `specs/004-demo-walkthrough/plan.md` whether source tests and earlier
   outputs remained byte-for-byte unchanged.

## Files

- `examples/end-to-end/*` — tracked, non-sensitive demo inputs and configs.
- `README.md` — complete walkthrough and output interpretation.
- `specs/004-demo-walkthrough/plan.md` — manual acceptance record.

## Validation

- Validate every tracked JSON config with the existing config loaders without
  making provider calls.
- Run the existing offline unit suite:
  `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`
- Scan tracked demo files for credentials and machine-specific absolute paths.
- Run the manual live workflow separately and explicitly: 10 generated cases,
  two bounded evaluations, and one comparison. Confirm all source/prior output
  hashes remain unchanged.

## Open Questions

None. The demo intentionally uses a neutral prompt and a clearly labeled
training-only biased prompt because it makes the comparison illustrative
without requiring two deployments.

## Manual Acceptance

On 2026-11-18, the bounded live workflow was exercised with local,
non-placeholder equivalents of this bundle:

- 10 gender-bias cases were generated.
- The same saved set was evaluated with neutral and training-only biased
  system prompts.
- `compare_runs.py` compared all 10 cases and reported one changed judgment.
- `evaluate_model.py` verified the saved test artifacts remained unchanged
  during each run; the shared source hashes were subsequently checked again.

Evidence remains local and ignored under `outputs/test-set-gender-bias`,
`outputs/evaluation-gender-bias-01`,
`outputs/evaluation-gender-bias-biased-training-01`, and
`outputs/comparison-neutral-vs-biased-training-02.json`. The tracked placeholder
bundle itself was validated offline and was not run with placeholder deployment
names.
