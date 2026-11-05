# Task packet: deployer

## Station prompt

# Deployer

## Role
Prepare and carry out the release step described by the project.

## Inputs
- approved change

## Outputs
- release record

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.


## Work order

- id: wo-gh-30
- kind: feature
- title: Verification run: model migration routes on merged main
- source: github-issue
- description: Pure verification run on merged main (model migration, issue 29, merged at 7e426af0). NO CODE CHANGES: the builder is barred from modifying, adding or deleting any file; the standing tree on main is the deliverable under judgment.

Purpose: prove the new per-station model wiring end to end on merged main. The run report is the evidence and must show, per executed step, configured_model and executed_model agreeing with the migration policy:
- builder: claude-opus-5-5
- spec-writer, test-writer: claude-sonnet-5-5
- reviewer-spec, reviewer-tests, reviewer-security, reviewer-architecture: claude-sonnet-5-5
- reviewer-design, reviewer-ux: openai/gpt-6.1-sol, executed through the agentic Codex runtime, each writing its own counted review file
- intake, observer: claude-sonnet-5-5

The surface under review is the factory status page (the project's servable UI: anvil.yaml declares static_root status, page_path /index.html): reviewers judge the status page as rendered after the migration (rendered evidence is captured by the line after the builder step), the standing wiring files (anvil.yaml, tools/dispatch_station.py, tools/codex_station.py, tools/claude_station.py, anvil/routing.py, anvil/knowledge.py), decision record brain/decisions/0004-model-migration.md, and the route smoke script tools/model_route_smoke.py, all as they stand on main. Reviewers: a station that cannot execute on its assigned route, a configured/executed model disagreement, or a missing self-report is a fail with the evidence named; if every route executes as assigned, pass.

GitHub issue: https://github.com/arananet/anvil-factory/issues/30

VERIFICATION ROUND 2 (on current main, after the wo-gh-31 tier totality merge). Round 1 verdict: no_reviews; the gate failed on two test defects, both since resolved at the root:
1. This run's own test-writer encoded the builder policy as always claude-opus-5-5 and flagged the builder's actual assignment. OPERATOR RULING: on a work order carrying a UI surface, the guided design model assignment for the builder (openai/gpt-6.1-sol) is the correct policy behavior (migration spec R5); the policy the evidence test must encode is: builder is claude-opus-5-5 on non-UI work and openai/gpt-6.1-sol on UI-surface work, with executed_model self-reported and equal to the assignment. The test-writer corrects its round 1 test accordingly; that correction is the only test change this round.
2. The readme showcase link test failed because the runs/ evidence tree was missing from main's tree at that time (a merge artifact, since repaired on main at d5368392 and confirmed present). No action needed here; the suite on current main is the judge.
Everything else in the round 1 brief stands: no code changes by the builder; reviewers judge the routes as executed on current main, reviewer-design and reviewer-ux on openai/gpt-6.1-sol included.
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed
- test-writer: executed
- builder: executed
- checks-gate: passed
- reviewer-spec: executed
- reviewer-security: routed_out
- reviewer-tests: executed
- reviewer-architecture: routed_out
- reviewer-design: executed
- reviewer-ux: failed
- approver: completed
- approver: loopback
- triage-human: completed
