# Test writer: wo-gh-42 (station-budgets-completeness), re-run after the owner ruling of 2026-11-22

Test file: `tests/test_station_budgets_completeness.py`. This order adds it as a new file; it does not exist at base ref 72a84126a600fafb99446946694b5de809e01e66. No test file that exists at the base ref was touched.

## Context of this re-run

The build is already on the branch from run 44912754341, so the suite before this re-run was not a pre-build baseline. On arrival the file had 28 tests: 27 passed and 1 failed, `test_s11_no_dashes_in_changed_files`. The owner ruling scoped R4, S4, S5 and S8 to projects that configure efficiency partitions, and no test covered that scope.

## Changes in this re-run

- **Added 3 scope tests (S4, S5 and S8 as amended):**
  - `test_s4_s8_scope_no_partitions_keeps_present_behavior`: a project with neither `efficiency.station_budgets` nor `efficiency.default_station_budget`, and an attempt with an empty delta, still dispatches reviewers. No completeness record is written.
  - `test_s4_s8_scope_default_station_budget_alone_gates_review`: setting only `default_station_budget` turns completeness on. The empty delta is named as a gap and zero reviewers are dispatched.
  - `test_s5_scope_station_budgets_alone_gates_and_passes_complete_work`: setting only `station_budgets` turns completeness on. A complete attempt passes and reaches review.
- **Edited `test_s11_no_dashes_in_changed_files`:**
  - It now skips `runs/*.packet.md`. Those files are the line's own rendering of frozen station prompts.
  - It failed on `runs/wo-gh-42/reviewer-ux.packet.md`. That packet copies an em dash from `stations/reviewer-ux/PROMPT.md`, a reviewer prompt that the order marks frozen and the builder cannot edit.
  - Every file the order produces is still checked.
- **Updated the docstring scenario map.** It now lists the S4 tests and the scope tests.

## Evidence that the scope tests can fail

I mutated `completeness_active` in `anvil/runner.py`, ran the file, then restored the line with `git checkout`. Its committed form is `any(station_budget_settings(config))`.

| Mutation | Result |
|---|---|
| `True` (unconditional) | fails `test_s4_s8_scope_no_partitions_keeps_present_behavior` |
| station_budgets only | fails `test_s4_s8_scope_default_station_budget_alone_gates_review` |
| default only | fails `test_s5_scope_station_budgets_alone_gates_and_passes_complete_work` and 8 other completeness tests |

At the base ref the scope test for a project without partitions would pass, because that is the present behavior it protects. The other two would fail there, because no completeness record exists at the base ref.

## Scenario map

| Scenario | Tests |
|---|---|
| S1 | test_s1_in_flight_ceiling_stops_builder_at_its_partition |
| S2 | test_s2_exhausted_builder_is_refused_loopback_with_zero_calls, test_s2_station_inside_its_partition_is_dispatched_again |
| S3 | test_s3_over_cap_example_names_pipeline_and_excess, test_s3_default_applies_to_unnamed_model_stations, test_s3_worst_case_equal_to_cap_loads_one_more_fails, test_s3_bad_partition_value_is_rejected, test_s3_factory_partitions_sum_to_exactly_15000000, test_s3_factory_config_validates_for_every_pipeline, test_s3_factory_other_keys_and_packet_budgets_unchanged, test_s3_over_cap_project_does_not_run |
| S4 | test_s4_missing_builder_report_dispatches_zero_reviewers, test_s4_missing_report_alone_blocks_review_when_checks_pass, test_s4_completeness_gaps_names_a_missing_or_empty_report, test_s4_failing_checks_verdict_dispatches_zero_reviewers, test_s4_s8_scope_no_partitions_keeps_present_behavior, test_s4_s8_scope_default_station_budget_alone_gates_review |
| S5 | test_s5_complete_attempt_dispatches_the_reviewer_stage, test_s5_scope_station_budgets_alone_gates_and_passes_complete_work |
| S6 | test_s6_cost_section_prices_partitions_where_the_table_covers |
| S7 | test_s7_unmeasured_with_require_usage_is_refused, test_s7_unmeasured_without_require_usage_proceeds_and_says_so |
| S8 | test_s8_failed_test_writer_without_artifact_blocks_review, test_s8_empty_delta_blocks_review_at_max_loopbacks, plus the two S4/S8 scope tests |
| S9 | test_s9_completeness_never_reruns_the_suite_or_literal_check |
| S10 | test_s10_execution_doc_names_both_budget_keys, test_s10_changelog_and_one_decision_record, test_s10_builder_report_evidence |
| S11 | test_s11_diff_stays_inside_the_allowed_write_set, test_s11_existing_test_files_untouched, test_s11_no_dashes_in_changed_files |

## Project check

Command: `python -m unittest discover -s tests -p 'test_*.py'`, run with the GitHub identity variables unset, as factory CI runs it.

- Result: `Ran 802 tests ... OK (skipped=6)`.
- Before this order the suite had 771 tests. This file adds 31: 28 before this re-run plus 3 new.

## Not covered

- No test runs an in-session correction re-dispatch through the runner. S2 exercises the pre-call check through the loopback re-dispatch, which the spec accepts ("a correction or a loopback").
- The "code review of gates.py" half of S9 is left to the reviewer.
- The in-flight ceiling (S1) runs against a stand-in claude CLI, not the real runtime.
{"model": "claude-opus-5-5"}
