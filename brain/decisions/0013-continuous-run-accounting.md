# 0013: The run record is checkpointed after every station and completed on every exit

Status: accepted 2026-11-20, work order wo-gh-41, spec continuous-run-accounting.

## Context

report.json was written once, at the end of `_run_pipeline`. A run that died
before that line (wo-gh-6 in the C64 chain, killed at the 6000000 token cap
mid-builder) left no accounting, and a second run (wo-gh-7) was spent writing
paperwork for work that already existed.

## Decision

- `anvil/runner.py` owns one `RunAccounting` per run. After every station the
  runner writes report.json in its final shape plus a `checkpoint` object,
  through a sibling temporary file and `os.replace`.
- `run_pipeline` traps SIGTERM and SIGINT for the length of the run (main
  thread only) and turns any exception or signal into a completed record with
  `exit_status` and `termination_reason`, the in-flight station and every
  unreached station as `not_run`. The exception still propagates; a signal
  leaves as KeyboardInterrupt (SIGINT) or exit code 128 plus the signal number.
- A run token cap crossed by a station, a station timeout, the runtime turn
  limit and a failed pre-review gate with no attempt left now end the line at
  that station. Before this, the line ran the deterministic stations after an
  overspent builder, and reviewers (as skipped), approver and observer after a
  timeout or a failed gate.
- The swimlane renderer is `render_swimlane(report)`, a function of the report
  alone, so a killed run renders without a run.

## Consequences

- A killed run's accounting exists without a second run; for SIGKILL the last
  checkpoint is the record.
- A run that raises now leaves a report.json (exit_status error). The
  governed-delivery test `test_crash_and_stall_are_visible_s1` asserted the
  opposite; that assertion conflicts with R1 of this spec and is reported to
  the owner rather than edited (existing tests are protected for this order).
- A reviewer that times out ends the run instead of being left uncounted.
  This is stricter than before and costs a re-run where the earlier line would
  have produced an incomplete panel verdict.
- One extra JSON write per station; no model call and no station is added.
