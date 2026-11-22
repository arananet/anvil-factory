I wrote no new tests this attempt. The two test files from the earlier pass still match the spec, which didn't change (only the base ref moved, to `ae0bbfb`), so I kept them. The handoff is in `runs/wo-gh-47/test-writer.output.md`.

**Test files** (neither exists at the base ref):
- `tests/test_live_progress_sinks.py`: 24 tests for the issue sink, config validation, what ships, and the guardrails.
- `tests/test_live_progress_project_sink.py`: 6 tests for the board sink.

All 16 spec scenarios, S1 to S16, have at least one test named after them; the full map is in the handoff. The tests run a real scripted pipeline through `anvil.runner.run_pipeline` against a local stand-in for the GitHub API, so nothing reaches real GitHub.

**Failing before the build:** on a copy of the base ref tree with the two files added, 28 of the 30 tests fail because the feature is missing (`KeyError: 'sinks'`, no requests reach the stand-in API, `ValueError not raised`, missing docs and module), not because of import errors. The other 2 (S13, S14) skip unless `ANVIL_WORK_ORDER_ID=wo-gh-47`.

**On this branch,** which already holds the earlier builder's work:
- The new tests pass: `Ran 30 tests ... OK (skipped=2)`. With `ANVIL_WORK_ORDER_ID=wo-gh-47` set, all 24 in the issue sink file run and pass.
- S3, the flaky test the operator fixed in 48a8e85, passed three runs in a row.

**Project check:** the base ref suite has 802 tests. The full suite here gives `Ran 832 tests`, `FAILED (failures=6, errors=1, skipped=14)`. Those 7 are older tests in `test_autonomous_line`, `test_governed_delivery` and `test_token_efficiency`, and the cause is this machine's environment. With `GITHUB_ACTOR` and the station's `ANVIL_*` variables unset, those three files run 51 tests and pass. The test that broke the gate last attempt (`test_station_budgets_completeness`) passes on this tree after the ae0bbfb fix.

**For review:**
- S13 says the runner must contain no `urllib`, but the base ref runner already imports `urllib.parse`. The test forbids `urllib.request`, `urlopen`, `http.client`, `import socket` and `retry` instead; a reviewer should confirm that reading.
- The spec lists a state write at run start, which the runner doesn't do today. S1 counts the writes that actually happen, so it holds either way.