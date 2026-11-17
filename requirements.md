# Model Evaluation Workbench: Reusable MVP

Status: Draft for review | Date: 2026-11-17

## 1. Purpose

Provide a reusable local workbench for manually evaluating a configured hosted model with a selected system prompt, using saved tests, ASSERT's UI, and a thin Python runner in a new customer repository. Support repeated use across model/prompt combinations and behaviors through configuration, without CI, a database, or cloud storage.

All custom functionality belongs to the customer repository. Consume ASSERT through its pinned CLI/configuration and artifact formats; do not require engine changes or imports from its repository scripts. Defer capabilities unavailable through that dependency rather than silently expanding scope.

The customer demo is the first use case, not a hard-coded workflow. The tool supports a human approval decision; it does not certify safety or approve deployment. Sample sizes and thresholds are user-selected, not claims of statistical confidence. This document authorizes no implementation.

## 2. User workflow

1. List saved packs by name, version, behavior, and case count.
2. Create a trial evaluation in ASSERT's UI and inspect its taxonomy and prompts.
3. Use Python to save the reviewed artifacts as a versioned pack.
4. Choose a model from the list configured in `.env` and a system prompt, then run that combination against the pack without regenerating tests.
5. Read the console/JSON gate result and inspect evidence in the UI.
6. Reopen earlier runs, change the model or system prompt, or create a new pack version without changing runner code.

Include a documented example for onboarding and demonstrations, separate from customer configuration. Label any recorded example results as recorded, never live.

## 3. MVP requirements

### Test packs

- Support multiple named packs, each containing one atomic behavior and initially using single-turn prompts with a configurable case count.
- Include context, taxonomy with explicit permissible/impermissible labels, test set with unique case IDs, judge rubrics, and source configuration. Review coverage of both permitted and prohibited requests before saving.
- Freeze the judge model identifier, settings, and scoring configuration with the pack. Configure generation and judge models independently of the candidate; changing the target must not change the judge through model defaults.
- Record name, version, intended application context/target compatibility, source suite/run, case count, creation time, and content checksums.
- Store packs separately from working artifacts. Reject overwrites and checksum mismatches; changes require a new version.
- Persist the catalogue on disk across restarts. Add packs through the same save operation, not edits to runner code; validate declared context/target compatibility before reuse.

### Model/prompt selection and execution

- Use `ASSERT_MODEL_OPTIONS` as a JSON array of explicit provider/model identifiers. Load the customer repository's root `.env` for both UI and runner; existing process variables take precedence. Both must expose only this configured list, with no inferred or manual model additions. Document provider credential variable names, not values.
- Let users independently select a configured model and a system prompt from a local prompt file. Adding a model or prompt requires configuration/files only.
- Route target configuration through the adapter boundary below. Implement only model plus system prompt initially; agents, tools, callable/HTTP targets, and trace capture remain future work.
- Provide one Python entry point for listing/saving packs, running model/prompt combinations through `assert-ai run`, and listing/inspecting previous runs.
- Select model, system prompt, pack version, gate configuration, and local data location explicitly. Do not hard-code providers, behaviors, thresholds, or machine-specific paths.
- Validate inputs, verify pack checksums, and copy pack inputs into a run-local working area before invoking ASSERT with strict input parsing and generation disabled. Never execute against published pack files: ASSERT may normalise/rewrite test-set inputs. Preserve the published files unchanged.
- Give each run a unique directory containing resolved target and judge settings, the exact system prompt, pack version/checksums, thresholds, ASSERT revision, timestamps, status, and viewer-compatible evidence. Changing the model/prompt must not change pack inputs or scoring settings.
- Explicitly report an empty/invalid model list, unknown model selections, missing credentials or prompt files, provider errors, incomplete execution, and invalid scores. Do not silently substitute another model.
- Configure concurrency, request timeouts, and bounded retries through the pinned engine's supported settings. Do not add a second retry loop; exhausted calls and interrupted runs remain visibly incomplete.

### Extension boundary

- Use a typed target configuration and one function that validates it and builds ASSERT's target mapping. Initially support only model plus system prompt; reject other kinds explicitly.
- Keep target-specific logic out of pack storage, gating, and reporting. Document the extension point; do not implement capability negotiation, plugin discovery, or unused adapters.
- Future targets can map to `target.callable` with `target.trace`, `target.endpoint`, or model `target.tools`. ASSERT drives evaluation and its Prompt Agent tool loop; callable agents retain their own orchestration. Do not build a parallel runtime.

### Gate and reporting

Configure maximum rates in `[0, 1]` per behavior and snapshot them with each run. Equality with a threshold passes. Gate on these explicit metrics:

- **Impermissible violation:** `policy_violation_not_permissible`, derived from node judgments and taxonomy. Divide flagged cases by cases with at least one relevant impermissible behavior.
- **Overrefusal:** `overrefusal`, using ASSERT's valid, applicable dimension judgments and denominator; exclude declared N/A values.

Also report `policy_violation_permissible` over its relevant-case denominator. Do not substitute aggregate `policy_violation` for impermissible violations or treat permissible-side failures as equivalent to overrefusal.

Require exactly one successful final score per expected case ID, with required dimensions and valid node judgments; duplicate, missing, unexpected, skipped, failed, or invalid cases prevent a pass. Report each metric's numerator/denominator and require nonzero applicable evidence for both permissible and impermissible behaviors. Missing applicability is not a zero violation rate.

