I added `tests/test_station_timeout.py` with 15 tests. 12 fail now and 2 pass. The `S11` test skips, because the builder report isn't written yet. They fail for the right reason: the wrapper still applies the hardcoded 1500s cap.

**Suite baseline.** The full check, `python -m unittest discover -s tests -p 'test_*.py'`, ran 725 tests with 17 failures and 7 skips. 12 of the failures are my new tests. The other 5 are not related to timeouts:
- `test_autonomous_line.TestHumanGate`: `test_approval_rules_s4`, `test_approve_and_resume_deploys_s4`, `test_publisher_held_until_approved_s5`.
- `test_governed_delivery.TestApprovalPolicy`: `test_identity_and_policy_s5`, `test_policy_comes_from_the_operator_checkout_s5`.

I only added one new file and did not run the suite without it, so I haven't confirmed these 5 fail on the base too. I didn't touch any existing test.

**Scenario to test map.** "Fails now" is the failing test's message at the base, not a count of tests:

| Scenario | Test(s) | Fails now because |
|---|---|---|
| S1 | `test_s1_cap_constant_is_gone_or_configurable_and_history_is_recorded` | the cap is still 1500 |
| S2 | `test_s2_env_beats_project_config_beats_class_default`, `test_s2_project_config_in_anvil_yaml_reaches_the_wrapper` | `1500 != 100`; the `anvil.yaml` value never reaches the wrapper |
| S3 | `test_s3_class_defaults_producing_3600_other_1500` | `builder` gets 1500, not 3600 |
| S4 | `test_s4_ceiling_7200_and_bad_values` | `9000` does not clamp to 7200 |
| S5 | `test_s5_executor_timeout_never_below_station_timeout` | executor timeout stays 300 |
| S6 | `test_s6_job_timeout_is_360_minutes` | the workflow still says 180 |
| S7 | `test_s7_timed_out_station_records_elapsed_timeout_model_and_usage`, `test_s7_run_record_step_is_timed_out_with_model` | a 4s fake-`claude` run passes under the old cap; the run record step is `executed`, not `timed_out` |
| S8 | `test_s8_healthy_station_record_shape_unchanged` | passes now, as intended: it guards the unchanged behaviour |
| S9 | `test_s9_producing_station_past_scaled_legacy_cap_completes`, `test_s9_station_over_configured_cap_dies_and_is_recorded` | the configured caps of 5s and 1s are ignored |
| S10 | `test_s10_decision_changelog_and_docs` | `brain/decisions/0011-station-timeout.md` is missing |
| S11 | `test_s11_builder_report_literals` | skips until `runs/wo-gh-39/builder.output.md` exists |

I also added `test_no_dash_characters_in_new_files`, which passes. S1's file-and-line diagnosis can only be checked in the builder report, so no test covers it directly.

The tests exercise the real `tools/claude_station.py`. They call its `main()` with `subprocess.run` mocked, and also run it as a real process against a fake `claude` CLI that sleeps. The run-record tests go through `run_pipeline`.

**Names the builder must match.** The spec leaves these open, so I fixed them in the test file's docstring:
- **Project config:** the `anvil.yaml` key is `runtime.station_timeout_seconds`, and the runner hands it to the wrapper as `ANVIL_STATION_TIMEOUT_SECONDS`.
- **Executor config:** the executor reads the same `station_timeout_seconds` key and uses it to raise its own timeout.
- **Usage artifact:** a killed attempt carries `status: "timed_out"`, `duration_ms`, `timeout_seconds`, `reason` and `station`.
- **Run record step:** a killed step carries `status: "timed_out"`, `executed_model`, `elapsed_ms` and `reason`.
- **Ceiling:** a value above 7200 is clamped to 7200 or fails with a message naming 7200.
- **Bad values:** `abc`, `0` and `-5` must fail with the value named in stderr.

Two assumptions could be wrong. S4 accepts either a clamp or a rejection. Separately, the 2s fake-delay runs in S9 only mean something once the default exceeds 1500s.
{"model": "claude-sonnet-5-5"}
