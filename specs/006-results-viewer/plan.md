# Implementation Plan: Lightweight Results Viewer

**Branch**: `006-results-viewer` | **Date**: 2026-11-19 | **Spec**: [spec.md](spec.md)

## Summary

Add one self-contained `results-viewer.html` that reads selected EvalGate
`summary.json` and `comparison.json` files with browser-local APIs and renders
the existing evidence without a server, package install, build, upload, or
network request.

## Technical Context

- **Runtime/dependencies**: Standard HTML, CSS, and JavaScript only. No Node.js,
  external library, CDN, backend, or generated bundle.
- **Inputs**: One or more user-selected JSON files via `<input type="file"
  multiple>`.
  - Supported run shape: Feature 2 `summary.json`.
  - Supported comparison shape: Feature 3 `comparison.json`.
- **Outputs**: In-memory read-only run cards and comparison tables/case lists.
  Nothing is written, uploaded, or persisted.
- **Theming**: Use the required Clawpilot CSS variables, theme-detection script,
  Segoe UI typography, 16px cards, and variable-only colors.
- **Evidence boundaries**: Validate JSON shapes before rendering. Display saved
  reference strings for changed-case response/judgments; do not attempt to fetch
  or scan referenced local files.

## Constitution Check

- **Sufficient evidence**: passes by rejecting incomplete/unsupported JSON and
  preserving unavailable states instead of fabricating zero values.
- **Traceability**: passes by displaying candidate/prompt identity and exact
  saved case references.
- **Data protection**: passes because all reading and rendering is local and
  there are no network, storage, upload, or telemetry APIs.
- **Simple design**: passes with one portable HTML file and no project tooling.
- **Honest reporting**: passes by labeling all output as observational and
  omitting winner/significance/deployment claims.

## Dependency Findings

- Run summaries contain top-level `status`, `assert_version`, `expected_count`,
  `scored_count`, `candidate_model`, `system_prompt_sha256`, `source_sha256`,
  and named `metrics`.
- The viewer also needs the exact system prompt required by FR-003; Feature 2's
  current `summary.json` stores only its hash. To avoid duplicating or browsing
  extra files, the minimal implementation will add `system_prompt` to future
  summaries in `evaluate_model.py`; existing summaries without it remain valid
  and display "not saved in this artifact" rather than reading outside the
  selected file.
- Comparison JSON already embeds both exact prompts and all required run/metric
  fields.
- Unavailable metrics are represented by `status: "unavailable"` and must not be
  given a numeric rate or difference.

## Implementation

1. Add `results-viewer.html` with the mandatory theme bootstrap and all CSS/JS
   inline.
2. Add schema checks for summary and comparison top-level shapes, required
   counts, candidates, metric objects, and changed-case fields. One invalid
   selection is shown in an error card without preventing valid selected files
   from rendering.
3. Render run summaries with identity/count cards and a metric table. Render
   comparisons with run cards, a side-by-side metric table, and an expandable or
   searchable changed-case list using text only.
4. Add clear and reset controls, an empty state, file-name labels, unavailable
   states, and changed-denominator warnings when first/second denominators
   differ.
5. Add `system_prompt` to newly written evaluation summaries in
   `evaluate_model.py` and a focused backward-compatible summary test. Do not
   change existing saved artifacts.
6. Update `README.md` with how to open the viewer, select artifacts, local-file
   limitations, and the no-network/no-upload guarantee.
7. Validate with representative local `summary.json` and `comparison.json`
   artifacts plus malformed and unavailable-metric fixtures. Confirm the HTML
   has no external URL, `fetch`, XHR, WebSocket, storage, or form navigation.

## Files

- `results-viewer.html` — self-contained local viewer.
- `evaluate_model.py` — minimal prompt field addition for future summaries.
- `tests/test_evaluate_model.py` — exact prompt and backward-compatible output
  validation.
- `README.md` — opening and privacy limitations.

## Validation

- Run the evaluation unit tests:
  `.\.venv\Scripts\python.exe -m unittest tests.test_evaluate_model -v`
- Open the viewer locally and select the existing neutral run summary and
  neutral-vs-biased comparison; verify 10/10 counts, metric values, and the one
  changed case.
- Select malformed JSON and an unavailable-metric fixture; verify a visible
  error/unavailable state and no false completion.
- Static-check the HTML for external resources/network/storage APIs and confirm
  all CSS colors use the Clawpilot variables.

## Open Questions

None. Evidence references remain display-only because browsers opened from disk
cannot safely resolve arbitrary absolute local paths.
