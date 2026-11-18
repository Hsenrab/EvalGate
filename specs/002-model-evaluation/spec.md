# Feature Specification: Model Evaluation

**Feature Branch**: `002-model-evaluation`
**Created**: 2026-11-18
**Status**: Draft
**Input**: Plan feature 2, "Evaluation script", from [feature-breakdown.md](../../feature-breakdown.md), subject to [requirements.md](../../requirements.md) and the project constitution.

## Clarifications

### Session 2026-11-18

- Q: Should an incomplete or failed evaluation run remain for diagnosis? → A:
  Keep the run folder with failed status and diagnostics.

## User Scenarios & Testing

### User Story 1 - Evaluate a Saved Test Set (Priority: P1)

As an evaluation author, I want to apply a selected model and system prompt to a
previously generated test set so that I receive traceable responses, judgments,
and labeled metrics without changing or regenerating the tests.

**Acceptance Scenarios**:

1. **Given** a complete saved test set, a referenced system-prompt file, a
   candidate model, and a new output folder, **When** evaluation is invoked,
   **Then** every expected case has one final response and judgment, the
   requested metrics are saved and displayed, and the original test set is
   unchanged.
2. **Given** the same saved test set and a different model or system prompt,
   **When** evaluation is invoked again, **Then** it produces a separate run
   while preserving the same source cases and judge/scoring configuration.
3. **Given** an existing output folder, missing input, invalid configuration,
   provider failure, duplicate result, or missing judgment, **When** evaluation
   runs, **Then** it exits nonzero with a useful error and does not report the
   run as complete. Any newly created run folder is retained with failed status
   and available diagnostics for inspection.

## Requirements

### Functional Requirements

- **FR-001**: The user MUST invoke evaluation with one JSON configuration file
  selecting a saved test-set folder, a candidate model and supported settings,
  a system-prompt file, and a new output folder.
- **FR-002**: Relative file and output paths MUST resolve from the configuration
  file's directory.
- **FR-003**: Evaluation MUST use ASSERT's inference and judge workflow against
  working copies of the saved tests with test generation disabled. It MUST NOT
  modify source tests, taxonomy, rubrics, or judge/scoring settings.
- **FR-004**: Each successful run MUST save the source test set and taxonomy,
  exact candidate prompt, resolved candidate and judge settings, ASSERT version,
  responses, judgments, execution status, and final summary.
- **FR-005**: The run MUST require exactly one successful final result for every
  expected case ID. Duplicate, missing, malformed, failed, or otherwise invalid
  judgments MUST NOT be counted as successful evidence. A valid judgment may
  mark an individual dimension as not applicable; that remains a successful
  case-level result.
- **FR-006**: The summary MUST show expected and scored counts and preserve
  distinct labels and numerators/denominators for impermissible policy
  violations, permissible-side violations, and overrefusal.
- **FR-007**: A metric with missing scores or no applicable evidence MUST be
  reported as unavailable, not as a successful zero rate.
- **FR-008**: Existing output destinations MUST be rejected before model calls
  or writes. Invalid inputs and execution failures MUST return nonzero without
  changing the source test set. Once the new output destination has been
  created, handled failures MUST leave it in place with failed status and the
  available evidence and diagnostics. A retry MUST select a different output
  destination.
- **FR-009**: Credentials MUST come from the environment and MUST NOT be accepted
  in configuration or saved in run artifacts.
- **FR-010**: The script MUST reuse ASSERT's supported timeout, retry, and strict
  validation settings without adding a separate retry loop.

### Common Errors

- Missing saved test artifacts, taxonomy, prompt file, or required credentials.
- Existing output file or folder.
- Candidate or judge provider execution failure.
- Incomplete, duplicate, malformed, or failed result rows.
- Metric evidence missing or no applicable cases.

## Success Criteria

- **SC-001**: One valid configuration evaluates every expected case against the
  chosen model and prompt and saves a complete traceable run.
- **SC-002**: Two configurations using the same saved test set produce separate
  results while leaving source test content and judge settings unchanged.
- **SC-003**: Required metrics expose their labels, numerators, denominators, and
  rates, with unavailable evidence clearly marked.
- **SC-004**: Invalid, incomplete, duplicate, or failed results cannot produce a
  completion marker or successful evaluation summary.

## Scope and Assumptions

- The feature composes the pinned ASSERT 0.3.0 inference and judge capabilities;
  it does not implement a model client, judge, or scoring engine.
- The saved test set produced by feature 1 remains the source of cases, taxonomy,
  context, rubrics, and judge configuration.
- This feature is single-run and local: one script, one configuration, and one
  new output folder per invocation.
- Run comparison, threshold gates, UI, statistical claims, automatic deployment
  decisions, and live-model automated tests are out of scope.
- Failed and incomplete run folders are diagnostic artifacts, not successful
  evaluation results, and are not overwritten on retry.
