# Continuous Run Accounting

Status: proposed
Slug: continuous-run-accounting

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose

A run's accounting in ANVIL is written at the end of the run, by the same code whose death would make the accounting matter most. The C64 blueprint chain paid for that shape twice. Work order wo-gh-6 (project c64-retro-hardware, run 43668712644) exhausted its budget: the builder's single call measured 6,359,529 cache-inclusive tokens against the 6,000,000 run cap, the run died with status budget_exceeded before the builder wrote its report, and the branch held finished product with no builder report and no complete run record. Work order wo-gh-7 then spent a second run (5,697,863 tokens measured) largely to write the paperwork wo-gh-6 never wrote: the builder report and the comparison records for work that already existed. The comparison against other software factories (factory research of 2026-11-15, section "Mechanisms ANVIL Does Not Have", mechanisms 7 to 12) shows the standard shape elsewhere: mini-SWE-agent saves its trajectory in a finally block after every step and converts limit exceptions into recorded exit outcomes inside the saved record; Attractor checkpoints after every node and resumes from the last checkpoint; OpenHands treats an append-only event log as the run record, reconstructable after any kill. In all three, the record is a by-product of execution, not a final step. This order gives ANVIL that property: the run record is checkpointed after every station and completed on every exit path, so a killed run still leaves a complete report with its exit status, its measured cost and its per-station outcomes, and no second run is ever needed to write paperwork.

## Requirements

### R1. Checkpoint after every station
- The runner writes the run record (runs/<work-order-id>/report.json, with the step records it aggregates) after every station completes, fails or is skipped, in the same shape the final report uses, plus a checkpoint field set: the last completed station, the run's elapsed milliseconds at the checkpoint, and the measured usage so far.
- A reader opening the record mid-run sees a valid report that is complete as of the last finished station, never a partial document: each checkpoint write is atomic (written to a sibling temporary file and renamed over the record).
- The final report of a healthy run is the last checkpoint plus the verdict and decision sections; checkpointing adds no station and no model call.

### R2. Save on every exit path
- Every termination path of a run completes the record before the process exits: normal completion; a verdict reached; budget exhausted (exit status budget_exceeded); a station timeout (using the station-timeout capability's honest timeout records); the runtime turn limit; a checks gate stop; an intake stop (rejected, rescoped stop or waiting_info); an uncaught exception in spine code; and the external termination signals the runner can trap (SIGTERM, SIGINT).
- The completed record names: the exit status; the termination reason in the run's own vocabulary; every station that ran, with its outcome and its executed model (null only when no model ran, per the station artifact contract); every station that never ran, recorded as not run; and the cost section under cost-measurement semantics (the total is the sum of measured steps, unmeasured steps are recorded as unmeasured with their reason).
- A budget death is itself a recorded, complete outcome: the record carries status budget_exceeded, the measured consumption that crossed the cap, and the station in flight when the cap was crossed, with that station's partial usage when the runtime exposed it.

### R3. No second run for paperwork
- Inspecting or resuming after a killed run reads the checkpointed record as the run's accounting. The report tooling (tools/line_comment.py and the swimlane renderer) renders a killed run's record without any station executing.
- When a later run of the same work order starts, the killed run's record is preserved in the run history (the token-efficiency spec already requires earlier reports to be preserved in project totals); the new run never overwrites the killed run's accounting.

### R4. Regression tests
- The order's own tests are new files under tests/ and drive scripted runs through the runner with a fake runtime: (a) a run killed at the run token cap in the middle of the builder station leaves a complete record on disk: exit status budget_exceeded, per-station outcomes for the stations that ran, the builder station recorded with its measured partial usage, the unrun stations named as not run, and the record parses as JSON; (b) the same completeness assertions hold for a run ended by a station timeout and for a run ended by an uncaught error injected into a station step, each with its own exit status and reason; (c) a healthy scripted run leaves a checkpoint after each station, and its final report equals the last checkpoint plus the verdict sections; (d) a scripted run that receives SIGTERM leaves a completed record naming the signal as the termination reason.

### Guardrails
- Python standard library only, consistent with the factory spine. No new dependency.
- The report schema grows additively (checkpoint field set, exit status, termination reason). Existing report consumers (the line comment, the status page, the swimlane) keep working on reports written before this change and on checkpointed reports.
- Frozen surfaces: cost-measurement semantics (totals are sums of measured steps only; unmeasured stays unmeasured and says why); the station-timeout record fields; the station artifact contract's executed model honesty; the review parse contract; the reviewer prompts; pipeline definition files (protected in anvil.json); anvil.json itself (protected).
- Relationship to token-efficiency: its per-attempt usage artifacts and its rule that a budget stop preserves the report are inputs to this order, not replaced by it; this order generalizes preservation from the budget stop to every exit path and makes it a property of the runner.
- Existing test files at the base ref are not modified or deleted; new tests arrive as new files.
- No em dash or en dash character in any produced file (project style rule).
- Nothing in this order merges, publishes or deploys anything; the run stops at the owner human gate.

## Scenarios

### Scenario: A budget death leaves a complete report
- S1: Given a scripted run whose builder station crosses the run token cap mid-station, when the run dies, then the record on disk parses, carries exit status budget_exceeded with the measured consumption that crossed the cap, records the stations that ran with their outcomes and executed models, names the stations that never ran as not run, and no station executes to produce that record after the death.

### Scenario: Timeout and error deaths are recorded the same way
- S2: Given a scripted run ended by a station timeout, and a second scripted run ended by an uncaught error in a station step, when each run ends, then each record is complete in the S1 sense and carries its own exit status and termination reason, distinct from budget_exceeded and from each other.

### Scenario: Checkpoints accumulate during a healthy run
- S3: Given a healthy scripted run, when each station finishes, then a checkpoint of the run record exists naming that station as the last completed one, and the final report equals the last checkpoint plus the verdict and decision sections.

### Scenario: A killed run needs no second run for its accounting
- S4: Given the record left by the S1 budget death, when the line comment tooling renders it, then it renders without executing any station; and given a later run of the same work order, when it starts, then the killed run's record is preserved in the run history and is not overwritten.

### Scenario: An external kill still completes the record
- S5: Given a scripted run in progress, when the runner process receives SIGTERM, then the record on disk is completed with the signal named as the termination reason and the per-station outcomes as of the last finished station.
