# EvalGate

## Generate a reusable test set

EvalGate uses a pinned ASSERT CLI to generate one single-turn test set for later
evaluation.

### Install

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

For Entra authentication, sign in with Azure CLI and put only the non-secret
endpoint settings in the ignored root `.env` file:

```powershell
az login
```

```dotenv
ASSERT_AZURE_USE_AAD=1
AZURE_API_BASE=https://YOUR-RESOURCE.openai.azure.com/
AZURE_API_VERSION=YOUR-API-VERSION
```

Do not add tokens or the `AZURE_API_KEY` setting. The supported config is JSON, with ASSERT model and stage field
names plus `behavior_file`, `context_file`, and `output_folder`:

```json
{
  "behavior": {"name": "support_scope"},
  "behavior_file": "behavior.txt",
  "context_file": "context.txt",
  "output_folder": "outputs/test-set-01",
  "pipeline": {
    "systematize": {
      "model": {
        "name": "openai/REPLACE_GENERATION_MODEL",
        "max_tokens": 10000
      },
      "behavior_category_count": 5,
      "web_search": false
    },
    "test_set": {
      "prompt": {
        "sample_size": 10,
        "model": {
          "name": "openai/REPLACE_GENERATION_MODEL",
          "max_tokens": 3000
        }
      }
    },
    "judge": {
      "model": {
        "name": "openai/REPLACE_JUDGE_MODEL",
        "max_tokens": 12000
      },
      "n": 1
    }
  }
}
```

All relative paths resolve from the config file's directory. The destination
must not already exist. Long behavior and context values should be stored in the
referenced text files rather than command-line arguments.

Run:

```powershell
.\.venv\Scripts\python.exe .\generate_tests.py --config .\local\generation.json
```

Generation writes native ASSERT artifacts, `resolved-config.json`, and
`complete.json`. Review the saved taxonomy, cases, and configured judge settings
before evaluation. A failed or incomplete child run exits nonzero and normally
removes output created by that invocation.

ASSERT may make multiple provider calls for taxonomy generation, batching, and
its own retries; case count is not a call count or cost guarantee. Automated
tests make no provider calls. Live generation requires approved non-sensitive
inputs and environment credentials.

Live validation note (2026-11-17): Entra authentication and generation of 10
validated cases succeeded with ASSERT 0.3.0 using
`azure/gpt5_series/assert-intermediate` for the GPT-5.4 deployment. The
`gpt5_series/` routing hint lets LiteLLM translate ASSERT's `max_tokens` setting
to `max_completion_tokens` without changing the Azure deployment name. Using
`azure/assert-intermediate` without that hint previously failed because the
deployment name did not identify the model family. The judge stage was not run.

### Gender-bias example

[examples/gender-bias/generation.json](examples/gender-bias/generation.json)
contains the behavior, context, model routes, and settings used for the gender-bias
example. Its output destination is portable; replace `assert-intermediate` with
your own GPT-5 deployment name before running:

```powershell
.\.venv\Scripts\python.exe .\generate_tests.py --config .\examples\gender-bias\generation.json
```

The saved [test cases](examples/gender-bias/test_set.jsonl) contain 10 generated
prompts, and the [taxonomy](examples/gender-bias/taxonomy.json) contains five
behavior categories. These are sample outputs, not scored assistant responses;
regeneration may produce different cases. The taxonomy copy omits the original
machine-specific source path. Credentials and full local run artifacts remain
ignored.