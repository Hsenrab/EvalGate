---
description: "Proportionate task list for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: [spec.md](spec.md), [plan.md](plan.md), and relevant supporting documents
only if they exist.

**Scope**: [Requested deliverable and important exclusions.]

<!--
For a small script, use one short checklist. The entries below are examples,
not a required count or mandatory stages. Replace them with actual cohesive tasks.
Do not split each helper, field, error variation, or documentation paragraph.
-->

## Tasks

- [ ] T001 [Verify required dependency support and make necessary setup changes in named files.]
- [ ] T002 [Implement the supported workflow and common errors in the implementation file.]
- [ ] T003 [Add a few focused behaviour tests in the test file, if tests are requested.]
- [ ] T004 [Document usage and run the relevant validation with named files/commands.]

## Validation

[Required focused checks and the manual acceptance outcome. Distinguish offline
tests from live execution; do not invent extra validation tooling.]

<!--
Optional for larger features:
- Group tasks by genuinely distinct user journeys using [US1], [US2], etc.
- Add phases only for real execution boundaries, not empty setup/foundation/polish scaffolding.
- Mark [P] only for genuinely independent tasks touching different files.
- Explain dependencies if list order is insufficient.
- Add graphs, parallel examples, or delivery strategy only when they help execution.

Keep sequential T001-style IDs and actual file paths. Reference approved constraints
rather than duplicating field schemas. Tests-first ordering is required only when
the user requests TDD; requesting a few tests does not imply it.

Preserve approved requirements. If the spec or plan is disproportionate, surface
the conflict before simplifying it; do not silently omit required work.
-->
