I reused the two test files the earlier test-writer pass wrote, which are already on this branch. The spec did not change: the spec-writer pass this attempt made no edits, and only the base ref moved, to `ae0bbfb2af95b41d96d8e2af7c9f8b787f54d83b`. Neither file exists at that base ref, so both are new files. No existing test file was modified or deleted, and no dependency was added.

**New test files:**
- `tests/test_live_progress_sinks.py`: 24 tests covering the issue sink, config validation, what ships, and the guardrails.
- `tests/test_live_progress_project_sink.py`: 6 tests covering the project sink.

Each test drives a real scripted sdlc-default run through `anvil.runner.run_pipeline`, reads the real `anvil.yaml`, scaffold and docs, and calls `load_anvil_config`. A local HTTP collector stands in for the GitHub REST comments API and the Projects v2 GraphQL API. The tests clear the GitHub variables and point `GITHUB_API_URL` and `GITHUB_GRAPHQL_URL` at the collector, so nothing reaches real GitHub. The operator fix in 48a8e85 makes S3 treat wall clock figures as volatile; I ran S3 three times in a row and it passed each time.

**Fail first, checked this attempt.** I exported the tree at the base ref with `git archive ae0bbfb` and copied the two new files in. Result: `Ran 30 tests ... FAILED (failures=19, errors=9, skipped=2)`. The failures come from the missing feature, with no import or harness errors:
- `KeyError: 'sinks'` (no sinks field in state.json)
- the collector received no requests
- `ValueError not raised` (malformed sinks not validated)
- the sink module, the OPERATIONS section and the README section are missing

The 2 skips are S13 and S14, which skip unless `ANVIL_WORK_ORDER_ID=wo-gh-47`.

**On the current branch tree**, which already holds the builder's earlier work:
- New files alone: `Ran 30 tests ... OK (skipped=2)`.
- With `ANVIL_WORK_ORDER_ID=wo-gh-47`, `test_live_progress_sinks`: `Ran 24 tests ... OK`, so S13 and S14 run and pass.

**Project check** (`python -m unittest discover -s tests -p 'test_*.py'`):
- **Base ref suite:** 802 tests. That is 832 minus the 30 new ones; the earlier pass measured the same baseline as `Ran 802`.
- **Full suite, current tree, this runner's environment:** `Ran 832 tests in 105.319s`, `FAILED (failures=6, errors=1, skipped=14)`.
- **The 7 existing failures are caused by the environment, not by this order:**
  - `test_autonomous_line` (3 tests: `test_approval_rules_s4`, `test_approve_and_resume_deploys_s4`, `test_publisher_held_until_approved_s5`)
  - `test_governed_delivery` (2 tests: `test_identity_and_policy_s5`, `test_policy_comes_from_the_operator_checkout_s5`)
  - `test_token_efficiency` (2 tests: `test_claude_correction_includes_both_attempts_s2`, `test_project_handoff_executes_in_target_tree_s2`)
- **Proof:** I re-ran those three modules with `GITHUB_ACTOR`, `GITHUB_TRIGGERING_ACTOR` and the station `ANVIL_*` hand-off variables unset. Result: `Ran 51 tests ... OK`. The checks gate of attempt 3 ran without those variables, and there these 7 passed.
- **The one failure the gate saw in attempt 3** was `test_station_budgets_completeness` (an anvil.yaml comparison from wo-gh-42). It does not occur on this tree, because factory main ae0bbfb scoped that evidence to wo-gh-42's own run.

**Scenario to test map:**

| Scenario | Test(s) |
|---|---|
| S1 (a) | `test_s1_one_comment_created_then_only_edited` |
| S2 (b) | `test_s2_edit_before_builder_shows_builder_running` |
| S3 (c) | `test_s3_http_500_changes_nothing_but_one_export_error`, `test_s3_unreachable_api_gives_one_export_error`, `test_s3_silent_api_is_bounded_by_the_timeout` |
| S4 (d) | `test_s4_non_wo_gh_id_...`, `test_s4_missing_token_...`, `test_s4_missing_repository_records_reason` |
| S5 (e) | `test_s5_status_changes_only_when_the_phase_changes`, `test_s5_item_already_in_project_is_not_added_again` |
| S6 (e) | `test_s6_missing_option_names_it_and_goes_inactive`, `test_s6_missing_project_names_it_and_goes_inactive` |
| S7 (f) | `test_s7_no_sink_configured_makes_no_call` |
| S8 (g) | `test_s8_malformed_sinks_fail_loading_naming_the_entry`, `test_s8_valid_sinks_load`, `test_s8_token_env_reaching_a_station_fails_loading` |
| S9 (h) | `test_s9_token_appears_only_in_the_authorization_header` |
| S10 | `test_s10_runtime_refused_is_shown_as_final_state`, `test_s10_unknown_exit_status_is_shown_verbatim` |
| S11 | `test_s11_crash_edits_the_same_comment` |
| S12 | `test_s12_factory_and_scaffold_enable_github_issue_only`, `test_s12_operations_documents_the_project_sink` |
| S13 | `test_s13_runner_holds_no_network_code`, `test_s13_frozen_paths_and_existing_tests_untouched` (skips unless wo-gh-47) |
| S14 | `test_s14_docs_decision_changelog_and_no_dashes`, `test_s14_no_dashes_in_lines_this_order_adds` (skips unless wo-gh-47) |
| S15 | `test_s15_headers_workflow_link_and_scalar_facts_only`, `test_s15_no_workflow_link_without_run_id` |
| S16 | `test_s16_unset_projects_token_makes_no_call`, `test_s16_projects_token_never_written` |

Every scenario is covered. Neither test file contains an em dash or en dash.

**Unresolved, for review:**
- **S13 reading.** The spec asks that `anvil/runner.py` contain no `urllib`. The base ref already has `from urllib.parse import urlparse`, so the test forbids `urllib.request`, `urlopen`, `http.client`, `import socket` and `retry` instead. A reviewer should confirm this reading.
- **Run start write.** R1.2 lists a state write at the start of the run. S1 counts the state writes that actually happen, so it holds whether or not the builder adds one.
- **Variables in local runs.** Anyone who runs the suite locally with `GITHUB_ACTOR` exported will see the 7 existing failures listed above.
{"model": "claude-opus-5-5"}
