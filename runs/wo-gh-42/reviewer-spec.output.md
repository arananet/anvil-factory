I'm requesting changes again on wo-gh-42 (re-review, attempt 3 of 3). The verdict is `changes_requested` and is saved in `runs/wo-gh-42/reviewer-spec.review.json`.

**Still open, and it needs your ruling:** the spec says the completeness check runs before every reviewer dispatch, with no condition. The code runs it only when station partitions are configured (`anvil/runner.py:1652`, used at `anvil/runner.py:2440`). So a project without partitions sends incomplete attempts straight to review. The spec's R4 is unchanged, and attempt 3 changed no code. The builder tried running the check unconditionally: 22 protected existing tests then fail (21 failures, 2 errors). Their test setups really do lack the artifacts the check requires, so this is a conflict between the spec and the rule protecting existing tests. The builder can't settle it inside this order. The two ways out are:
1. Amend R4 so completeness only applies to projects with configured partitions. This matches the current code and decision 0014.
2. Allow updates to those 22 protected tests, then make the check always run. That's a one-line runner change.

**Resolved:** the builder report (`runs/wo-gh-42/builder.output.md`) was missing from the run tree and is back, with the four required literals and the required evidence.

**No regressions:** the fixes from attempt 2 still hold, and the code hasn't changed since then.

**Checks I ran:**
- The new test file runs 28 tests, all passing.
- The full suite runs 799 tests, all passing with 6 skipped. That's the 771 base tests plus the 28 new ones.
- Nothing changed under `tests/`, `pipelines/` or `anvil.json` compared with the base commit.

One gap remains and doesn't block: the path where a station is refused mid-session for a correction has no test through the runner. The spec allows testing either a correction or a loopback, and the loopback path is tested.
{"model": "claude-opus-5-5"}
