# Initial Demo Feature Breakdown

Based on [requirements.md](./requirements.md), deliver six features:
three Python scripts, then demo files and a walkthrough.

The outcome is **generate once, evaluate twice, compare**. This document is a
breakdown of the work, not an instruction to implement it.

## 1. Test generation script

**Outcome:** Generate and save a small test set for human review and reuse.

**Includes:**

- First verify that a pinned ASSERT version supports generation, saved-test
  execution, and the required scoring artifacts through its documented CLI.
  Surface unsupported capabilities rather than building a replacement engine.
- Add the pinned Python dependency and basic installation instructions.
- Accept a JSON config-file path with behavior/context, case count, generation
  model, judge model/settings, and output folder.
- Use ASSERT's supported config-file mechanism for large inputs. Reference
  text files for long content and resolve relative paths from the config folder.
- Save test cases with unique IDs, context, taxonomy, rubrics, and explicit
  judge/scoring configuration.
- Reject existing output folders and clearly report failed or incomplete
  generation. If ASSERT requires a trial evaluation, document its extra model
  calls and cost.
- Read credentials from the environment, keep secrets out of configuration and
  output, and exclude generated/customer data from Git.

**Done when:** A config-driven invocation creates a reviewable test set in a new
folder, including the artifacts needed for evaluation without regeneration.

**Depends on:** None.

## 2. Evaluation script

**Outcome:** Evaluate a chosen model and system prompt against saved tests.

**Includes:**

- Accept a JSON config-file path selecting the test-set folder, candidate
  provider/model and settings, system-prompt file, and new output folder.
- Run ASSERT against working copies with generation disabled. Preserve the
  source tests and their judge/scoring configuration.
- Save run-local inputs, resolved settings, exact prompt, ASSERT version,
  responses, judgments, and execution status.
