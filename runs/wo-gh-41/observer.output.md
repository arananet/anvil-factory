# Observer: wo-gh-41 (continuous-run-accounting)

## Summary
Nothing was released. No release record exists. The deployer station is `packet_ready`, and `runs/wo-gh-41/deployer.output.md` was never written. The change never passed the checks gate: all three builder attempts failed it, all six reviewers were skipped, and the run reached the owner human gate with verdict `no_reviews`. This report covers what was observed in the run. It does not cover a release.

## Missing input
- Release record (the deployer output). Not produced. Nothing was merged, published or deployed. That matches the order's guardrail that the run stops at the owner human gate.

## What happened (run 51d802ce7e4740e4a38bd90cb02ba1f0, state.json and events.jsonl)
- intake, spec-writer, test-writer: executed.
- builder attempts 1, 2, 3: executed.
- checks-gate attempts 1, 2, 3: failed. Each time `python -m unittest discover -s tests -p 'test_*.py'` reported `Ran 760 tests ... FAILED (failures=1, skipped=6)`.
- loopbacks: 2 of 2 used.
- reviewer-spec, -security, -tests, -architecture, -design, -ux: skipped.
- approver, triage-human: completed. deployer: packet_ready.
- state.json still shows `state: running` with `current_station: observer`.

## The single persistent failure
`test_governed_delivery.TestLiveState.test_crash_and_stall_are_visible_s1`, at `tests/test_governed_delivery.py:113`:
`self.assertFalse((h.proj / "runs/wo-crash/report.json").exists())`

This existing test is protected at base ref 4675a131eb9aa88097741dc3cdc9772c3db17550. It requires that a crashed run leave no report.json. The continuous-run-accounting spec requires the opposite: R1 checkpoints report.json after every station, and R2 requires a completed record with exit status `error` when an uncaught exception occurs. Code that satisfies the spec cannot pass this assertion. The work order's statement "No active spec conflicts" was therefore wrong. The builder (attempt 3) and the test-writer both reported this conflict. Loopbacks could not resolve it, because the fix needs a decision outside the builder's authorized surface. All three attempts failed for the same reason, so the two loopbacks spent tokens without changing the outcome.

## Delivered on the branch (unreviewed)
Diff against main: anvil/runner.py (+463/-62 overall), anvil/line.py, tools/line_comment.py, docs/EXECUTION.md, CHANGELOG.md, brain/decisions/0013-continuous-run-accounting.md, and the new test file tests/test_continuous_run_accounting.py (19 tests, which the builder reports as passing). The builder exercised a scripted budget death and reports that `tools/line_comment.py` rendered `Exit status: budget_exceeded` with the builder `failed` and later stations `not_run`. The observer did not reproduce that output. No reviewer has validated any of this work.

## Record integrity observations
- `runs/wo-gh-41/report.json` is stale. Its run_id is 6fc43cc391534641a9fdf48ab5053bab and its verdict is `budget_exceeded`, from the earlier run in commit 5f698fb. This run (51d802ce...) has not written its own report.json. That is the exact gap this order is meant to close, observed on the factory itself.
- The working tree has uncommitted edits to `.openspec/specs/continuous-run-accounting/spec.md` (4 lines) and `tests/test_continuous_run_accounting.py` (29+/8-). The spec edit is outside the builder's authorized surface. It should be inspected before any merge.
- `runs/wo-gh-41/observer.output.md.usage.json` shows as deleted in git status.

## Owner decision required (carried from builder report)
1. Authorize a one-line change at `tests/test_governed_delivery.py:113`: drop the assertion, or invert it to require a completed record with exit_status `error`. Then rerun the gate and the reviewers. Or:
2. Amend the spec so that an uncaught exception leaves no report.json. This contradicts R2/S2 and the purpose of the order.

Recommendation: option 1. The test's other assertions (crashed state, run.crashed event, the exception propagating, stall detection) are unaffected. The governed-delivery spec does not require that report.json be absent.

## Known gaps stated by the builder
- No scripted test for the R2 branch where the in-flight station's usage is unmeasured (with its reason).
- No dedicated tests for the intake rescoped stop or the pre-deploy checks stop.
- The `anvil runs` inspect path reads through anvil/observe.py. That file is outside the write set, so the path is untested for R3.
{"model": "claude-opus-5-5"}
