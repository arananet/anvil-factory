# Existing Project Onboarding

Status: approved
Slug: existing-project-onboarding

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
Most real projects already exist. Onboarding brings an existing codebase onto the factory line without moving or rewriting it: ANVIL reads what is there, adds only the factory pieces that are missing, drafts a baseline spec of the current state, and reports the gaps as suggested first work orders.

## Requirements
- Analysis is read only and detects the stack, tests, specs, CI and documentation that already exist.
- Onboarding never overwrites an existing file. Anything already present is kept and listed as kept.
- A project that is already onboarded (it has anvil.json) stops with a clear error instead of being onboarded twice.
- The brain is seeded from what the project already says about itself, starting with its README.
- The report names the gaps it found and turns each into a suggested first work order.

## Scenarios

### Scenario: Analysis detects what exists
- S1: Given an existing project, when analysis runs, then it reports the detected stack, whether tests exist, whether specs exist, whether CI exists, and the top file types, without writing anything.

### Scenario: Onboarding adds only what is missing
- S2: Given a project with a README and source but no factory files, when onboarding runs, then anvil.json, anvil.yaml, the brain, the OpenSpec structure and an ONBOARDING.md report are created, and the README and source files are byte for byte untouched.

### Scenario: A baseline spec is drafted
- S3: Given a project being onboarded, when it finishes, then a draft baseline spec exists under .openspec/specs/existing-baseline/ describing the project as found, with Status draft.

### Scenario: Double onboarding is refused
- S4: Given a project that already has anvil.json, when onboarding runs, then it raises a clear error and changes nothing.

### Scenario: Gaps become suggested work
- S5: Given a project with no tests and no CI, when the report is written, then it lists those gaps and suggests a first work order for each.
