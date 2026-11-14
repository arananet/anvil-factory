# Test writer handoff: wo-gh-39

File: tests/test_station_timeout.py (19 tests). Note: a file with this name was already in the tree from the earlier run commit fd72230 (not at base a011c14). I did not read it before writing and replaced it wholesale with this version; it is not a protected base-ref test.

## Scenario map
- S1 -> test_s1_wrapper_has_no_hardcoded_1500_cap
- S2 -> test_s2_environment_beats_project_config_beats_default
- S3 -> test_s3_class_defaults, test_s3_wrapper_write_stations_match_the_eight
- S4 -> test_s4_ceiling_and_bad_values, test_s4_project_config_above_ceiling_never_exceeds_7200, test_s9_runaway_cannot_exceed_ceiling_through_the_wrapper
- S5 -> test_s5_executor_timeout_never_below_station_timeout, test_s5_factory_anvil_yaml_value
- S6 -> test_s6_job_timeout_is_360
- S7 -> test_s7_killed_station_records_what_is_knowable_in_the_usage_artifact, test_s7_partial_usage_from_timeout_stdout_is_kept, test_s7_run_record_step_names_model_and_status
- S8 -> test_s8_other_station_default_is_unchanged_in_shape (plus the whole existing suite)
- S9 -> test_s8_s9_producing_station_survives_scaled_legacy_cap_and_is_counted, test_s9_run_record_counts_the_slow_producing_station, test_s9_station_past_its_configured_cap_still_dies
- S10 -> test_s10_decision_changelog_and_docs, test_s10_no_dashes_in_new_artifacts
- S11 not covered by a test: the builder report does not exist yet; it is checked against the report itself.

## Interface the tests pin (names chosen here, spec leaves them open)
- anvil.config.station_timeout_seconds(station, environ=None), STATION_TIMEOUT_CEILING = 7200, effective_executor_timeout(configured, environ=None).
- anvil.yaml runtime.station_timeout_seconds, handed by CommandExecutor to the wrapper as ANVIL_STATION_TIMEOUT_SECONDS unless the environment already sets it.
- Usage artifact attempt for a kill carries status timed_out, station, timeout_seconds, reason, duration_ms, configured_model; run record step has status timed_out, executed_model not null, detail naming the timeout.
- Over-ceiling values: clamp to 7200 or ValueError naming 7200, both accepted.

## Evidence
Tests use the real wrapper tools/claude_station.py with a fake claude CLI on PATH (sleep 1 to 10 s, scaled), the real CommandExecutor and the real run_pipeline.
- Baseline before my change (file removed): 710 tests, failures=5, skipped=6. The 5 failures are existing and unrelated: test_autonomous_line TestHumanGate s4 (2) and s5 (1), test_governed_delivery TestApprovalPolicy s5 (2).
- New file alone, run now: 19 tests, 8 failures and 5 errors (the other 6 pass vacuously or on already-true behaviour: S3 write-stations set, S4 ceiling-through-wrapper, S8 shape, S9 slow-station survives, no-dash check, S9 run record survives because 10s fake work is under the 1500 cap). Failures are for the right reason: missing anvil.config functions, anvil.yaml 1800, workflow 180, the 1500 constant, missing decision record, and the wrapper not killing at ANVIL_STATION_TIMEOUT_SECONDS=1.
- Full suite with the new file: 729 tests expected (710 + 19). No existing test edited, skipped or deleted.
- Note: the scaled "survives" tests pass before the build by design (fake work is far under 1500); the kill tests are the ones that fail now.
