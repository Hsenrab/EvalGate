# Feature Specification: Lightweight Results Viewer

**Feature Branch**: `006-results-viewer`
**Created**: 2026-11-19
**Status**: Draft
**Input**: Feature 6, "Lightweight results viewer", from [feature-breakdown.md](../../feature-breakdown.md), subject to the project constitution.

## User Scenarios & Testing

### User Story 1 - Inspect Saved Results Locally (Priority: P1)

As an evaluation author, I want to open a local HTML file and select saved
evaluation or comparison JSON so that I can review results without a server,
build step, upload, or command-line JSON inspection.

**Acceptance Scenarios**:

1. **Given** one valid saved `summary.json`, **When** the user selects it in the
   viewer, **Then** the completion status, candidate identity, system-prompt
   text, case counts, and labeled metrics are displayed accurately.
2. **Given** a valid `comparison.json`, **When** the user selects it, **Then**
   both runs, side-by-side metric values, second-minus-first differences, and
   changed cases are displayed accurately.
3. **Given** an invalid, incomplete, or unsupported JSON file, **When** the
   user selects it, **Then** the viewer shows a clear local error and does not
   present partial values as a complete result.
4. **Given** sensitive local artifacts, **When** the viewer is used, **Then**
   files are read only in the browser and no upload or network request occurs.

## Requirements

### Functional Requirements

- **FR-001**: The viewer MUST be one self-contained, read-only HTML file that
  opens directly from disk without a backend, package installation, Node.js,
  framework build, account, or service.
- **FR-002**: The user MUST be able to select one saved run summary, one
  comparison file, or multiple supported JSON artifacts through browser-local
  file selection.
- **FR-003**: For a run summary, the viewer MUST show completion status,
  ASSERT version, candidate model, exact system prompt, expected/scored counts,
  and every metric's status, numerator, denominator, and rate.
- **FR-004**: For a comparison, the viewer MUST show both candidate identities,
  both system prompts, both case counts, side-by-side metric values, explicitly
  labeled second-minus-first differences, and changed cases by `test_case_id`.
- **FR-005**: Changed cases MUST expose the saved response and judgment
  reference strings from the comparison without requiring the browser to
  scan arbitrary folders or upload files.
- **FR-006**: A metric with unavailable evidence MUST be shown as unavailable.
  The viewer MUST NOT display a zero, fake rate, or numeric difference for it.
- **FR-007**: The viewer MUST validate the selected top-level JSON shape and
  required fields before rendering. Unsupported or incomplete evidence MUST
  produce a clear error state.
- **FR-008**: The viewer MUST make no network requests and MUST NOT persist,
  transmit, or modify selected files.
- **FR-009**: The viewer MUST describe results as observations and MUST NOT
  calculate or display a winner, significance, threshold decision, safety
  certification, or deployment approval.
- **FR-010**: Documentation MUST explain browser file-selection limitations and
  advise users to open sensitive artifacts only on an approved local machine.

### Common Errors

- User selects ordinary JSON that is neither a run summary nor comparison.
- Selected JSON is malformed or lacks required metric fields.
- Comparison contains changed-case references but not a complete metric shape.
- Browser disallows a local file operation needed for an optional evidence link.

## Success Criteria

- **SC-001**: Representative saved summaries and comparisons render source
  counts, rates, and differences without manual data transformation.
- **SC-002**: Invalid or unsupported input shows a visible error and no
  completion-shaped result.
- **SC-003**: The delivered HTML works from disk with zero package/build steps
  and makes zero network requests.
- **SC-004**: Changed cases are discoverable by ID and retain references to both
  runs' saved response and judgment evidence.

## Scope and Assumptions

- Feature 2's `summary.json` and Feature 3's `comparison.json` are the only
  supported top-level artifact shapes in the first version.
- Browser-local file selection is the minimum practical file-access mechanism;
  folder scanning, direct arbitrary filesystem access, uploads, and accounts
  are excluded.
- This viewer is read-only and local. It does not modify saved evidence or
  replace the command-line validation performed when those artifacts were
  generated.
- Hosting, multi-user access, editing, drag-and-drop catalogs, persistence,
  server APIs, and enhanced Stage 2 UI are out of scope.
