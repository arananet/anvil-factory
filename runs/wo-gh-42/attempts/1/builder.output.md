# Builder report: wo-gh-42 (station-budgets-completeness)

Spec: .openspec/specs/station-budgets-completeness/spec.md (slug station-budgets-completeness).

## Base ref verified

The tree was verified against factory main 72a84126a600fafb99446946694b5de809e01e66, which is HEAD~1 of this branch. HEAD is the owner's correction commit 1d8f96a. `git diff 72a84126a600fafb99446946694b5de809e01e66 --name-only` plus the untracked files lists only allowed paths: the S11 tests pass, and pipelines/, anvil.json and the existing tests are untouched. The base anvil.yaml carries max_run_tokens 15000000, max_runtime_turns 100 and max_packet_tokens 48000. None of them changed.

## Partition table shipped (anvil.yaml, efficiency.station_budgets, sdlc-default)

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
| **sum** | **15000000** |

The sum is exactly 15000000, equal to max_run_tokens. No efficiency.default_station_budget is set. Every sdlc-default station is named and the sum already equals the cap, so any default would fail validation for any pipeline with an unnamed model station. Worst cases computed by `validate_station_budgets` over every factory pipeline: sdlc-default 15000000, greenfield 13800000, plan-build-test 11200000, hotfix 8400000, docs-only 7400000, content-default 2100000, content-short 1700000, scout 0.

## What changed, by scenario

- **anvil/config.py (R1, S3):**
  - `station_budget_settings` validates both keys: positive integers only, rejecting bool, str, float and negative values, with the station named in the error.
  - `is_model_station` treats agent kind and intake as model stations.
  - `pipeline_partitions` builds the partitions: named stations, plus the default for unnamed model stations. The checks gate takes none.
  - `validate_station_budgets(config, pipelines, registry)` returns each pipeline's worst case. It raises ValueError naming the pipeline and the excess. A worst case equal to the cap loads.
- **anvil.yaml (R1, S3):** the 14-station table above, inside the efficiency section. No other key changed. The top level packet `station_budgets` lookup is unaffected.
- **anvil/telemetry.py (R2, S2, S7):**
  - `station_consumption` sums a station's consumption over all of its dispatches, from the per-attempt usage records each step carries from `<station>.output.md.usage.json`. Its consumed value is None when any call went unmeasured.
  - `precall_decision` returns proceed, refuse or proceed_unmeasured.
- **anvil/runner.py (R1 to R5; S1, S2, S4 to S9):**
  - The partitions are validated at run start, before any model call.
  - The pre-call check runs before every first dispatch and loopback re-dispatch. A refusal adds a step with no executor and a budget outcome (station, partition, consumed, refused_at), then ends the run through the wo-gh-41 exit path: exit_status budget_exceeded, a termination_reason naming the station and its partition, unreached stations not_run.
  - An unmeasured re-dispatch is refused under require_usage. Without it the dispatch proceeds and is recorded as proceeded_unmeasured.
  - The wrapper gets the rest of the partition as ANVIL_STATION_BUDGET_TOKENS and the partition as ANVIL_STATION_PARTITION. A ceiling kill becomes a step with status budget_exceeded, the partial usage, the dispatched model as executed_model and a `budget_ceiling` record, and `_station_stop` ends the run.
  - The completeness precondition (`completeness_gaps`) runs after the pre-review gate and before any reviewer. Gaps send the attempt back to the builder as a gate loopback, bounded by max_loopbacks, and reviewers are skipped. The report gets its own `completeness` list (attempt, passed, gaps, gate_verdict). The gate's step and verdict are untouched.
  - The report also gets `budgets` (stations and outcomes) and `cost.stations`: partition, consumed, amount, priced and source, labelled as priced from the recorded table and not an invoice. A station without a price shows tokens only.
