# Factory Gates

Status: approved
Slug: factory-gates

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
Deterministic gates check specs, test mapping, reviews and human triage risk without any model call.

## Requirements
- Gates return a clear pass or fail with a reason.
- Review gate needs all four reviewers passing.
- Human triage is driven by explicit risk hints.

## Scenarios

### Scenario: Spec gate passes on a complete spec
- S1: Given a spec with a Status line and a Scenario line, when the spec gate runs, then it passes.

### Scenario: Spec gate fails without scenarios
- S2: Given a spec with no Scenario line, when the spec gate runs, then it fails.

### Scenario: TDD gate passes when scenarios map to tests
- S3: Given every scenario id in the spec appears in tests, when the TDD gate runs, then it passes.

### Scenario: TDD gate fails on an unmapped scenario
- S4: Given a scenario id missing from tests, when the TDD gate runs, then it fails and names the missing id.

### Scenario: Review gate and approver aggregation
- S5: Given four passing reviews, when the review gate and approver run, then the gate passes and the verdict is approved; a fail gives rejected and changes_requested gives changes_requested.

### Scenario: Human triage follows risk hints
- S6: Given a work order with a payments risk hint, when human triage runs, then a human is required; with no risk hints and an approved verdict, no human is required.
