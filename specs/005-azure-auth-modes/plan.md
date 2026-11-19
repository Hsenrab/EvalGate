# Implementation Plan: Azure Authentication Modes

**Branch**: `005-azure-auth-modes` | **Date**: 2026-11-19 | **Spec**: [spec.md](spec.md)

## Summary

Document and validate ASSERT 0.3.0's existing Azure auth selection so the
unchanged demo commands work with either `AZURE_API_KEY` or Entra. The expected
implementation is documentation and tests only; add EvalGate code only if the
bounded checks expose an upstream gap at the subprocess boundary.

## Technical Context

- **Runtime/dependencies**: Existing `assert-ai[azure-auth]==0.3.0`; no new
  dependency. That extra already includes Azure Identity.
- **Inputs**: Process environment or ignored root `.env` values:
  - shared: `AZURE_API_BASE`, `AZURE_API_VERSION`;
  - API key: `AZURE_API_KEY`;
  - Entra: `ASSERT_AZURE_USE_AAD=1` plus a usable
    `DefaultAzureCredential` source such as `az login`, managed identity,
    environment/service-principal identity, or an approved identity source.
  - Automatic Entra fallback: no AAD flag and no key, using the same
    `DefaultAzureCredential` chain.
- **Outputs**: Unchanged generation, evaluation, and comparison artifacts.
  Authentication values are never copied into JSON configs or saved by
  EvalGate.
- **Execution boundary**: Generation/evaluation already call the same
  installed `assert-ai.exe`; comparison stays offline. ASSERT resolves auth and
  injects Azure request credentials.

## Constitution Check

- **Compose ASSERT rather than rebuild it**: passes; no custom token acquisition
  or credential adapter is planned.
- **Credential protection**: passes by retaining credential-field rejection and
  documenting ignored `.env`/process environment use.
- **Sufficient evidence**: passes by separating provider-free tests from bounded
  manual smoke evidence and disclosing unrun modes.
- **Simple implementation**: passes; README and tests are the default surface.
  Runtime changes require a reproduced ASSERT gap, not an anticipated one.
- **Honest errors**: passes by pointing all live failures to the same selected
  auth-mode troubleshooting path without echoing credential values.

## Dependency Findings

- ASSERT 0.3.0 resolves auth in this precedence order:
  1. truthy `ASSERT_AZURE_USE_AAD` forces Entra;
  2. otherwise a non-empty matching API key selects key auth;
  3. otherwise it falls back to Entra via `DefaultAzureCredential`.
- `DefaultAzureCredential` excludes interactive browser and VS Code credentials,
  so documentation must tell local users to run `az login` or use an approved
  non-interactive identity source.
- A key and AAD flag may coexist: the AAD flag explicitly wins. README examples
  should avoid leaving ambiguous stale values in `.env`.
- No EvalGate code currently reads or copies authentication environment values
  into saved artifacts, and config credential-field rejection already blocks
  API key/token keys.

## Implementation

1. Add a short README auth section with two isolated `.env` examples:
   - API-key mode: no AAD flag, `AZURE_API_KEY` placeholder;
   - Entra mode: `ASSERT_AZURE_USE_AAD=1`, no API key, plus `az login`.
   Document the supported fallback when neither is set.
2. Clarify precedence, process-environment-over-JSON rules, approved endpoints,
   and that comparison requires no credentials.
3. Add one common troubleshooting block for a failed
   `DefaultAzureCredential` chain, missing key/Entra login,
   `azure-identity` installation, endpoint/API version, and role assignment
   without exposing secrets.
4. Add focused provider-free tests only where needed to prove generation and
   evaluation config loaders continue rejecting credential fields and produce
   resolved configs that do not contain auth environment values. If existing
   tests already cover the boundary, update rather than duplicate.
5. Do not change runtime auth code unless a minimal check demonstrates ASSERT
   cannot perform either mode. Any such gap requires a separately justified
   patch.
6. Record bounded manual smoke results for whichever modes are run; disclose
   the other mode as unverified.

## Files

- `README.md` — API-key and Entra setup/troubleshooting.
- Existing focused tests in `tests/` — only small additions if coverage is
  missing.
- `specs/005-azure-auth-modes/plan.md` — manual smoke evidence and limitations.
- No new authentication module is planned.

## Validation

- Provider-free config tests verify credential keys are rejected in both
  generation and evaluation JSON.
- A subprocess/CLI check confirms unchanged commands still invoke the same
  pinned ASSERT executable for each mode.
- Run the smallest relevant existing suite:
  `.\.venv\Scripts\python.exe -m unittest tests.test_generate_tests tests.test_evaluate_model -v`
- Manual live checks are separate and bounded: one smoke generation per selected
  mode, with `AZURE_API_KEY` removed in Entra mode to remove ambiguity.

## Open Questions

None. If API-key smoke testing is not performed in the current environment, it
will be documented as unverified rather than simulated.

## Manual Smoke Evidence

- **Entra / `DefaultAzureCredential`**: Verified on 2026-11-17. With
  `ASSERT_AZURE_USE_AAD=1` and `az login`, ASSERT authenticated successfully and
  completed a 10-case generation. The original run later exposed a GPT-5
  parameter-routing issue, which was resolved separately with the documented
  `gpt5_series/` model route. No credential was saved in the repository.
- **API key**: Not run in the current environment. This mode is supported by
  ASSERT 0.3.0's verified upstream path and is documented, but remains
  explicitly unverified for this repository.
- **Automatic fallback**: No separate smoke run. It uses the same
  `DefaultAzureCredential` chain as explicit Entra once no API key or AAD flag
  is present; fallback success remains environment-dependent.
