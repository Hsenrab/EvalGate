# Initial Demo Feature Breakdown

Based on [requirements.md](./requirements.md), deliver four features:
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

## Scope boundary

UI work is Stage 2 and is scoped separately. Do not add catalogues, formal
versioning, adapter frameworks, threshold gates, automated regression decisions,
partial comparisons, CI, scheduling, or shared hosting to these four features.
