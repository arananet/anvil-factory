# Observer report: wo-gh-42

Work order: wo-gh-42, station-budgets-completeness (per-station token budgets and the completeness precondition before review).
Run: d5e5335799cf4d87a9c7328822a7ab04, pipeline sdlc-default, started 2026-11-22T15:24:31Z, last update 2026-11-22T15:41:34Z.

## Input status: release record missing

The observer's input is a release record. None exists: the deployer step is recorded `packet_ready` (runs/wo-gh-42/state.json, events.jsonl), there is no runs/wo-gh-42/deployer.output.md, and report.json has `deployment_status: null`. This is what the order asks for: "Nothing in this order merges, publishes or deploys anything; the run stops at the owner human gate." So no release happened, and nothing released can be watched. This report covers only what the run recorded up to the deployer packet. It is not a post-release observation.

What is needed for a real observation: a deployer release record (or the owner's merge of the run branch into main), and after that a later factory run on main where the partitions and the completeness gate actually ran.

## What the run recorded

| Step | Status |
|---|---|
| intake, spec-writer, test-writer, builder | executed |
| checks-gate (pre-review, attempt 1, basis builder_delta) | passed: `Ran 802 tests`, `OK (skipped=6)` |
| reviewer-spec / security / tests / architecture / design | executed, all verdict pass (6 / 10 / 7 / 8 / 0 non-blocking findings) |
| reviewer-ux | routed_out |
| approver | completed, verdict approved ("All counted reviews passed. Expected 5 reviews after routing.") |
| triage-human | completed |
| deployer | packet_ready (no release) |

- Loopbacks: 0 (max_loopbacks applies, none used).
- Tokens: 9 model calls, all measured, 3204155 total tokens. That is well inside the 15000000 run cap. `efficiency.stopped` is false.
- Partitions in force for the run (report.json `efficiency.limits.station_budgets`): intake 200000, spec-writer 600000, test-writer 3200000, builder 6400000, six reviewers 600000 each, approver 200000, triage-human 100000, deployer 300000, observer 400000. Sum 15000000, equal to max_run_tokens 15000000. No budget refusal and no budget_exceeded outcome was recorded.
- Cost: `total 0, measured_steps 0, unmeasured_steps 9`. No price table covered the executed models, so money stays unmeasured (R5 behavior: tokens only, no price shown).
- Builder report states base ref 72a84126a600fafb99446946694b5de809e01e66 and 802 tests (771 at base plus 31 in tests/test_station_budgets_completeness.py, the only new test file).

## Observations for the owner gate

1. **No release, so no live evidence.** Nothing shows yet that R2 (pre-dispatch refusal), R3 (in-flight ceiling) or R4 (completeness) behave correctly in a real run. The only evidence is the scripted tests in the new test file. No run consumption came near a partition, so neither budget path ran here.
2. **The completeness outcome is not in report.json.** The key `completeness` is absent (null) from the top level of this run's report, even though the factory's anvil.yaml configures partitions and R4 says the outcome lands in the run report. This run's report may predate the build (the line's own report writer runs from the base code, not the code under review). The owner should confirm this on the first run after merge.
3. **Base refs differ.** report.json `base_ref` is 1d8f96ad8b9d3a259ebccdde0c2f4933ac5cd4e5 (the run branch correction commit that the checks gate's builder delta is measured from). The builder verified against factory main 72a84126a600fafb99446946694b5de809e01e66. Both are consistent with the order, but the two values mean different things.
4. **TDD red warning.** The project checks passed before the builder ran, so the new tests did not fail first (report.json warnings). reviewer-tests was told to verify the tests and passed them.
5. **Uncommitted working-tree changes.** At observation time the working tree holds uncommitted changes to tests/test_station_budgets_completeness.py. The diff adds three scope tests for the owner ruling of 2026-11-22 and exempts runs/*.packet.md from the tree evidence check. This is the order's own new file (not a protected file), but the change has to be in the commit the owner reviews.
6. **Human gate.** triage-human is recorded `completed` with `human_required: false`. The order says the run stops at the owner human gate. Merging remains the owner's decision; this station approves nothing.

## Evidence paths

- runs/wo-gh-42/state.json, runs/wo-gh-42/report.json, runs/wo-gh-42/events.jsonl
- runs/wo-gh-42/checks-gate.pre-review.output.md
- runs/wo-gh-42/reviewer-*.review.json
- runs/wo-gh-42/builder.output.md
{"model": "claude-opus-5-5"}
