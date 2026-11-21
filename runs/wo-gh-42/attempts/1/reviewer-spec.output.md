My verdict is **changes_requested**: the change meets the spec everywhere except one place, and that one needs your decision rather than a builder fix. The review is written to `runs/wo-gh-42/reviewer-spec.review.json`.

**What needs your decision (R4):** the spec says the completeness check runs before every reviewer dispatch, with no conditions. The builder only turns it on when a project configures token partitions (`anvil/runner.py:1650` and `:2438`). The factory's own `anvil.yaml` does configure them, so factory runs get the check; any other project skips it and can still send unfinished work to review.

The builder says that turning it on everywhere breaks 22 existing tests, which the order says must not be edited. They wrote this down in decision 0014. This is a conflict inside the order itself, so the builder cannot fix it on a loopback. You can either:
- change R4 so the check only applies where partitions are configured, or
- allow those 22 tests to be updated so the check can run everywhere.

**Everything else matches the spec:**
- **Partition table:** it is exactly the corrected one and sums to 15000000. Configurations over the cap fail to load and the error names the pipeline and the excess.
- **Check before each dispatch:** it runs before first attempts, loopbacks and reviewer corrections. Refusals make no model call and are recorded. Usage that was never measured is not counted as zero.
- **Session kill at the partition:** it works and is recorded as `budget_exceeded` with the partial usage. It has only been run against a stand-in for the Claude CLI, not the real one. The Copilot runtime has no mid-session kill, only the check before each dispatch.
- **Completeness mechanics, where it is on:** it does not re-run the suite or repeat the literal checks.
- **Cost section:** it labels amounts as priced from the recorded table, and unpriced stations show tokens only.
- **Docs, changelog, decision record and builder report:** all present.
- **Protected paths and dashes:** nothing under `pipelines/`, `anvil.json` or the existing tests changed, and no em or en dashes appear.

One small test gap: refusing a reviewer's correction attempt has no test through the runner; only the loopback refusal is tested.

I re-ran the new test file together with the two protected tests the spec names: 81 tests passed. I did not re-run the full suite. The builder reports 797 tests passing (6 skipped), and the checks gate before review passed.
{"model": "claude-opus-5-5"}
