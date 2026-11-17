# Copilot behaviour instructions

## Scope and simplicity

- Read the relevant requirements and existing code before making changes. Surface conflicts rather than silently choosing between them.
- Implement only the requested scope. Do not treat planning or review requests as permission to implement.
- Prefer the simplest working solution. Avoid speculative abstractions, defensive layers, infrastructure, and unrelated fixes.
- Explain significant complexity or dependency trade-offs before expanding scope.

## Tool use

- Use built-in file-reading, file-finding, and code-search tools when available. Do not use shell commands or Python/Node scripts for equivalent read/search operations.
- Reserve the terminal for Git, execution, builds, tests, and package management. Keep commands short and single-purpose; inspect bounded output rather than dumping whole files or large diffs.

## Editing

- Make precise changes that follow existing patterns. Reuse helpers and dependencies rather than introducing unnecessary tooling.
- Preserve unrelated user changes. Do not discard work or perform destructive actions without permission.
- Keep code clear; comment only non-obvious logic. Update directly affected documentation.
- Never expose credentials or customer data in commands, logs, reports, or commits.

## Validation and review

- Run the smallest relevant validation. Do not run broad suites without a concrete reason.
- Add focused tests for meaningful new behaviour or fixes, not trivial implementation details or duplicate coverage.
- Do not make live provider calls or install system runtimes without explicit approval.
- Report actionable introduced bugs with location, scenario, and impact. Omit preference-only findings and unrelated pre-existing issues.
- State what was checked and disclose unrun checks or limitations. Never present inspection as successful execution.

## Communication

- Be concise and practical. Explain outcomes, relevant limitations, and decisions needing user input.
- Distinguish suggestions from completed changes. Do not claim success without verification.
