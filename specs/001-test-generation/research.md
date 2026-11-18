# Research: Test Generation

**Date**: 2026-11-17
**Scope**: Public documentation/source check only. No installation or model calls.

## Decision

Pin `assert-ai==0.3.0` and use its documented CLI:

```text
assert-ai run --config <path> --strict
```

ASSERT's documented configuration is YAML, so the wrapper accepts the project's
JSON boundary format and writes one native YAML file. Python 3.11+ is required.

## Supported workflow

Use only the native `systematize` and prompt-only `test_set` stages. ASSERT writes
the generated taxonomy and `test_set.jsonl`; the wrapper preserves those files
unchanged. The executable generation config does not include inference or judge
stages.

The wrapper saves the resolved behavior/context and configured judge settings in
one JSON file so the output can be reviewed and later reused. It does not copy
upstream scorer code or reproduce built-in rubric implementation details.

## Relevant limitations

- ASSERT accepts `context` as text, not as a file reference. The wrapper reads a
  referenced file and places its content in native YAML.
- Generated IDs are positional within the saved file. Preserve them; do not
  recreate or promise cross-regeneration identity.
- A child process may exit after writing fewer cases than requested. The wrapper
  checks the final count and fails unless it matches.
- Provider authentication, retry, timeout, and diagnostics belong to ASSERT.
  The wrapper adds no parallel credential, retry, logging, or recovery system.
- Generation can make multiple model calls because systematization and batching
  occur upstream. Do not promise a fixed call count or cost.

## Minimum smoke check

After dependency installation, confirm:

1. `assert-ai` is version `0.3.0`.
2. `assert-ai run --help` offers `--config` and `--strict`.
3. One mocked generation test can write native-looking artifacts and one
   complete marker.

Live behavior is not verified until the explicitly requested manual 10-case run.
If the pinned CLI does not support the smoke-check command, stop and report the
gap rather than replacing ASSERT.

## Local implementation check

On 2026-11-17, the repository virtual environment reported `assert-ai 0.3.0`
and `assert-ai run --help` listed both required options, `--config` and
`--strict`. The focused offline suite ran four tests successfully. No provider
calls are required by the automated suite.

The explicitly approved live check used Entra successfully, and confirmed that
deployment `azure/assert-intermediate` exists for model `gpt-5.4 2026-03-05`.
The initial run failed during systematization because `max_tokens` reached the
deployment unchanged, which that model rejects in favor of
`max_completion_tokens`. A subsequent approved run using
`azure/gpt5_series/assert-intermediate` succeeded and the wrapper validated
exactly 10 cases, saved the taxonomy, and wrote `complete.json`. The routing hint
enables LiteLLM's GPT-5 parameter handling; no ASSERT patch or model fallback was
needed. T008 is complete. The judge stage was not run.

Sources: [ASSERT v0.3.0 package manifest](https://github.com/responsibleai/ASSERT/blob/v0.3.0/pyproject.toml),
[configuration reference](https://github.com/responsibleai/ASSERT/blob/v0.3.0/docs/config/schema.md),
and [results artifacts](https://github.com/responsibleai/ASSERT/blob/v0.3.0/docs/guides/results.md).
