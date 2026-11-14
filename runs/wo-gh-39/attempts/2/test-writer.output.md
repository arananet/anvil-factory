# Test writer report: wo-gh-39 (station-timeout)

Tests live in the new file `tests/test_station_timeout.py` (19 tests, no existing test file edited, skipped or deleted). The file was already on the branch from an earlier run of this station. I re-read it against the approved spec, ran it, and confirmed the failures below. I made no changes to it.

## Scenario map
The spec scenarios are S1 to S11. The test names use the same ids.

| Scenario | Test |
|---|---|
| S1 diagnosis, no bare 1500 cap left | test_s1_wrapper_has_no_hardcoded_1500_cap |
| S2 environment over anvil.yaml over class default | test_s2_environment_beats_project_config_beats_default |
| S3 defaults 3600 for the eight WRITE_STATIONS, at least 1500 otherwise | test_s3_class_defaults, test_s3_wrapper_write_stations_match_the_eight |
| S4 ceiling 7200, bad values rejected | test_s4_ceiling_and_bad_values, test_s4_project_config_above_ceiling_never_exceeds_7200 |
| S5 executor coordination, factory anvil.yaml at least 7200 | test_s5_executor_timeout_never_below_station_timeout, test_s5_factory_anvil_yaml_value |
| S6 job timeout 360 | test_s6_job_timeout_is_360 |
| S7 honest timeout record (usage artifact, partial usage, run record step) | test_s7_killed_station_records_what_is_knowable_in_the_usage_artifact, test_s7_partial_usage_from_timeout_stdout_is_kept, test_s7_run_record_step_names_model_and_status |
| S8 healthy record shape unchanged | test_s8_s9_producing_station_survives_scaled_legacy_cap_and_is_counted, test_s8_other_station_default_is_unchanged_in_shape |
| S9 scaled mechanism (2 s work against a 1 s legacy cap passes, work past the configured cap dies) | test_s8_s9_producing_station_survives_scaled_legacy_cap_and_is_counted, test_s9_run_record_counts_the_slow_producing_station, test_s9_station_past_its_configured_cap_still_dies, test_s9_runaway_cannot_exceed_ceiling_through_the_wrapper |
| S10 decision record, CHANGELOG, docs, no dashes | test_s10_decision_changelog_and_docs, test_s10_no_dashes_in_new_artifacts |
| S11 builder report literals | Not covered. The builder report does not exist yet, so a test would only check a file that is absent. The reviewer checks it. |

## Interface the tests pin
The spec leaves the names to the builder. The docstring at the top of the test file records them:
- `anvil.config.station_timeout_seconds(station, environ=None)`
- `anvil.config.STATION_TIMEOUT_CEILING`
- `anvil.config.effective_executor_timeout(configured, environ=None)`
- the executor hands `runtime.station_timeout_seconds` to the wrapper as ANVIL_STATION_TIMEOUT_SECONDS.

## Failing now, for the right reason
Run of `tests.test_station_timeout`: 19 tests, 7 failures, 5 errors. The other 7 pass.
- The 5 errors are AttributeError: anvil.config has no `station_timeout_seconds`, `STATION_TIMEOUT_CEILING` or `effective_executor_timeout`.
- test_s1: the wrapper still has `TIMEOUT_SECONDS = 1500`.
- test_s5_factory_anvil_yaml_value: runtime.timeout_seconds is 1800, which is below 7200.
- The three S7 tests and test_s9_station_past_its_configured_cap_still_dies: a scaled cap is not honoured, so the wrapper exits 0 and the step status is `executed` rather than `timed_out`.
- test_s10: the decision record, changelog entry and docs are missing.

The 7 tests that pass already hold against the base. One is S6: anvil-line.yml already reads timeout-minutes: 360 at line 66, from an operator commit. The others are guard and shape checks, such as healthy-record shape and the dash check.

## Project check
Command: `python -m unittest discover -s tests -p 'test_*.py'`

Result: `Ran 729 tests ... FAILED (failures=12, errors=5, skipped=6)`.
- The 12 failures plus errors that come from `tests/test_station_timeout.py` are the expected red state.
- The other 5 failures are in test_autonomous_line.TestHumanGate (s4 twice, s5) and test_governed_delivery.TestApprovalPolicy (s5 twice). I did not run them at the base ref. The one I opened fails with "Approval refused: --by ana does not match the authenticated GitHub actor arananet", which comes from the runner's GitHub identity, not from this work order. I did not touch them.

Baseline: 729 total, minus the 19 in the new file, is 710 existing tests. With this file, 17 fail.
{"model": "claude-sonnet-5-5"}
