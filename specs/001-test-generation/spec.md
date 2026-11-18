# Feature Specification: Test Generation

**Feature Branch**: `main` (existing branch; no branch-creation hook configured)

**Created**: 2026-11-17

**Status**: Draft

**Input**: Specify feature 1, "Test generation script", from
[feature-breakdown.md](../../feature-breakdown.md), subject to
[requirements.md](../../requirements.md) and the project constitution.

## Clarifications

### Session 2026-11-17

- Q: If ASSERT requires a trial evaluation to generate tests, how should the script obtain permission for those extra model calls? A: Invoking generation grants permission, provided the required extra work and cost implications are documented beforehand; no separate opt-in is required.
- Q: When the script stops with an error, should it leave any partial files in place or remove them? A: Stop with an error and remove files created by this invocation where possible; report cleanup failures and any retained output.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate a Small Test Set (Priority: P1)

As an evaluation author, I want to supply one configuration file describing a
behavior and its context so that I can generate a small test set without
repeatedly entering long text or model settings.

**Why this priority**: Generating a usable test set is the foundation of the
generate-once, evaluate-twice workflow.

**Independent Test**: Invoke generation with a valid configuration requesting
10 cases and a new output folder. Verify that exactly 10 complete, uniquely
identified cases are saved and the completion message identifies their folder.

**Acceptance Scenarios**:

1. **Given** a valid configuration, available credentials, supported model
   settings, and a new output folder, **When** the author invokes generation,
   **Then** the requested number of single-turn cases for one behavior is saved
   and generation reports success.
2. **Given** a configuration referencing behavior or context text files with
   relative paths, **When** generation is invoked from another working
   directory, **Then** the same files and output location are resolved relative
   to the configuration file's directory.
3. **Given** long behavior or context text in referenced files, **When**
   generation runs, **Then** the full content is supplied without requiring the
   author to embed it in command-line arguments.

---

### User Story 2 - Review and Reuse Saved Tests (Priority: P1)

As an evaluation author, I want to inspect the generated cases and their scoring
basis so that later evaluations can reuse the same tests and judge settings.

**Why this priority**: Generation has value only if its output can be reviewed
and reused without generating another test set.

**Independent Test**: Inspect a saved test set without the original configuration
or referenced text files. Confirm that each case, its context, taxonomy, rubrics,
and resolved judge/scoring settings can be recovered from the saved artifacts.
Actual candidate evaluation is delivered by feature 2.

**Acceptance Scenarios**:

1. **Given** completed generation, **When** the author opens the saved artifacts,
   **Then** each case has a unique ID, request content, applicable context,
   taxonomy, and judge rubrics, with explicit resolved judge/scoring settings.
2. **Given** completed generation, **When** the original configuration or
   referenced text is subsequently changed, **Then** the saved test set still
   contains the original content and scoring basis needed for reuse.
3. **Given** completed generation, **When** the author manually reviews
   permitted and prohibited request coverage, **Then** the saved cases expose
   the classification and rubric information needed for that review without
   requiring model calls or an approval workflow.

---

### User Story 3 - Recognize Failure Without Losing Data (Priority: P1)

As an evaluation author, I want invalid inputs, unsupported capabilities, and
incomplete generation to fail clearly so that I neither overwrite existing work
nor mistake partial output for a reusable test set.

**Why this priority**: Protecting saved data and reporting honest outcomes are
mandatory even for a small demo.

**Independent Test**: Use local fixtures or controlled failures for an existing
destination, invalid configuration, missing credentials, and incomplete generated
artifacts. Verify a nonzero exit status, actionable diagnostics, and unchanged
pre-existing files without live model calls.

**Acceptance Scenarios**:

1. **Given** an output path that already exists, including an empty folder,
   **When** generation is invoked, **Then** it fails before model calls and
   leaves the existing destination unchanged.
2. **Given** malformed configuration, missing required values or files, an
   invalid case count, or missing required credentials, **When** generation is
   invoked, **Then** it fails before model calls with an actionable diagnostic
   that does not expose credentials.
