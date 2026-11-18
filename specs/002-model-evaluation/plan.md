# Implementation Plan: Model Evaluation

**Branch**: `002-model-evaluation` | **Date**: 2026-11-18 | **Spec**: [spec.md](spec.md)

## Summary

Add one small `evaluate_model.py` CLI that accepts a JSON config, evaluates a
saved feature-1 test set through ASSERT 0.3.0 with generation disabled, saves a
traceable run summary, and fails unless every expected case has one valid
judgment. The wrapper will orchestrate ASSERT and validate its artifacts; it will
not implement inference, judging, retries, or metric calculation.

## Technical Context

- **Runtime and dependencies**: Python 3.11+, existing pinned
  `assert-ai[azure-auth]==0.3.0`, standard library, and the existing YAML
  dependency. No new package is needed.
- **Inputs**:
  - One JSON config containing a config-relative saved test-set folder, candidate
    model/settings, config-relative system-prompt file, and a new output folder.
  - Feature-1 `complete.json`, `resolved-config.json`, `test_set.jsonl`, and
    `taxonomy.json`.
  - Credentials only from the environment.
- **Outputs**: An ASSERT run with `manifest.json`, `inference_set.jsonl`,
  `scores.jsonl`, and `metrics.json`; run-local copies of the source artifacts
  and resolved inputs; plus EvalGate `summary.json` and `complete.json`.
- **Execution boundary**: Invoke `assert-ai run --config <absolute-yaml>
  --strict`. Reuse ASSERT's `inference` and `judge` stages, timeout/retry
  behavior, and `assert-ai results status <suite> <run> --json` summary. The
  wrapper owns boundary validation, immutability, completion checks, and clear
  errors only.
- **Data safety**: Reject credential-like config fields. Never overwrite a
  destination. Copy source artifacts into the new run before pointing ASSERT at
  them because ASSERT may normalize/rewrite a writable test-set input.

## Constitution Check

- **Compose ASSERT rather than rebuild it**: passes by delegating inference,
  judging, retries, and metric calculation to ASSERT.
- **Reusable configuration**: passes with config-relative paths and explicit
  candidate and output settings.
- **Sufficient evidence**: passes by requiring complete, unique, successful
  scores before writing a completion marker; absent or inapplicable metrics are
  unavailable, never zero.
- **Immutable inputs and traceability**: passes by copying and hashing source
  cases, taxonomy, prompt, resolved judge settings, model identifiers, and
  ASSERT version into each run.
- **Protect customer data**: passes by using environment credentials and
  preserving the existing local/output exclusions.
- **Simple and tested**: passes with one orchestration script and focused
  offline fixtures; no runtime framework, adapter system, or alternate scoring.

## Dependency Findings

- ASSERT 0.3.0 supports a pipeline containing only `inference` and `judge`;
  generation stages can be omitted.
- A hosted target uses `pipeline.inference.target.model` plus
  `pipeline.inference.target.system_prompt`.
- ASSERT accepts explicit `test_set_path` and `taxonomy_path`, writes
  `inference_set.jsonl` and `scores.jsonl`, and records run status in
  `manifest.json`.
- `--strict` is available for malformed JSONL rejection.
- `assert-ai results status --json` derives score-based metrics, including
  expected/scored counts, judge failures, policy-violation permissibility
  buckets, and overrefusal dimension data.
- ASSERT's general inference path can rewrite the supplied test-set file. The
  evaluation wrapper must therefore supply a run-owned copy, not the source.
- The installed `assert-ai==0.3.0` parser accepted an evaluation-only YAML with
  explicit `test_set_path` and `taxonomy_path`, and no generation stages. Its CLI
  exposes the planned strict run and JSON run-status commands.

## Implementation

1. Add `evaluate_model.py` with config loading and credential-field rejection,
   following `generate_tests.py` conventions.
2. Validate the source set before any provider call:
   - non-existing destination;
   - complete marker, resolved generation config, test set, and taxonomy;
   - expected count from the source completion record;
   - exactly one structurally valid row per unique expected case ID.
3. Resolve and read the exact system prompt, then copy `test_set.jsonl`,
   `taxonomy.json`, `resolved-config.json`, `complete.json`, and the prompt into a
   new run-owned `inputs` directory. Record SHA-256 hashes and verify the
   originals still match after ASSERT exits.
4. Build one native ASSERT YAML containing only:
   - shared suite/results paths under the new output;
   - inference target model/settings and system prompt;
   - the copied test-set and source taxonomy paths;
   - the judge settings copied from the source resolved generation config.
5. Run ASSERT once in strict mode with its supported timeout/concurrency
   settings from evaluation config. On handled failure, preserve the run folder
   for inspection, write a failed status, and return nonzero; never label
   partial evidence complete.
6. Validate that `manifest.json` is completed, and that `inference_set.jsonl`
  and `scores.jsonl` contain exactly one successful, judge-valid row for every
  expected ID, with no duplicates or unexpected IDs. A valid score row may mark
  one or more dimensions not applicable; reject only failed, malformed, or
  otherwise invalid judgments.
7. Query ASSERT's JSON run-status result, then write `summary.json` containing:
   expected/scored counts, candidate model and prompt hash, judge model,
   `policy_violation_not_permissible`, `policy_violation_permissible`, and
   `overrefusal`, each with `numerator`, `denominator`, `rate`, or status
   `unavailable`.
8. Write `complete.json` last only after artifact validation, source hash
   verification, and summary creation.
9. Update README setup and commands with one evaluation example and the
   distinction between generated cases, evaluated runs, and unavailable
   metrics.

## Files

- `evaluate_model.py` — config, orchestration, immutable-input copies, and
  completion validation.
- `tests/test_evaluate_model.py` — focused offline fixtures and mocked ASSERT
  executions.
- `README.md` — evaluation configuration, command, outputs, and limitations.
- One new non-sensitive example evaluation config/system prompt under
  `examples/` only if needed to make the walkthrough directly runnable.

## Validation

- Unit tests prove that two runs can use different candidates without changing
  source bytes or judge settings.
- Tests prove duplicate, missing, failed, malformed, and zero-applicable evidence
  return nonzero and do not create `complete.json`.
  A separate case proves that a valid judgment with a not-applicable dimension
  remains a complete result while its affected metric is unavailable.
- Tests prove metric labels and `numerator/denominator/rate` values are carried
  correctly, while unavailable metrics omit a numeric rate.
- Run the smallest suite:
  `.\.venv\Scripts\python.exe -m unittest tests.test_generate_tests tests.test_evaluate_model -v`
- Manual live validation is separate and explicitly invoked with bounded
  cases/timeouts. It must evaluate the existing 10-case test set and confirm the
  source directory remains byte-for-byte unchanged.

## Open Questions

None. The result schema is intentionally derived from the saved ASSERT status
JSON plus the required EvalGate validity checks rather than introducing a
provider-neutral evaluation abstraction.
