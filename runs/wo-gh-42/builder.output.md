# Builder report: wo-gh-42 (station-budgets-completeness), attempt after the owner ruling of 2026-11-22

Base ref verified against: 72a84126a600fafb99446946694b5de809e01e66 (factory main, carries wo-gh-41 continuous run accounting, the factory CI fix and the runtime refusal stop). The run cap is max_run_tokens 15000000 and is unchanged.

## What this attempt changed

The one blocking finding from run 44912754341 (R4 unconditional in the spec, scoped in code) is closed by the owner ruling of 2026-11-22 (commit eb22a19648b44a45f4fa464ab775f9ac2115806b). The spec now scopes the completeness precondition to projects that configure efficiency partitions. The code already does that: `anvil/runner.py:1652` sets `completeness_active = any(station_budget_settings(config))`, and the pre-review step at `anvil/runner.py:2440` runs the precondition only when that flag is set. As the ruling says, no code change was needed.

- `brain/decisions/0014-station-budgets-completeness.md`: the Decision section now cites the owner ruling of 2026-11-22 and says the spec carries it in R4, S4, S5 and S8. The record had described the scoping as the builder's choice. It now matches the spec. (R7, S10)

No other file changed in this attempt. The implementation from the earlier attempts stands on the branch:

| File | Requirement / scenario |
|---|---|
| anvil/config.py (`station_budget_settings`, `validate_station_budgets`) | R1 / S3 |
| anvil.yaml (efficiency.station_budgets only) | R1 / S3 |
| anvil/runner.py (pre-call check, budget outcomes, completeness precondition, report fields `budgets`, `completeness`, `cost.stations`) | R2, R4, R5 / S2, S4, S5, S6, S7, S8, S9 |
| anvil/executor.py (budget_exceeded record) | R3 / S1 |
| anvil/telemetry.py (priced per-station consumption) | R5 / S6 |
| tools/claude_station.py (in-flight ceiling) | R3 / S1 |
| docs/EXECUTION.md, CHANGELOG.md, brain/decisions/0014-station-budgets-completeness.md | R7 / S10 |
| tests/test_station_budgets_completeness.py (new file) | R6 / S1 to S11 |

## Partition table shipped (anvil.yaml efficiency.station_budgets)

| Station | Partition |
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

Sum: 15000000, which equals max_run_tokens 15000000. There is no default_station_budget. The checks gate is deterministic and has no partition. Checked by calling `anvil.config.load_anvil_config('anvil.yaml')` and `station_budget_settings`, which printed `14 partitions sum 15000000 default None cap 15000000`.

## Verification

- Project check, with the host identity variables unset as factory CI runs it: `env -u GITHUB_ACTIONS -u GITHUB_ACTOR -u GITHUB_ACTOR_ID python -m unittest discover -s tests -p 'test_*.py'`
  - Before this report existed: `Ran 802 tests`, `FAILED (failures=1, skipped=6)`. The one failure was `test_s10_builder_report_evidence`, because this report file did not exist yet.
  - Final tree, after writing this report: `Ran 802 tests`, `OK (skipped=6)`. The full factory test count is 802 tests: 771 at the base ref plus 31 in the new file.
- `git diff --name-only 72a84126a600fafb99446946694b5de809e01e66 -- tests pipelines anvil.json` lists only `tests/test_station_budgets_completeness.py`. No existing test file, no pipeline file and no anvil.json changed.
- No em dash or en dash in the decision record or in this report.

New test files added: tests/test_station_budgets_completeness.py (the only one).

## Open, not done in this order

- The completeness precondition does not run in projects that configure no partitions (owner ruling). Making it unconditional needs its own order, because it breaks 22 protected existing tests.
- Non-blocking reviewer follow-ups, not built here so the change stays small: (1) the in-flight ceiling fails open to the pre-call check and the run cap when the CLI streams no usage events; it should record "ceiling unmeasured". (2) The wrapper does not forward SIGTERM to the CLI child's process group if an outside timeout kills it. (3) `_nonempty_file` uses `read_bytes` where a bounded read would do.
- No test covers the in-session correction refusal (wrapper exit 12) through the runner. S2 is covered on the loopback path.
- The in-flight ceiling (S1) has only been run against a stand-in claude CLI, not the real runtime.
- Which runs first, this order or wo-gh-28, is the owner's decision. Completeness works either way.
{"model": "claude-opus-5-5"}
