# Builder report: wo-gh-41 (continuous-run-accounting), attempt 3 of 3

## Summary
The continuous-run-accounting implementation from the earlier attempts is on this branch and satisfies every spec scenario S1 to S8. All 19 tests in the new file pass. The full factory suite has one remaining failure. It is not a defect in this change. It is a direct conflict between this spec and a protected existing test, and no honest build can resolve it from inside the authorized write set (details under "Unmet"). This attempt made no code change, because the only change that would turn the suite green is one to a protected test, or code that special-cases that test's inputs. I refused both.

## Base refs
- Spec base ref: 4675a131eb9aa88097741dc3cdc9772c3db17550 (the order's parent; its test files are the protected set).
- Tree verified: HEAD 17dab24d86d430320d326ca88abc8d6984f92085 (branch anvil/wo-gh-41, origin/main merged in). The diff summarized below is `origin/main...HEAD`.

## What changed and which scenario it serves
- `anvil/runner.py`
  - `write_report_atomic`: writes a sibling temporary file, then `os.replace`. If the write fails, the previous report.json stays on disk unchanged and the reason goes to stderr. (R1.2, R2.5, S6)
  - `RunAccounting.checkpoint`: writes report.json after every station that completes, fails, times out or is skipped. The report has the final shape plus a `checkpoint` object {last_completed_station, elapsed_ms, usage_so_far}. It adds no station and makes no model call. (R1.1, R1.3, S3)
  - `RunAccounting.record_exit`, `EXIT_STATUSES`, `_budget_death`, `_station_stop`, `_not_run_steps`: complete the record on every exit path. Each path sets `exit_status` from the closed set and a `termination_reason`. Stations that never ran are listed with status `not_run`. A budget death records the measured consumption, the cap and the in-flight station with its partial usage. Cost-measurement semantics are unchanged. (R2.1 to R2.4, S1, S2, S8)
  - `RunSignal`, `_install_signal_handlers` / `_restore_signal_handlers`: SIGTERM and SIGINT become a completed record with exit_status `signal`. (S5)
  - `render_swimlane`: renders from report.json alone. History preservation runs before the new run writes its first checkpoint. (R3.1, R3.2, S4)
- `anvil/line.py` `load_resume`: a killed run's record (any exit_status other than completed, with no approval) is reported as the run's accounting, with nothing to resume. (R3.1)
- `tools/line_comment.py`: renders Exit status and Termination reason when present. A checkpoint-only record shows its last checkpoint. Legacy reports render as before. (R3.1, R3.3, S4, S7)
- `docs/EXECUTION.md`, `CHANGELOG.md`, `brain/decisions/0013-continuous-run-accounting.md`: describe the checkpoint, the exit paths and the decision.
- New test file: `tests/test_continuous_run_accounting.py` (19 tests, scenario ids in the method names). This is the only new test file.

## Verification (real output, final tree)
- `python -m unittest tests.test_continuous_run_accounting` gave `Ran 19 tests ... OK`.
- `python -m unittest discover -s tests -p 'test_*.py'` with this shell's environment gave `Ran 760 tests ... FAILED (failures=6, skipped=6)`. Five of the six come from the environment: GITHUB_ACTOR=arananet is set here, so the approval identity tests in test_autonomous_line (3) and test_governed_delivery.TestApprovalPolicy (2) refuse the test identity. Those tests do not touch this change.
- Same command with GITHUB_ACTOR, GITHUB_ACTIONS and ANVIL_* unset gave `Ran 760 tests ... FAILED (failures=1, skipped=6)`. The exact full factory test count is 760. The one failure is `test_governed_delivery.TestLiveState.test_crash_and_stall_are_visible_s1`.
- Exercised as a user would: I ran the S1 scripted budget death and then ran `tools/line_comment.py <report.json> 3` on the record it left. Output: `Exit status: budget_exceeded`, `Termination reason: run token cap crossed in station builder: measured 6359859 tokens against max_run_tokens 6000000`, builder recorded as failed with its executed model. Every station after builder is `not_run`.
- No em dash or en dash character in any changed file (grep over the diff came back empty).

## Unmet: spec conflicts with a protected test (owner decision required)
`tests/test_governed_delivery.py:113` is present at base ref 4675a131eb9aa88097741dc3cdc9772c3db17550 and is protected. It is unchanged on current origin/main. It asserts `assertFalse((h.proj / "runs/wo-crash/report.json").exists())` after a run whose builder raises RuntimeError. This spec requires the opposite:
- R1.1: report.json is checkpointed after intake and test-writer finish, which happens before builder runs.
- R2.1 and S2: an uncaught error in a station step must leave a completed report.json with exit_status `error`.

So R4.2 ("full suite passes with no existing test file modified") cannot hold together with R1.1/R2.1. The other assertions in that test still pass: state `crashed`, current_station `builder`, error text, the `run.crashed` event, the exception propagating, and stall detection. The governed-delivery spec does not require report.json to be absent. Only that one assertion conflicts. The test-writer station raised the same finding. I did not edit the protected test, and I did not add any code that tells the two cases apart, because that would mean special-casing test inputs.

The owner must choose one:
1. Authorize a one-line change to `tests/test_governed_delivery.py:113`: drop the assertion, or invert it to require a completed record with exit_status `error`.
2. Amend the spec so an uncaught exception leaves no report.json. That contradicts S2 and the purpose of this order.

## Other gaps (carried from earlier attempts, stated plainly)
- R2.4's "unmeasured with its reason" branch for the in-flight station has no scripted test. A fake runtime cannot cross the cap without reporting usage.
- The rescoped intake stop and a pre-deploy gate checks stop have no dedicated test. Rejected, waiting_info and the checks gate stop are tested.
- The R3.1 cli inspect path (`anvil runs`) reads through anvil/observe.py, which is outside the write set. It is not changed or tested here. statuspage.py did not need changes for R3.3.
- No visual deliverable. The Quality Charter (physical_product) does not apply to this non-visual change, so no comparison record was produced.
{"model": "claude-opus-5-5"}
