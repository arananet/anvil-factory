# Test writer: wo-gh-41 (continuous-run-accounting)

## Files
- tests/test_continuous_run_accounting.py (new file of this order; at base ref 4675a131eb9aa88097741dc3cdc9772c3db17550 it does not exist). The earlier attempt of this order wrote it; this pass reused it and made two edits:
  - added `test_s8_intake_waiting_info_stop` (S8, the intake waiting_info stop path of R2.1);
  - narrowed `test_s9_existing_test_files_untouched` to the test files present at the base ref. It used to flag any change under tests/ against HEAD, so it failed on this order's own new file.

No existing test file was modified or deleted (`git diff --name-status HEAD -- tests` lists only the new file).

## How the tests exercise the real artifact
Every death and checkpoint test drives the real `anvil.runner.run_pipeline` on the real `pipelines/sdlc-default.json` with a scripted fake runtime that records each call (no network, no model). Signal tests run the runner in a child process and send it a real SIGTERM or SIGINT while the builder is in flight. Atomic write tests wrap `os.replace` and `os.rename` to observe each write onto report.json. The runner is never mocked. Rendering tests call the real `tools/line_comment.render`, `anvil.statuspage.render_status_page` and `anvil.runner.render_swimlane`.

## Scenario map
| Scenario | Test(s) |
|---|---|
| S1 | test_s1_budget_death_mid_builder_leaves_complete_report |
| S2 | test_s2_station_timeout_death_is_recorded, test_s2_uncaught_error_death_is_recorded, test_s2_timeout_and_error_statuses_differ |
| S3 | test_s3_checkpoints_accumulate_during_healthy_run, test_s3_final_report_is_last_checkpoint_plus_verdict |
| S4 | test_s4_killed_record_renders_without_a_run, test_s4_later_run_preserves_killed_record_in_history |
| S5 | test_s5_sigterm_completes_the_record, test_s5_sigint_completes_the_record |
| S6 | test_s6_checkpoint_writes_are_atomic, test_s6_failed_rename_keeps_previous_report |
| S7 | test_s7_legacy_report_still_renders (runs/wo-gh-20/report.json) |
| S8 | test_s8_turn_limit_stop, test_s8_checks_gate_stop, test_s8_intake_rejected_stop, test_s8_intake_waiting_info_stop |
| S9 | test_s9_existing_test_files_untouched, test_s9_no_dashes_in_this_file |

## Fail before build, for the right reason
The spine code from the earlier attempt is already on this branch, so the new tests pass on the current tree (19 of 19 OK). To show they can fail, I ran them on a copy of the tree with anvil/ and tools/ restored to base ref 4675a131eb9aa88097741dc3cdc9772c3db17550. Result: `Ran 19 tests ... FAILED (failures=17, skipped=1)`. Every failure is missing behaviour, not an import error: exit_status is None, the run left no report.json, no checkpoint was written, report.json was never written by rename, and there is no render_swimlane. In that copy the S9 git check skipped (no .git), and the dash check passed.

## Project check (real results, current tree)
- Baseline before this pass: 18 tests in this file. The earlier attempt's handoff recorded a factory baseline of 741 tests without the file.
- As given, `python -m unittest discover -s tests -p 'test_*.py'`: `Ran 760 tests ... FAILED (failures=6, skipped=6)`.
  - 5 of the 6 come from the environment: test_autonomous_line (3) and test_governed_delivery TestApprovalPolicy (2). This station's process sets GITHUB_ACTOR, so the approval identity checks refuse the test identity.
- With the ANVIL_* and GITHUB_* variables cleared: `Ran 760 tests ... FAILED (failures=1, skipped=6)`. The remaining failure is the finding below.

## Finding: the spec conflicts with a protected existing test
`tests/test_governed_delivery.py:113` (`TestLiveState.test_crash_and_stall_are_visible_s1`, present at the base ref, protected) asserts that a run whose builder raises leaves **no** `runs/wo-crash/report.json`. This spec requires the opposite: R1.1 checkpoints report.json after every station, and R2.1 completes the record on an uncaught exception. Any build that satisfies this spec fails that assertion. So R4.2 / S9 ("full suite passes with no existing test file modified") cannot be met as written. The governed-delivery spec R1 itself does not require the absence of report.json (it requires state.json to say crashed and the exception to propagate, and both still hold). The work order's statement "No active spec conflicts" therefore misses this test. I did not weaken or edit it. The owner must decide: authorize a one line change to that protected test (drop or invert the report.json assertion), or amend this spec.

## Not covered, and why
- R2.4 unmeasured in-flight usage: a fake runtime cannot cross the cap without reporting usage, so the "unmeasured with its reason" branch has no scripted test.
- R2.1 rescoped intake stop and a pre-deploy gate checks stop: no dedicated test. Rejected and waiting_info, and the checks gate with no loopback left, are covered.
- R3.1 cli inspect path: `anvil runs` reads through anvil/observe.py, which is outside the allowed write set. That path is not tested here.
- S9 literal base ref diff: main has modified several test files since 4675a131eb9aa88097741dc3cdc9772c3db17550, so the S9 test diffs those base-ref files against HEAD instead.
{"model": "claude-opus-5-5"}
