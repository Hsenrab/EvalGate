# EvalGate

EvalGate is a lightweight, local workflow for evaluating AI assistants against
behavior-specific tests. It wraps a pinned [ASSERT](https://github.com/responsibleai/ASSERT)
release so you can:

1. **Generate once** — create and review a reusable single-turn test set.
2. **Evaluate repeatedly** — run any number of model, system-prompt, agent, or
   release variants against the same saved cases and judge settings.
3. **Compare offline** — inspect metric differences and changed judgments
   without making additional model calls.

The tools use JSON configuration files and ordinary folders. They do not require
Node.js, a UI, or a separate ASSERT checkout. Credentials stay in the environment;
test sets, responses, judgments, and comparisons stay in ignored local output
folders unless you deliberately choose to share them.

EvalGate reports observed evaluation evidence. It does not assign deployment
approval, statistical significance, safety certification, or an overall winner.
Generation and evaluation make provider calls and may incur usage costs.

## Generate a reusable test set

EvalGate uses a pinned ASSERT CLI to generate one single-turn test set for later
evaluation.

### Install

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Azure authentication

ASSERT selects Azure authentication from environment variables; the JSON demo
configs do not contain credentials and remain identical for every auth mode.
Existing process environment variables take precedence over the ignored root
`.env`.

**API key**

Remove `ASSERT_AZURE_USE_AAD` and set a key in your ignored `.env`:

```dotenv
AZURE_API_BASE=https://YOUR-RESOURCE.openai.azure.com/
AZURE_API_VERSION=YOUR-API-VERSION
AZURE_API_KEY=YOUR-API-KEY
```

**Explicit Entra**

Force Entra mode and remove `AZURE_API_KEY`:

```powershell
az login
```

```dotenv
ASSERT_AZURE_USE_AAD=1
AZURE_API_BASE=https://YOUR-RESOURCE.openai.azure.com/
AZURE_API_VERSION=YOUR-API-VERSION
```

ASSERT also supports **automatic Entra fallback**: if neither
`ASSERT_AZURE_USE_AAD` nor `AZURE_API_KEY` is set, it uses
`DefaultAzureCredential`. This may resolve `az login`, managed identity, a
service principal from environment variables, or another supported
non-interactive identity source. Interactive browser and VS Code credentials
are intentionally excluded by ASSERT.

Selection precedence is:

1. Truthy `ASSERT_AZURE_USE_AAD` forces Entra.
2. Otherwise, a non-empty `AZURE_API_KEY` selects API-key auth.
3. Otherwise, `DefaultAzureCredential` is attempted.

If authentication fails, confirm the endpoint and API version, then check the
selected mode:

- API key: verify `AZURE_API_KEY` is present in the process running EvalGate.
- Entra: run `az login`, or provide the approved managed/service identity, and
  verify that identity has access to the Azure OpenAI resource.
- Fallback: if no explicit mode was selected, inspect which
  `DefaultAzureCredential` sources are available.
- If `azure-identity` is missing, reinstall the pinned dependencies from
  `requirements.txt`; they include `assert-ai[azure-auth]`.

Do not add API keys, tokens, or other credentials to JSON configs or tracked
files. The supported config is JSON, with ASSERT model and stage field
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

## Evaluate a saved model

Keep the generated test set unchanged and create an evaluation configuration
such as `local/evaluation.json`:

```json
{
  "test_set_folder": "../outputs/test-set-gender-bias",
  "system_prompt_file": "candidate-system-prompt.txt",
  "output_folder": "../outputs/gender-bias-candidate-01",
  "candidate": {
    "model": {
      "name": "azure/gpt5_series/REPLACE_CANDIDATE_DEPLOYMENT",
      "max_tokens": 3000
    }
  },
  "inference": {
    "max_turns": 1,
    "concurrency": 2
  }
}
```

All relative paths resolve from the configuration file. The output destination
must not exist. Credentials must remain in environment variables and are never
accepted in this JSON file. For custom Azure deployments, use the explicit GPT
family routing shown above so LiteLLM applies the correct token parameter.

Run:

```powershell
.\.venv\Scripts\python.exe .\evaluate_model.py --config .\local\evaluation.json
```

Evaluation copies the test cases, taxonomy, resolved generation settings, and
exact system prompt into the new run. ASSERT then runs inference and its existing
judge configuration without regeneration. The source test-set folder is checked
afterward for byte-for-byte changes.

The evaluation step can be run as many times as needed against the same saved
test set. Create a new output folder for each candidate model, updated system
prompt, agent release, or other behavioral change. This keeps historical results
separate and makes it possible to compare behavior over time without regenerating
the tests.

A successful run ends with `complete.json` and `summary.json`. The summary keeps
`policy_violation_not_permissible`, `policy_violation_permissible`, and
`overrefusal` separate. Each available metric includes a numerator, denominator,
and rate; a metric with no applicable evidence is `unavailable`, not a
zero-violation result.

Failed and incomplete runs are retained for inspection with `failed.json` and
available native ASSERT artifacts, but never receive `complete.json`. Use a new
output folder for a retry. Native responses, judgments, and ASSERT execution
status remain under the run's `native/` directory.

## Compare two evaluation runs

Comparison is entirely offline. It reads two completed Feature 2 run folders,
makes no provider calls, and rejects incompatible or incomplete evidence:

```powershell
.\.venv\Scripts\python.exe .\compare_runs.py `
  .\outputs\candidate-a-run `
  .\outputs\candidate-b-run `
  --output .\outputs\candidate-comparison.json
```

The two runs must use identical saved test content, context, taxonomy, rubrics,
and judge/scoring settings. Candidate models and system prompts may differ.
`--output` is optional and defaults to `comparison.json` in the current
directory; an existing destination is never overwritten.

The JSON report shows:

- each candidate model and exact system prompt;
- expected and scored case counts;
- side-by-side metric numerators, denominators, and rates;
- differences labeled `second_minus_first`;
- case-level judgment changes matched by `test_case_id`, with references back
  to each run's response and score evidence.

If a metric lacks applicable evidence, its result is marked `unavailable` and
no numeric difference is written. Comparison reports observations only; it
does not declare a winner, statistical significance, safety certification, or
deployment approval.

### How test cases become metrics

Applicability denominators change because the judge independently decides which
saved taxonomy categories are relevant for each response. Different candidate
responses or system prompts can expose different relevant behaviors, even when
the test set is unchanged.

1. Generation creates a fixed test set. Every case in that set is sent to the
   candidate and receives a response.
2. The judge scores every completed case. It decides which behavior categories
   in the saved taxonomy are relevant to that case and whether the response
   violated each relevant category.
3. ASSERT then groups the judgments into metrics. A case enters a metric's
   denominator when at least one relevant category belongs to that metric's
   group. It may enter a permissible-side metric, an impermissible-side metric,
   both groups, or neither.
4. The numerator counts violations among those applicable cases. The rate is
   `violations / applicable cases`.

For example, a request asking whether women should be excluded from leadership
is likely applicable to gender-stereotyping and unequal-advice categories. A
request for a gender-neutral resume scoring rubric may be applicable only to
permissible, gender-neutral behavior and may not enter an impermissible
violation metric.

For example, if 10 cases ran, 6 are applicable to a metric, and 1 violates it,
the result is `1/6`. This does not mean the judge ran six tests. The other four
cases were still scored, but did not contribute to that metric.

That applicability classification is made for each run. If one run shows `0/5`
and another shows `1/6`, compare both the outcome change and the relevance
decision that added one applicable case. Inspect the changed cases and saved
judgments before interpreting the rate difference.

## End-to-end demo

The tracked [examples/end-to-end](examples/end-to-end) bundle demonstrates the
complete workflow with non-sensitive inputs:

1. Generate one 10-case test set.
2. Review its taxonomy and permitted/prohibited coverage.
3. Evaluate the same test set twice with different system prompts.
4. Compare the two runs offline.

### 1. Prepare

Install dependencies as shown above, sign in, and set the non-secret values in
the ignored root `.env`:

```dotenv
ASSERT_AZURE_USE_AAD=1
AZURE_API_BASE=https://YOUR-RESOURCE.openai.azure.com/
AZURE_API_VERSION=YOUR-API-VERSION
```

Do not put tokens or API keys in demo files. Replace each
`REPLACE_*_DEPLOYMENT` value in
[examples/end-to-end/generation.json](examples/end-to-end/generation.json),
[examples/end-to-end/evaluation-neutral.json](examples/end-to-end/evaluation-neutral.json),
and
[examples/end-to-end/evaluation-biased-training.json](examples/end-to-end/evaluation-biased-training.json)
with deployments you are approved to use. The supplied `azure/gpt5_series/`
prefix is the GPT-5 routing form; choose the appropriate provider/model form if
using another family.

All output names in the examples are relative to the config files. Outputs must
not already exist; change their names rather than overwrite prior evidence.
The example live workflow makes provider calls and may incur usage charges.

### 2. Generate and review

```powershell
.\.venv\Scripts\python.exe .\generate_tests.py --config .\examples\end-to-end\generation.json
```

Review:

- `outputs\demo-test-set\native\generated\taxonomy.json` for the generated
  behavior categories and permissible/prohibited coverage.
- `outputs\demo-test-set\native\generated\test_set.jsonl` for every prompt.
- `outputs\demo-test-set\complete.json` for requested/completed counts.

A completed generation only proves the requested artifacts exist; it does not
approve the cases or their coverage. Manually review them before continuing.

### 3. Evaluate twice

Both configs use the same saved test set and judge settings. Only the system
prompt and output folder differ:

```powershell
.\.venv\Scripts\python.exe .\evaluate_model.py --config .\examples\end-to-end\evaluation-neutral.json
.\.venv\Scripts\python.exe .\evaluate_model.py --config .\examples\end-to-end\evaluation-biased-training.json
```

The second prompt is explicitly a training-only bias demonstration, not a
recommended production prompt. Each run writes a `complete.json`,
`summary.json`, copied inputs, responses, and judgments under its separate
`outputs\demo-run-*` folder. Repeat this step with a new output folder whenever
you test a new model, system prompt, agent release, or configuration change.

### 4. Compare

```powershell
.\.venv\Scripts\python.exe .\compare_runs.py `
  .\outputs\demo-run-neutral `
  .\outputs\demo-run-biased-training `
  --output .\outputs\demo-comparison.json
```

Open `outputs\demo-comparison.json` for metric counts/rates, changed cases, and
references to both runs' response and judgment evidence. Differences are always
the second run minus the first. If the metric denominators differ, inspect the
case-level applicability and evidence before interpreting the rate difference.

Comparison and its source runs stay under ignored `outputs/`. The walkthrough
does not declare a winner, significance, certification, or deployment approval.

## View saved results locally

Open [results-viewer.html](results-viewer.html) directly in a modern browser.
Select one or more saved `summary.json` or `comparison.json` files; no server,
package install, upload, or build step is required.

The viewer shows:

- run completion, candidate, system prompt, case counts, and metrics;
- comparison metric tables and second-minus-first differences;
- changed cases and their saved response/judgment references;
- unavailable metrics and warnings when comparison denominators differ.

The applicability-denominator warning in the comparison expands to explain the
distinction between total scored cases and metric applicability.

The page reads selected files only in the browser. It makes no network requests,
stores no data, and does not upload or modify evidence. Evidence references are
display-only because a local HTML page cannot safely resolve arbitrary
filesystem paths. Open sensitive results only on an approved local machine.