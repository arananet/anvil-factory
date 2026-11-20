# Test writer: wo-gh-41 (continuous-run-accounting)

## Test file
- `tests/test_continuous_run_accounting.py` (new file, not present on factory main at merge base 5354c7130e116658cc31dec270738ffaf2de67d6; an earlier attempt of this order created it and this station revised it).
- No existing test file was modified or deleted: `git diff --name-status --diff-filter=MD 5354c71 -- tests` is empty.

## What changed this station
- S9 test rewritten to match the revised spec R4.2/S9: it now computes the merge base of HEAD with factory main at run time (falling back to 5354c7130e116658cc31dec270738ffaf2de67d6), runs `git diff --name-status --diff-filter=MD <base> -- tests` to the working tree, and asserts the result is empty. Before, it diffed against HEAD only, which ignored committed edits.
- Scenario map in the module docstring updated to match. All other tests were reused unchanged; I checked them against S1 to S8.

## Scenario to test map
| Scenario | Test(s) |
|---|---|
| S1 | `test_s1_budget_death_mid_builder_leaves_complete_report` |
| S2 | `test_s2_station_timeout_death_is_recorded`, `test_s2_uncaught_error_death_is_recorded`, `test_s2_timeout_and_error_statuses_differ` |
| S3 | `test_s3_checkpoints_accumulate_during_healthy_run`, `test_s3_final_report_is_last_checkpoint_plus_verdict` |
| S4 | `test_s4_killed_record_renders_without_a_run`, `test_s4_later_run_preserves_killed_record_in_history` |
| S5 | `test_s5_sigterm_completes_the_record`, `test_s5_sigint_completes_the_record` (real subprocess, real signal) |
| S6 | `test_s6_checkpoint_writes_are_atomic`, `test_s6_failed_rename_keeps_previous_report` |
| S7 | `test_s7_legacy_report_still_renders` (runs/wo-gh-20/report.json through line_comment, status page, swimlane) |
| S8 | `test_s8_turn_limit_stop`, `test_s8_checks_gate_stop`, `test_s8_intake_rejected_stop`, `test_s8_intake_waiting_info_stop` |
| S9 | `test_s9_existing_test_files_untouched`, `test_s9_no_dashes_in_this_file` |

All tests drive the real `anvil.runner.run_pipeline` on the real sdlc-default pipeline with a scripted fake runtime (no network, no model). They read the real report.json from disk, call the real `tools/line_comment.render`, `anvil.statuspage.render_status_page` and `anvil.runner.render_swimlane`, and observe atomic writes by wrapping `os.replace`/`os.rename`. The runner itself is never mocked.

## Interface the tests pin (where the spec leaves names open)
- `report["checkpoint"] = {last_completed_station, elapsed_ms, usage_so_far}`, where `usage_so_far.total_tokens` equals `telemetry.summarize_steps(steps)`.
- `report["exit_status"]`, `report["termination_reason"]`, step status `not_run`.
- `report["budget_death"] = {measured_tokens, max_run_tokens, station_in_flight}`.
- `anvil.runner.render_swimlane(report_dict) -> str`.
- A turn limit is the runtime failure carrying `subtype=error_max_turns` in the executor error.

## Fail before build (confirmed)
The file ran in a detached worktree of factory main 5354c71, which has none of this order's runner code: `Ran 19 tests ... FAILED (failures=17)`. Every failure is a missing-behaviour assertion, not an import error: `the run left no report.json`, `None not found in {exit statuses}`, `no checkpoint of report.json was written`, `anvil.runner has no render_swimlane(report) renderer`, `report.json was never written by rename`. The 2 S9 guard tests pass at baseline, as intended.

Note: an earlier attempt of this order left implementation code on this branch (anvil/runner.py, anvil/line.py, tools/line_comment.py and others). Against the current branch tree all 19 tests pass. Whether that code counts as accepted is for the builder and reviewers to judge; the tests do not depend on it.

## Project check
`python -m unittest discover -s tests -p 'test_*.py'`
- Baseline, factory main 5354c71: `Ran 741 tests ... FAILED (failures=5, skipped=6)`.
- Branch tree, as run in this CI environment: `Ran 760 tests ... FAILED (failures=5, skipped=6)`.
- Branch tree with `GITHUB_ACTOR`, `GITHUB_ACTIONS`, `GITHUB_ACTOR_ID` unset: `Ran 760 tests ... OK (skipped=6)`.
- Added: 19 tests (760 = 741 + 19). Edited existing: none.
- The 5 failures happen at baseline too and depend on the environment, not on this order: test_autonomous_line.TestHumanGate (test_approval_rules_s4, test_approve_and_resume_deploys_s4, test_publisher_held_until_approved_s5) and test_governed_delivery.TestApprovalPolicy (test_identity_and_policy_s5, test_policy_comes_from_the_operator_checkout_s5). This runner sets `GITHUB_ACTOR=arananet`, so `anvil/line.py:151` refuses `--by ana`/`--by mallory` before the checks those tests expect. This is a finding about test isolation in existing protected tests. I did not change those tests.

## Not covered
- None of S1 to S9 is uncovered. Untrappable kills (SIGKILL) are out of scope per the spec.
{"model": "claude-opus-5-5"}
