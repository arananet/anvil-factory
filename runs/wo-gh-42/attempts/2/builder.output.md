# Builder report: wo-gh-42 (station-budgets-completeness), attempt 2

Base ref verified: 72a84126a600fafb99446946694b5de809e01e66 (factory main, merge base of HEAD 1d8f96a, which is the owner's correction commit on top of it). `git merge-base HEAD 72a84126a600fafb99446946694b5de809e01e66` returns 72a84126a600fafb99446946694b5de809e01e66.

Spec: .openspec/specs/station-budgets-completeness/spec.md

## Loopback findings from attempt 1 and what I did

1. reviewer-tests CHANGES REQUESTED (R4(a), S4): the missing builder report case had no test that could fail. Fixed.
   - `test_s4_missing_builder_report_dispatches_zero_reviewers` now requires a gap naming `runs/wo-sbc/builder.output.md`, not just any gap containing "builder".
   - New `test_s4_missing_report_alone_blocks_review_when_checks_pass`: the builder succeeds and changes `src/feature.py`, the test-writer writes its test file, the checks command passes, and the report is empty or whitespace only. Through the real runner, the gate's report validation always runs on an executed builder attempt and already fails an empty report. So this test stubs `anvil.runner.validate_builder_report` to return passed, standing in for a gate that passed. Assertions: gate_verdict pass, completeness failed with exactly one gap that names the report path, zero reviewer calls.
   - New `test_s4_completeness_gaps_names_a_missing_or_empty_report`: calls `anvil.runner.completeness_gaps` directly on an otherwise complete attempt with verdict pass. A missing, empty or whitespace-only report gives exactly one gap naming the report path. A real report gives no gaps.
   - Mutation check repeated: with `if not _nonempty_file(report):` replaced by `if False:` in completeness_gaps, `python -m unittest tests.test_station_budgets_completeness.CompletenessGate` gives `FAILED (failures=5)`. With the line restored, all tests pass.
   - The new test found a real defect, now fixed: `_nonempty_file` (anvil/runner.py) treated a whitespace-only file as present. The artifact contract's validate_builder_report treats it as empty. It now uses the same rule, `read_bytes().strip()`. The gate's own validation is unchanged.
2. approver R4 / S4, S5, S8 non-conformance (completeness runs only when partitions are configured): **not fixed, needs an owner ruling.** It cannot be fixed inside the guardrails. Running completeness for every project breaks 22 protected existing tests (scripted sdlc-default runs that write no test files and no delta), and existing test files at the base ref are protected. The scoping is still `completeness_active = any(station_budget_settings(config))` in anvil/runner.py and is recorded in decision 0014. The owner has two options:
   - amend R4 to say completeness applies where efficiency partitions are configured (the factory's own anvil.yaml configures them, so the factory runs it), or
   - authorize updates to those 22 tests, so the gate can run unconditionally (a one-line change in the runner).

## What changed (whole order, final tree)

- anvil.yaml (R1, S3): the efficiency.station_budgets partition table below. Nothing else changed.
- anvil/config.py (R1, S3): `station_budget_settings`, `validate_station_budgets` (worst case per pipeline against max_run_tokens, names the pipeline and the excess).
- anvil/telemetry.py (R2, S2, S7): measured consumption per station from the per-attempt usage artifacts, and `precall_decision`.
- anvil/runner.py (R2, R4, R5, S2, S4, S5, S6, S8, S9): the pre-call check before first and loopback dispatches, the completeness precondition (`completeness_gaps`) with its own `completeness` field set, budget outcomes, per-station cost entries priced from the recorded price table (not an invoice), and run end through the wo-gh-41 exit path. Attempt 2 change: `_nonempty_file` whitespace rule.
- anvil/executor.py, tools/claude_station.py (R2, R3, S1): partition env passed to the wrapper, in-session correction refusal (exit 12), streamed in-flight ceiling recording budget_exceeded with partial usage.
- docs/EXECUTION.md, CHANGELOG.md, brain/decisions/0014-station-budgets-completeness.md (R7, S10).
- tests/test_station_budgets_completeness.py (R6, S1 to S11): the only new test file. Attempt 2 adds 2 tests and tightens 1.

## Partition table shipped (efficiency.station_budgets, sdlc-default)

| station | partition |
|---|---|
| intake | 200000 |
| spec-writer | 600000 |
| test-writer | 3200000 |
| builder | 6400000 |
| reviewer-spec | 600000 |
| reviewer-security | 600000 |
| reviewer-tests | 600000 |
| reviewer-architecture | 600000 |
| reviewer-design | 600000 |
| reviewer-ux | 600000 |
| approver | 200000 |
| triage-human | 100000 |
| deployer | 300000 |
| observer | 400000 |

Sum: 15000000, equal to max_run_tokens 15000000. default_station_budget is left unset, because any positive default would push pipelines with unnamed model stations over the cap. The checks gate takes no partition.

## Verification (final tree)

- `env -u GITHUB_ACTIONS -u GITHUB_ACTOR -u GITHUB_ACTOR_ID python -m unittest discover -s tests -p 'test_*.py'`: `Ran 799 tests` ... `OK (skipped=6)`. That is 771 base tests plus 28 in the new file. The test count is 799 tests.
- `python -m unittest tests.test_station_budgets_completeness`: `Ran 28 tests` ... `OK`.
- `git diff --name-only 72a84126a600fafb99446946694b5de809e01e66 -- tests pipelines anvil.json`: empty (no existing test, pipeline or anvil.json touched; the new test file is untracked).
- New test files added: tests/test_station_budgets_completeness.py

## Unmet, unverified or open

- R4 unconditional completeness: open, waiting on the owner ruling above.
- The in-flight ceiling has been exercised only against a stand-in claude CLI (S1 test), not the real CLI. The copilot runtime has the pre-call check only, with no in-flight ceiling.
- The correction-refusal path (wrapper exit 12) has no test through the runner. S2 is tested on the loopback path.
- Security follow-ups from attempt 1, not addressed in this order: record "ceiling unmeasured" when a ceiling was set but no usage streamed; forward SIGTERM from the wrapper to the CLI's process group.
{"model": "claude-opus-5-5"}
