# EvalGate

EvalGate is a lightweight, local workflow for evaluating AI assistants against
behavior-specific tests. It wraps a pinned
[ASSERT](https://github.com/responsibleai/ASSERT) release so you can:

1. **Generate once** — create and review a reusable single-turn test set.
2. **Evaluate repeatedly** — run model, system-prompt, agent, or release
   variants against the same saved cases and judge settings.
3. **Compare offline** — inspect metric differences and changed case evidence
   without making additional model calls.

EvalGate reports observed evidence. It does not assign deployment approval,
statistical significance, safety certification, or an overall winner.
Generation and evaluation make provider calls and may incur usage costs.

## Quick start

This path uses the tracked, non-sensitive
[end-to-end demo](examples/end-to-end).

For commands covering both gender bias and significant decisions, see the
[demo walkthrough](demo.md).

### Prerequisites

- Python 3.11 or later
- Git
- An Azure OpenAI endpoint and a deployment you are approved to use
- Azure CLI for Entra login, or an approved API key

### 1. Install

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Configure authentication

Choose one setup in the ignored root `.env`.

**API key**

```dotenv
AZURE_API_BASE=https://YOUR-RESOURCE.openai.azure.com/
AZURE_API_VERSION=YOUR-API-VERSION
AZURE_API_KEY=YOUR-API-KEY
EVALGATE_AZURE_DEPLOYMENT=YOUR-DEPLOYMENT-NAME
```

**Entra**

```powershell
az login
```

```dotenv
ASSERT_AZURE_USE_AAD=1
AZURE_API_BASE=https://YOUR-RESOURCE.openai.azure.com/
AZURE_API_VERSION=YOUR-API-VERSION
EVALGATE_AZURE_DEPLOYMENT=YOUR-DEPLOYMENT-NAME
```

If neither explicit setting is present, ASSERT attempts its
`DefaultAzureCredential` fallback. The wrappers also load the nearest `.env`
while walking upward from the config file, without overriding existing process
environment variables. Keep credentials out of tracked JSON files.

### 3. Set the deployment

Set `EVALGATE_AZURE_DEPLOYMENT` once in `.env`. The tracked demo configs already
reference it:

- [generation.json](examples/end-to-end/generation.json)
- [evaluation-neutral.json](examples/end-to-end/evaluation-neutral.json)
- [evaluation-biased-training.json](examples/end-to-end/evaluation-biased-training.json)

For custom GPT-5 Azure deployments, the examples use
`azure/gpt5_series/<deployment-name>` form so LiteLLM applies GPT-5 parameter
handling.

### 4. Generate and review

```powershell
.\.venv\Scripts\python.exe .\generate_tests.py --config .\examples\end-to-end\generation.json
```

Expected output:

```text
outputs\demo-test-set\
```

Stop and review:

- `native\generated\taxonomy.json` — behavior categories and permissible/
  prohibited coverage
- `native\generated\test_set.jsonl` — all generated prompts
- `complete.json` — requested and completed counts

A completion marker proves generation completed; it does not approve test
quality or coverage.

### 5. Evaluate the saved set twice for the demo

```powershell
.\.venv\Scripts\python.exe .\evaluate_model.py --config .\examples\end-to-end\evaluation-neutral.json
.\.venv\Scripts\python.exe .\evaluate_model.py --config .\examples\end-to-end\evaluation-biased-training.json
```

Expected outputs:

```text
outputs\demo-run-neutral\
outputs\demo-run-biased-training\
```

The second prompt is a training-only bias demonstration, not a recommended
production prompt. Both runs reuse the reviewed test set and its judge settings.

### 6. Compare

```powershell
.\.venv\Scripts\python.exe .\compare_runs.py `
  .\outputs\demo-run-neutral `
  .\outputs\demo-run-biased-training `
  --output .\outputs\demo-comparison.json
```

Comparison is entirely offline. It validates compatibility and completeness,
matches cases by ID, calculates second-minus-first metric differences, and
identifies changed judgments.

### 7. View results

Open [results-viewer.html](results-viewer.html) in a modern browser:

- **Evaluation** → select a completed run folder
- **Comparison** → select `outputs\demo-comparison.json`
- **Test prompts** → select a generated test-set folder (for example,
  `outputs\significant-decisions-test-set`) to read all prompts, titles, and
  behavior categories before evaluation. Use Ctrl+F to find text.

The viewer is local-only and makes no network requests.

## Significant decisions example

The [significant decisions example](examples/significant-decisions) tests whether
an assistant supports accountable human decision-makers without making,
finalising, or effectively determining significant decisions itself. It also
covers case-by-case necessity and proportionality rather than blanket adverse
outcomes, using fictional scenarios.

Use the same authentication and deployment setup as the quick start:

```powershell
.\.venv\Scripts\python.exe .\generate_tests.py --config .\examples\significant-decisions\generation.json
```

Review the generated taxonomy and prompts in
`outputs\significant-decisions-test-set\native\generated` before evaluating:

Two candidates use the same model, saved tests, and judge settings:

- [Helpful only](examples/significant-decisions/system-prompt-helpful.txt) has
  only the instruction "You are a helpful assistant."
- [Policy aligned](examples/significant-decisions/system-prompt-policy-aligned.txt)
  explicitly follows the significant decisions policy.

```powershell
.\.venv\Scripts\python.exe .\evaluate_model.py --config .\examples\significant-decisions\evaluation-helpful.json
.\.venv\Scripts\python.exe .\evaluate_model.py --config .\examples\significant-decisions\evaluation-policy-aligned.json
```

Compare the two runs offline:

```powershell
.\.venv\Scripts\python.exe .\compare_runs.py `
  .\outputs\significant-decisions-run-helpful `
  .\outputs\significant-decisions-run-policy-aligned `
  --output .\outputs\significant-decisions-comparison.json
```

This example tests single-turn responses, not whether a deployed workflow
actually enforces human decision-making. The helpful-only candidate has no
policy-specific system instructions, but the underlying model may still have
its own safeguards.

## What gets created

```text
outputs/
├── demo-test-set/
│   ├── complete.json
│   ├── resolved-config.json
│   └── native/generated/
│       ├── taxonomy.json
│       └── test_set.jsonl
├── demo-run-neutral/
│   ├── complete.json
│   ├── summary.json
│   ├── inputs/
│   └── native/evaluation/run/
│       ├── inference_set.jsonl
│       ├── scores.jsonl
│       └── manifest.json
├── demo-run-biased-training/
└── demo-comparison.json
```

The scripts reject existing destinations. Choose a new output folder for every
generation, evaluation, and comparison; never reuse an existing name.

## Working with the tools

### Generate tests

Script:

```powershell
.\.venv\Scripts\python.exe .\generate_tests.py --config <generation-config.json>
```

The config supplies:

- behavior and context, either inline or through text files;
- generation and judge models;
- behavior-category count;
- prompt sample size;
- output folder.

All relative paths resolve from the config file's directory. Generation writes
`resolved-config.json`, native ASSERT artifacts, and a final `complete.json`.
Failed or incomplete generation exits nonzero and normally removes output
created by that invocation.

### Evaluate the saved test set

Script:

```powershell
.\.venv\Scripts\python.exe .\evaluate_model.py --config <evaluation-config.json>
```

The config selects:

- an existing completed test-set folder;
- a candidate model and settings;
- a system-prompt file;
- a new output folder.

Evaluation copies and preserves the source tests, taxonomy, generation settings,
and exact prompt, then runs ASSERT inference and judging. A complete run writes
`complete.json` and `summary.json`. A failed run remains for diagnosis with
`failed.json` but never receives `complete.json`.

Run this step as often as needed for a new model, prompt, agent release, or
configuration change. Each attempt uses a new output folder, so historical
results remain separate.

### Compare evaluation runs

Script:

```powershell
.\.venv\Scripts\python.exe .\compare_runs.py <first-run> <second-run> --output <new-comparison.json>
```

The comparison is offline: it makes no ASSERT or provider calls. It requires:

- complete runs;
- exactly one valid score per expected case;
- identical tests, context, taxonomy, rubrics, and judge settings.

The report includes:

- candidate identities and exact system prompts;
- expected/scored counts;
- side-by-side metrics and second-minus-first differences;
- every case matched by ID, with changed cases first;
- prompts, responses, judgments, and evidence references.

The viewer intentionally accepts a validated `comparison.json`, not two raw
folders, because compatibility and completeness checks belong in the CLI.

## Test another prompt

1. Create a local prompt:

   ```powershell
   New-Item .\local -ItemType Directory -Force
   New-Item .\local\my-system-prompt.txt -ItemType File -Force
   ```

2. Write the prompt and save the file.

3. Copy an evaluation config:

   ```powershell
   Copy-Item .\examples\end-to-end\evaluation-neutral.json .\local\my-evaluation.json
   ```

4. In `local\my-evaluation.json`, change:

   - `test_set_folder` to `../outputs/demo-test-set`, because the copied config
     now lives in `local/`;
   - `system_prompt_file` to `my-system-prompt.txt`;
   - `output_folder` to a new path such as `../outputs/my-prompt-run`;
   - leave `candidate.model.name` using `EVALGATE_AZURE_DEPLOYMENT`, or replace
     the model name when intentionally testing a different route;
   - confirm `test_set_folder` points to the reviewed test set.

5. Evaluate:

   ```powershell
   .\.venv\Scripts\python.exe .\evaluate_model.py --config .\local\my-evaluation.json
   ```

6. Compare with an earlier run:

   ```powershell
   .\.venv\Scripts\python.exe .\compare_runs.py `
     .\outputs\demo-run-neutral `
     .\outputs\my-prompt-run `
     --output .\outputs\my-prompt-comparison.json
   ```

7. Open the viewer, select **Comparison**, and load the new comparison file.

## Understanding results

### How a test becomes a metric

1. Every generated case is sent to the candidate.
2. The judge scores every completed response.
3. The judge decides which taxonomy behavior categories are relevant.
4. ASSERT includes the case in a metric when at least one relevant category
   belongs to that metric's group.
5. The numerator counts violations among applicable cases:
   `violations / applicable cases`.

This is why denominators can differ. If two runs report `0/5` and `1/6`, all
cases were still scored; the second judge classified one additional case as
applicable to that metric.

Example:

- A prompt asking to exclude women from leadership may be applicable to
  stereotyping and unequal-advice categories.
- A request for a gender-neutral resume rubric may be applicable only to
  permissible, gender-neutral behavior.

Inspect the changed judgments before interpreting a rate difference.

### Metric labels

EvalGate keeps these separate:

- `policy_violation_not_permissible`
- `policy_violation_permissible`
- `overrefusal`

An unavailable metric has no numeric rate or difference; it is not a successful
zero.

## Azure authentication reference

ASSERT uses this precedence:

1. Truthy `ASSERT_AZURE_USE_AAD` forces Entra.
2. Otherwise `AZURE_API_KEY` selects API-key auth.
3. Otherwise ASSERT attempts `DefaultAzureCredential`.

The `DefaultAzureCredential` chain can use approved local or managed identity
sources, including `az login` or managed/service identity. ASSERT excludes
interactive browser and VS Code credentials.

Credentials belong in the process environment or ignored root `.env`, never in
JSON configs or tracked examples.

## Troubleshooting

### Existing output

All three scripts reject an existing output destination. Choose a new folder or
file name; they do not overwrite evidence.

### Missing or invalid authentication

- API key: verify `AZURE_API_KEY` is present in the process running EvalGate.
- Entra: run `az login` and verify the identity has access to the Azure OpenAI
  resource.
- Default fallback: inspect the available `DefaultAzureCredential` sources.
- Reinstall `requirements.txt` if `azure-identity` is missing.
- Verify `AZURE_API_BASE` and `AZURE_API_VERSION`.

Never include the credential value in an error report or issue.

### Incomplete evaluation

Check the run's `failed.json`, native `manifest.json`, and any provider diagnostics.
Use a new output folder after correcting the problem. A failed run is not a
completed result.

### Viewer limitations

The viewer is local-only and uses browser file/folder selection. It makes no
network requests and does not upload or persist selected evidence. A local
comparison file can still contain sensitive prompts and responses; open it only
on an approved machine.

## Scope and privacy

EvalGate is a local demonstration workflow, not a production platform. It does
not provide UI hosting, accounts, shared storage, thresholds, automated
regression decisions, statistical claims, or deployment certification.

Generated tests, responses, and judgments can contain sensitive data. Keep
`outputs/` local, apply your organization's retention/access rules, and review
files before sharing them.
