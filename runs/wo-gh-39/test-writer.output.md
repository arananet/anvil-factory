# Test writer report: wo-gh-39 (station-timeout)

The tests already exist from the earlier run on this branch: tests/test_station_timeout.py (22 tests incl. helpers' cases) and tests/test_station_timeout_config.py. Both are new files; no existing test file was modified, skipped or deleted (`git status tests` is clean). I reviewed them against the spec and added no new files.

## Scenario map
- S1 (diagnosis): TestDiagnosis.test_s1_wrapper_has_no_hardcoded_1500_cap. The builder report text itself is checked by the reviewers at S11.
- S2: test_s2_environment_beats_project_config_beats_default; TestExecutorHandoff (config tests).
- S3: test_s3_class_defaults, test_s3_wrapper_write_stations_match_the_eight.
- S4: test_s4_ceiling_and_bad_values, test_s4_project_config_above_ceiling_never_exceeds_7200.
- S5: test_s5_executor_timeout_never_below_station_timeout, test_s5_factory_anvil_yaml_value.
- S6: test_s6_job_timeout_is_360.
- S7: test_s7_killed_station_records_what_is_knowable_in_the_usage_artifact, test_s7_partial_usage_from_timeout_stdout_is_kept, test_s7_run_record_step_names_model_and_status, TestTimeoutEvidence.
- S8: test_s8_s9_producing_station_survives_..., test_s8_other_station_default_is_unchanged_in_shape.
- S9: test_s8_s9_producing_station_survives_scaled_legacy_cap_and_is_counted, test_s9_run_record_counts_the_slow_producing_station, test_s9_station_past_its_configured_cap_still_dies, test_s9_runaway_cannot_exceed_ceiling_through_the_wrapper.
- S10: test_s10_decision_changelog_and_docs, test_s10_no_dashes_in_new_artifacts.
- S11: not covered by a test (the builder report does not exist yet when tests are written); the checks and reviewers read it.

## Results
- New files run alone: 26 tests, OK.
- Full project check `python -m unittest discover -s tests -p 'test_*.py'`: Ran 736 tests, FAILED (failures=5, skipped=6).
- The 5 failures are in tests/test_autonomous_line.py and tests/test_governed_delivery.py (approval identity). Cause: this runner sets GITHUB_ACTOR=arananet, so `approve --by ana` is refused. They are unrelated to timeouts. With GITHUB_ACTOR emptied, those two modules pass (32 tests OK). Existing tests were not changed.

## Caveat: the fail-before-build check
The implementation is already in the tree from the earlier run, so I could not show these tests failing before the build. I did not revert the implementation to check. The tests pass now against the real wrapper, config, executor, workflow and docs.
{"model": "claude-sonnet-5-5"}
