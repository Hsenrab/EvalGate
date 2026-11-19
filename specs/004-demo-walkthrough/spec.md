# Feature Specification: Demo Walkthrough

**Feature Branch**: `004-demo-walkthrough`
**Created**: 2026-11-19
**Status**: Draft
**Input**: Feature 4, "Demo files and walkthrough", from [feature-breakdown.md](../../feature-breakdown.md), subject to [requirements.md](../../requirements.md) and the project constitution.

## User Scenarios & Testing

### User Story 1 - Run the Complete Demo (Priority: P1)

As a first-time evaluation author, I want non-sensitive example files and a
short walkthrough so that I can generate one reviewed test set, evaluate it
twice, and compare the resulting evidence using a few commands.

**Acceptance Scenarios**:

1. **Given** the installed dependencies, approved environment credentials, and
   unused demo output paths, **When** the user follows the walkthrough, **Then**
   one 10-20 case test set, two separate evaluation runs, and one comparison
   report are created.
2. **Given** the generated test set, **When** the user reviews it before
   evaluation, **Then** the walkthrough identifies where to inspect permitted
   and prohibited coverage without implying automatic approval.
3. **Given** the two evaluations, **When** comparison runs, **Then** the
   walkthrough explains side-by-side metrics, second-minus-first differences,
   and case-level changes using the same cases and judge settings.
4. **Given** source tests and earlier outputs already exist, **When** later demo
   steps run, **Then** they remain unchanged and the user is directed to new
   output folders rather than overwriting prior work.

## Requirements

### Functional Requirements

- **FR-001**: The repository MUST provide non-sensitive demo behavior, context,
  and system-prompt files suitable for the complete workflow.
- **FR-002**: The demo MUST provide one generation configuration for one
  behavior requesting 10-20 single-turn cases.
- **FR-003**: The demo MUST provide two evaluation configurations that reference
  the same generated test set and judge settings and differ only in the
  candidate model or system prompt, with separate output destinations.
- **FR-004**: Demo configurations MUST contain placeholder deployment names and
  placeholder-only credential instructions. They MUST NOT contain tokens,
  secrets, customer data, or machine-specific paths.
- **FR-005**: The walkthrough MUST cover installation, environment setup,
  config-relative paths, generation, manual permitted/prohibited review, two
  evaluations, comparison, common output locations, and reuse of prior outputs.
- **FR-006**: The commands MUST use the repository's three scripts and MUST NOT
  require Node.js, a UI, or a separate ASSERT source checkout.
- **FR-007**: The walkthrough MUST state that model calls are live, bounded by
  the demo case count and configured settings, and subject to the user's
  approved provider credentials and usage costs.
- **FR-008**: Generated tests, evaluation runs, and comparison reports MUST
  remain local and excluded from Git by the repository's existing ignore rules.
- **FR-009**: The feature MUST include a manual end-to-end acceptance check
  confirming that one test set can be reviewed, evaluated twice, and compared
  while source tests and earlier outputs remain unchanged.
- **FR-010**: The walkthrough MUST describe the practical limitation that
  denominator or applicability changes can affect rate differences and direct
  users to inspect changed cases and their evidence.

### Common Errors

- A demo output folder already exists; the walkthrough directs the user to
  choose a new folder rather than overwrite it.
- A placeholder model deployment has not been replaced.
- Credentials are missing or point to an unapproved destination.
- The user skips test-set review and assumes successful generation means the
  cases are suitable.

## Success Criteria

- **SC-001**: A new user can follow the walkthrough to produce one test set,
  two complete runs, and one comparison using no more than the documented
  commands and example files.
- **SC-002**: The demo's tracked files contain no credential values, generated
  customer data, machine-specific paths, or live run artifacts.
- **SC-003**: A manual end-to-end check records that the shared test set and
  prior evaluation output remain byte-for-byte unchanged after the second
  evaluation and comparison.
- **SC-004**: The resulting comparison exposes metric counts/rates, changed
  cases, and evidence references without claiming a winner or deployment
  approval.

## Scope and Assumptions

- Features 1-3 are implemented and provide the commands used by the demo.
- The demo uses placeholders for provider deployment names and requires the
  user to supply approved environment credentials outside Git.
- Only a short command-line walkthrough and example input/config files are
  included.
- Automated live model tests, sample live outputs in Git, UI work, hosting, CI,
  scheduling, catalogues, and formal versioning are out of scope.
