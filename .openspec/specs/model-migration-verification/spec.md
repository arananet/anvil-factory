# Model migration verification: routes on merged main (round 2)

Status: draft
Slug: model-migration-verification

## Roles
- implementer: the builder; makes no change in this run
- reviewer: judges the standing tree and the run evidence against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
Prove the per-station model wiring of the model migration (issue 29, merged at 7e426af0, capability model-migration) end to end on current main, after the tier totality merge (wo-gh-31, capability model-tier-map). The run report is the evidence. This is a verification run: the standing tree on main is the deliverable under judgment. Work order: wo-gh-30, issue 30, round 2. Round 1 verdict was no_reviews because of two test defects, resolved as recorded under Round 2 rulings.

## Requirements

R1. No code changes. The builder does not modify, add or delete any file. The diff of the run against main is empty apart from run records the runner itself writes.

R2. Policy the evidence must show. For every executed step the run report records configured_model and executed_model, and they agree with the policy below. executed_model is the runtime's self-report, never a copy of the configured label (model-migration R3). A missing self-report is a failure.
- builder: claude-opus-5-5 on non-UI work; openai/gpt-6.1-sol on a work order carrying a UI surface (model-migration R5).
- spec-writer, test-writer: claude-sonnet-5-5.
- reviewer-spec, reviewer-tests, reviewer-security, reviewer-architecture: claude-sonnet-5-5.
- reviewer-design, reviewer-ux: openai/gpt-6.1-sol, executed through the agentic Codex runtime, each writing its own review file that the runner counts.
- intake, observer: claude-sonnet-5-5.
Tier labels (review-cheap, review-balanced, review-strong, fast-builder, reasoning-strong) never appear as configured_model; each is resolved to a concrete model at hand-off (model-migration R10, model-tier-map R1).

R3. This work order carries the surface "ui". Its builder assignment is therefore openai/gpt-6.1-sol, and that is correct policy, not a disagreement.

R4. Surface under review. Reviewers judge: the factory status page as rendered after the migration (anvil.yaml declares static_root status, page_path /index.html; the rendered evidence is captured by the line after the builder step); the standing wiring files anvil.yaml, tools/dispatch_station.py, tools/codex_station.py, tools/claude_station.py, anvil/routing.py and anvil/knowledge.py; the decision record brain/decisions/0004-model-migration.md; and tools/model_route_smoke.py, all as they stand on main.

R5. Reviewer verdict rule. A station that cannot execute on its assigned route, a configured_model and executed_model disagreement, or a missing self-report is a fail, with the evidence named (step, configured_model, executed_model). If every route executes as assigned, the verdict is pass.

R6. Round 2 rulings (operator).
- The test-writer corrects its round 1 evidence test to the R2 builder policy: claude-opus-5-5 on non-UI work, openai/gpt-6.1-sol on UI-surface work, executed_model self-reported and equal to the assignment. This is the only test change this round.
- The readme showcase link test failed in round 1 only because runs/ was missing from main at that time; it was repaired on main at d5368392. No action is taken here; the suite on current main is the judge.

## Scenarios

### Scenario: Per-step agreement
- S1: Given the completed run report, when each executed step is read, then configured_model equals executed_model and equals the R2 assignment for that station, with executed_model taken from the runtime self-report.

### Scenario: Builder policy by surface
- S2: Given a work order whose surfaces include ui, when the builder step is read, then configured_model and executed_model are both openai/gpt-6.1-sol. Given a work order with no UI surface, then both are claude-opus-5-5. The evidence test encodes both cases and fails on any other value.

### Scenario: Design reviewers on Codex
- S3: Given the run, when reviewer-design and reviewer-ux are read, then each executed on openai/gpt-6.1-sol through the Codex runtime, each wrote its own review file, and the runner counted both.

### Scenario: No tier labels at hand-off
- S4: Given every step in the run report, then no configured_model is an unresolved tier label, including reviewer steps at low risk (review-cheap resolves to claude-sonnet-5-5).

### Scenario: Missing self-report fails
- S5: Given a step whose runtime reported no model, then executed_model is null and the verdict is fail with that step named.

### Scenario: Empty change
- S6: Given the builder step finished, when the working tree is compared with main, then no file was modified, added or deleted by the builder.

### Scenario: Suite on current main
- S7: Given current main with runs/ present, when the full factory suite runs, then it is green, including the readme showcase link test and the corrected evidence test of R6.
