# Model Evaluation Scripts: Initial Demo

Status: Draft for review | Date: 2026-11-17

## 1. Goal

Demonstrate a simple workflow: **generate tests once, evaluate twice, compare the results**.

Build three small local Python scripts around ASSERT. Use ordinary folders and JSON configuration files, with shared helpers only where useful. No framework or UI is needed.

Use config files for larger inputs and ASSERT settings rather than long command lines or embedded JSON arguments. Keep prompts and other long text in files referenced by configuration. Prefer ASSERT's existing configuration format and fields over a new configuration layer.

## 2. Scripts

### Generate tests

- Accept a JSON config-file path specifying the behavior/context or its text-file path, case count, generation model, judge model/settings, and output folder.
- Use ASSERT to generate a single-turn test set for one behavior. Start with 10-20 cases for the demo.
- Save the tests with unique case IDs, context, taxonomy, judge rubrics, and explicit judge model/settings needed to reuse the same scoring configuration.
- Let the user inspect the saved tests before evaluation, including coverage of permitted and prohibited requests. No approval workflow is required.
- Reject an existing output folder and report failed or incomplete generation clearly.

### Evaluate a model

- Accept a JSON config-file path specifying the existing test-set folder, chosen provider/model identifier and supported settings, system-prompt file, and new output folder.
- Run ASSERT against a working copy of the saved tests with generation disabled. Do not modify the source test set or change its judge/scoring configuration.
- Save the input copies, chosen model, exact system prompt, resolved judge/scoring settings, ASSERT version, responses, judgments, and execution status in the run folder.
- Print and save a simple summary with scored/expected case counts and ASSERT's applicable violation and overrefusal rates, including their numerators and denominators.
- Label metrics explicitly: distinguish impermissible violations (`policy_violation_not_permissible`) from permissible-side violations and overrefusal. Do not substitute aggregate policy violations for either metric.
- Reject an existing output folder. Report missing inputs, configuration errors, provider failures, and incomplete or invalid results clearly, returning a nonzero exit status. Missing scores or zero applicable evidence must not look like a successful zero-violation result.
- Do not add threshold-based pass/fail gates for this demo.

### Compare two runs

- Accept two saved run folders. Do not generate tests or make model calls.
- Require complete, valid results: exactly one successful final result per expected case ID, with the judgments needed for the reported metrics.
- Verify that both runs used the same test content, context, taxonomy, rubrics, and judge/scoring settings using their saved input copies and settings, not just paths or case IDs.
- Reject incomplete or incompatible runs with a clear error and nonzero exit status. Partial comparisons are not required.
- Show the candidate model and system prompt used by each run; either may differ.
- Print and save a JSON comparison with side-by-side case counts, metric numerators/denominators, rates, and rate differences labeled as second run minus first run. Mark metrics with no applicable evidence as unavailable rather than zero, and omit their rate differences.
- Match cases by ID and identify changed judgments, showing the corresponding responses or references to their saved evidence.
- Report observed differences only. Do not declare a winner, statistical significance, safety certification, or deployment approval.

## 3. Setup and boundaries

- First verify that a pinned ASSERT version supports the required generation, saved-test execution, and scoring workflow through its documented CLI/configuration and artifact formats.
- If generation requires a trial evaluation, document the extra model calls and cost. Do not silently run an extra evaluation or build a replacement engine.
- Install ASSERT as a pinned Python dependency. Reuse its supported timeout and retry settings; do not build a parallel runtime or retry loop.
- Read credentials from environment variables. A local `.env` file is optional; existing process variables take precedence. Never print or save credentials.
- Keep secrets out of configuration files. Resolve relative file paths against the config file's directory, independent of the shell's working directory, and report missing files or invalid configuration clearly.
- Pass larger inputs to ASSERT through its supported config-file mechanism. Do not construct long command lines containing prompts, test cases, rubrics, or serialized configuration. Do not add a custom configuration framework.
- Keep credentials, customer data, and generated outputs out of Git. Use non-sensitive demo inputs.
- Supply small, non-sensitive example config files. Document installation and short commands for generating tests, evaluating two model/prompt combinations using config files, and comparing the resulting run folders.
- The scripts must work without Node.js, a UI, or a separate ASSERT source checkout.

## 4. Demo acceptance

1. Generate and manually review one small test set.
2. Evaluate it twice, changing the candidate model or system prompt while keeping tests and judge settings fixed.
3. Compare the saved runs without additional model calls and explain the metric and case-level differences.
4. Confirm the original tests and earlier outputs remain unchanged.

Include a few focused automated tests:

- Evaluation reuses saved tests without modifying them or regenerating cases.
- Comparison correctly calculates metric differences and matches changed outcomes by case ID.
- Comparison rejects different test content or judge/scoring settings.
- Missing, duplicate, failed, or invalid results cannot appear complete or produce a successful comparison.

Use small local fixtures for automated tests; live model calls belong to the manual demo, not the test suite.

## 5. Later work

UI work is Stage 2 and will be scoped separately after the scripts work.

Catalogues, formal versioning, adapter frameworks, threshold gates, automated regression decisions, partial comparisons, CI, scheduling, and shared hosting are not required for this demo.
