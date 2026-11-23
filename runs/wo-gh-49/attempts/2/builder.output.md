# Builder report: wo-gh-49, stop-futile-loops (attempt 2)

## Outcome: STOPPED. An existing protected test contradicts a requirement (R7.2)

Attempt 1 wrote no builder report, so this is the first report on the record. Under R7.2 and the work order's reconciliation rule, I am reporting the contradiction and stopping. I have not worked around it: no protected test was edited, and the requirement was not weakened or special-cased so those tests would pass.

### The contradiction

- Requirements: R3.1 and R3.2 (an attempt that answers a loopback to the builder but changes no file outside runs/ ends the run with exit_status no_progress, and no checks gate or reviewer runs for it), together with R5.2 (stop_on_no_progress is true by default).
- Protected tests at base ref d74c83aefff95fba777ca04505116cfb63c6c8f3: each drives the runner with a fake builder that changes no file outside runs/ on any attempt. Each asserts that every later attempt is still gated or reviewed and still loops back. That is exactly the behavior R3 removes:
  - tests/test_anvil.py TestRunner.test_loopback_s9 (expects max_loopbacks loopbacks; the builder writes nothing)
  - tests/test_checks_gate.py TestChecksGateFailingChecks.test_failing_checks_return_to_builder_no_reviewer_s2 (expects 1 + loopbacks gate steps)
  - tests/test_checks_gate.py TestChecksGateProtectedPaths.test_protected_path_touch_fails_gate_automatically_s3
  - tests/test_decision.py TestDecisionRecorded.test_changes_requested_names_reviewer_s11
  - tests/test_decision.py TestDecisionRecorded.test_rejected_run_names_failing_reviewer_s11
  - tests/test_execution.py TestDeployVerify.test_no_deploy_when_not_approved_s7
  - tests/test_station_artifact_contract.py TestObservedModes.test_empty_captured_output_with_valid_review_json_s4a
  - tests/test_station_budgets_completeness.py CompletenessGate.test_s4_failing_checks_verdict_dispatches_zero_reviewers (expects 2 completeness evaluations)
  - tests/test_station_budgets_completeness.py CompletenessGate.test_s4_missing_builder_report_dispatches_zero_reviewers (builder scripted {"fail": True} on both attempts; expects 2 evaluations)
  - tests/test_station_budgets_completeness.py CompletenessGate.test_s9_completeness_never_reruns_the_suite_or_literal_check
- How I isolated the cause: I temporarily read each switch from an environment override and ran the 10 tests above with one switch off at a time. With stop_on_no_progress off, all 10 pass. With stop_on_repeated_gate_failure off or stop_on_owner_ruling off, all 10 still fail. Afterwards I reverted the override (anvil/config.py reads `efficiency.get(key, True)` again).
- These are the checks-gate failures attempt 1 got back. The loopback feedback quotes the test_station_budgets_completeness ones.
- Owner ruling needed. Options I see:
  (a) Keep R5.2's default for stop_on_no_progress at true and authorize amending these protected tests: either their fake builders change a file, or they set efficiency.stop_on_no_progress false.
  (b) Change R5.2 so stop_on_no_progress defaults to false, or is on only for named projects. The factory's anvil.yaml could then turn it on, but the new test S3 (test_s3_* in tests/test_stop_futile_loops.py) relies on the default and would need an explicit switch.
  (c) Narrow R3 in the spec to a condition these tests do not meet. I found no principled condition. The only things that tell these runs apart from S3 are details of the test fixtures (for example the executor name, or whether attempt 1 wrote a file), and keying on those would be special-casing tests.

## What is built (all per spec; kept from attempt 1, re-read this attempt)

- anvil/model.py: Review.owner_ruling is optional and kept by from_dict and to_dict (R1.1).
- anvil/runner.py:
  - parse_review keeps a non-blank string owner_ruling. owner_ruling_value drops a non-string or blank value, and the reviewer step records owner_ruling_ignored with the reason (R1.3).
  - OWNER_RULING_NOTE is added to reviewer packets by the runner and is not in review_suffix (R1.2).
  - The owner_ruling_needed stop runs after the approver (R2.1).
  - The report gets top-level owner_rulings and next_human_action fields, and the human gate rule contains "Owner ruling needed" (R2.2, R2.3, R5.3).
  - _tree_fingerprint is a content hash of the files outside runs/ (git file list, .gitignore respected). The no_progress stop runs before the gate (R3).
  - The checks_stuck stop compares failure signatures between consecutive attempts, with the reason capped at 2000 characters (R4.2, R4.3).
  - EXIT_STATUSES gains owner_ruling_needed, no_progress and checks_stuck, all completed through the existing exit path (R5.1, R5.4).
- anvil/gates.py: failure_signature(), plus check_outputs on the gate result (R4.1).
- anvil/config.py: FUTILE_LOOP_SWITCHES, DEFAULT_GATE_FAILURE_PATTERNS and futile_loop_settings(). A malformed value raises ValueError naming the key (R4.1, R5.2).
- tools/claude_station.py: the docstring of validate_review_file records that owner_ruling never rejects a review. The function already ignores unknown keys (R1.3).
- tools/line_comment.py: an "Owner ruling needed" heading with one line per question, plus a "Next human action" line (R2.4, R5.3).
- stations/reviewer-*/PROMPT.md (10 files): two lines added to each, a blank line and the one instruction sentence. Nothing removed (R1.2).
- New test file: tests/test_stop_futile_loops.py (written by test-writer; 29 tests covering S1 to S10).
- Not done, and left for after the ruling: docs/EXECUTION.md, docs/OPERATIONS.md, CHANGELOG.md, and the decision record under brain/decisions/.

## Verification (on the final tree, base ref d74c83aefff95fba777ca04505116cfb63c6c8f3)

- `python -m unittest discover -s tests -p 'test_*.py'`: `Ran 862 tests in 90.145s`, `FAILED (failures=16, errors=1, skipped=16)`. That is the exact full factory test count, 862.
  - 10 of the failures are the R3 contradiction listed above.
  - The other 7 (6 failures, 1 error) also fail at the base ref in this sandbox, so they are environmental: test_autonomous_line TestHumanGate x3, test_governed_delivery TestApprovalPolicy x2, test_token_efficiency WrapperEvidenceTests x2. I confirmed this with a clean worktree at the base ref: `Ran 833 tests`, `FAILED (failures=6, errors=1, skipped=14)`, same 7 tests. The gate excerpt attempt 1 got back does not show them.
- `python -m unittest test_stop_futile_loops` (run from tests/): `Ran 29 tests`, `OK (skipped=2)`. With ANVIL_WORK_ORDER_ID=wo-gh-49: `Ran 29 tests`, `OK`.
- `git diff --name-only d74c83aefff95fba777ca04505116cfb63c6c8f3 -- tests .github pipelines anvil.json anvil/sinks.py anvil/telemetry.py` prints nothing. No protected file is modified or deleted; the only new test file is untracked.

## Status of the four stops vocabulary

- stop-futile-loops: implemented. The suite is red only because of the R3 contradiction above.
- owner_ruling_needed: implemented and covered by S1, S7 and S9 tests, all passing.
- no_progress: implemented as specified. This is the stop that contradicts the protected tests listed above.
- checks_stuck: implemented and covered by S4 to S7 and S9 tests, all passing.
{"model": "claude-opus-5-5"}
