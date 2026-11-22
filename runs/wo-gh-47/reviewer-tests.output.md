The tests review passes, and I wrote it to `runs/wo-gh-47/reviewer-tests.review.json`.

- **Loopback finding is resolved.** Attempt 1 changed no file. Attempt 2 changes three files, all allowed for this order:
  - `anvil/sinks.py`: when the GitHub API answers with an HTTP error, the sink now closes that connection before passing the error on.
  - A new test, `tests/test_live_progress_sink_errors.py`, which checks this.
  - A matching `CHANGELOG.md` line.
- **I re-ran everything on the final tree.**
  - Full suite, with `GITHUB_ACTOR`, `GITHUB_TRIGGERING_ACTOR` and the station `ANVIL_*` variables unset: `Ran 833 tests`, `OK (skipped=14)`. This matches the builder's report.
  - The order's three test files with `ANVIL_WORK_ORDER_ID=wo-gh-47`: `Ran 31 tests`, `OK`. That includes S13 and S14, which skip without that variable.
- **The test count adds up.** There are 802 tests at the base ref (`ae0bbfb`). The earlier passes added 30 (24 in `tests/test_live_progress_sinks.py`, 6 in `tests/test_live_progress_project_sink.py`), and this attempt adds 1, making 833. All three test files are new, and no existing test file was edited or deleted.
- **The new test fails without the fix.** With `anvil/sinks.py` set back to its previous version, it fails with "5 descriptors held open by failed sink requests". With the fix back in place it passes, and the file is restored.
- **Every spec scenario has a test.** Scenarios S1 to S16 each have at least one test. The tests run real pipelines against a local HTTP stand-in for GitHub, so nothing reaches real GitHub.
- **One minor point, not a blocker:** the new test swaps out an internal helper (`note_for`) so it can keep the errors it checks. That ties the test to the helper's name. It also counts the process's open sockets while a local test server is running.

Two items stay open for the approver, as the spec review also noted:
- **Resumed runs:** a resumed run sends its first update just before its next station, not when it resumes. Sending one earlier would mean changing the runner beyond the one place this order allows.
- **Network check on the runner:** the test forbids network imports in `anvil/runner.py`. It does not forbid every mention of `urllib`, because the runner already imported `urllib.parse` before this order.
{"model": "claude-opus-5-5"}
