# EvalGate demo walkthrough

Run these commands in PowerShell from the repository root.
Generation and evaluation make live model calls and may incur costs.
Comparison and viewing are offline.

## 1. Setup

Use the authentication setup in the [README](README.md), then select the
deployment used for the demos:

```powershell
$env:EVALGATE_AZURE_DEPLOYMENT = 'assert-intermediate'
```

**Existing outputs:** the scripts reject existing output destinations.
If a test set is already generated and reviewed, skip its generation command.
For fresh runs, change `output_folder` in the relevant configs below to unused
paths. If generating a new test set, update both of its evaluation configs'
`test_set_folder` to that same path. Adjust the comparison commands accordingly.
Do not delete previous results just to rerun the demo.

## 2. Generate the two test sets

Both commands use [generate_tests.py](generate_tests.py).

Gender bias: [generation config](examples/end-to-end/generation.json) and
[behavior](examples/end-to-end/behavior.txt).

```powershell
.\.venv\Scripts\python.exe .\generate_tests.py --config .\examples\end-to-end\generation.json
```

Significant decisions:
[generation config](examples/significant-decisions/generation.json) and
[policy](examples/significant-decisions/behavior.txt).

```powershell
.\.venv\Scripts\python.exe .\generate_tests.py --config .\examples\significant-decisions\generation.json
```

Open [the viewer](results-viewer.html), select **Test prompts**, and review each
generated set before continuing:

- `outputs\demo-test-set`
- `outputs\significant-decisions-test-set`

Direct links to show the generated files (available after generation):

- Gender bias: [test prompts (JSONL)](outputs/demo-test-set/native/generated/test_set.jsonl)
  and [taxonomy (JSON)](outputs/demo-test-set/native/generated/taxonomy.json).
  This demo output has not been generated yet.
- Significant decisions: [test prompts (JSONL)](outputs/significant-decisions-test-set/native/generated/test_set.jsonl)
  and [taxonomy (JSON)](outputs/significant-decisions-test-set/native/generated/taxonomy.json).

## 3. Evaluate the gender-bias candidates

Neutral instructions: [evaluation config](examples/end-to-end/evaluation-neutral.json)
and [system prompt](examples/end-to-end/system-prompt-neutral.txt).

```powershell
.\.venv\Scripts\python.exe .\evaluate_model.py --config .\examples\end-to-end\evaluation-neutral.json
```

Deliberately biased instructions (training-only demonstration):
[evaluation config](examples/end-to-end/evaluation-biased-training.json) and
[system prompt](examples/end-to-end/system-prompt-biased-training.txt).

```powershell
.\.venv\Scripts\python.exe .\evaluate_model.py --config .\examples\end-to-end\evaluation-biased-training.json
```

## 4. Evaluate the significant-decisions candidates

Helpful only: "You are a helpful assistant."
[Evaluation config](examples/significant-decisions/evaluation-helpful.json) and
[system prompt](examples/significant-decisions/system-prompt-helpful.txt).

```powershell
.\.venv\Scripts\python.exe .\evaluate_model.py --config .\examples\significant-decisions\evaluation-helpful.json
```

Policy-aligned instructions:
[evaluation config](examples/significant-decisions/evaluation-policy-aligned.json)
and [system prompt](examples/significant-decisions/system-prompt-policy-aligned.txt).

```powershell
.\.venv\Scripts\python.exe .\evaluate_model.py --config .\examples\significant-decisions\evaluation-policy-aligned.json
```

Each pair uses the same saved test set, model, and judge settings.
Wait for each command to succeed before continuing.

## 5. Create the two comparisons

Gender bias: biased minus neutral.

```powershell
.\.venv\Scripts\python.exe .\compare_runs.py `
  .\outputs\demo-run-neutral `
  .\outputs\demo-run-biased-training `
  --output .\outputs\demo-comparison.json
```

Significant decisions: policy aligned minus helpful only.

```powershell
.\.venv\Scripts\python.exe .\compare_runs.py `
  .\outputs\significant-decisions-run-helpful `
  .\outputs\significant-decisions-run-policy-aligned `
  --output .\outputs\significant-decisions-comparison.json
```

## 6. Show the results

In [the viewer](results-viewer.html):

- **Evaluation:** select any of the four completed run folders to inspect
  metrics, prompts, responses, and judgments.
- **Comparison:** open each comparison JSON to show side-by-side evidence and
  changed cases.

These are observed results, not safety certification or deployment approval.
