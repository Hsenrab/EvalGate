# EvalGate Constitution

## Core Principles

### I. Compose ASSERT Rather Than Rebuild It

EvalGate MUST compose ASSERT capabilities rather than reimplement them. Integration code MUST
remain focused on orchestration and the gaps needed by supported workflows. Limitations in
ASSERT MUST be made explicit; elaborate workarounds require user agreement before implementation.

**Rationale:** reuse keeps the tool small and avoids maintaining a competing evaluation engine.

### II. Configure Reusable Workflows

Workflows MUST be reusable through explicit configuration. Customer-specific values and behaviour
MUST NOT be hard-coded into shared logic. Configuration errors MUST produce clear, actionable
errors rather than silently selecting a different workflow.

**Rationale:** one understandable tool must serve different customers without divergent code paths.

### III. Never Report Success Without Sufficient Valid Evidence

Success and pass decisions MUST be supported by sufficient valid evidence for the stated
evaluation criteria. Failed, incomplete, invalid, or missing evaluation evidence MUST NOT be
presented as a pass. Reports MUST disclose the scope evaluated, failures, and gaps that limit
the conclusion. Skipped or unrun checks MUST NOT imply validation or approval.

**Rationale:** a useful evaluation tool must distinguish demonstrated success from uncertainty.

### IV. Preserve Immutable Inputs and Traceable Results

Evaluation inputs used by a run MUST be preserved without mutation. Results MUST remain traceable
to the inputs, configuration, and evaluation implementation used, including relevant ASSERT and
model identifiers where available. Retries MUST NOT overwrite prior evidence or sever its link
to the originating run. Traceability MUST respect the data protections in Principle V.

**Rationale:** conclusions must be auditable even when configuration or dependencies later change.

### V. Protect Customer Data and Credentials

Customer data and credentials MUST be protected during configuration, execution, storage, and
reporting. Credentials MUST NOT be committed or exposed in logs, reports, or saved evaluation
artifacts. Customer data MUST NOT be sent to an unapproved destination. Saved data MUST be
protected against accidental loss or overwrite; retention and access requirements MUST be
explicit for supported workflows.

**Rationale:** lightweight scope never excuses credential exposure or damage to saved data.

### VI. Keep the Design Simple, Extensible, and Demonstrably Tested

Implementations MUST use the simplest design that satisfies supported requirements. Extension
points MUST address an actual requirement rather than hypothetical future use. Meaningful new
behaviour and bug fixes MUST have focused test evidence, with limitations disclosed. Conventional
code and dependencies MUST be preferred over clever solutions or unnecessary infrastructure.

**Rationale:** maintainability and demonstrated behaviour matter more than architectural breadth.

### VII. Bounded, Selective Testing

Testing MUST remain fast, purposeful, and independently runnable.

- Tests MUST be organised by component and execution cost so developers can run only the
  relevant subset.
- Validation MUST default to the smallest test selection that validates a change. Broader suites
  MUST have a clear reason, not run automatically after every edit.
- Fast unit tests, integration tests, and live model evaluations MUST be separately selectable.
  Default development tests MUST NOT make provider calls.
- Tests MUST cover meaningful behaviour, regressions, and boundary cases, not duplicate coverage
  or trivial implementation details.
- Test groups MUST define runtime budgets. Material increases MUST be justified; redundant tests
  MUST be consolidated rather than allowing unchecked growth.
- Live evaluations MUST be explicitly invoked with bounded case counts, concurrency, retries,
  and timeouts. Runs MUST NOT silently expand.
- Skipped or unrun checks MUST be disclosed. A partial selection MUST NOT be presented as complete
  validation or approval.

**Rationale:** confidence must increase through focused evidence, not an ever-growing suite that
becomes too expensive to use.

## Lightweight Scope

EvalGate MUST remain a useful, reusable tool, not a production platform.

- Development MUST prioritise the supported happy path and common errors.
- Clear errors and documented manual retry MUST be preferred over complex recovery, rollback,
  or self-healing.
- Defensive layers, abstractions, and infrastructure MUST NOT be added for hypothetical problems.
- Documented limitations MUST be accepted where the workaround is reasonable.
- Hardening MUST be justified by a requirement or observed failure and its implementation and
  testing cost.
- Scope reductions MUST NOT compromise credentials, saved data, or honest evaluation outcomes.

## Requirement Challenges

Requirements are open to challenge, not instructions to implement at any cost.

- Work MUST pause for user consultation when a request introduces complexity, workarounds,
  dependencies, or maintenance out of proportion to its value.
- The trade-off MUST be explained plainly with a simpler alternative, reduced scope, or deferral.
- Contradictory requirements, unclear benefits, and requests that conflict with the tool's
  lightweight purpose MUST be challenged.
- Elaborate workarounds for limitations in ASSERT or other dependencies MUST NOT be built silently.
- Material scope or architecture expansion MUST receive user agreement before implementation.
  Routine implementation choices do not require approval.

**Rationale:** surfacing an awkward requirement early is better than delivering an unnecessarily
complicated solution.

## Clear Ownership and Handover

The tool MUST be understandable and operable without its original author.

- Documentation MUST cover setup, common commands, configuration, and known limitations.
- Code and dependencies MUST favour conventional, understandable approaches.
- Upstream ASSERT code MUST remain distinguishable from customer-owned changes.
- Behaviour changes MUST update directly affected documentation without creating unnecessary
  documentation.

**Rationale:** reuse depends on clear ownership and practical handover, not author-specific knowledge.

## Governance

This constitution governs EvalGate specifications, plans, implementation, and review. Conflicts
MUST be surfaced and resolved before conflicting work proceeds; a feature request alone does not
override these principles.

Amendments MUST identify the affected principles, explain the trade-off and any migration impact,
and obtain project-owner approval. Approved amendments MUST update this document's version and
last-amended date. The original ratification date MUST remain unchanged.

Constitution versions MUST follow semantic versioning:

- MAJOR for incompatible principle removals or redefinitions.
- MINOR for new principles or materially expanded guidance.
- PATCH for clarifications and non-semantic wording fixes.

Specifications, plans, and change reviews MUST check compliance with affected principles,
including scope, evidence validity, data protection, and bounded testing. Validation reports MUST
state the checks run and disclose unrun or skipped checks. Exceptions MUST be explicit and
approved; changes to a governing rule require an amendment rather than an undocumented bypass.

**Version**: 1.0.1 | **Ratified**: 2026-11-17 | **Last Amended**: 2026-11-17
