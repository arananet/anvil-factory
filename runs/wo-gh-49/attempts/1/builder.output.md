# Builder report: wo-gh-49 (stop-futile-loops)

## Outcome: stopped on attempt 1, an existing protected test contradicts R3 with R5.2 (rule R7.2)

All of R1 to R5 are built and the new test file passes in full (29 of 29, with the two run evidence tests run under ANVIL_WORK_ORDER_ID=wo-gh-49). The full factory suite does not pass. Ten existing protected tests at the base ref assert the line's old loopback behaviour for a fake builder that writes no file on a loopback attempt. R3.1 and R3.2, with R5.2 (stop_on_no_progress on by default), require exactly that run to end with no_progress at attempt 2. Following R7.2 and the work order, I stopped there. I did not work around it: no test edited, no default flipped, and no stop scoped down to dodge the fake builders.

**Proof that this is the only cause:** with stop_on_no_progress forced to false in code as a temporary experiment (reverted, not in the tree), the six affected modules pass: `Ran 110 tests ... OK (skipped=6)`.

### The contradicting tests (requirement R3.1, R3.2 with R5.2 default true)
- tests/test_anvil.py TestRunner.test_loopback_s9: expects len(loopbacks) == max_loopbacks and max_loopbacks + 1 builder attempts. It gets `1 != 2`.
- tests/test_checks_gate.py TestChecksGateFailingChecks.test_failing_checks_return_to_builder_no_reviewer_s2: expects a gate step for every attempt (`1 != 2`).
- tests/test_checks_gate.py TestChecksGateProtectedPaths.test_protected_path_touch_fails_gate_automatically_s3: same assertion.
- tests/test_decision.py TestDecisionRecorded.test_changes_requested_names_reviewer_s11 and test_rejected_run_names_failing_reviewer_s11: expect the approver rule of the last attempt. The run ends no_progress before that attempt's approver.
- tests/test_execution.py TestDeployVerify.test_no_deploy_when_not_approved_s7: expects the deployer packet_ready. It is not_run.
- tests/test_station_artifact_contract.py TestObservedModes.test_empty_captured_output_with_valid_review_json_s4a: expects reviewer-design counted on the final attempt.
- tests/test_station_budgets_completeness.py CompletenessGate.test_s4_failing_checks_verdict_dispatches_zero_reviewers, test_s4_missing_builder_report_dispatches_zero_reviewers and test_s9_completeness_never_reruns_the_suite_or_literal_check: each expects one completeness evaluation per attempt over two attempts (`1 != 2`).

### Options for the owner
1. Make stop_on_no_progress default false. This contradicts R5.2 as written.
2. Allow an order to amend these protected tests so their fake builders write a file per attempt. This contradicts the guardrail that existing tests are protected.
3. Have the base-ref factory's own anvil.yaml turn the stop off for these fixtures. This does not apply, because these tests build their own projects.

## What changed, by scenario
- **anvil/model.py:** Review gains the optional field owner_ruling, which defaults to None. to_dict emits it only when set and from_dict keeps it. Serves R1.1, S8.
- **anvil/runner.py:**
  - EXIT_STATUSES gains owner_ruling_needed, no_progress and checks_stuck (R5.1, S1).
  - parse_review is split into _review_object plus validation, and owner_ruling_value keeps a non-blank string. Otherwise it returns the reason the value was dropped ("not a string: int", "empty"). JSON null counts as absent. Serves R1.3, S8.
  - The reviewer step record gets owner_ruling_ignored (R1.3).
  - OWNER_RULING_NOTE is appended to every reviewer packet the runner builds, including the scoped reviewer-design packet, and never to review_suffix (R1.2).
  - The approver collects owner_rulings from counted reviews only. With stop_on_owner_ruling on, the run ends owner_ruling_needed before any loopback, with the verdict as computed (R2.1, R2.5, S1, S2).
  - _tree_fingerprint is a content hash of files outside runs/. In a git tree it uses git ls-files --cached --others --exclude-standard, so .gitignore is honoured. It is compared before and after a builder attempt that answers a loopback to the builder, and the first attempt is never compared. Nothing changed means no_progress, with no gate or reviewer dispatched (R3, S3).
  - The pre-review gate signature is kept per builder attempt. A non-empty signature equal to the previous attempt's means checks_stuck, with the reason bounded to 2000 characters (R4.2, R4.3, S4, S5, S6).
  - futile_loop_settings is loaded before any station, so a bad config raises ValueError (R4.1, S7).
  - On the three stops the report gets owner_rulings (only for owner_ruling_needed) and next_human_action, and the human gate is closed with a rule sentence. For owner_ruling_needed it starts "Owner ruling needed:". Serves R2.2, R2.3, R5.3.
  - The checks-gate step carries failure_signature when it is non-empty.