3. **Given** a provider failure or fewer complete cases than requested,
   **When** generation ends, **Then** it returns nonzero, reports the failure
   and any available complete/requested counts, and does not describe the output
   as ready for reuse. It removes its newly created output where possible and
   reports any cleanup failure and retained output location.
4. **Given** the selected ASSERT release cannot support the required saved-test
   workflow through its documented interfaces, **When** feasibility is assessed,
   **Then** the limitation is reported and dependent implementation stops for
   user agreement rather than substituting a replacement engine.

### Edge Cases

- An output path names an existing file rather than a folder: reject it without
  modifying the file.
- A case count is zero, negative, fractional, or absent: reject it before model
  calls. The demo uses 10-20 cases; no arbitrary maximum is introduced here.
- A referenced file is missing or unreadable, or required behavior text is
  empty: identify the affected input and stop before model calls.
- Generated cases have missing or duplicate IDs, missing review/scoring fields,
  or a total different from the requested count: report incomplete or invalid
  generation, never success.
- Generation fails or handles an interruption after creating output: stop with
  an error and remove only output created by that invocation where possible.
  Report cleanup failures explicitly. An abrupt termination may prevent cleanup;
  any retained output must not be marked complete, and a retry must use a
  non-existing destination.
- ASSERT requires a trial evaluation during generation: disclose the additional
  candidate/judge calls and cost implications in the usage documentation before
  invocation. Invoking generation grants permission for that documented work;
  no separate opt-in or interactive confirmation is required.
- Generated coverage is imbalanced between permitted and prohibited requests:
  make that visible for manual review; do not claim balanced coverage or
  automatically approve the test set.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The author MUST be able to invoke generation using one JSON
  configuration-file path specifying one behavior and context, a positive
  integer case count, the generation model, explicit judge model/settings, and
  a new output folder.
- **FR-002**: Behavior and context MUST support text-file references for long
  content. All relative file and output paths MUST resolve against the
  configuration file's directory, independent of the working directory.
- **FR-003**: Generation MUST save exactly the requested number of complete,
  single-turn cases before reporting success.
- **FR-004**: Saved artifacts MUST preserve each case's unique ID and request
  content together with the shared context, taxonomy, judge rubrics, resolved
  judge/scoring settings, ASSERT release, and generation model/settings needed
  for manual review and later evaluation without regeneration or mutable
  original files. They MUST exclude credentials and MUST NOT require model
  calls, an approval workflow, or automatic coverage certification for review.
- **FR-005**: Generation MUST reject every existing output destination before
  model calls or writes to that destination. It MUST NOT overwrite existing
  test sets, configuration, or referenced input files.
- **FR-006**: Invalid inputs and missing credentials MUST produce actionable,
  credential-free diagnostics and a nonzero exit status before model calls.
  Execution failures and incomplete or invalid generated artifacts MUST also
  return nonzero and MUST NOT be reported or marked as complete. On handled
  failures or interruptions, generation MUST attempt to remove only output
  created by the current invocation. Cleanup failures MUST be reported with
  retained output locations without hiding the original error. Cleanup after
  abrupt termination is not guaranteed; automatic recovery is not required.
- **FR-007**: Completion reporting MUST identify the output folder and
  complete/requested case counts. Failure reporting MUST distinguish invalid
  inputs, unsupported capabilities, execution failure, and incomplete output,
  reporting counts when available.
- **FR-008**: Credentials MUST come from environment variables, never from
  configuration fields or saved artifacts. If local environment-file loading
  is offered, existing process variables MUST take precedence. Diagnostics and
  outputs MUST NOT expose credentials.
- **FR-009**: Setup MUST exclude local credentials, generated outputs, and
  customer data from Git. Documentation MUST state that saved inputs and
  outputs remain local until the author deletes them and that the author is
  responsible for restricting local access and using approved model destinations.
- **FR-010**: Installation and usage documentation MUST describe dependency
  installation, required environment-variable names using placeholders only,
  configuration fields, config-relative paths, output locations, manual review,
  common errors, failure cleanup and its limitations, and retrying with a
  non-existing destination after failure.

### Required Compatibility and Scope Constraints

