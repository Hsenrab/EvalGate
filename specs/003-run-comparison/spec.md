# Feature Specification: Run Comparison

**Feature Branch**: `003-run-comparison`
**Created**: 2026-11-18
**Status**: Draft
**Input**: Feature 3, "Run comparison script", from [feature-breakdown.md](../../feature-breakdown.md), subject to [requirements.md](../../requirements.md) and the project constitution.

## User Scenarios & Testing

### User Story 1 - Compare Two Saved Runs (Priority: P1)

As an evaluation author, I want to compare two completed evaluations of the
same saved tests so that I can inspect metric differences and case-level
judgment changes without generating tests or making model calls.

**Acceptance Scenarios**:

1. **Given** two complete compatible run folders, **When** comparison is
   invoked, **Then** it prints and saves each candidate's identity, case counts,
   labeled metrics, and differences calculated as second run minus first run.
2. **Given** the same case ID has different judgments in the two runs, **When**
   comparison is invoked, **Then** the saved output identifies the change and
   provides response or evidence references for both sides.
3. **Given** different source tests, context, taxonomy, rubrics, judge settings,
   incomplete runs, duplicate results, or invalid judgments, **When** comparison
   is invoked, **Then** it exits nonzero and produces no successful comparison.

## Requirements

### Functional Requirements

- **FR-001**: The user MUST invoke comparison with two saved run-folder paths.
- **FR-002**: Comparison MUST make no provider or model calls.
- **FR-003**: Both runs MUST have successful completion markers and exactly one
  valid final judgment for every expected case ID.
- **FR-004**: Before comparison, the runs MUST be proven compatible using saved
  test content, context, taxonomy, rubrics, and judge/scoring settings. Matching
  folder names or case IDs alone MUST NOT establish compatibility.
- **FR-005**: The comparison MUST show the candidate model and system prompt for
  each run.
- **FR-006**: The saved and printed comparison MUST contain side-by-side
  expected/scored counts and each metric's numerator, denominator, rate, and
  labeled difference (`second_minus_first`).
- **FR-007**: A metric with no applicable evidence MUST be reported as
  unavailable, and its numeric difference MUST be omitted.
- **FR-008**: Cases MUST be matched by case ID. Changed judgments MUST be listed
  with references to the two runs' responses and judgments.
- **FR-009**: Incomplete, incompatible, duplicate, failed, or invalid run
  evidence MUST return nonzero and MUST NOT produce a comparison marked
  complete.
- **FR-010**: Comparison output MUST describe observed differences only. It MUST
  NOT declare a winner, statistical significance, safety certification, or
  deployment approval.

### Common Errors

- A run folder is missing or lacks a successful completion marker.
- A run is incomplete or has missing, duplicate, failed, or invalid score rows.
- The saved test content, taxonomy/context, rubric, or judge settings differ.
- A required metric is unavailable in one or both runs.

## Success Criteria

- **SC-001**: Two compatible complete runs produce one machine-readable
  comparison and one understandable console summary without model calls.
- **SC-002**: Every metric difference is explicitly second minus first, and
  unavailable metrics have no numeric difference.
- **SC-003**: Every changed case is matched by ID and contains references to
  both runs' evidence.
- **SC-004**: No incomplete or incompatible pair can produce a completion marker
  or successful comparison.

## Scope and Assumptions

- Feature 2's saved evaluation-run folders are the input contract.
- Existing run files and their evidence remain unchanged.
- This is a local, offline comparison: no generation, inference, judge,
  network call, or provider credential is required.
- Partial comparisons, statistical claims, winner selection, thresholds, UI,
  and deployment decisions are out of scope.