- **anvil/gates.py:** failure_signature(outputs, patterns) is the sorted set of distinct matching lines, right-stripped (R4.1). checks_gate keeps its exact signature, which tests/test_gates.py pins, and returns one added key, check_outputs (the full command outputs; the summary keeps only tails). Its pass/fail decision is unchanged.
- **anvil/config.py:** FUTILE_LOOP_SWITCHES and DEFAULT_GATE_FAILURE_PATTERNS (`^FAIL:`, `^ERROR:`, `^FAILED\b`, `^\s*not ok\b`), plus futile_loop_settings(config). A non-boolean switch, a value that is not a list of strings, or a pattern that does not compile raises ValueError naming efficiency.<key>. Serves R4.1, R5.2.
- **tools/line_comment.py:** a "### Owner ruling needed" heading with one "- station: question" line per ruling (bounded to 1000 characters, not the 160-character cell), and a "Next human action:" line (R2.4, R5.3). No heading appears when there are no rulings.
- **tools/claude_station.py:** a docstring note only. validate_review_file already accepts unknown keys, so it accepts owner_ruling unchanged (S8).
- **stations/reviewer-*/PROMPT.md (all 10):** one sentence added after the "station field must equal" line, nothing removed (R1.2). The wording avoids the substring "set" ("Fill the optional field ..."), because tests/test_quality_same_subject.py scans the reviewer-design packet for "deliverable" plus "set".
- **anvil/sinks.py, anvil/observe.py, anvil/telemetry.py, pipelines/, anvil.json, .github/workflows and every existing test:** untouched. No event kind was added (S9 passes).

## Verification (base ref d74c83aefff95fba777ca04505116cfb63c6c8f3, an ancestor of HEAD 7a35056)
- `python -m unittest tests.test_stop_futile_loops`: `Ran 29 tests ... OK (skipped=2)`
- `ANVIL_WORK_ORDER_ID=wo-gh-49 python -m unittest tests.test_stop_futile_loops`: `OK` (all 29 run, including test_s10_protected_paths_untouched and test_s10_no_dashes_in_lines_this_order_adds)
- Full factory suite, `python -m unittest discover -s tests -p 'test_*.py'`: `Ran 862 tests in 83.842s` / `FAILED (failures=16, errors=1, skipped=16)`. The 17 break down as:
  - 10 are the R3/R5.2 contradiction listed above.
  - 7 already failed before this build, as the test-writer recorded: test_autonomous_line.TestHumanGate (3) and test_governed_delivery.TestApprovalPolicy (2) fail because the CI machine is not the authenticated GitHub actor, and test_token_efficiency.WrapperEvidenceTests has 1 error and 1 failure.
- `git diff --name-only --diff-filter=MD d74c83a -- tests .github/workflows pipelines anvil.json anvil/sinks.py anvil/telemetry.py`: empty.
- No em or en dash in the lines added outside runs/, and the word "retry" does not occur in anvil/runner.py.
- **Exercised by hand:** ran the S1 scripted line through the real run_pipeline and rendered tools/line_comment.py on its report. It showed exit_status owner_ruling_needed, the next human action, the human gate rule "Owner ruling needed: reviewer-spec ...", and the question under "### Owner ruling needed".

## New test files
- tests/test_stop_futile_loops.py (written by test-writer). The builder added none.

## Not done, not verified, open
- **Not written, because I stopped under R7.2:** docs/EXECUTION.md, docs/OPERATIONS.md, CHANGELOG.md and the decision record brain/decisions/0016-stop-futile-loops.md. They belong to the attempt after the owner's ruling. A comment in anvil/config.py already points to decision 0016.
- **No .gitignore outside git:** a project that is not a git work tree has its .gitignore ignored by the no_progress comparison. Files such as __pycache__ written during a builder attempt then count as a change, so the stop fails open (the line loops as today).
- **Trade-off:** a kept owner_ruling also stops a run whose counted reviews all pass (spec-writer decision 4). The verdict stays approved but the human gate is closed.
{"model": "claude-opus-5-5"}
