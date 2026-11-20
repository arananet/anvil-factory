The tests for every scenario are in place, but the full project check fails. It still has 1 failure with the CI variables cleared, and that failure blocks the order until you decide how to resolve it.

**The blocker.** The existing test `tests/test_governed_delivery.py:113` checks that a run that crashes in the builder leaves **no** `report.json`. This spec requires the opposite: a checkpoint after every station (R1.1), and a completed record when an uncaught error ends the run (R2.1). Any build that meets the spec will fail that line. So "full suite passes with no existing test file modified" (R4.2 / S9) can't be met as written. The governed-delivery spec itself doesn't require the report to be absent; what it does require (`state.json` says crashed, the exception still propagates) still holds. I left the test alone because it's protected. You need to either allow a one-line change to that test or amend this spec.

**What I did**
- An earlier attempt had already written `tests/test_continuous_run_accounting.py` (18 tests covering S1 to S9). I reused it and made two edits:
  - **Added** `test_s8_intake_waiting_info_stop` for the intake `waiting_info` stop path.
  - **Fixed** `test_s9_existing_test_files_untouched`. It flagged any change under `tests/`, including this order's own new file. It now checks only the test files that exist at base ref `4675a131eb9aa88097741dc3cdc9772c3db17550`.
- No existing test file was changed.
- The tests drive the real `run_pipeline` on `pipelines/sdlc-default.json` with a fake runtime that records every call. The signal tests send a real SIGTERM or SIGINT to a child process, and the rendering tests call the real renderers.

**Results**
- **Fail before the build:** code from the earlier attempt is already on this branch, so all 19 new tests pass on the current tree. To show they can fail, I ran them with `anvil/` and `tools/` restored to the base ref: 17 failed, all because the behaviour is missing (no `exit_status`, no `report.json`, no checkpoint, no `render_swimlane`), not because of import errors.
- **Baseline:** 18 tests in the file before my edits; the earlier attempt recorded 741 tests for the whole suite without the file.
- **Project check as given:** `Ran 760 tests ... FAILED (failures=6, skipped=6)`. Five of those failures come from this environment: it sets `GITHUB_ACTOR`, so the approval identity checks refuse the test identity.
- **With the `ANVIL_*` and `GITHUB_*` variables cleared:** `Ran 760 tests ... FAILED (failures=1, skipped=6)`. The one failure is the blocker above.

| Scenario | Tests |
|---|---|
| S1 | `test_s1_budget_death_mid_builder_leaves_complete_report` |
| S2 | `test_s2_station_timeout_death_is_recorded`, `test_s2_uncaught_error_death_is_recorded`, `test_s2_timeout_and_error_statuses_differ` |
| S3 | `test_s3_checkpoints_accumulate_during_healthy_run`, `test_s3_final_report_is_last_checkpoint_plus_verdict` |
| S4 | `test_s4_killed_record_renders_without_a_run`, `test_s4_later_run_preserves_killed_record_in_history` |
| S5 | `test_s5_sigterm_completes_the_record`, `test_s5_sigint_completes_the_record` |
| S6 | `test_s6_checkpoint_writes_are_atomic`, `test_s6_failed_rename_keeps_previous_report` |
| S7 | `test_s7_legacy_report_still_renders` |
| S8 | `test_s8_turn_limit_stop`, `test_s8_checks_gate_stop`, `test_s8_intake_rejected_stop`, `test_s8_intake_waiting_info_stop` |
| S9 | `test_s9_existing_test_files_untouched`, `test_s9_no_dashes_in_this_file` |

**Not covered**
- **Budget death with no usage reported:** a fake runtime can't cross the token cap without reporting usage, so the "unmeasured with its reason" case of R2.4 has no test.
- **Two stop paths:** there is no dedicated test for a rescoped intake stop or a pre-deploy gate checks stop.
- **The cli inspect path:** it reads through `anvil/observe.py`, which is outside the allowed write set.
- **Literal S9 diff:** main has changed several test files since the spec's base ref, so the S9 test diffs those files against HEAD instead.

The handoff is in `runs/wo-gh-41/test-writer.output.md`.