I've written the tests for wo-gh-42 as one new file, `tests/test_station_budgets_completeness.py`, with 26 tests covering all eleven scenarios (S1 to S11). Before the build, 22 of them fail, each because the behaviour this order adds is missing. No existing test file was touched.

**Project check** (`python -m unittest discover -s tests -p 'test_*.py'`, run without the GitHub identity variables, the same way factory CI runs it since commit 3a51973):
- **Before my file:** `Ran 771 tests ... OK (skipped=6)`
- **With my file:** `Ran 797 tests ... FAILED (failures=17, errors=5, skipped=6)`. All 22 failures are in the new file.

If you run the suite with the GitHub variables still set, five approval tests in `test_autonomous_line` and `test_governed_delivery` also fail. They pass once the variables are unset, as CI does, so that has nothing to do with this order.

**How the tests work.** The runner tests drive a real sdlc-default run through `run_pipeline` with a fake runtime. That runtime writes the same per-attempt usage files the real executor writes, so the budget checks read real usage records. S1 runs end to end with the real executor and the real `tools/claude_station.py`, against a stand-in claude CLI on PATH.

| Scenario | Tests | Why it fails now |
|---|---|---|
| S1 (R3, R6a) | `test_s1_in_flight_ceiling_stops_builder_at_its_partition` | the builder hits its 12s timeout (`timed_out`) instead of being stopped at its 3000 token partition (`budget_exceeded`) |
| S2 (R2, R6b) | `test_s2_exhausted_builder_is_refused_loopback_with_zero_calls`, `test_s2_station_inside_its_partition_is_dispatched_again` | the builder is dispatched 3 times instead of 1; the run report has no budget outcomes |
| S3 (R1, R6c) | `test_s3_over_cap_example_names_pipeline_and_excess`, `..._default_applies_to_unnamed_model_stations`, `..._worst_case_equal_to_cap_loads_one_more_fails`, `..._bad_partition_value_is_rejected`, `..._factory_partitions_sum_to_exactly_15000000`, `..._factory_config_validates_for_every_pipeline`, `..._over_cap_project_does_not_run`, `..._factory_other_keys_and_packet_budgets_unchanged` | the validation function doesn't exist yet, the factory `anvil.yaml` has no partition table, and an over-cap project still runs. The last test (nothing else in `anvil.yaml` changed) passes now as a guard. |
| S4 (R4, R6d) | `test_s4_missing_builder_report_dispatches_zero_reviewers`, `test_s4_failing_checks_verdict_dispatches_zero_reviewers` | the report has no completeness record |
| S5 (R4, R6d) | `test_s5_complete_attempt_dispatches_the_reviewer_stage` | the report has no completeness record |
| S6 (R5) | `test_s6_cost_section_prices_partitions_where_the_table_covers` | the cost section has no per-station view |
| S7 (R2) | `test_s7_unmeasured_with_require_usage_is_refused`, `test_s7_unmeasured_without_require_usage_proceeds_and_says_so` | the report has no budget outcomes |
| S8 (R4) | `test_s8_failed_test_writer_without_artifact_blocks_review`, `test_s8_empty_delta_blocks_review_at_max_loopbacks` | 5 reviewers are dispatched today; the tests expect 0 |
| S9 (R4) | `test_s9_completeness_never_reruns_the_suite_or_literal_check` | the report has no completeness record. The suite-run count and the literal-check count already hold today. |
| S10 (R7, R8) | `test_s10_execution_doc_names_both_budget_keys`, `test_s10_changelog_and_one_decision_record`, `test_s10_builder_report_evidence` | the docs, changelog entry, decision record and builder report don't exist yet |
| S11 | `test_s11_diff_stays_inside_the_allowed_write_set`, `test_s11_existing_test_files_untouched`, `test_s11_no_dashes_in_changed_files` | these pass now as guardrails and must still pass after the build |

I checked each runner scenario's setup against today's code first: reviewers do run on a complete attempt, the checks gate does loop back on failures, and the suite count already matches. So each test fails only on the missing behaviour.

**Names and formats the builder must match.** The spec leaves these open, so I chose them; they are listed in the file's docstring:
- **Validation function:** `anvil.config.validate_station_budgets(config, pipelines, registry=None)`. It returns the worst-case total per pipeline, or raises `ValueError` naming the pipeline and the excess.
- **Run report fields:**
  - `budgets.stations` and `budgets.outcomes`, where an outcome is `refused` (with `refused_at`), `budget_exceeded` or `proceeded_unmeasured`.
  - `completeness`, a list of `{attempt, passed, gaps}`.
  - `cost.stations`, with `{partition, consumed, amount, priced, source}` per station.
- **Absent default:** if `default_station_budget` is not set, it adds 0 to the worst case. That matches the spec's S3 example, which needs an excess of exactly 100000. This settles the default value the spec-writer left open.
- **In-flight ceiling:** the wrapper has to read the session's usage while it runs. The stand-in CLI emits stream-json events only when `--output-format stream-json` is requested, as the real CLI does. That is the only realistic way to stop a session mid-flight.

**Open issues:**
- **Existing tests may break.** Completeness needs test files and a non-empty file delta before any reviewer runs. Many existing protected tests use scripted test-writers and builders that write no files and still expect reviewers to run. The builder has to meet the spec without editing those tests, so this is a likely source of regressions to watch.
- **The S11 write-set check allows more than the spec lists.** It also accepts `work-orders/issue-42.json`, `work_orders/wo-gh-42.json`, the revised spec directory and `status/`. The line itself writes these (the merge of wo-gh-41 carried `status/` changes), not the builder. The test's comments say so.
- **Not covered:** the in-session correction re-dispatch (a reviewer's second attempt inside the wrapper) has no dedicated test. S2 exercises the pre-call check through the loopback re-dispatch only. The "code review of gates.py" part of S9 is left to the reviewer.
{"model": "claude-opus-5-5"}
