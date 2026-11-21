# Observation report: wo-gh-42 (station-budgets-completeness)

Observer, 2026-11-21. Run id fa800c2ff04f424283b0b3a573742b02, pipeline sdlc-default, branch anvil/wo-gh-42.

## Headline

Nothing was released. No release record exists. The deployer finished with status `packet_ready`: it wrote `runs/wo-gh-42/deployer.packet.md` and no `deployer.output.md`. `report.json` has `deployment_status: null`, `verdict: changes_requested` and `human_required: true`. That matches the order's guardrail ("Nothing in this order merges, publishes or deploys anything; the run stops at the owner human gate"). The change is still uncommitted in the worktree, on top of 1d8f96a, which is the correction commit over base 72a84126a600fafb99446946694b5de809e01e66.

**Missing input:** the station prompt asks for a release record. None was produced, so this report observes the run and the tree as they stand, not a released change. Once the owner decides, a real post-release observation needs the merge commit or PR, plus a factory run on main that uses the new partitions.

## What actually happened in the run

- 3 builder attempts (the cap: max_loopbacks used 2 of 2). Every attempt passed the checks gate. In every attempt all 5 counted reviewers (spec, security, tests, architecture, design) returned `changes_requested`. reviewer-ux was routed out every time.
- Final approver rule: "Reviewers reviewer-spec, reviewer-security, reviewer-tests, reviewer-architecture, reviewer-design requested changes." After that, triage-human was `completed` (envelope only, no human output file) and the deployer was `packet_ready`.
- The one blocking finding is the same in all three rounds. R4 in the spec requires an unconditional completeness precondition. The code gates it on partitions being configured: `anvil/runner.py:1652` sets `completeness_active = any(station_budget_settings(config))`, and `anvil/runner.py:2440` checks that flag. The builder measured that making it unconditional breaks 22 protected existing tests. The line cannot resolve this. It needs an owner ruling: amend R4, or authorize edits to the 22 tests.
- Builder attempt 3 made no code change (164 output tokens, 579 s). It only restored the builder report, which was missing from the run tree.

## Token consumption (report.json token_usage, measured, complete)

| station | calls | total tokens | shipped partition (R1) |
|---|---|---|---|
| intake | 1 | 100555 | 200000 |
| spec-writer | 1 | 287440 | 600000 |
| test-writer | 1 | 318588 | 3200000 |
| builder | 3 | 10135682 | 6400000 |
| reviewer-spec | 3 | 851725 | 600000 |
| reviewer-security | 3 | 626896 | 600000 |
| reviewer-tests | 3 | 1145297 | 600000 |
| reviewer-architecture | 3 | 516643 | 600000 |
| reviewer-design | 3 | 521985 | 600000 |
| run total | 21 | 14504811 | run cap 15000000 |

Builder per attempt (events.jsonl): attempt 1 used 9281113, attempt 2 used 797986, attempt 3 used 56583. Money: `cost.total 0`, with 21 unmeasured steps, so no priced amount is available.

Observations from these numbers:
1. The run finished 495189 tokens (3.3%) under the 15000000 run cap.
2. The partitions this order ships were not in force for this run. The efficiency limits in the report list no station budgets, because the run executed the pre-change spine. Had they been in force, builder attempt 1 alone (9281113) would have crossed the 6400000 builder partition and hit the R3 in-flight ceiling. reviewer-spec (851725), reviewer-security (626896) and reviewer-tests (1145297) also passed their 600000 partitions over the three rounds. By the third round each would have been refused by the pre-call check or stopped by the in-flight ceiling. The partition table does not hold up against this order's own measured consumption. The owner should weigh this before merging. The correction claims the table "covers the largest consumption measured per station" across wo-gh-39, wo-gh-43 and wo-gh-41, and this run exceeds it for four stations.
3. Most of the spend went to the single first builder attempt (64% of the run), and it is almost all cache reads (9002513 cached input).

## State of the tree, checked independently by this station

- Full suite: `env -u GITHUB_ACTIONS -u GITHUB_ACTOR -u GITHUB_ACTOR_ID python -m unittest discover -s tests -p 'test_*.py'` gives `Ran 799 tests`, `OK (skipped=6)`. This matches the builder report (771 base plus 28 new).
- `git diff --name-only 72a84126a600fafb99446946694b5de809e01e66 -- tests pipelines anvil.json` is empty, so the protected paths are untouched (the correction commit 1d8f96a only touches the spec and work-orders/issue-42.json).
- No em dash or en dash in the changed or new files.
- The worktree has 12 uncommitted entries (9 modified, 3 untracked), as in the git status at the start.

## Unresolved, for the owner gate

1. R4 scope ruling (above). Until it is made, the change carries an open approver finding.
2. The partition table is undersized against this run's measured usage (observation 2).
3. Low-severity follow-ups carried by reviewers: the ceiling fails open when no usage events stream; the CLI child is orphaned on an outside kill; `_nonempty_file` reads whole files; the wrapper exit-12 correction refusal has no test through the runner.
{"model": "claude-opus-5-5"}
