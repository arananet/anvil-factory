I added one new test file, `tests/test_stop_futile_loops.py`, with 29 tests covering S1 to S10. 24 of them fail now because the behaviour doesn't exist yet. No existing test file was changed.

**Project check** (`python -m unittest discover -s tests -p 'test_*.py'`):
- **Before:** 833 tests and 14 skipped. 7 of them already fail without my file, so they are not caused by this order:
  - 5 approval tests in `test_autonomous_line.TestHumanGate` and `test_governed_delivery.TestApprovalPolicy` fail with "does not match the authenticated GitHub actor arananet", so they depend on the CI machine.
  - 2 tests in `test_token_efficiency.WrapperEvidenceTests` also fail on their own (one `TypeError`, one wrong boolean). I did not work out why.
- **After:** `Ran 862 tests ... FAILED (failures=30, errors=1, skipped=16)`. That is the 7 above plus 24 new failures. The 2 new skips are the run-evidence tests.

**Why the new tests fail now.** Every new failure comes from missing behaviour, not an import or setup error. For example:
- the exit statuses `owner_ruling_needed`, `no_progress` and `checks_stuck` are not in `EXIT_STATUSES`;
- the builder runs 3 times where the spec wants 1 or 2;
- `owner_ruling` is not kept on the review, and the reviewer packet doesn't mention it;
- there is no "Owner ruling needed" heading in the comment;
- a bad `gate_failure_patterns` raises no `ValueError`.

**Tests that pass today on purpose.** 5 tests guard behaviour that must not change: S2, S5, S6, the "repeated gate failure off" and "no progress off" switch cases, and the `review_suffix` and `validate_review_file` checks. Each test with the order id set passes too.

**How the tests work.** They drive the real `run_pipeline` on `sdlc-default`, with a fake runtime inside the test process.
- The fake builder writes real files for each attempt, and the fake reviewers write their real `runs/<wo>/<station>.review.json`.
- The checks gate runs a real command that prints `gate.txt` and fails when it isn't empty.
- The live progress sink is observed by wrapping `SinkSet.deliver`; nothing in the runner is mocked.

| Scenario | Tests |
|---|---|
| S1 | `test_s1_owner_ruling_ends_the_run_after_one_builder_call`, `test_s1_comment_prints_the_question_under_its_heading`, `test_s1_comment_without_rulings_has_no_heading`, `test_s1_reviewer_packet_and_prompts_carry_the_instruction` (R1.2), `test_s1_exit_statuses_are_registered` |
| S2 | `test_s2_ordinary_finding_still_loops_back` |
| S3 | `test_s3_unchanged_second_attempt_ends_with_no_progress`, `test_s3_second_attempt_writing_only_under_runs_is_no_progress`, `test_s3_unanswered_checks_gate_loopback_is_no_progress`, `test_s3_first_attempt_is_never_compared` |
| S4 | `test_s4_same_fail_line_twice_ends_with_checks_stuck`, `test_s4_each_default_pattern_is_recognized` (`ERROR:`, `FAILED`, `not ok`), `test_s4_long_repeated_signature_is_truncated` (at most 2000 characters) |
| S5 | `test_s5_different_failure_loops_on` |
| S6 | `test_s6_unrecognized_failure_never_stops_early` |
| S7 | `test_s7_owner_ruling_stop_off_loops_back`, `test_s7_no_progress_stop_off_dispatches_gate_and_reviewers`, `test_s7_repeated_gate_failure_stop_off_makes_third_attempt`, `test_s7_custom_failure_patterns`, `test_s7_malformed_failure_patterns_fail_loading` (`"("`, `["("]`, `[7]`, an object) |
| S8 | `test_s8_validate_review_file_accepts_owner_ruling`, `test_s8_parse_review_keeps_owner_ruling`, `test_s8_parse_review_drops_bad_values`, `test_s8_dropped_value_is_recorded_on_the_step`, `test_s8_review_suffix_unchanged` |
| S9 | `test_s9_stops_reach_the_sink_and_add_no_event_kind` (one sub-test per stop) |
| S10 | `test_s10_no_dashes_in_this_file`; `test_s10_protected_paths_untouched` and `test_s10_no_dashes_in_lines_this_order_adds` skip unless `ANVIL_WORK_ORDER_ID=wo-gh-49` |

**Names the builder must use.** The spec left these open, so the tests fix them (they are listed in the file's docstring):
- `Review.owner_ruling`, and `owner_ruling` in `Review.to_dict()`;
- `owner_ruling_ignored` as a reason string on the reviewer's step record;
- `report["owner_rulings"]` and `report["next_human_action"]`;
- a bad `gate_failure_patterns` makes `run_pipeline` raise `ValueError`, and the message names `efficiency.gate_failure_patterns`.

**Not covered:**
- **Previous attempt passed the gate:** this R4.3 case only applies when there is a failure before it to compare against, so I wrote no test for it.
- **Full suite passing:** the R6.3 part of S10 is the project check itself, which can't pass until the build is done.
{"model": "claude-opus-5-5"}