| Result         | Rule                                                                                                                                                                            |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `pass`         | Evidence is complete and valid, all required denominators are nonzero, and both thresholds are met.                                                                             |
| `fail`         | Evidence is complete and valid, all required denominators are nonzero, and a threshold is exceeded.                                                                             |
| `needs_review` | Execution/scoring is incomplete or invalid, or required applicable evidence is absent. Show any observed violations, but do not present partial rates as a final gate decision. |

Console and JSON output must show scored/expected counts, rates, thresholds, and failing-case references. Use documented non-success exit codes for failures, review-required results, and execution/configuration errors. Results apply only to the tested configuration and behavior; human sign-off stays outside the tool.

Retain previous runs across restarts and use ASSERT's existing UI to compare compatible runs. Automated baseline/regression decisions remain outside the MVP.

### Packaging and UI

- Install ASSERT's engine as a pinned Python dependency; do not copy it.
- Vendor the UI source and lockfile, recording the upstream commit, MIT licence/copyright notices, and local changes. Exclude installed dependencies, build output, and local configuration.
- Limit UI changes to packaging, paths, executable integration, configured-model enforcement, and exposing only model plus system prompt initially. Hide unsupported target controls rather than removing upstream functionality needed later. Use the workbench artifact location and intended installed `assert-ai` executable.
- Document Python/Node.js setup, startup, adding models/prompts/packs, artifact paths, and UI update/compatibility checks. No separate ASSERT checkout is required; the customer repo maintains its UI snapshot.
- Do not copy the repository regression runner's commit/worktree machinery or import it as a package API. Use its frozen-test approach as prior art for the customer runner.

**UI boundary:** trial authoring uses the existing system-prompt text area; selecting a local prompt file is a Python-runner feature, not a new UI picker. Authoring currently requires a trial evaluation, not generation alone. Pack saving and gating also belong to the script. Avoid undocumented UI HTTP APIs.

### Data and safety

- Keep `.env`, generated packs, traces, logs, results, and credentials out of Git. Supply a placeholder-only `.env.example`; never print or snapshot environment-file contents or credential values.
- Use customer-approved evaluation data and system prompts, with non-sensitive bundled examples.
- Bind the unauthenticated UI to localhost only.

## 4. Acceptance checks

- Complete the user workflow from documented setup without a separate ASSERT checkout.
- Verify UI trial creation/run launch and evidence viewing against the pinned engine in the new repository layout.
- Rerun a pack with identical contents into separate results; verify both UI and script runs use the configured artifact location and the script works with the UI stopped.
- Reject altered packs and overwrites. Demonstrate threshold pass/fail and an incomplete/invalid run that cannot pass.
- Verify zero-applicability, duplicate/missing case IDs, skipped scores, and provider timeout/retry exhaustion cannot pass. Confirm execution leaves published pack checksums unchanged.
- Add a second behavior pack, model-list entry in `.env`, and prompt file without editing the runner; confirm the UI and runner show the same models and reject incompatible pack/context selections and invalid inputs.
- Rerun a pack while changing only the model or only the system prompt. Confirm target selection changes while judge settings and pack inputs remain fixed.
- Restart the workbench and reopen its catalogue and run history. Changed thresholds or prompt files must not alter earlier run records.
- Verify UI/runner environment precedence and model-list enforcement without logging credentials. Run setup and compatibility checks using the installed dependency, not an ASSERT source checkout.

## 5. Future features

- **Tests:** multi-turn scenarios, multi-behavior packs, external imports, coverage/deduplication, and holdout sets.
- **Gates:** approval profiles, severity blockers, compatible-baseline regression, confidence intervals, and production sample sizes. Prefer a supported upstream API or selectively adapt comparison code/tests with attribution.
- **Governance:** reviewer roles, pack lifecycle, signed decisions, expiring exceptions, and approval-system integration.
- **Integrations:** additional target adapters for real agents through traced callables or HTTP targets, tools, sandboxed actions, broader provider validation, and generation-only UI, reusing the same pack/gate/report flow.
- **Operations:** remote storage, authenticated shared hosting, concurrent users, retention/backups, and tamper-evident audit records.
- **Usability:** catalogue filtering, cost previews, resumable runs, richer exports, and scheduling.

Formal production approval use also requires agreed acceptance criteria, judge calibration against human-reviewed examples, and security/data-retention controls.

## 6. Decisions before implementation

1. Repository location and supported operating system.
2. Initial behavior, case count, and acceptance thresholds.
3. Initial `.env` model list, providers, and credential provisioning.
4. System prompt examples to ship.
5. Customer permission to install Node.js.

## 7. References

[UI walkthrough](https://github.com/responsibleai/ASSERT/blob/main/docs/guides/use-local-viewer.md) |
[Viewer setup](https://github.com/responsibleai/ASSERT/blob/main/viewer/README.md) |
[Packaging](https://github.com/responsibleai/ASSERT/blob/main/pyproject.toml) |
[Regression prior art](https://github.com/responsibleai/ASSERT/blob/main/scripts/regression_test.py) |
[Config schema](https://github.com/responsibleai/ASSERT/blob/main/docs/config/schema.md) |
[Targets](https://github.com/responsibleai/ASSERT/blob/main/docs/targets/README.md) |
[Behavior library](https://github.com/responsibleai/ASSERT/blob/main/assert_ai/library/behaviors/README.md)

Confirm capabilities against the chosen ASSERT revision before implementation.
