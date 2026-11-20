I added 18 tests in one new file, `tests/test_continuous_run_accounting.py`. 16 of them fail now because the runner doesn't have the behaviour yet, which is the right reason; the other 2 already pass. No existing test file was changed.

**Test counts**
- **Before my change:** 741 tests, `OK (skipped=6)`, with the `ANVIL_*` and `GITHUB_*` variables cleared. I measured this by moving the new file aside for one run.
- **With the new file:** `Ran 759 tests ... FAILED (failures=16, skipped=6)`, with those variables cleared. All 16 failures are in the new file.
- **The project check as given** (`python -m unittest discover -s tests -p 'test_*.py'`) in this station's own environment: `FAILED (failures=21, skipped=6)`. The 5 extra failures are in `test_autonomous_line` (3) and `test_governed_delivery` (2), and they come from the environment. This process sets `GITHUB_ACTOR=arananet`, so approval-identity checks refuse `--by bo`. They pass with a clean environment and are unrelated to this order.

**How the tests run.** Every death test drives the real `run_pipeline` on `pipelines/sdlc-default.json` with a fake runtime that records each call. The signal tests run the runner in a child process and send it a real SIGTERM or SIGINT while the builder is in flight. The atomic-write tests wrap `os.replace` and `os.rename` to capture every write onto `report.json`; the runner itself is not mocked.

**Why the 16 fail now.** The runner writes no `exit_status`, `termination_reason` or checkpoint, and nothing reaches `report.json` by rename. An uncaught error, a signal and an intake `rejected` leave no report at all. There is no `render_swimlane`.

| Scenario | Test(s) | Status now |
|---|---|---|
| S1 | `test_s1_budget_death_mid_builder_leaves_complete_report` | fails |
| S2 | `test_s2_station_timeout_death_is_recorded`, `test_s2_uncaught_error_death_is_recorded`, `test_s2_timeout_and_error_statuses_differ` | fail |
| S3 | `test_s3_checkpoints_accumulate_during_healthy_run`, `test_s3_final_report_is_last_checkpoint_plus_verdict` | fail |
| S4 | `test_s4_killed_record_renders_without_a_run`, `test_s4_later_run_preserves_killed_record_in_history` | fail |
| S5 | `test_s5_sigterm_completes_the_record`, `test_s5_sigint_completes_the_record` | fail |
| S6 | `test_s6_checkpoint_writes_are_atomic`, `test_s6_failed_rename_keeps_previous_report` | fail |
| S7 | `test_s7_legacy_report_still_renders` (uses `runs/wo-gh-20/report.json`) | fails |
| S8 | `test_s8_turn_limit_stop`, `test_s8_checks_gate_stop`, `test_s8_intake_rejected_stop` | fail |
| S9 | `test_s9_existing_test_files_untouched`, `test_s9_no_dashes_in_this_file` | pass |

**Names the tests fix where the spec left them open** (also listed in the file's docstring; the builder should confirm them):
- **Budget death fields:** `budget_death` holds `measured_tokens`, `max_run_tokens` and `station_in_flight`.
- **Checkpoint usage:** `checkpoint.usage_so_far.total_tokens` must equal what `summarize_steps` gives over the steps recorded so far.
- **Swimlane:** a new function, `anvil.runner.render_swimlane(report_dict)`, that renders from the report alone.
- **Turn limit:** detected from the runtime's `subtype=error_max_turns` failure.
- **Final report versus last checkpoint:** `human_required` may change between them along with `verdict`, `decision` and the exit fields, because it repeats `decision.human_gate.required`.

**How I read the spec** (decisions you may want to check):
- A budget death, station timeout, turn limit or checks gate stop ends the run there. Every station after it must be `not_run`, and the runtime gets no further call. Today the runner carries on: after a timeout it runs the checks gate, the reviewers (as `skipped`) and the observer.
- For the in-flight builder, the tests don't check its step status or executed model on a budget, error or signal death. They check only that it appears once and is not `not_run`.

**Gaps:**
- **S9 base ref:** the spec's base ref `4675a131eb9aa88097741dc3cdc9772c3db17550` is out of date. Main has since modified five test files there, including `test_curated_skills.py` and `test_model_migration.py`, so a literal diff against it fails no matter what the builder does. The S9 test diffs against `HEAD` instead; the spec should name a current base ref.
- **Not covered:**
  - **SIGTERM-or-SIGINT runs:** the R2.1 path of the same name is only partly covered. The tests fire a signal at a run that is not part of these paths. The existing scenarios cover rescoped stop and `waiting_info` for intake stops, and pre-deploy gate failure for checks stops; none of those has its own test.
  - **Unexposed usage:** a budget death where the runtime exposes no usage, which R2.4 says should be recorded as unmeasured with its reason. A fake can't cross the cap without reporting usage, so I couldn't script it.
  - **The cli inspect path:** `anvil runs` reads state through `anvil/observe.py`, which is outside the allowed write set.
{"model": "claude-opus-5-5"}
