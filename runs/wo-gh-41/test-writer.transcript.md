The tests for wo-gh-41 are in place, one or more for each scenario S1 to S9. They fail against main for the right reason. In this CI environment the full project check reports 5 failures. Those 5 also fail on unchanged main, and the suite passes once the runner's GitHub identity variables are unset.

**Test file:** `tests/test_continuous_run_accounting.py`, 19 tests. An earlier attempt of this order had already written it, and I reused it after checking each test against S1 to S8. I rewrote only the S9 test, to match the revised spec. It now finds the merge base of the branch with main when it runs (`5354c71` today), and checks that `git diff --diff-filter=MD` from there to the working tree lists nothing under `tests/`. The old version only diffed against HEAD, so it missed edits that had already been committed. No existing test file was modified or deleted.

| Scenario | Tests |
|---|---|
| S1 | `test_s1_budget_death_mid_builder_leaves_complete_report` |
| S2 | `test_s2_station_timeout_death_is_recorded`, `test_s2_uncaught_error_death_is_recorded`, `test_s2_timeout_and_error_statuses_differ` |
| S3 | `test_s3_checkpoints_accumulate_during_healthy_run`, `test_s3_final_report_is_last_checkpoint_plus_verdict` |
| S4 | `test_s4_killed_record_renders_without_a_run`, `test_s4_later_run_preserves_killed_record_in_history` |
| S5 | `test_s5_sigterm_completes_the_record`, `test_s5_sigint_completes_the_record` (sends a real signal to a child process) |
| S6 | `test_s6_checkpoint_writes_are_atomic`, `test_s6_failed_rename_keeps_previous_report` |
| S7 | `test_s7_legacy_report_still_renders` |
| S8 | `test_s8_turn_limit_stop`, `test_s8_checks_gate_stop`, `test_s8_intake_rejected_stop`, `test_s8_intake_waiting_info_stop` |
| S9 | `test_s9_existing_test_files_untouched`, `test_s9_no_dashes_in_this_file` |

Every test drives the real runner on the real sdlc-default pipeline with a scripted fake runtime. They read the real `report.json` from disk and call the real report renderers. The runner itself is never mocked. No scenario is left uncovered.

**Fail before build:** I ran the file against a clean copy of main (`5354c71`), which has none of this order's runner code: 17 of 19 fail. Each failure is missing behaviour, such as "the run left no report.json" or "no checkpoint of report.json was written", not an import error. The 2 S9 guard tests pass there, as they should.

**On this branch:** all 19 pass, because the earlier attempt also left implementation code (in `anvil/runner.py`, `anvil/line.py`, `tools/line_comment.py` and others). Whether to keep that code is still the open question the spec-writer raised; the builder and reviewers should decide it.

**Project check** (`python -m unittest discover -s tests -p 'test_*.py'`):
- **Main, as baseline:** 741 tests, 5 failures, 6 skipped.
- **This branch, in this CI environment:** 760 tests (741 plus the 19 new), 5 failures, 6 skipped.
- **This branch with `GITHUB_ACTOR`, `GITHUB_ACTIONS` and `GITHUB_ACTOR_ID` unset:** `Ran 760 tests ... OK (skipped=6)`.

**Finding for the owner:** the 5 failures are three tests in `test_autonomous_line.TestHumanGate` and two in `test_governed_delivery.TestApprovalPolicy`. The runner sets `GITHUB_ACTOR=arananet`, so `anvil/line.py:151` refuses `--by ana` and `--by mallory` before the checks those tests expect to reach. The tests don't isolate themselves from the CI identity. They are protected files, so I didn't change them.

The station output, with the full evidence, is in `runs/wo-gh-41/test-writer.output.md`.