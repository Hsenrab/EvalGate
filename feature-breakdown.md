# MVP Feature Breakdown

Based on [requirements.md](./requirements.md), the MVP is split into 12 features
in dependency order. Each feature has a distinct outcome and acceptance boundary.
This breakdown is for planning; it does not authorize implementation.

## Phase 1 - Establish the foundation

### 1. Standalone workbench setup

Package the pinned ASSERT engine and vendored UI so no separate ASSERT checkout
is required.

**Includes:** Python/Node setup, upstream revision and licence records, local
artifact directory, Git exclusions, and localhost-only UI.

**Done when:** A fresh installation starts the UI and invokes the installed
`assert-ai` executable.

**First checkpoint:** Verify the chosen ASSERT revision supports the required
artifact formats, scoring fields, and execution settings. Defer unsupported
capabilities rather than expanding the engine.

### 2. Shared configuration and model selection

Give the UI and runner one consistent configuration source.

**Includes:** Root `.env` loading, process-variable precedence, strict
`ASSERT_MODEL_OPTIONS` validation, configured-model-only selection, and a
placeholder-only environment example.

**Done when:** Both interfaces expose the same models, reject invalid/unknown
selections, and never expose credentials.

**Depends on:** 1.

### 3. Model-and-prompt target adapter

Introduce the narrow extension boundary for evaluation targets.

**Includes:** Typed target configuration, local prompt-file loading for the
runner, one validation/mapping function, and explicit rejection of unsupported
target kinds.

**Done when:** Changing the model or prompt requires only configuration/files and
cannot change judge settings.

**Depends on:** 2.

## Phase 2 - Create reusable evaluation packs

### 4. Trial authoring through ASSERT's UI

Make the existing authoring workflow work in the new repository layout.

**Includes:** Trial creation/run launch, taxonomy and prompt inspection, the
existing system-prompt text area, configured-model enforcement, and hiding
unsupported target controls.

**Done when:** A user can create a trial and inspect its artifacts using the
pinned engine.

**Depends on:** 1-2.

### 5. Save an immutable, versioned pack

Turn reviewed trial artifacts into reusable tests.

**Includes:**

- One atomic behavior and single-turn cases with unique IDs.
- Context, compatibility declarations, taxonomy, rubrics, and source configuration.
- Frozen judge identifier, settings, and scoring configuration.
- Metadata, checksums, and overwrite protection.
- Validation of permissible and impermissible coverage before saving.

**Done when:** A reviewed trial saves as a new pack version; invalid contents and
overwrites are rejected.

**Depends on:** 4.

### 6. Persistent pack catalogue

Discover and validate saved packs without editing runner code.

**Includes:** Listing name/version/behavior/case count, inspecting metadata,
checksum verification, and context/target compatibility validation.

**Done when:** Packs remain discoverable after restart; altered or incompatible
packs are rejected.

**Depends on:** 5.

## Phase 3 - Run frozen tests reliably

### 7. Execute a saved pack

Run an explicit model/prompt combination against a selected pack version.

**Includes:** One Python entry point, explicit execution selections, run-local
copies of pack inputs, strict parsing, generation disabled, and invocation
through `assert-ai run`.

**Done when:** Repeated executions create separate runs while published pack
files and judge configuration remain unchanged. The runner works with the UI
stopped.

**Depends on:** 3, 6.

### 8. Execution controls and durable run records

Make execution reliable and reproducible, including unsuccessful runs.

**Includes:** Engine-supported concurrency/timeouts/bounded retries, unique run
directories, timestamps/status, resolved target and judge settings, exact prompt,
pack checksums, thresholds, ASSERT revision, and viewer-compatible evidence.

**Done when:** Provider failures, retry exhaustion, and interruptions remain
visibly incomplete; later configuration changes cannot alter earlier run records.

**Depends on:** 7.

## Phase 4 - Produce trustworthy gate decisions

### 9. Evidence completeness validation

Determine whether a run contains enough valid evidence to support a decision.

**Includes:** Exactly one successful final score per expected case, required
dimensions/node judgments, rejection of duplicate/missing/unexpected/skipped/
failed/invalid cases, and applicability validation.

**Done when:** Incomplete, invalid, or zero-applicability evidence cannot produce
a pass.

**Depends on:** 8.

### 10. Gate calculation and reporting

Calculate the specified metrics and return an actionable result.

**Includes:**

- Impermissible violation rate using its relevant-case denominator.
- Overrefusal using valid, applicable dimension judgments, excluding N/A.
- Separate permissible-side violation reporting.
- Threshold validation in `[0, 1]`; equality passes.
- `pass`, `fail`, and `needs_review`.
- Console/JSON output with counts, numerators/denominators, thresholds, and
  failing-case references.
- Documented non-success exit codes.

**Done when:** Focused fixtures demonstrate pass, fail, and review-required
outcomes without treating partial evidence as a final decision.

**Depends on:** 9.

### 11. Run history and evidence inspection

Reopen previous results through the runner and ASSERT UI.

**Includes:** Run listing/inspection, persistent history, UI evidence viewing, and
comparison of compatible runs.

**Done when:** Earlier runs remain accessible after restart through the same
artifact location. No automated regression decision is introduced.

**Depends on:** 8; final gate display depends on 10.

## Phase 5 - Make it reusable

### 12. Onboarding example and end-to-end acceptance

Document and demonstrate the complete workflow.

**Includes:** Non-sensitive examples, setup/startup instructions, adding
models/prompts/packs, credential variable names, artifact paths, UI update checks,
extension-boundary documentation, and clearly labelled recorded results.

**Done when:** A fresh user completes the workflow, adds a second
behavior/model/prompt without runner changes, and passes the acceptance checks
in [requirements.md](./requirements.md#4-acceptance-checks).

**Depends on:** All preceding features. Update documentation alongside each
feature rather than leaving it all until the end.

## Suggested delivery milestones

| Milestone | Features | Demonstrable outcome |
| --- | --- | --- |
| Foundation | 1-3 | Standalone setup with controlled model/prompt selection |
| Reusable tests | 4-6 | Author, save, and discover immutable packs |
| Repeatable execution | 7-8 | Run frozen tests and preserve evidence |
| Trustworthy decisions | 9-11 | Validate, gate, report, and reopen results |
| Reusable MVP | 12 | Documented, verified customer onboarding |

## Decisions before implementation

- Repository location and supported operating system.
- Initial behavior, case count, and acceptance thresholds.
- Initial model/provider configuration and credential provisioning.
- System prompt examples to ship.
- Customer permission to install Node.js.

## Outside the MVP

Keep the future capabilities listed in
[requirements.md](./requirements.md#5-future-features) out of these MVP features,
including agents/tools, multi-turn tests, regression gates, governance, shared
hosting, and scheduling.
