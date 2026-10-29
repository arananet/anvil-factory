# Intake Outcomes

Status: approved
Slug: intake-outcomes

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
Intake today formats whatever arrives and passes it down the line, so the factory spends its budget building things that should have been refused, shrunk, or questioned first. This spec gives intake judgment with a paper trail: it can reject work that must not be built, rescope work that is too big or too vague to build as stated, and park work it cannot judge until the requester answers recorded questions. Every outcome is written on the work order, and intake also stamps each accepted work order with the risk rating and surfaces the routing step downstream consumes.

## Requirements
- The work order model gains an intake outcome record: outcome (accepted, rejected, rescoped, waiting_info), reasons (a list of strings), questions (a list of strings, for waiting_info), the rescoped description when the outcome is rescoped, risk (low, medium or high, null until intake runs), and surfaces (a list drawn from ui, security, data, payments, deploy, content and the factory's other existing domains).
- A rejected outcome is terminal for the run: the runner stops after intake, no spec-writer, test-writer or builder station is spawned, and the work order status becomes rejected. The reasons are recorded on the work order and in the run report. Intake's contract names the refusal class plainly: work whose purpose is harmful, deceptive or unlawful (for example a request to add a covert miner to someone else's machines) is rejected with the reason stated, never quietly reformatted into something buildable.
- A rescoped outcome rewrites the work order's description to the buildable scope and records the cut: what was removed and why, in the outcome record. The run proceeds with the rescoped description, and every downstream packet shows the rescoped scope, so reviewers judge the work that was actually agreed.
- A waiting_info outcome parks the work order: its status becomes waiting_info, the questions are recorded, the runner stops after intake and spawns nothing further. When the requester answers (the work order is updated with the answers and returned to a runnable status), a later run proceeds from intake again. Parked is a waiting state, not a failure: the report records it as waiting, with no verdict of approval or rejection.
- Accepted and rescoped work orders carry intake's risk rating and surfaces. Risk is intake's judgment of blast radius and irreversibility, stated in its contract: high for work touching payments, credentials, data deletion or production deploy paths, low for small reversible changes, medium between. Surfaces name what the work touches, not what it is about.
- The run report and the swimlane render rejected and waiting states honestly: a rejected run's report carries the rejection and its reasons, a waiting run's report carries the questions; neither shows a station as executed when it never ran, and neither state is rendered as a pass.
- Intake's station prompt and contract describe all four outcomes, the refusal class, the rescope discipline (cut recorded, never silent) and the risk and surface vocabulary, so an executed intake produces the outcome record in the standard place in its output.

## Scenarios

### Scenario: Harmful work is rejected at the door with reasons
- S1: Given a work order whose purpose falls in the refusal class, when intake executes, then the outcome is rejected with reasons recorded, the work order status becomes rejected, the runner spawns no further station, and the run report and swimlane show the rejection and its reasons.

### Scenario: Oversized work is rescoped with the cut recorded
- S2: Given a work order that asks for more than one buildable change or is too vague to build as stated, when intake executes, then the outcome is rescoped, the work order description becomes the buildable scope, the outcome record states what was cut and why, and downstream station packets carry the rescoped description.

### Scenario: Unjudgeable work is parked until the requester answers
- S3: Given a work order missing information intake needs to judge it, when intake executes, then the outcome is waiting_info, the questions are recorded on the work order, its status becomes waiting_info, no further station is spawned, and the report records the run as waiting rather than passed or failed; and given the answers are later recorded on the work order and it returns to a runnable status, when a new run starts, then intake runs again and the work can proceed.

### Scenario: Accepted work carries a risk rating and surfaces
- S4: Given a work order intake accepts, when intake executes, then the work order carries a risk of low, medium or high and a surfaces list drawn from the defined vocabulary, and both appear in the run report.

### Scenario: States render honestly in the report and the swimlane
- S5: Given a rejected run and a waiting run, when their reports and swimlanes are read, then no station beyond intake is listed as executed, the rejected run shows its reasons, the waiting run shows its questions, and neither is rendered as approved.
