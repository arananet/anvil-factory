# Builder report: wo-gh-41 (continuous-run-accounting)

## Summary
The continuous-run-accounting implementation from the earlier attempts of this order is on the branch. It satisfies spec scenarios S1 to S9 on the final tree. The one blocker from attempt 3 was `tests/test_governed_delivery.py:113`, which asserted that a crashed run leaves no report.json. It is gone: owner-authorized operator commit 5354c7130e116658cc31dec270738ffaf2de67d6 changed that test on main, and that commit is merged into this branch. I re-read the full implementation diff as a reviewer and found nothing to change, so this attempt makes no code change. Rewriting working, tested code would only add risk.

## Base refs
- Parent ref of the order: 4675a131eb9aa88097741dc3cdc9772c3db17550.
- Base ref I verified the tree against: 5354c7130e116658cc31dec270738ffaf2de67d6, which is `git merge-base HEAD origin/main`, the merge base named in R4.2 and S9.
- Tree verified: HEAD 11526561000e3fe11d3cfa7e8c0c04bf178effd7 (branch anvil/wo-gh-41) plus this station's run artifacts.

## What changed (diff 5354c71..HEAD, outside runs/) and which scenario each change serves
- `anvil/runner.py`
  - `write_report_atomic` writes report.json to a sibling temporary file (`tempfile.mkstemp` in the run dir, then fsync and `os.replace`). If the write fails, the temporary file is removed, the previous report.json stays unchanged and the reason goes to stderr. (R1.2, R2.5, S6)
  - `RunAccounting.checkpoint` runs after every station that completes, fails, times out or is skipped. It writes the report in the final shape plus `checkpoint` {last_completed_station, elapsed_ms, usage_so_far}. `usage_so_far` is `summarize_steps(steps)`. It adds no station and no model call. (R1.1, R1.3, S3)
  - `EXIT_STATUSES`, `_station_stop`, `_budget_death` and `_not_run_steps`, plus the `stop` record in `_run_pipeline`, give every exit path its own `exit_status` from the closed set and a `termination_reason`. Every unreached station is recorded as `not_run`. A budget death records the measured tokens, the cap, the station in flight and that station's partial usage, or an explicit reason when the runtime exposed no usage. Cost-measurement semantics are unchanged: `RunReport.to_dict` still builds the cost section from measured steps only. (R2.1 to R2.4, S1, S2, S8)
  - `RunAccounting.record_exit` and the `run_pipeline` wrapper complete the record for an uncaught exception (`error`) and for SIGTERM/SIGINT (`signal`, via `RunSignal` and `_install_signal_handlers`). The in-flight station's honest executed model is recorded only while the runtime is actually being called. After the record is written, the wrapper still marks state crashed (governed-delivery S1 kept) and re-raises. (R2.1, R2.2, S2, S5)
  - `render_swimlane(report)` renders from a report dict alone and tolerates legacy reports. History preservation still runs before the first checkpoint of a new run. (R3.1, R3.2, R3.3, S4, S7)
- `anvil/line.py` `load_resume`: when a run ended with any exit_status other than `completed` and has no approval, it reports the killed run's record as the run's accounting and says there is nothing to resume. (R3.1)
- `tools/line_comment.py`: shows Exit status and Termination reason when present, and shows the last checkpoint for a checkpoint-only record. Legacy reports render as before. (R3.1, R3.3, S4, S7)
- `docs/EXECUTION.md`, `CHANGELOG.md`, `brain/decisions/0013-continuous-run-accounting.md` document the checkpoint, the exit paths and the decision.
- New test file (the only one): `tests/test_continuous_run_accounting.py`, 19 tests with scenario ids in the method names.

## Verification (real output, final tree)
- `python -m unittest tests.test_continuous_run_accounting` gave `Ran 19 tests in 0.727s` and `OK`.
- Full factory suite, `python -m unittest discover -s tests -p 'test_*.py'`, run with GITHUB_ACTOR, GITHUB_ACTIONS and GITHUB_ACTOR_ID unset: `Ran 760 tests in 69.750s`, `OK (skipped=6)`. The exact full factory test count is 760 (741 at the base ref plus 19 new).
- The same command in this shell's raw CI environment gave `Ran 760 tests in 68.030s`, `FAILED (failures=5, skipped=6)`. All five are approval identity tests: test_autonomous_line.TestHumanGate (test_approval_rules_s4, test_approve_and_resume_deploys_s4, test_publisher_held_until_approved_s5) and test_governed_delivery.TestApprovalPolicy (test_identity_and_policy_s5, test_policy_comes_from_the_operator_checkout_s5). They fail because this runner sets GITHUB_ACTOR, so `--by` identities are refused. They fail the same way at the base ref, do not touch this change, and are protected. The checks gate's own pre-review run showed only the governed-delivery failure, which commit 5354c71 has since fixed.
- S9 guard: `git diff --name-status --diff-filter=MD 5354c7130e116658cc31dec270738ffaf2de67d6 -- tests` is empty. `--diff-filter=A` lists only `tests/test_continuous_run_accounting.py`.
- Write set: `git diff --stat 5354c71 -- . ':!runs'` touches only anvil/runner.py, anvil/line.py, tools/line_comment.py, docs/EXECUTION.md, CHANGELOG.md, brain/decisions/0013-continuous-run-accounting.md and the new test file. Nothing under pipelines/ and no change to anvil.json.
- No em dash or en dash in the added lines (grep over the diff came back empty).
- Exercised as a user would: I ran a scripted sdlc-default run (the test module's fake runtime, the real runner) where the builder call crosses the cap. Results:
  - Runtime calls: `['intake', 'spec-writer', 'test-writer', 'builder']`. Nothing was called after the builder.
  - Record: `exit_status: budget_exceeded`, `termination_reason: run token cap crossed in station builder: measured 6359859 tokens against max_run_tokens 6000000`.
  - `budget_death` carries station_in_flight `builder` and station_usage {input_tokens 6300000, output_tokens 59529}.
  - The three upstream stations are `executed`, builder is `failed`, and checks-gate through observer are `not_run`.
  - `tools/line_comment.py <report.json> 3` rendered that record with `Exit status: budget_exceeded`, the termination reason and the per-station table, with no station executing.

## Unmet, unverified or open
- No scripted test covers the R2.4 branch where the in-flight station is unmeasured with a reason (`station_usage_reason`). A fake runtime cannot cross the cap without reporting usage. The code path exists in `_budget_death`.
- A rescoped intake does not stop the sdlc-default line. The run continues on the rescoped description, so no separate rescoped stop path exists to record. Rejected and waiting_info stops are tested. The pre-deploy gate stop (`checks_stopped` with no further loopback) is implemented, but only the pre-review gate stop has a dedicated test.
- The cli inspect path (`anvil runs`) reads through anvil/observe.py, which is outside the write set. It is not changed here. The resume path (`anvil/line.py load_resume`) is changed. anvil/statuspage.py needed no change for R3.3, and S7 shows it renders a legacy report.
- Untrappable kills (SIGKILL) are out of scope. For those, the last checkpoint is the record.
- The Quality Charter in the packet (physical_product) does not apply to this non-visual change, so no comparison record was produced.
{"model": "claude-opus-5-5"}
