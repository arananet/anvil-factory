# Builder report: wo-gh-41 (continuous-run-accounting)

## Summary
The spine change for continuous-run-accounting was already on branch anvil/wo-gh-41 from the earlier attempt of this order (the attempt that died with budget_exceeded before writing this report, which is the defect this order closes). This pass read the spec, the tests and the full diff against origin/main, verified each requirement against the code, ran the new tests and the full suite, and ran a budget death by hand. The diff needed no code changes, so this pass changed no code. One spec scenario (S9 / R4.2) cannot be met because of a conflict with a protected existing test. Details are below; the owner must decide.

Base refs:
- Order parent ref: 4675a131eb9aa88097741dc3cdc9772c3db17550
- Tree verified against: origin/main (17dab24 merges origin/main into this branch)
- Write set check: `git diff --stat origin/main HEAD` touches only allowed files: anvil/runner.py, anvil/line.py, tools/line_comment.py, docs/EXECUTION.md, CHANGELOG.md, brain/decisions/0013-continuous-run-accounting.md and tests/test_continuous_run_accounting.py. Other files that differ from 4675a131eb9aa88097741dc3cdc9772c3db17550 (for example anvil/config.py and tools/claude_station.py) came in through main merges, not through this order.

## What changed, by scenario
- **R1.1 / R1.3 / S3**, `anvil/runner.py`:
  - New `RunAccounting.checkpoint()` writes report.json after every station, in the final report's shape plus a `checkpoint` object (`last_completed_station`, `elapsed_ms`, `usage_so_far` via `summarize_steps`).
  - The final report is the last checkpoint plus the verdict, decision and exit fields.
  - Checkpointing adds no station and no model call.
- **R1.2 / R2.5 / S6**, `write_report_atomic()`:
  - Writes with mkstemp in the same directory, then fsync, then `os.replace`.
  - On failure the temporary file is removed, the previous report.json is left unchanged and the reason is printed on stderr.
- **R2.1 / R2.2 / R2.3 / S2 / S5 / S8**:
  - `run_pipeline` traps SIGTERM and SIGINT (as `RunSignal`) and catches every exception. `record_exit()` then completes the record with `exit_status` (`error` or `signal`), `termination_reason`, the in-flight station and every unreached station as `not_run`.
  - `_station_stop()` ends the line on a crossed cap (`budget_exceeded`), a station timeout (`station_timeout`, timeout record fields unchanged) or the turn limit (`turn_limit`).
  - A failed pre-review gate with no loopback left ends the line with `checks_stopped`. An intake stop ends it with `intake_stopped`.
  - Normal completion ends with `completed`.
- **R2.4 / S1**: the `budget_death` section carries the limit, measured_tokens, max_run_tokens, station_in_flight and station_usage. When the runtime exposed no usage, it carries a `station_usage_reason` instead.
- **R3.1 / R3.3 / S4 / S7**:
  - `render_swimlane(report)` is a pure function of the report, and every key is optional.
  - `tools/line_comment.py` prints the exit status and termination reason, or the last checkpoint when no exit status was recorded.
  - `anvil/line.py` `load_resume` names a killed run's exit status and refuses to resume it.
  - Reports without the new keys render as before.
- **R3.2 / S4**: the existing content-addressed copy into runs/<id>/history/ runs before the first checkpoint of the new run (runner.py, before `RunAccounting` is wired).
- **Docs and decision**: docs/EXECUTION.md, CHANGELOG.md and brain/decisions/0013-continuous-run-accounting.md.

## New test files
- tests/test_continuous_run_accounting.py (19 tests, S1 to S9; written by the test-writer station, unchanged here)

## Verification (real output, final tree)
- `python -m unittest tests.test_continuous_run_accounting`: `Ran 19 tests in 0.853s` / `OK`
- `python -m unittest discover -s tests -p 'test_*.py'` as given in this station's environment: `Ran 760 tests in 80.322s` / `FAILED (failures=6, skipped=6)`
  - test_autonomous_line.TestHumanGate (3 tests) and test_governed_delivery.TestApprovalPolicy (2 tests) fail because this process sets GITHUB_ACTOR and other CI variables. They fail the same way on a clean origin/main worktree here: `Ran 32 tests` / `FAILED (failures=5)` for those two files.
  - test_governed_delivery.TestLiveState.test_crash_and_stall_are_visible_s1: see the open issue below.
- The same suite with every ANVIL_* and GITHUB_* variable unset: `Ran 760 tests in 84.179s` / `FAILED (failures=1, skipped=6)`. The one failure is test_crash_and_stall_are_visible_s1.
- Full factory test count: 760.
- By hand, I scripted a run that dies at the cap mid-builder (fake runtime, 6359529 builder tokens, cap 6000000) and then rendered its record. Results:
  - report.json parses.
  - exit_status is budget_exceeded, with termination_reason "run token cap crossed in station builder: measured 6359859 tokens against max_run_tokens 6000000".
  - budget_death.station_in_flight is builder, with station_usage {input 6300000, output 59529}.
  - intake, spec-writer and test-writer are executed. builder is failed. All 11 later stations are not_run.
  - tools/line_comment.render and render_swimlane both print the exit status and the reason without running anything.
- Dash check: none of the files this order produced contains an em dash or an en dash. The only hit in the branch diff is the runner-generated runs/wo-gh-41/reviewer-ux.packet.md.

## Unmet / open (owner decision needed)
- **S9 / R4.2 is unmet because of a spec conflict.**
  - tests/test_governed_delivery.py:113 is present at the base ref and protected. It asserts that a run whose builder raises leaves no runs/wo-crash/report.json.
  - R1.1 (a checkpoint after every station) and R2.1 (the record is completed on an uncaught exception) require that file to exist.
  - No build can satisfy both.
  - The other assertions in that test still hold: crashed state, current_station builder, the RuntimeError propagating, and run.crashed as the last event.
  - I did not edit the test and did not special case it.
  - The owner must either authorize removing or inverting that one assertion, or amend the spec. Decision 0013 records this.
- R2.4 when the runtime exposes no usage: the code covers it (station_usage null plus a reason), but no scripted test does.
- The rescoped intake stop and the pre-deploy gate stop have no dedicated tests. The rejected and waiting_info intake stops and the pre-review gate stop are tested.
- The `anvil runs` inspect path goes through anvil/observe.py, which is outside the write set and was not changed. Resume (`load_resume`) is covered.
- Not changed by this order: when a reviewer times out, the run now ends (decision 0013, Consequences). That is stricter than the earlier line.
{"model": "claude-opus-5-5"}
