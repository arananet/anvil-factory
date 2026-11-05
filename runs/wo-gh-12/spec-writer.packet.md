# Task packet: spec-writer

## Station prompt

# Spec Writer

## Role
Write or revise an OpenSpec spec from a work order.

## Inputs
- work order
- brain

## Outputs
- spec

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.


## Work order

- id: wo-gh-12
- kind: feature
- title: A dedicated UX reviewer station (reviewer-ux), separate from reviewer-design
- source: github-issue
- description: Implement the spec in .openspec/specs/reviewer-ux/spec.md in the factory. It builds on the routing capability and the design knowledge capability, both landed earlier in this program's sequence, and on the rendered evidence capability where screenshots exist.

Build, per the spec scenarios:

S1: stations/reviewer-ux/ in the catalog (agent kind, standard review format) whose contract judges the experience: user flows and task completion, usability heuristics, accessibility basics, and clarity of the interface copy; the contract explicitly excludes visual system compliance (tokens, type scale, palette) as reviewer-design's lens, and the catalog entry carries the guided design station designation naming the design model from the recorded routing policy.

S2: reviewer-ux joins the reviewer group of sdlc-default, content-default and content-short (the pipelines reviewer-design serves). The routing step activates it when the work order carries a ui surface; its packet then carries the design knowledge guidelines slice for the project's product type and, where the run produced rendered screenshots, the rendered evidence.

S3: on work with no ui surface the router routes reviewer-ux out before execution, records it as routed out with the surface rule named, and the approver's expected review count excludes it; no reviewer-ux step executes and non-UI work pays nothing for the lens.

S4: the run report and swimlane list reviewer-design and reviewer-ux as separate entries with independent verdicts and findings.

S5: when a ui surface run has no rendered screenshots, reviewer-ux's recorded review states it judged from source and the knowledge slice without rendered evidence.

Tests covering S1 to S5 in the factory suite style, including the ui-surface selection and the non-ui skip, docs updated, CHANGELOG Unreleased updated. Keep the whole suite green and every pipeline valid.

GitHub issue: https://github.com/arananet/anvil-factory/issues/12

Operator standing note for every round of this order: the builder must not create or modify anything under .github/workflows/ (the Actions token cannot push workflow changes; a run that touches them loses its commit-back). Tooling the run needs is staged by the operator in the workflow before the line step. Test changes are written by the test-writer station; the builder must not modify tests/, anvil.json or pipelines/. Tests must be real: every test calls the implementation it names and asserts behavior, never the mere existence of data structures.

CLOSING AND REPAIR RUN (after run 41777213190, verdict no_reviews). Two facts frame this run, stated plainly. First, round 1's builder added reviewer-ux to pipelines/sdlc-default.json, pipelines/content-default.json and pipelines/content-short.json; pipelines/ is a protected path, so the checks gate blocked round 1 before any review. That pipeline composition change is this item's core deliverable; it stands in the tree and is part of what the reviewers judge in this run. The builder must not modify pipelines/, anvil.json or .github/workflows/ in this run. Second, the gate suite on the standing tree fails 10 tests (319 run), reproduced by the operator locally. They are the work of this run:

Implementation defects, owned by the builder:
A. test_review_parsing_integrity.test_reviewer_prompts_have_no_json_examples_s5 fails: the new stations/reviewer-ux/PROMPT.md violates the reviewer prompt contract (no parseable JSON examples; the canonical Output Format contract shape only). Fix the prompt.
B. The routing surface rule: four test_risk_routing full panel tests and three test_supervisor flow tests fail. Per this item's spec S3, reviewer-ux is routed out when the work has no UI surface, with the reason recorded; the risk routing and supervisor fixtures describe non UI work, so their counted panel stays the classic five. If the routing integration selects reviewer-ux for non UI work anywhere in the default path, that is an implementation defect: fix the routing so the surface rule applies in every path that builds the selected set. Do not fix these by editing the tests to expect six reviewers for non UI work.

Test defects, owned by the test-writer station:
C. test_reviewer_ux.test_s5_no_screenshots_declared_in_review fails on its executor simulation (the builder's round 1 output admits the spec behavior is in the prompt but the simulation does not drive it). Fix the simulation so the S5 declaration is genuinely exercised.
D. test_anvil.TestRegistry.test_registry_s6 pins the station registry from before this item existed. This item adds a station by design; update the expectation to the registry as it now stands, including reviewer-ux, and nothing else about that test.

Success is a green gate: the full suite passes (319 tests at round 1 count, plus any legitimately added), protected paths pass, and the reviewers judge the whole standing change, pipeline composition included. Keep every pipeline valid.

VERIFICATION RUN (after run 41779746722, verdict no_reviews). Full history, stated plainly for the reviewers who judge this run: round 1's builder added reviewer-ux to the three pipeline files (protected), which blocked its gate. The repair run fixed the prompt contract and the routing surface rule, and its builder also edited two test fixtures in its own delta (tests/test_risk_routing.py: the null risk fixture now describes non UI work, matching what that test asserts; tests/test_supervisor.py: the REVIEWERS constant now includes reviewer-ux, matching the pipeline it validates), which tripped the protected path rule again even though the suite is green. The operator has verified the standing tree directly: 319 tests, all passing, all 8 pipelines valid.

This run changes nothing. The builder and the test-writer verify the standing implementation and make no edits to any file: not tests/, not pipelines/, not anvil.json, not .github/workflows/, and no implementation file unless a genuine defect is found, in which case the run stops and reports it instead of fixing it here. The reviewers judge the whole standing change on its merits: the reviewer-ux station and its contract, the routing surface rule (in for UI work, routed out with the reason recorded otherwise), the prompt contract compliance, the pipeline composition in the three pipeline files, and the fixture updates named above. On an approved verdict this order closes.
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
