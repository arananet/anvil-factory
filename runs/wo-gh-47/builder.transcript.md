Attempt 2 now changes three files, so the delta the checks gate rejected is no longer empty. The live-progress-sinks feature itself was already on the branch from the earlier passes. This attempt fixes one real defect I found re-reviewing it: when GitHub answers with an error (400 or higher), the sink left the connection open.

**Changes in this attempt**
- `anvil/sinks.py`: on an HTTP error, `Sink.request` now closes the response before passing the error on. Before, every failed request held a socket open until the error object was cleaned up. What gets recorded is unchanged: still `github-issue: HTTP <status>`.
- `tests/test_live_progress_sink_errors.py` (new): a local server answers 500 five times. The test checks that exactly one error is recorded and no connection stays open. Without the fix it fails with "6 descriptors held open"; with it, it passes.
- `CHANGELOG.md`: one line about the fix, and the new test file added to the entry's test list.

**Verification on the final tree**
- Full suite `python -m unittest discover -s tests -p 'test_*.py'`, run in the checks gate's environment: `Ran 833 tests`, `OK (skipped=14)`, exit 0. That is 802 at the base ref, 30 from the earlier passes and 1 new.
- The order's 31 tests with `ANVIL_WORK_ORDER_ID=wo-gh-47`, so the two checks that only run inside this order's own run (S13, S14) are included: `Ran 31 tests`, `OK`.
- Nothing changed under `.github/workflows`, `pipelines/`, `anvil.json`, `anvil/executor.py` or `tools/line_comment.py`. No existing test file was modified. `anvil/runner.py` contains no network imports and no "retry". No em or en dashes.

**Still open (also in the report)**
- **Resumed runs:** a resumed run gets no separate state write at the start; its first write comes just before the first remaining station. Adding a separate one would mean changing `anvil/runner.py` beyond the one line this order allows, so a reviewer needs to decide whether the current behaviour meets the spec.
- **Reading of "no `urllib` in `anvil/runner.py"`:** the runner already imports `urllib.parse` at the base ref, so the check bans network imports rather than the word `urllib`. A reviewer should confirm that reading.
- **Real GitHub:** neither sink has run against real GitHub, only a local test server.
- **`github-project` sink:** it ships documented and off, because the workflow has no token that can reach Projects.
- **Station environment:** in the builder station's own environment, 7 existing tests fail. They fail the same way on the base ref and pass in the checks gate's environment.

I did not commit anything. The report is at `runs/wo-gh-47/builder.output.md`.