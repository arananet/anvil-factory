I've added two test files covering all 16 spec scenarios. All 28 runnable new tests fail on the unbuilt tree, and they fail because the feature is missing: no requests reach the collector, there's no `sinks` field in state.json, loading doesn't validate, and the docs and the sink module don't exist yet. There are no import or harness errors.

**Project check** (`python -m unittest discover -s tests -p 'test_*.py'`):
- **Baseline, without my files:** `Ran 802 tests ... FAILED (failures=6, errors=1, skipped=11)`.
- **With my files:** `Ran 832 tests ... FAILED (failures=25, errors=10, skipped=13)`. That is 30 added tests: 28 new failures and 2 skips.
- **The 7 existing failures** are identical in both runs and are not caused by this order. They come from this runner's environment: `GITHUB_ACTOR` makes the approval tests in `test_autonomous_line` and `test_governed_delivery` refuse the typed approver, and `test_token_efficiency` wrapper usage comes back `None`. The checks gate will see them until whatever environment variables cause them are cleared.
- **No existing test file was modified or deleted.** No new dependency.

**New files:** `tests/test_live_progress_sinks.py` (issue sink, config, what ships, guardrails) and `tests/test_live_progress_project_sink.py` (project sink).

Each test runs a real scripted sdlc-default run through `anvil.runner.run_pipeline` with a fake runtime in the same process. A local collector stands in for the GitHub comments API and for a Projects v2 GraphQL board. The tests clear every GitHub variable from the environment and point `GITHUB_API_URL` and `GITHUB_GRAPHQL_URL` at the collector, so nothing reaches real GitHub.

| Scenario | Test(s) |
|---|---|
| S1 (a) | `test_s1_one_comment_created_then_only_edited` |
| S2 (b) | `test_s2_edit_before_builder_shows_builder_running` |
| S3 (c) | `test_s3_http_500_changes_nothing_but_one_export_error`, `test_s3_unreachable_api_gives_one_export_error`, `test_s3_silent_api_is_bounded_by_the_timeout` |
| S4 (d) | `test_s4_non_wo_gh_id_...`, `test_s4_missing_token_...`, `test_s4_missing_repository_records_reason` |
| S5 (e) | `test_s5_status_changes_only_when_the_phase_changes`, `test_s5_item_already_in_project_is_not_added_again` |
| S6 (e) | `test_s6_missing_option_names_it_and_goes_inactive`, `test_s6_missing_project_names_it_and_goes_inactive` |
| S7 (f) | `test_s7_no_sink_configured_makes_no_call` (sinks key absent, and empty list) |
| S8 (g) | `test_s8_malformed_sinks_fail_loading_naming_the_entry`, `test_s8_valid_sinks_load`, `test_s8_token_env_reaching_a_station_fails_loading` |
| S9 (h) | `test_s9_token_appears_only_in_the_authorization_header` |
| S10 | `test_s10_runtime_refused_is_shown_as_final_state`, `test_s10_unknown_exit_status_is_shown_verbatim` |
| S11 | `test_s11_crash_edits_the_same_comment` |
| S12 | `test_s12_factory_and_scaffold_enable_github_issue_only`, `test_s12_operations_documents_the_project_sink` |
| S13 | `test_s13_runner_holds_no_network_code`, `test_s13_frozen_paths_and_existing_tests_untouched` (skips unless `ANVIL_WORK_ORDER_ID=wo-gh-47`) |
| S14 | `test_s14_docs_decision_changelog_and_no_dashes`, `test_s14_no_dashes_in_lines_this_order_adds` (skips unless wo-gh-47) |
| S15 | `test_s15_headers_workflow_link_and_scalar_facts_only`, `test_s15_no_workflow_link_without_run_id` |
| S16 | `test_s16_unset_projects_token_makes_no_call`, `test_s16_projects_token_never_written` |

**Names the builder has to match** (the spec leaves these open, so the tests pin them; each file's docstring lists them):
- **State writes:** a state write is a call to `RunRecorder.state` or `mark_crashed`. The tests count calls to `RunRecorder.state`.
- **Config loading:** a malformed `observability.sinks` must make `load_anvil_config(path)` raise `ValueError`.
- **Comment table:** rows read `| station | status | attempt | tokens |`.
- **GraphQL:** the project sink sends GraphQL POSTs and is identified by the mutation names `addProjectV2ItemById` and `updateProjectV2ItemFieldValue`. The fake board treats any other mutation as changing the project's layout, which the tests forbid.

**Spec conflicts and gaps:**
- **S13 can't be met as written.** It asks that `anvil/runner.py` contain no `urllib`, but the base ref already has `from urllib.parse import urlparse` at line 9, and the builder may only change the runner where the recorder is constructed. The test instead checks that the runner has no `urllib.request`, `urlopen`, `http.client`, `import socket` or `retry`. A reviewer should confirm that reading.
- **No state write at run start.** R1.2 lists a "run start" write, but today the runner sends only the `run.started` event and writes state first just before intake. S1 counts actual state writes, so it holds whether or not the builder adds one.
- **S3 timeout bound is per state write.** "Each request returns within 2 seconds" is checked as each state write taking under 2.5 seconds with `timeout_seconds: 1`, on a short 3-station pipeline to keep the test fast.
{"model": "claude-opus-5-5"}
