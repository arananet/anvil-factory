# Autonomous Line: real loopbacks, a resumable human gate, one workflow

Status: implemented
Slug: autonomous-line

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
An audit on 2026-11-12 found that ANVIL was an assembly line an operator started and repaired by hand, not a factory. The run record said so itself: a loopback was written into the report but no station ran again (a second execution needed a copied workflow on a new branch), every work order had its own hand written workflow file, the intake worker returned a work order and forwarded it nowhere, the human gate computed a boolean nobody could answer, `anvil run` exited 0 whatever the verdict, and the publisher ran in execute mode even behind a closed human gate.

This spec closes those gaps in the engine, so every project inherits them: a work order travels from a labeled issue to an approved pull request, through its own corrections and through a recorded human decision, without anyone writing YAML or relaunching a run.

Provenance: this change is owner-authored work outside the line (decision 0006). The line neither produced nor reviewed it; the evidence is the test suite named below.

## Requirements

- R1, real loopback. In execute mode, when the approver verdict is rejected or changes_requested, or the pre-review checks gate fails, and loopbacks remain, the runner re-enters the line at the return station and runs every station from there again. The stations of the new attempt receive a Loopback feedback section with the sender, the reason and the findings; reviewers are told it is a re-review. Reviews of the replaced attempt never count. The replaced attempt's outputs and reviews are archived under runs/<id>/attempts/<n>/. Re-executed steps carry their attempt number, and the return station's step carries the feedback.
- R2, bounded. A new attempt starts only when the run thresholds leave room for it (agent calls for the whole attempt, run tokens). When they do not, or loopbacks are exhausted, the verdict stands and the loopback step records why nothing was re-executed. The default agent call limit rises from 16 to 32 so the default line can afford one full correction.
- R3, exit codes. `anvil run` and `anvil resume` exit 0 when the run ended well, 1 when the line did not approve or a step or deploy failed, 3 when a human must act, 4 when intake stopped the order. A run without --execute judges nothing and exits 0.
- R4, the human gate is an act. `anvil approve <project> <work-order-id> --by <name>` records an approval bound to the run id it approves. A verdict the line did not approve needs --override, which is recorded; a run that did not finish (failed, budget_exceeded, gate_failed, packet_ready) cannot be approved. `anvil resume` re-enters the line after the gate with the previous steps kept, never re-running an earlier station, and records the approval in the decision record. An approval for a different run is refused. With an override the report keeps the line's own verdict.
- R5, publishing is held like deploying. In execute mode the publisher never runs on an unapproved run or behind a closed human gate; it runs on resume after a recorded approval.
- R6, issue to work order. `anvil work-order-from-issue` maps a GitHub issue to a work order: id wo-gh-<number>, kind from a label naming a kind (default feature), risk hints from labels (bare or risk:<hint>), pipeline from a pipeline:<name> label.
- R7, intake is connected. The intake worker forwards a work order as a repository_dispatch event of type anvil-work-order when GITHUB_REPO and GITHUB_TOKEN are set: for a signature verified issue delivery labeled anvil, and for POST /work-orders only with the INTAKE_TOKEN bearer. A failed forward is reported in the response and never throws.
- R8, red before green is evidence. In execute mode with project checks configured, the checks run once after the test-writer and before the builder; the result is recorded on the test-writer step. When they pass, the report warns and reviewer-tests is told to verify the tests exercise the new behavior.
- R9, one workflow. .github/workflows/anvil-line.yml serves every work order: started by the anvil label, by repository_dispatch or manually; `/anvil approve` from an owner, member or collaborator answers the human gate. No workflow names a work order.
- R10, isolation. `--isolate` runs the order on branch anvil/<work-order-id> in a git worktree beside the project and commits the result there, run evidence included. The checkout the operator works in is not edited.
- R11, the standing review gate counts every review on record: the four core reviews are required, and any other reviewer file present must pass too.
- R12, routing never empties a panel by omission. A reviewer the pipeline names that is in neither configured routing panel (the content reviewers, or a project's own) is always selected; the policy reduces only the panels it knows. Before this, every content run in execute mode ended no_reviews.

Guardrails: Python standard library only. Parallel reviewer execution is out of scope: the reviewer tree guard compares the whole working tree, so concurrent reviewers in one tree would fail each other. The station runtimes still run without their own sandbox; isolation here is a branch and a worktree, not a jail.

## Scenarios

### Scenario: The line corrects itself
- S1: Given a reviewer that fails the first attempt and passes the second, when the line runs in execute mode, then the builder runs twice, the second builder packet carries the finding, the first review is archived and not counted, and the verdict is approved with one loopback.
- S2: Given a reviewer that always fails, when the line runs, then the builder runs once per allowed attempt and the verdict stands; and given a call limit with no room for another attempt, then nothing is re-executed and the loopback step says why.

### Scenario: CI can gate on the line
- S3: Given run reports with each outcome, when the exit code is computed, then it is 0, 1, 3 or 4 as R3 states, and the CLI returns it.

### Scenario: A human answers the gate
- S4: Given an approved run held by a production-deploy risk hint, when a human approves and the run is resumed, then the deploy command runs, no earlier station runs again, and the decision record names the approver; an approval is refused without --override for a rejected run and refused for a different run.
- S5: Given a content order with the publishing risk hint, when the line runs, then the publisher does not run; after approve and resume it does.

### Scenario: Orders arrive without an operator
- S6: Given a GitHub issue with labels, when it is mapped, then the work order carries the id, kind, risk hints and pipeline R6 names.
- S7: Given a verified issue delivery labeled anvil, when the intake worker handles it, then a repository_dispatch of type anvil-work-order is sent, the same event type the workflow listens for.
- S9: Given the workflows directory, then anvil-line.yml is the only line workflow, it listens for the label, the comment, the dispatch and the manual start, and it names no work order.

### Scenario: Evidence and isolation
- S8: Given project checks that pass before the builder runs, when the line runs, then the test-writer step records the check as not red, the report warns, and the reviewer-tests packet says so.
- S10: Given a git project, when the line runs with --isolate, then branch anvil/<id> holds a commit with the change and the run report, and the project checkout is unchanged.
- S11: Given standing reviews with a failing reviewer-design file beside four passing core reviews, when the review gate runs, then it fails naming that review.
- S12: Given a pipeline with content reviewers, when reviewers are routed at any risk level, then the content reviewers are selected and a content run can reach approved.
