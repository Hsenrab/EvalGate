# Implementation Plan: Test Generation

**Branch**: `main` (`001-test-generation` feature identifier)  
**Date**: 2026-11-17  
**Spec**: [spec.md](spec.md)

## Summary

Add one Python wrapper that reads a JSON config, resolves referenced text
relative to that config, writes an ASSERT-native YAML file, and invokes the
pinned `assert-ai==0.3.0` CLI once. Preserve ASSERT's native output unchanged,
save the resolved inputs and judge settings, and write `complete.json` only when
the requested single-turn case count is valid.

## Technical Context

- **Runtime/dependencies**: Python 3.11+, `assert-ai==0.3.0`, and standard-library
  JSON/path/subprocess/test facilities.
- **Input**: One `--config <JSON path>` argument. The JSON follows ASSERT field
  names for behavior, models, settings, and judge configuration, plus only
  `behavior_file`, `context_file`, and `output_folder` for wrapper behavior.
- **Output**: A newly created folder containing native ASSERT artifacts,
  `resolved-config.json`, `assert-generation.yaml`, and `complete.json`.
- **Execution boundary**: ASSERT handles generation, model access, provider
  errors, retries, and artifacts. The wrapper resolves files, rejects an
  existing destination, invokes one CLI command, and checks the saved count/IDs.
- **Scope**: One local author, one behavior, 10-20 cases for the demo. No
  evaluation, comparison, UI, cache, adapter, or recovery system.

## Constitution Check

Pass: compose ASSERT rather than replace it; preserve the saved inputs and
configured judge basis; never mark incomplete output complete; keep credentials
out of config/artifacts; and use a few local tests without provider calls.

## Dependency Findings

ASSERT 0.3.0 provides a `assert-ai run --config <YAML> --strict` CLI and can
write `taxonomy.json` and `test_set.jsonl` through the `systematize` and prompt
`test_set` stages. ASSERT accepts context as text, so the wrapper reads any
referenced context file and inserts its contents. Native case IDs are positional,
so preserve them within the saved set rather than regenerate or reinterpret
them. See [research.md](research.md) for source references and limitations.

Before implementation, confirm only the installed version and that `run --help`
contains `--config` and `--strict`. If not, stop and report the mismatch rather
than changing the integration silently.

## Implementation

1. Add the pinned dependency and ignore local credentials, inputs, and generated
   output.
2. Parse the JSON and basic wrapper-level values. Resolve behavior/context text
   and output paths relative to the config file. Reject missing required files,
   invalid counts, credential fields, and an existing destination.
3. Save `resolved-config.json`, then materialize native YAML with only
   `systematize` and prompt `test_set` stages. Omit inference and judge execution;
   retain the requested judge settings in the resolved snapshot.
4. Run one argument-list subprocess:
   `assert-ai run --config <absolute YAML path> --strict`.
5. On exit zero, preserve native files and require exactly the requested number
   of prompt cases with unique IDs. Write `complete.json` last. On input or
   child failure, return nonzero; remove the output only when this invocation
   created it and do not leave a completion marker.
6. Document the command, config shape, environment credentials, manual review,
   and the fact that generation may make multiple upstream model calls.

## Files

- `requirements.txt`
- `.gitignore`
- `generate_tests.py`
- `tests/test_generate_tests.py`
- `README.md`

## Validation

Run one small local test module with:

1. Successful mocked 10-case generation and saved-input independence.
2. Config-relative referenced files.
3. Rejection of existing output.
4. Failure on short output despite a zero child exit.
5. One ordinary child failure with owned-output cleanup.

Also run the version/CLI smoke check:

```text
assert-ai run --help
```

A manual 10-case generation is a separate, explicitly authorized check using
non-sensitive inputs and environment credentials. Record any unrun live check
as unverified; implementation tests do not make provider calls.

No unresolved planning decisions remain.
