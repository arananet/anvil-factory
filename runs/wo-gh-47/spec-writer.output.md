I checked the spec at `.openspec/specs/live-progress-sinks/spec.md` against the work order line by line and against the code at base ref `ae0bbfb2af95b41d96d8e2af7c9f8b787f54d83b`. It already covers the whole order, so I made no edits this attempt. I ran no tests; this station only checks the spec.

**Checks against the base ref:**
- `runtime_refused` is a real exit status in `anvil/runner.py:748` and `:874`. The spec says sinks show it as is (R2.5, S10), along with any future status.
- `GH_TOKEN` is on the station deny list at `anvil/executor.py:41`, which R5.3 relies on.
- `build_default_config` and `render_anvil_yaml` are in `anvil/config.py`, which is where R4.2 puts the default for new projects.
- `mark_crashed(run_dir, error)` and the default `timeout_seconds` of 5 are in `anvil/observe.py`, as R1.7 and R1.10 assume.
- `brain/decisions/0015` is still free; the highest existing record is 0014.
- The spec contains no em dash or en dash.

**Requirement and scenario ids (unchanged since the earlier spec-writer pass, only the base ref was moved by the operator in 491979f):**
- R1.1 to R1.10, R2.1 to R2.6, R3.1 to R3.6, R4.1 to R4.5, R5.1 to R5.3, R6.1 to R6.3.
- S1 to S16. The order's test items map like this: (a) S1, (b) S2, (c) S3, (d) S4, (e) S5 and S6, (f) S7, (g) S8, (h) S9. `runtime_refused` is S10, a crash is S11, and the order's own run evidence is S13, which skips unless `ANVIL_WORK_ORDER_ID` is `wo-gh-47`.
- Out of scope and the allowed write set are both stated, including the protected paths and the rule that existing test files are not modified.

**Still open for you to decide:**
1. **Board columns:** while deployer or observer runs, the card stays where it was. At the end, any result other than approved, and not a human gate, goes to Failed. That includes `gate_failed`, `no_reviews` and the dry-run `packet_ready`.
2. **Running the suite by hand:** if someone runs it with `GH_TOKEN` and `GITHUB_REPOSITORY` exported, the existing tests that scaffold `wo-gh-<n>` projects could comment on real issues. CI and the line's checks step don't carry `GH_TOKEN`, so they are safe. The existing tests can't be changed under this order.
3. **No retry:** when the GitHub API can't be reached, each state write can wait up to `timeout_seconds`.
4. **The Projects board can't run in the factory yet:** it needs a Projects token supplied by a workflow change, which this order forbids. So the github-project sink ships documented and off.
{"model": "claude-opus-5-5"}