- Print and save scored/expected counts and applicable violation/overrefusal
  metrics with explicit labels, numerators, and denominators as specified in
  [requirements.md](./requirements.md#evaluate-a-model).
- Reject existing output folders. Return nonzero for invalid inputs,
  execution failures, or incomplete/invalid results. Missing scores or absent
  applicability must not appear as successful zero-violation results.
- Reuse ASSERT's supported timeout/retry settings; do not add another retry loop.

**Focused test:** Verify evaluation reuses saved tests without changing them or
regenerating cases.

**Done when:** Two invocations can use the same test set with different candidate
models or prompts, producing separate results while keeping tests and judge
settings fixed.

**Depends on:** Feature 1's saved test artifacts.

## 3. Run comparison script

**Outcome:** Explain differences between two evaluations of the same tests.

**Includes:**

- Accept two run-folder paths; make no model calls.
- Require exactly one successful final result per expected case ID and valid
  judgments. Reject incomplete or incompatible runs with a clear error and
  nonzero exit status.
- Verify matching test content, context, taxonomy, rubrics, and judge/scoring
  settings from saved inputs, not merely paths or case IDs.
- Show each candidate model and system prompt.
- Print and save a JSON comparison with side-by-side counts, metric
  numerators/denominators, rates, and differences labeled second minus first.
- Mark metrics without applicable evidence as unavailable and omit their
  differences.
- Match cases by ID and identify changed judgments, with responses or evidence
  references. Do not declare a winner or make statistical or deployment claims.

**Focused tests:**

- Correct metric differences and changed-outcome matching by case ID.
- Rejection of different tests or judge/scoring settings.
- Missing, duplicate, failed, or invalid results cannot appear complete or
  produce a successful comparison.

Use small local fixtures, not live model calls, for automated tests.

**Done when:** Two compatible saved runs produce an understandable comparison
without generating tests or invoking models.

**Depends on:** Feature 2's saved run artifacts.

## 4. Demo files and walkthrough

**Outcome:** Demonstrate the complete workflow with a few short commands.

**Includes:**

- Non-sensitive behavior/context and prompt files.
- A generation config for one behavior with 10-20 cases.
- Two evaluation configs using the same generated test set and judge settings,
  differing only in candidate model or system prompt, with separate outputs.
- Placeholder-only credential instructions; no secrets in example files.
- A short walkthrough covering installation, config-relative paths, generation,
  manual review of permitted/prohibited coverage, two evaluations, comparison,
  and output locations.
- A manual end-to-end run confirming that source tests and earlier outputs stay
  unchanged. Generated outputs remain local and out of Git.

**Done when:** Following the walkthrough generates one reviewed test set,
evaluates it twice, and compares metric and case-level differences without
Node.js, a UI, or a separate ASSERT source checkout.

**Depends on:** Features 1-3 for final end-to-end verification.

## 5. Azure authentication modes

**Outcome:** Run the existing demo with either an Azure OpenAI API key or Entra
authentication, with no new credential implementation.

**Includes:**

- Document the environment variables required for each mode:
  `AZURE_API_KEY` for API-key auth, or `ASSERT_AZURE_USE_AAD=1` with an
  available `DefaultAzureCredential` login for Entra auth.
- Define a simple selection rule: use Entra mode when `ASSERT_AZURE_USE_AAD=1`;
  otherwise use the API key. Do not invent token acquisition, store credentials,
  or add an authentication adapter.
- Keep credentials in process environment or the ignored root `.env`; never put
  keys or tokens in JSON configs, tracked examples, logs, or saved artifacts.
- Reuse ASSERT/LiteLLM's existing Azure authentication and fallback behavior so
  generation, evaluation, and comparison demo commands remain unchanged apart
  from environment setup.
- Verify one bounded smoke generation with each approved authentication mode;
  automated tests remain provider-free and validate only configuration and
  credential-field rejection.
- Update the demo README with both setup paths, placeholder-only examples, and
  one shared failure message for missing/invalid credentials.

**Focused test:** Confirm both documented setups reach the same ASSERT CLI path
without changing generation, evaluation, or comparison configuration.

**Done when:** Users can switch auth mode through environment variables alone
and run the complete demo while tracked files remain credential-free.

**Depends on:** Features 1-4 and ASSERT/LiteLLM's existing Azure auth support.

## Scope boundary

## 6. Lightweight results viewer

**Outcome:** Inspect saved evaluation runs and comparisons visually without
adding a service or build system.

**Includes:**

- Prefer one self-contained, read-only HTML file that opens locally in a
  browser. It should need no backend, JavaScript package install, Node.js, or
  framework build.
- Let the user select one or more generated run folders or saved JSON artifacts
  through browser-local file selection. Do not add file-system scanning,
  uploads, accounts, or shared hosting.
- Show a concise run summary for the candidate model/system prompt, expected and
  scored counts, metric numerators/denominators/rates, completion status, and
  unavailable metrics.
- Render comparison metric differences side by side and make changed cases
  discoverable by `test_case_id`, with links or references to the saved response
  and judgment evidence.
- Treat all values as observational evidence. Do not calculate winners,
  significance, safety certification, thresholds, or deployment approval in
  the UI.
- Read files locally in the browser and avoid sending data anywhere. Document
  that browser file access is limited and that sensitive saved artifacts should
  remain on an approved local machine.

**Focused validation:** Open representative saved `summary.json` and
`comparison.json` files, confirm the displayed counts and rate differences
match the source, and verify no network calls occur.

**Done when:** A user can open the HTML locally, select saved run/comparison
artifacts, and review the main results and changed cases without a server or
command-line JSON inspection.

**Depends on:** Features 2 and 3's stable saved result artifacts.

UI work beyond this local viewer is Stage 2 and remains separately scoped. Do
not add catalogues, formal
versioning, adapter frameworks, threshold gates, automated regression decisions,
partial comparisons, CI, scheduling, or shared hosting to these six features.
