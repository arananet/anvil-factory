# Builder report: wo-gh-42 (attempt 3 of 3)

Spec: .openspec/specs/station-budgets-completeness/spec.md (slug station-budgets-completeness).
Base ref verified: factory main 72a84126a600fafb99446946694b5de809e01e66. `git merge-base HEAD 72a84126a600fafb99446946694b5de809e01e66` returns 72a84126a600fafb99446946694b5de809e01e66.

## Attempt 3 summary

The only finding still open from the approver is R4 / S4, S5, S8: completeness runs only where partitions are configured. This attempt makes no code change. The finding needs an owner ruling, and this attempt adds fresh, measured evidence for that ruling (below). Everything that passed in attempt 2 is kept as it was. The previous report file was missing from the run tree, which made S10 (test_s10_builder_report_evidence) fail. This file restores it.

## Open: R4 scope needs an owner ruling (not fixed)

The spec's R4 says the completeness precondition runs before any reviewer dispatch, with no condition. The code runs it only when `completeness_active = any(station_budget_settings(config))` (anvil/runner.py, in run_pipeline, next to the partition validation). The pre-review check depends on that flag. Decision 0014 records the scoping.

In this attempt I checked whether a principled change could make the gate unconditional without touching protected tests. It cannot. Measured on the final tree:

- I temporarily replaced the flag with `True` and ran the full suite: `Ran 799 tests`, `FAILED (failures=21, errors=2, skipped=6)`. That is 22 protected existing tests across test_anvil, test_checks_gate, test_continuous_run_accounting, test_model_migration_round4, test_practice_skills, test_reviewer_ux, test_risk_routing and test_station_artifact_contract. The 23rd failure was S10, caused by the missing report.
- I instrumented the gaps those runs produced. The dominant ones are "the builder changed no file" (an empty run delta, which S8 requires as a gap), "test-writer test files absent", and "checks gate verdict is not_configured, not pass". Under R4(a), R4(b) and S8 these are true gaps for those fixtures: their scripted builders write no file and many configure no checks. Treating not_configured as pass, or an empty delta as complete, would contradict the spec's own text. So the conflict cannot be closed inside the write set.
- I restored the change afterwards. `git diff` on anvil/runner.py matches attempt 2.

The owner needs to choose one of these:
1. Amend R4 to scope completeness to projects that configure efficiency partitions. That matches the current code and decision 0014. The spec file is outside this order's write set, so the builder did not edit it.
2. Authorize updates to the 22 protected tests, then change the flag to always on. That is a one-line runner change.

## What shipped (unchanged since attempt 2), by scenario

- R1 / S3: anvil/config.py adds `efficiency.station_budgets`, `efficiency.default_station_budget` and `validate_station_budgets`. The worst case per pipeline must fit max_run_tokens 15000000; an over-cap set fails with the pipeline and excess named. The factory anvil.yaml partitions for sdlc-default:

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
  | sum | 15000000 |

  Verified by loading anvil.yaml through anvil.config.load_anvil_config: the sum is 15000000. The checks gate takes no partition.
- R2 / S2, S7: anvil/runner.py runs a pre-call check before first, correction and loopback dispatches. It reads the per-attempt usage artifacts, refuses an exhausted station with zero model calls, and records the refusal (station, partition, consumed, refused_at). With require_usage set, an unmeasured station counts as exhausted; otherwise the record says proceeded_unmeasured. The run then ends through the wo-gh-41 exit path (exit_status budget_exceeded).
- R3 / S1: tools/claude_station.py adds an in-flight ceiling that kills the session when measured usage crosses the partition. anvil/executor.py surfaces the budget_exceeded record with the partial usage.
- R4 / S4, S5, S8, S9: `completeness_gaps` in anvil/runner.py checks the report, the test-writer files, the run delta, the gate verdict, and failed stations that left no artifact. Gaps loop back to the builder and zero reviewers are dispatched. Results are recorded in their own completeness field set. The check runs no command and repeats no literal validation. Scope as described above.
- R5 / S6: anvil/telemetry.py adds per-station partition, consumed and priced amount, labelled as priced from the recorded table. A station with no price entry shows tokens only.
- R7 / S10: docs/EXECUTION.md (names both budget keys and the difference from the top level packet station_budgets key), CHANGELOG.md (wo-gh-42 entry), brain/decisions/0014-station-budgets-completeness.md.

## New test files

- tests/test_station_budgets_completeness.py (28 tests)

## Verification (final tree)

- `env -u GITHUB_ACTIONS -u GITHUB_ACTOR -u GITHUB_ACTOR_ID python -m unittest discover -s tests -p 'test_*.py'`: before this report was written, `Ran 799 tests`, `FAILED (failures=1, skipped=6)`. The one failure was test_s10_builder_report_evidence (report missing). Rerun after writing it, same command: `Ran 799 tests`, `OK (skipped=6)`.
- `git diff --name-only 72a84126a600fafb99446946694b5de809e01e66 -- tests pipelines anvil.json`: empty.
- Full factory test count: 799 tests (771 at base plus 28 new).

## Left open / unverified

- R4 unconditional scope: needs an owner ruling (above).
- The in-session correction refusal (wrapper exit 12) has no test through the runner. The S2 loopback path is tested.
- The in-flight ceiling has only been exercised against a stand-in claude CLI. When no usage events stream, it fails open to the pre-call check and the run cap.
- If an outside timeout kills the wrapper, the CLI child can be orphaned (security follow-up, not fixed).
- The emptiness check reads the whole file. A bounded read would be cheaper (nit).
{"model": "claude-opus-5-5"}
