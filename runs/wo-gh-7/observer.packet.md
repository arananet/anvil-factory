# Task packet: observer

## Station prompt

# Observer

## Role
Watch the released change and report what actually happened.

## Inputs
- release record

## Outputs
- observation report

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.


## Work order

- id: wo-gh-7
- kind: feature
- title: Intake outcomes: reject, rescope, needs-info parking, risk and surfaces
- source: github-issue
- description: Implement the spec in .openspec/specs/intake-outcomes/spec.md in the factory.

Build, per the spec scenarios:

S1: intake can REJECT a work order whose purpose is harmful, deceptive or unlawful, with reasons recorded on the work order; rejection is terminal, the runner spawns no further station, the work order status becomes rejected, and the report and swimlane show the rejection and its reasons.

S2: intake can RESCOPE an oversized or vague work order: the description becomes the buildable scope, the outcome record states what was cut and why, and downstream packets carry the rescoped description.

S3: intake can answer NEEDS-INFO: outcome waiting_info, questions recorded, work order status waiting_info, nothing further spawns, and the report records a waiting state rather than a pass or a failure. When answers are recorded and the work order returns to a runnable status, a later run proceeds from intake again.

S4: accepted and rescoped work orders carry intake's risk rating (low, medium, high) and surfaces list from the spec's vocabulary; both appear in the run report.

S5: rejected and waiting runs render honestly: no station beyond intake listed as executed, reasons and questions shown, neither rendered as approved.

The work order model gains the intake outcome record (outcome, reasons, questions, rescoped description, risk, surfaces). Intake's station prompt and contract describe all four outcomes, the refusal class, the rescope discipline and the risk and surface vocabulary. Tests covering S1 to S5 in the factory suite style, docs updated, CHANGELOG Unreleased updated. Keep the whole suite green and every pipeline valid.

GitHub issue: https://github.com/arananet/anvil-factory/issues/7
- risk_hints: 
- status: new

## Upstream steps

- intake: completed
- spec-writer: executed
- test-writer: executed
- builder: executed
- checks-gate: passed
- reviewer-spec: executed
- reviewer-security: executed
- reviewer-tests: executed
- reviewer-architecture: executed
- reviewer-design: executed
- approver: completed
- approver: loopback
- triage-human: completed
- deployer: packet_ready
