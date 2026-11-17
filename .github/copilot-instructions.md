# Copilot review instructions for EvalGate

## Review scope

- Follow the [constitution](../.specify/memory/constitution.md), [requirements](../requirements.md), and affected feature artifacts. Surface conflicts.
- Drafts do not authorize implementation; do not flag missing later features.
- Report actionable introduced bugs with location, scenario, impact, and proportionate severity. Consolidate duplicates; omit uncertain findings and unrelated pre-existing issues.

## MVP simplicity

- This is a local MVP, not a production platform. Prefer simple workflows, clear errors, and manual retry over speculative abstractions, recovery, or hardening.
- Validate external inputs and common failures, not hypothetical internal states. Extra defensive checks need a requirement or concrete failure.
- MVP scope never excuses credential exposure, saved-data loss, or invalid evidence reported as success.

## Style and maintainability

- Follow existing naming, formatting, types, and helpers. Leave mechanical style to existing linters; avoid preference-only comments, new tooling, or unrelated refactors.
- Preserve upstream UI styling/workflows. Flag readability, keyboard-access, or error-visibility regressions, not subjective redesigns.
- Prefer existing dependencies and clear code; comment non-obvious logic only. Suggest simpler alternatives without weakening requirements.

## ASSERT integration and setup

- Use pinned, installed `assert-ai` via supported CLI/configuration/artifacts, without a source checkout. No copied engine, upstream script imports, undocumented UI APIs, parallel runtime, or second retry loop.
- Require UI source/lockfile, upstream commit, licence notices, and local-change record. Defer unsupported capabilities; disclose unverified support.
- Check Windows 11/Ubuntu 24.04 LTS paths, spaces, and executable discovery. Preserve data; report setup failures. Never auto-install system runtimes. Bind UI to loopback; limit changes to feature scope.

## Configuration and immutable evidence

- UI and runner must load root `.env` with process-variable precedence and enforce `ASSERT_MODEL_OPTIONS` without fallback.
- Keep candidate model/prompt independent from generation and frozen judge/scoring. Adding models, prompts, or packs must not require code edits.
- Reject pack overwrites/checksum mismatches. Execute only run-local copies with strict parsing and generation disabled.
- Preserve unique runs with exact prompts, pack versions/checksums, target/judge settings, thresholds, ASSERT revision, timestamps, status, and evidence.
- Never commit/expose credentials, `.env` contents, or customer artifacts. Git-ignore local data, dependencies, and builds. Ship only non-sensitive examples and placeholder configuration.

## Gate correctness

- Require one successful final score per expected case and valid dimensions/node judgments. Missing, duplicate, unexpected, skipped, failed, or invalid cases cannot pass.
- Use `policy_violation_not_permissible` over relevant impermissible cases, not aggregate `policy_violation`. Compute `overrefusal` from valid applicable dimension judgments, excluding N/A. Report `policy_violation_permissible` separately.
- Thresholds must be in `[0, 1]`; equality passes. Zero required applicability or incomplete/invalid evidence means `needs_review`, not zero rates or final pass/fail.
- Report numerators/denominators, scored/expected counts, thresholds, and failing cases. Document non-success exit codes. Results never certify safety or approve deployment.

## Validation expectations

- Require focused behavior/regression/boundary tests, not exhaustive, duplicate, or trivial tests. Run the smallest relevant selection; default tests/setup must not call providers.
- Live evaluations require explicit invocation and bounded cases/concurrency/retries/timeouts. Disclose unrun checks; inspection is not live evidence.
- Update directly affected documentation.
