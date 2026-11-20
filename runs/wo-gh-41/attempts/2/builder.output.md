# Builder report: wo-gh-41 (continuous-run-accounting), loopback attempt 2

## Status: BLOCKED on a spec conflict with a protected test. No code change this attempt.

The checks gate sent this order back for one failing test:
`test_governed_delivery.TestLiveState.test_crash_and_stall_are_visible_s1`.
That test cannot pass on any tree that meets this spec unless a protected file is edited or the code special cases it. I did neither.

### The conflict
- `tests/test_governed_delivery.py:113` is present at base ref 4675a131eb9aa88097741dc3cdc9772c3db17550, so it is protected. It drives `run_pipeline` on the short line (intake, test-writer, builder, ...). The executor raises `RuntimeError` in builder. The test then asserts `self.assertFalse((h.proj / "runs/wo-crash/report.json").exists())`.
- The continuous-run-accounting spec requires the opposite:
  - R1.1 writes a checkpoint to runs/<work-order-id>/report.json after intake and after test-writer, which both finish before builder raises.
  - R2.1/R2.2 complete that record with exit_status `error` on an uncaught exception.
  - The new test `test_s2_injected_error_death` in tests/test_continuous_run_accounting.py asserts exactly this. It uses the same kind of executor (`RuntimeError` in builder) through the same `run_pipeline` entry point.
- No legitimate input separates the two cases. The only differences are the pipeline, a dict versus a `WorkOrder`, and executor attributes. Branching on any of them would special case a test, which implementation-craft forbids.
- The rest of that old test still passes on this tree. state.json says `crashed` with `current_station` builder, the error names `RuntimeError`, the exception still propagates, the last event is `run.crashed`, and stall detection works. The governed-delivery spec's own R1 does not require report.json to be absent. Only that one line conflicts.
- The test-writer (runs/wo-gh-41/test-writer.output.md) and the previous builder attempt reported the same conflict. The spec revision in this loop did not resolve it: it still says "No protected path changes are authorized" and R4.2 still requires the full suite to pass.

### What the owner must decide (one of)
1. Authorize a one line change to `tests/test_governed_delivery.py:113`: drop the assertion, or invert it to `assertTrue(... report.json exists)` with exit_status `error`. The rest of the tree then passes as is.
2. Amend the continuous-run-accounting spec to exempt the uncaught exception path from R1.1/R2.1. That would contradict the work order's R2 and leave the wo-gh-6 failure mode partly open, so I do not recommend it.

## What is on the tree (from attempt 1, kept unchanged)
Files changed by this order, all inside the authorized write set:
- `anvil/runner.py`:
  - atomic checkpoint of report.json after every station, written as a sibling temporary file and then renamed, with the `checkpoint` object (`last_completed_station`, `elapsed_ms`, `usage_so_far`) (R1.1, R1.2, R1.3; S3, S6)
  - completion on every exit path, with `exit_status` from the closed set and `termination_reason` (R2.1, R2.2; S1, S2, S8)
  - `not_run` for unreached stations, and the budget death's measured partial usage and cap (R2.3, R2.4; S1)
  - SIGTERM/SIGINT handlers that complete the record (S5)
  - stderr report when the write fails, with the last checkpoint kept (R2.5; S6)
  - the swimlane renders killed and legacy records (R3.1, R3.3; S4, S7)
- `anvil/line.py`: preserves the earlier report.json in history before the first checkpoint of a new run (R3.2; S4).
- `tools/line_comment.py`: renders exit_status/termination_reason and tolerates legacy reports (R3.1, R3.3; S4, S7).
- `docs/EXECUTION.md`, `CHANGELOG.md`, `brain/decisions/0013-continuous-run-accounting.md`: docs and the decision record.
- New test file: `tests/test_continuous_run_accounting.py` (19 tests, S1 to S9), written by test-writer. This attempt adds no new test files.

No edits to anvil.json, pipelines/, or any test file present at the base ref. No new dependency. Checked with grep: no em dash or en dash in any changed file.

## Verification (final tree, HEAD 17dab24d86d430320d326ca88abc8d6984f92085)
Base ref verified against: 4675a131eb9aa88097741dc3cdc9772c3db17550 (`git merge-base --is-ancestor` confirms it is an ancestor of HEAD). Changes to test files between the base ref and HEAD come only from main merges. The S9 test checks that no base ref test file is modified in the working tree, and it passes.

- `python -m unittest tests.test_continuous_run_accounting` gave `Ran 19 tests in 1.047s` / `OK`.
- `env -u GITHUB_ACTIONS -u GITHUB_ACTOR -u GITHUB_ACTOR_ID python -m unittest discover -s tests -p 'test_*.py'` (the gate's environment) gave `Ran 760 tests in 82.784s` / `FAILED (failures=1, skipped=6)`. The one failure is `test_crash_and_stall_are_visible_s1`, the conflict above.
- Full factory test count: 760.
- In this station's own shell, GITHUB_ACTOR is set, so the plain command shows 5 more approval identity failures (test_autonomous_line x3, TestApprovalPolicy x2). Those come from the environment and are not caused by this order; they do not occur with the variables unset, as above.
- I exercised the change through the scripted runs in the new tests:
  - a budget death at the 6000000 cap with builder measured at 6359529 gives exit_status budget_exceeded
  - timeout, error, signal, turn limit, checks and intake stops each leave their own complete record
  - line_comment and the swimlane render the killed record with zero runtime calls

## Unmet / open
- R4.2 / S9 (full suite passes with no existing test file modified) is UNMET because of the conflict above. Every other scenario, S1 to S8, is covered by passing tests.
- I did not run the cli inspect/resume paths by hand beyond what the tests cover.
{"model": "claude-opus-5-5"}