- **anvil/executor.py (R3):** the usage evidence exposes a wrapper `budget_exceeded` attempt as `result["budget_exceeded"]`, alongside the existing timeout handling.
- **tools/claude_station.py (R3, R2 correction re-dispatch, S1):**
  - When a ceiling is set, Claude runs with `--output-format stream-json --verbose`. A reader thread sums usage per message id, and the session's process group is killed once usage reaches the ceiling.
  - The attempt is recorded with status budget_exceeded, station, partition, reason, configured_model and partial usage, and the wrapper exits 11. Undone work is not resumed.
  - A reviewer's correction re-dispatch is refused with zero calls once the partition is spent (exit 12, marker text shared with the runner).
  - Without a ceiling, the old json path runs unchanged. The copilot runtime runs without a ceiling and the wrapper says so on stderr.
- **docs/EXECUTION.md (R7, S10):** a new section, "Per-station token budgets and the completeness gate". It names efficiency.station_budgets, efficiency.default_station_budget and the top level station_budgets packet cap, and states the difference. It also covers load time validation, the pre-call check, the in-flight ceiling and the completeness precondition.
- **CHANGELOG.md (R7):** a wo-gh-42 entry.
- **brain/decisions/0014-station-budgets-completeness.md (R7):** the partition decision and what it makes harder.

## Verification

- `python -m unittest tests.test_station_budgets_completeness`: Ran 26 tests, OK. This is the test-writer's file, unmodified.
- Full suite, run the way factory CI runs it (without GITHUB_ACTIONS, GITHUB_ACTOR and GITHUB_ACTOR_ID): `env -u GITHUB_ACTIONS -u GITHUB_ACTOR -u GITHUB_ACTOR_ID python -m unittest discover -s tests -p 'test_*.py'`: **Ran 797 tests, OK (skipped=6)** on the final tree. That is 797 tests in total: 771 existing tests and the 26 new ones.
- I exercised the wrapper by hand against a stand-in claude CLI:
  - A builder with a 100000 ceiling finished in stream mode: exit 0, status succeeded, 15 tokens measured.
  - A 10 token ceiling killed a session mid-stream: exit 11, budget_exceeded, 15 tokens.
  - A reviewer whose first answer wrote no review had its correction refused: exit 12, one attempt recorded, no second call.
  - A malformed ceiling value: exit 10, value named.
  - No ceiling: the json path, unchanged.
- Validating the factory anvil.yaml over all eight pipelines passes. Raising builder by one token fails with "pipeline sdlc-default: worst case 15000001 tokens exceeds max_run_tokens 15000000 by 1".

## New test files

- tests/test_station_budgets_completeness.py. The test-writer station wrote it; I did not edit it. I added no other test file.

## Unmet, unverified or open

- **Completeness only runs in projects that configure partitions.** The runner evaluates the precondition only when efficiency.station_budgets or efficiency.default_station_budget is configured. The factory's own anvil.yaml configures them, so factory runs get the gate.
  - Applied to every project, it broke 22 existing protected tests: 20 failures and 2 errors, in test_station_artifact_contract (9), test_checks_gate (3), test_continuous_run_accounting, test_practice_skills, test_reviewer_ux, test_model_migration_round4 (2 each), test_anvil and test_risk_routing (1 each). Those tests run sdlc-default with scripted stations that write no test files and no delta, and expect reviewers to run.
  - The order forbids editing them, so I scoped the gate and recorded it in decision 0014. Turning it on for every project is an owner decision, and those tests would need updating.
- **Validation runs only for the pipeline being run.** At run start the runner validates the pipeline it is about to run, not every file under pipelines/. `validate_station_budgets` accepts any list of pipelines, and the factory tests run it over all eight.
- **The ceiling has only been run against a stand-in CLI.** It depends on Claude Code's stream-json assistant events carrying per-message usage, and I could not reach the real CLI here.
- **Usage is summed per message id.** If a message's usage is repeated, the latest value counts, and cache-inclusive counts are normalised as for the json envelope.
- **Copilot has no in-flight ceiling.** The copilot runtime exposes usage only at the end of a session, so it gets the pre-call check but no ceiling.
- **The correction refusal is not fully covered by tests.** The new test file does not cover the in-session correction refusal through the runner. I only exercised the wrapper side by hand.
- **wo-gh-28 is not present.** The deterministic preflight is not on this base, so completeness reads the checks verdict as it exists, including the artifact contract's own validation result.
- I made no commit, merge, publish or deploy.
{"model": "claude-opus-5-5"}
