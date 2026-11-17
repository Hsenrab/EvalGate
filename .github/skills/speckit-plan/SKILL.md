---
name: "speckit-plan"
description: "Execute the implementation planning workflow using the plan template to generate design artifacts."
compatibility: "Requires spec-kit project structure with .specify/ directory"
metadata:
  author: "github-spec-kit"
  source: "templates/commands/plan.md"
---


## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Pre-Execution Checks

**Check for extension hooks (before planning)**:
- Check if `.specify/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_plan` key
- If the YAML cannot be parsed or is invalid, do not skip silently: tell the user that `.specify/extensions.yml` could not be read (include the parser error) and that no hooks were checked, including any mandatory (`optional: false`) hooks registered there, then continue normally
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
  - If the hook has no `condition` field, or it is null/empty, treat the hook as executable
  - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation
- When constructing command invocations from hook command names, replace dots (`.`) with hyphens (`-`). For example, `speckit.git.commit` → `/speckit-git-commit`.
- For each executable hook, output the following based on its `optional` flag:
  - **Optional hook** (`optional: true`):
    ```
    ## Extension Hooks

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
  - **Mandatory hook** (`optional: false`):
    ```
    ## Extension Hooks

    **Automatic Pre-Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}

    Wait for the result of the hook command before proceeding to the Outline.
    ```
    After emitting the block above you MUST actually invoke the hook and wait for it to finish before continuing. Run it the same way you would run the command yourself in this agent/session (the invocation may differ from the literal `{command}` id shown above, e.g. a skills-mode agent runs it as `/skill:speckit-...` or `$speckit-...`). Emitting the block alone does not run the hook.
- If no hooks are registered or `.specify/extensions.yml` does not exist, skip silently

## Learnings

For a small script or demo, put the implementation approach, input/output shape,
essential dependency findings, and focused validation in one short `plan.md`.
Separate research, data-model, contract, and quickstart documents are optional,
not a prerequisite for implementing a wrapper around an existing CLI.

### Proportionate planning

- These small-feature rules override larger-feature artifact defaults below.
  Keep required setup and extension hooks; omit unused template sections.
- Design only what the approved spec requires. A general obligation to protect data
  or report failures does not itself require provider preflight frameworks, custom
  subprocess lifecycle management, diagnostic pipelines, or extra metadata protocols.
- Prefer upstream configuration, validation, artifacts, and error handling. Add
  boundary checks only for the wrapper's inputs and promises that upstream cannot
  enforce. Do not duplicate the dependency's entire schema or provider validation.
- Verify the exact external capabilities needed by the workflow with a bounded
  lookup or minimal check. Do not turn feasibility verification into a permanent
  compatibility test framework or research every dependency's best practices.
- Preserve explicit requirements and user clarifications. If they imply
  disproportionate machinery, ask about reducing scope before designing around them.
- Example: config parsing, an upstream CLI invocation, saved inputs, a few local
  tests, and usage notes can fit in one plan without a service layer or contracts folder.

## Outline

1. **Setup**: Run `.specify/scripts/powershell/setup-plan.ps1 -Json` from repo root and parse JSON for FEATURE_SPEC, IMPL_PLAN, FEATURE_DIR, BRANCH. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Load context**: Read FEATURE_SPEC and `.specify/memory/constitution.md`. Load IMPL_PLAN template (already copied).

3. **Execute plan workflow**: Follow the structure in IMPL_PLAN template to:
   - Fill Technical Context (mark unknowns as "NEEDS CLARIFICATION")
   - Fill Constitution Check section from constitution
   - Evaluate gates (ERROR if violations unjustified)
   - Resolve material unknowns; put short findings in plan.md, creating research.md
     only when separate research materially helps
   - Describe inputs/outputs and validation in plan.md; create data-model.md,
     contracts/, or quickstart.md only when their content needs a separate artifact
   - Re-evaluate Constitution Check post-design

## Mandatory Post-Execution Hooks

**You MUST complete this section before reporting completion to the user.**

Check if `.specify/extensions.yml` exists in the project root.
- If it does not exist, or no hooks are registered under `hooks.after_plan`, skip to the Completion Report.
- If it exists, read it and look for entries under the `hooks.after_plan` key.
- If the YAML cannot be parsed or is invalid, do not skip silently: tell the user that `.specify/extensions.yml` could not be read (include the parser error) and that no hooks were checked, including any mandatory (`optional: false`) hooks registered there, then continue to the Completion Report.
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
  - If the hook has no `condition` field, or it is null/empty, treat the hook as executable
  - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation
- When constructing command invocations from hook command names, replace dots (`.`) with hyphens (`-`). For example, `speckit.git.commit` → `/speckit-git-commit`.
- For each executable hook, output the following based on its `optional` flag:
  - **Mandatory hook** (`optional: false`) — **You MUST emit `EXECUTE_COMMAND:` for each mandatory hook**:
    ```
    ## Extension Hooks

    **Automatic Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}
    ```
    After emitting the block above you MUST actually invoke the hook and wait for it to finish before continuing. Run it the same way you would run the command yourself in this agent/session (the invocation may differ from the literal `{command}` id shown above, e.g. a skills-mode agent runs it as `/skill:speckit-...` or `$speckit-...`). Emitting the block alone does not run the hook.
  - **Optional hook** (`optional: true`):
    ```
    ## Extension Hooks

    **Optional Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```

## Completion Report

Command ends after design. Report branch, IMPL_PLAN path, artifacts actually
created, and any unresolved limitations. Do not generate extra files to fill a report.

## Phases

### Phase 0: Outline & Research

1. Identify unresolved questions that affect feasibility or implementation.
   Do not generate a research task for every dependency or integration.

2. Resolve small questions directly with targeted reading or minimal checks.
   Do not delegate research automatically; use agents only when explicitly requested
   or when another applicable instruction requires delegation.

3. Record concise findings in `plan.md`, or `research.md` when separate research
   is warranted, using:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: Relevant unknowns resolved or surfaced for user input, with findings
in the plan or an optional research document.

### Phase 1: Design & Contracts

**Prerequisites:** Material feasibility questions resolved; no separate research
file is required.

1. **Describe data only as needed** in the plan, or `data-model.md` for a substantial
   model shared across components:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Define separate interface contracts only when useful** → `/contracts/`:
   - Identify what interfaces the project exposes to users or other systems
   - Document the contract format appropriate for the project type
   - Examples: public APIs for libraries, command schemas for CLI tools, endpoints for web services, grammars for parsers, UI contracts for applications
   - A small script's config and output notes belong in the plan; accepting a CLI
     argument alone is not a reason to create a contracts directory.

3. **Describe validation** in the plan; create `quickstart.md` only when a separate
   end-to-end guide is useful:
   - Document runnable validation scenarios that prove the feature works end-to-end
   - Include prerequisites, setup commands, test/run commands, and expected outcomes
   - Use links or references to contracts and data model details instead of duplicating them
   - Do not include full implementation code, model/service/controller bodies, migrations, or complete test suites
   - Keep this artifact as a validation/run guide; implementation details belong in `tasks.md` and the implementation phase

**Output**: A usable plan and only the supporting artifacts justified by the feature.

## Key rules

- Use absolute paths for filesystem operations; use project-relative paths for references in documentation
- ERROR on gate failures or unresolved clarifications

## Done When

- [ ] Plan completed with only the supporting artifacts needed for this feature
- [ ] Extension hooks dispatched or skipped according to the rules in Mandatory Post-Execution Hooks above
- [ ] Completion reported to user with branch, plan path, and generated artifacts
