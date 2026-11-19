# Implementation Plan: Run Comparison

**Branch**: `003-run-comparison` | **Date**: 2026-11-18 | **Spec**: [spec.md](spec.md)

## Summary

Add one offline `compare_runs.py` CLI that accepts two completed Feature 2 run
folders, proves they used compatible inputs and judge settings, and writes a
side-by-side metric and case-level comparison. It will read saved JSON/JSONL
evidence only and make no model or provider calls.

## Technical Context

- **Runtime and dependencies**: Python 3.11+ and standard library only.
- **Inputs**: Two Feature 2 run folders containing `complete.json`,
  `summary.json`, `resolved-config.json`, and `inputs/` plus native
  `inference_set.jsonl` and `scores.jsonl`.
- **Output**: A console summary and one new `comparison.json` file. The default
  destination is `comparison.json` in the current directory; an explicit
  `--output` path is supported. Existing destinations are rejected.
- **Compatibility evidence**:
  - copied `inputs/test_set.jsonl` and `inputs/taxonomy.json` must match byte for
    byte;
  - saved generation `behavior`, `context`, and `pipeline.judge` must match;
  - run completion and ASSERT version must be valid;
  - each run must contain exactly one valid final score and one inference row
    per expected case ID.
- **Difference direction**: Every numeric metric difference is labeled
  `second_minus_first` and computed as second rate minus first rate.
- **Case evidence**: Changed cases are matched by `test_case_id`; the output
  stores the two dimension verdicts and stable references to each run's
  `inference_set.jsonl` and `scores.jsonl`, not duplicated response transcripts.

## Constitution Check

- **Sufficient evidence**: passes by requiring complete, unique, valid score
  rows before producing a comparison.
- **Immutable inputs**: passes because comparison is read-only and writes only
  its explicitly selected output file.
- **Compose existing work**: passes by consuming Feature 2's saved artifacts and
  ASSERT verdict fields; it adds no judge or metric engine.
- **Simple and tested**: passes with one local script and focused fixtures.
- **Honest reporting**: passes by omitting unavailable metric differences and
  avoiding winner, significance, or deployment claims.

## Dependency Findings

- Evaluation runs already preserve candidate model, exact system prompt, source
  hashes, copied tests, copied taxonomy, copied resolved generation config,
  ASSERT version, completion state, responses, and judgments.
- ASSERT score rows identify cases with `test_case_id`, status with
  `judge_status`, and valid not-applicable dimensions through
  `dimension_applicability`.
- Inference and score JSONL rows are not guaranteed to have the same physical
  order, so matching must use case IDs.
- Feature 2 summaries already expose the three required metric numerator,
  denominator, and rate values.

## Implementation

1. Add `compare_runs.py` argument parsing for two run folders and optional output.
2. Load and validate each run's completion, summary, resolved candidate config,
   copied source artifacts, manifest, inference rows, and score rows. Reuse or
   extract the minimum common validation from `evaluate_model.py`; do not add a
   new framework.
3. Establish compatibility before computing results:
   - exact copied test/taxonomy bytes;
   - equal generation behavior/context and judge/scoring settings;
   - equal expected case-ID sets and ASSERT version.
4. Build side-by-side counts and three labeled metric sections. Compute a
   difference only when both rates are available; otherwise record
   `unavailable` and omit `second_minus_first`.
5. Compare score rows by case ID. Record a change when the dimension values or
   dimension applicability differ, with response/judgment evidence references
   for both runs. Include unchanged-count and changed-count summaries.
6. Print a compact factual summary and write `comparison.json` after all
   validation succeeds.
7. Update [README.md](../../README.md) with the command, comparison output,
   compatibility rules, and the no-provider-call boundary.

## Files

- `compare_runs.py` — offline compatibility validation and comparison.
- `tests/test_compare_runs.py` — focused local fixtures.
- `README.md` — comparison command and output interpretation.

## Validation

- Offline tests prove correct second-minus-first metric differences and
  changed-outcome matching by case ID.
- Tests prove rejection of different test content, taxonomy/context, or judge
  settings.
- Tests prove missing, duplicate, failed, malformed, and incompatible evidence
  cannot produce comparison output.
- A run-specific not-applicable metric produces no numeric difference.
- Run:
  `.\.venv\Scripts\python.exe -m unittest tests.test_compare_runs -v`
- No live model calls are required or permitted for this feature.

## Open Questions

None. The explicit optional output path avoids modifying either immutable run
folder while retaining a predictable default.
