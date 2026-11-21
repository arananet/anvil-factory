Nothing was released, so I wrote the observation report at `runs/wo-gh-42/observer.output.md` about the run and the tree as they stand. The deployer only prepared a release packet (status `packet_ready`) and never wrote a release record. The run report shows no deployment, a final verdict of `changes_requested`, and a stop at the owner's decision point, as the order's guardrails require. The change is still uncommitted in the worktree.

**What happened in the run**
- The builder ran 3 times, the maximum allowed. The automated test check passed every time, and all five reviewers asked for changes every time.
- The one blocking issue was the same in all three rounds. The spec (R4) says the completeness check always runs before reviewers, but the code only runs it when per-station token limits are configured (`anvil/runner.py:1652` and `:2440`). Making it always run breaks 22 existing tests that the order forbids changing. Only you can settle this: amend R4, or allow those tests to be updated.
- The builder's third attempt changed no code. It only restored its missing report.

**Token use**
- The run used 14,504,811 tokens against the 15,000,000 run cap. The builder used 10,135,682 of those, 9,281,113 of them in its first attempt.
- No cost in money could be shown: all 21 steps have no price recorded.

**The per-station limits look too small.** They were not in force for this run, because it ran on the code from before this change. Measured against this order's own usage, four stations would have gone over their limit:

| Station | Used in this run | Limit in the shipped table |
|---|---|---|
| builder (first attempt alone) | 9,281,113 | 6,400,000 |
| reviewer-spec | 851,725 | 600,000 |
| reviewer-security | 626,896 | 600,000 |
| reviewer-tests | 1,145,297 | 600,000 |

That contradicts the correction's claim that the table covers the largest use seen per station. You should weigh this before merging.

**Checks I re-ran myself**
- The full test suite passed: 799 tests, 6 skipped, matching the builder's report.
- None of the protected files (existing tests, pipeline files, `anvil.json`) changed.
- No em dash or en dash appears in the changed files.

To observe a real release later, I'll need the merge commit or pull request and a factory run on main with the new limits active.