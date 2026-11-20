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
- R1.1: When a station completes, fails, times out or is skipped, the runner shall write the run record runs/<work-order-id>/report.json, with the step records it aggregates, in the same shape the final report uses plus a top level `checkpoint` object with three fields: `last_completed_station` (the station id), `elapsed_ms` (the run's elapsed milliseconds at the checkpoint, a number) and `usage_so_far` (the measured usage summed over the steps recorded so far, under cost-measurement semantics).
- R1.2: Each checkpoint write is atomic: the record is written to a sibling temporary file in the same directory and renamed over report.json. A reader opening report.json at any moment during the run parses valid JSON that is complete as of the last finished station. No temporary file is left behind after a write.
- R1.3: Checkpointing adds no station and no model call. The final report of a healthy run equals the last checkpoint plus the verdict and decision sections (and the exit fields of R2.2); every other key and every step record is unchanged between the last checkpoint and the final report.

### R2. Save on every exit path
- R2.1: Every termination path of a run completes the record before the process exits. The paths are: normal completion; a verdict reached; run budget exhausted; a station timeout (using the station-timeout capability's timeout records as they stand); the runtime turn limit (max_runtime_turns); a checks gate stop; an intake stop (rejected, rescoped stop or waiting_info); an uncaught exception in spine code; and the trappable external signals SIGTERM and SIGINT.
- R2.2: The completed record carries a top level `exit_status` and a top level `termination_reason`. `exit_status` is one value from this closed set, one per path in R2.1: `completed` (normal completion or a verdict reached), `budget_exceeded`, `station_timeout`, `turn_limit`, `checks_stopped`, `intake_stopped`, `error`, `signal`. `termination_reason` is a non empty string in the run's own vocabulary that names the specific cause: the station and limit for a budget death or timeout, the exception type and message for `error`, the signal name (`SIGTERM` or `SIGINT`) for `signal`, the intake outcome for `intake_stopped`.
- R2.3: The completed record names every station in the pipeline exactly once in the step records: each station that ran with its outcome and its executed model (null only when no model ran, per the station artifact contract), and each station that never ran with status `not_run`. The cost section follows cost-measurement semantics unchanged: the total is the sum of measured steps; unmeasured steps are counted as unmeasured and say why.
- R2.4: A budget death is a recorded, complete outcome: the record carries exit_status `budget_exceeded`, the measured run consumption that crossed the cap together with the cap value, and the station in flight when the cap was crossed, recorded with that station's partial measured usage when the runtime exposed it, or as unmeasured with its reason when it did not.
- R2.5: If the record cannot be completed on an exit path (for example the write itself fails), the last checkpoint written under R1 stays on disk unchanged and the failure is reported on stderr naming its reason; the runner never leaves a truncated report.json.

### R3. No second run for paperwork
- R3.1: Inspecting or resuming after a killed run (the inspect and resume paths in anvil/cli.py) reads the checkpointed or completed report.json as the run's accounting. tools/line_comment.py and the swimlane renderer in anvil/runner.py render a killed run's record from report.json alone, with no station executing and no model call.
- R3.2: When a later run of the same work order starts, the earlier run's report.json, killed or not, is preserved in runs/<work-order-id>/history/ by the existing content-addressed preservation before any checkpoint of the new run is written; the new run never overwrites the earlier run's accounting.
- R3.3: Report consumers (tools/line_comment.py, anvil/statuspage.py, the swimlane renderer, the cli inspect path) keep working on reports written before this change, which carry no `checkpoint`, `exit_status` or `termination_reason` keys.

### R4. Regression tests
- R4.1: The order's tests are new files under tests/ that drive scripted runs through the runner with a fake runtime (no network, no real model). They cover: (a) a run killed at the run token cap in the middle of the builder station (S1); (b) a run ended by a station timeout and a run ended by an uncaught error injected into a station step (S2); (c) a healthy scripted run checkpointing after each station (S3); (d) a scripted run receiving SIGTERM (S5); plus the history preservation and legacy rendering of S4 and S7.
- R4.2: The full factory suite (python -m unittest discover -s tests -p 'test_*.py') passes with the new files added and no existing test file modified.

## Scenarios

### Scenario: A budget death leaves a complete report
- S1 (R2.1, R2.3, R2.4, R4.1a): Given a scripted sdlc-default run with max_run_tokens 6000000 whose fake runtime reports 6359529 measured tokens for the builder call, when the run dies at the cap, then report.json parses as JSON; exit_status is `budget_exceeded`; the record carries the consumption 6359529 and the cap 6000000; intake and spec-writer (and any other station before builder) carry their outcomes and executed models; builder is recorded as the station in flight with its measured partial usage; every station after builder is present with status `not_run`; and the fake runtime received no call after the builder call.

### Scenario: Timeout and error deaths are recorded the same way
- S2 (R2.1, R2.2, R2.3, R4.1b): Given one scripted run whose builder step exceeds its station timeout, and a second scripted run whose builder step raises RuntimeError("injected"), when each run ends, then each record satisfies every S1 completeness assertion except the budget fields; the first carries exit_status `station_timeout` with the station-timeout record fields unchanged on the builder step; the second carries exit_status `error` with termination_reason containing `RuntimeError` and `injected`; and the two exit_status values differ from each other and from `budget_exceeded`.

### Scenario: Checkpoints accumulate during a healthy run
- S3 (R1.1, R1.3, R4.1c): Given a healthy scripted run, when each station finishes, then the test, reading report.json after that station, finds checkpoint.last_completed_station equal to that station's id, checkpoint.elapsed_ms non decreasing across reads, and a step record for every station finished so far; and the final report equals the last checkpoint with only the verdict, decision and R2.2 exit fields added or changed, exit_status `completed`; the fake runtime's call count equals the count of model running stations.

### Scenario: Checkpoint writes are atomic
- S6 (R1.2, R2.5): Given a scripted run, when every checkpoint write completes, then report.json parses as JSON and no temporary file remains in runs/<work-order-id>/; and given a write that raises during the rename step, then the previous report.json content is unchanged on disk.

### Scenario: A killed run needs no second run for its accounting
- S4 (R3.1, R3.2, R4.1): Given the record left by the S1 budget death, when tools/line_comment.py and the swimlane renderer render it, then each returns output naming exit status `budget_exceeded` and the builder station with no station executing and the fake runtime receiving zero calls; and given a later run of the same work order, when it starts, then a file under runs/<work-order-id>/history/ is byte identical to the killed run's report.json and the new run's report.json is a different document.

### Scenario: Other stop paths complete the record
- S8 (R2.1, R2.2, R2.3): Given scripted runs ended respectively by the runtime turn limit, a checks gate stop, and an intake outcome of rejected, when each ends, then each record carries exit_status `turn_limit`, `checks_stopped` and `intake_stopped` respectively, a non empty termination_reason, and every unreached station as `not_run`.

### Scenario: An external kill still completes the record
- S5 (R2.1, R2.2, R4.1d): Given a scripted run in progress past at least one finished station, when the runner process receives SIGTERM, then report.json is completed with exit_status `signal`, termination_reason `SIGTERM`, the per-station outcomes as of the last finished station and the remaining stations as `not_run`; and the same holds for SIGINT with termination_reason `SIGINT`.

### Scenario: Old reports still render
- S7 (R3.3): Given a report.json written before this change (for example runs/wo-gh-20/report.json, which has no checkpoint, exit_status or termination_reason keys), when tools/line_comment.py, the status page and the swimlane renderer read it, then each renders without raising.

### Scenario: The suite stays green
- S9 (R4.2): Given the tree after the build, when python -m unittest discover -s tests -p 'test_*.py' runs, then it passes, and git diff against the base ref 4675a131eb9aa88097741dc3cdc9772c3db17550 shows no modified or deleted file among the test files present at that ref.

## Guardrails
- Python standard library only, consistent with the factory spine. No new dependency.
- The report schema grows additively (checkpoint object, exit_status, termination_reason, the `not_run` step status, the budget death fields). Existing keys keep their meaning.
- Frozen surfaces: cost-measurement semantics (totals are sums of measured steps only; unmeasured stays unmeasured and says why); the station-timeout record fields; the station artifact contract's executed model honesty; the review parse contract; the reviewer prompts; pipeline definition files under pipelines/ (protected in anvil.json); anvil.json itself (protected).
- Relationship to token-efficiency: its per-attempt usage artifacts and its rule that a budget stop preserves the report are inputs to this order, not replaced by it; this order generalizes preservation from the budget stop to every exit path and makes it a property of the runner.
- No em dash or en dash character in any produced file (project style rule).
- Nothing in this order merges, publishes or deploys anything; the run stops at the owner human gate.

## Allowed write set
- anvil/runner.py, anvil/line.py, anvil/telemetry.py, anvil/cost.py, anvil/executor.py
- anvil/cli.py (the resume and inspect paths only)
- tools/line_comment.py
- anvil/statuspage.py, only if needed for R3.3
- docs/EXECUTION.md and any other factory doc that describes run reports or resume
- CHANGELOG.md
- one new decision record under brain/decisions/ (next free number, 0013 at the time of writing)
- new test files under tests/
- the run's own artifacts under runs/wo-gh-41/
- No protected path changes are authorized: no edit to anvil.json, to any file under pipelines/, or to any test file present at the base ref.

## Out of scope
- Resuming execution from a checkpoint (re-dispatching from the last completed station). This order makes the record readable after a kill; it does not add automatic resume of execution.
- Per-station token partitions and the pre-review completeness gate (wo-gh-42, station-budgets-completeness).
- Changes to cost-measurement semantics, price tables, the station-timeout fields, review parsing or reviewer prompts.
- Untrappable kills (SIGKILL, host loss): for these the last R1 checkpoint is the record; no completion is required.
- Any change to the C64 project or its runs; the evidence there motivates this order but is not edited.

## Builder report required literals
- runs/wo-gh-41/builder.output.md contains, in full: 4675a131eb9aa88097741dc3cdc9772c3db17550, continuous-run-accounting, checkpoint, budget_exceeded; the base ref the tree was verified against; the exact full factory test count from the suite run; and the names of the new test files.