- **CC-001**: Before dependent implementation, verify and document whether one
  pinned ASSERT release supports generation, execution of saved tests with
  generation disabled, and the scoring artifacts required by
  [requirements.md](../../requirements.md), including separately identifiable
  impermissible violations, permissible-side violations, and overrefusal.
  Record the release, supporting documentation, artifact expectations, and
  limitations; do not claim support without evidence.
- **CC-002**: Use ASSERT's documented CLI, configuration-file mechanism, and
  artifact formats, preferring its existing fields. Do not construct long
  command lines containing behavior text, cases, rubrics, or serialized settings,
  and do not build a replacement generation or scoring engine.
- **CC-003**: If generation requires a trial evaluation, document its extra model
  calls and cost implications in the usage documentation before it is run.
  Invoking generation grants permission for that documented required trial
  evaluation, without a separate opt-in or interactive confirmation. This does
  not authorize optional extra evaluations or unbounded work. Unsupported
  capabilities or a workaround that materially expands scope require user
  agreement.
- **CC-004**: Deliver a small local Python script with ASSERT as a pinned
  dependency. It MUST work without Node.js, a UI, or a separate ASSERT source
  checkout. Reuse ASSERT's supported timeout and retry settings; add no parallel
  runtime or retry loop. Live invocations MUST have explicit bounded case counts,
  concurrency, retries, and timeouts.
- **CC-005**: Candidate evaluation and run comparison scripts, the complete
  demo walkthrough, UI, catalogues, formal versioning, adapter frameworks,
  threshold gates, automated regression decisions, partial comparisons, CI,
  scheduling, and shared hosting are outside this feature.

### Key Entities *(include if feature involves data)*

- **Generation Configuration**: The author's behavior/context or text-file
  references, requested case count, generation model/settings, judge
  model/settings, and destination. Contains no credentials.
- **Saved Test Set**: A complete collection of generated cases together with
  preserved shared inputs, resolved scoring configuration, generation provenance,
  and completion evidence needed for reuse.
- **Test Case**: A uniquely identified single-turn request with associated
  context, taxonomy, and rubrics that explain how it should be judged.
- **Generation Outcome**: A success or failure indication, output location,
  complete/requested counts when available, and non-sensitive diagnostics.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: One explicitly invoked generation requesting 10-20 cases creates
  exactly the requested number of complete cases in a new folder, with 100% of
  IDs unique and all required review/scoring information present.
- **SC-002**: A reviewer can locate every case's request, classification,
  context, rubric, and judge settings from saved artifacts alone, with zero
  additional model calls and no dependency on original input files.
- **SC-003**: Invoking the same configuration from two different working
  directories resolves 100% of referenced inputs and the destination identically.
  This measures path resolution, not identical generated text.
- **SC-004**: Every focused failure check for existing destinations, invalid
  configuration, missing inputs/credentials, provider failure, and incomplete or
  invalid artifacts returns nonzero; no pre-existing input or destination file
  is changed and no partial set is reported complete. Handled failure checks
  with normal write/delete permissions leave no newly created output; a
  controlled cleanup failure reports both the original error and retained
  output location.
- **SC-005**: Saved artifacts and repository status contain no configured
  credentials, generated outputs, or customer-data files.

## Assumptions

- This feature serves a local evaluation author generating single-turn tests
  for one behavior at a time; it does not provide multi-user operation.
- The author supplies approved model access, environment credentials, and
  non-sensitive inputs for the manual demo. No live model calls are authorized
  by writing this specification.
- ASSERT compatibility is an unverified prerequisite, not an established fact.
  Selecting its release and exact configuration/artifact fields belongs to
  planning and capability verification.
- The 10-20 case range is the initial demo size, not a guarantee of statistical
  coverage or a hard upper limit for all supported configurations.
- Human review is observational. Editing, approving, or formally versioning a
  test set is not a separate workflow in this feature.
- Focused automated validation uses small local fixtures and controlled failures,
  not provider calls. A separately invoked, bounded manual generation verifies
  the live happy path; feature 2 verifies actual saved-test evaluation reuse.
