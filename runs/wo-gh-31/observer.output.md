I wrote the observation report to `runs/wo-gh-31/observer.output.md`. It says there is nothing to observe yet. The deployer status is `packet_ready` and no release record exists. I didn't guess at post-release outcomes.

- **Reviewers:** reviewer-spec and reviewer-tests both ran this round and passed. Both report R1 to R3 met, and reviewer-spec says `review-cheap` now resolves at hand-off, so the round 1 gap is closed.
- **Fix in place:** `anvil/config.py` line 27 maps `review-cheap` to `claude-sonnet-5-5`. The checks gate passed.
- **Stale reports:** `runs/wo-gh-31/report.md` and `report.json` still show round 1's `no_reviews` with both reviewers failed. They contradict the current envelopes and should be regenerated.
- **Unchecked claims:**
  - reviewer-spec had no `main` ref to diff against, so nobody confirmed that existing files under `tests/` are unmodified.
  - reviewer-tests ran only the new tests (4 pass), not the full suite.
  - Dispatcher loudness on unmapped values was checked by test and inspection, not by a live dispatch.
  - I didn't re-run the suite. The 586 tests OK (6 skipped) figure comes from reviewer-spec.
- **Not merged:** the change is still uncommitted edits on `anvil/run-tier-map`.

The report contains no em or en dashes.
{"model": "claude-sonnet-5-5"}
