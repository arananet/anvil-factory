The spec review passes, and I wrote it to `runs/wo-gh-47/reviewer-spec.review.json`. The order's three test files ran 31 tests, all passing, when I re-ran them with `ANVIL_WORK_ORDER_ID=wo-gh-47`. I did not re-run the full suite myself; the checks gate passed it.

- **Loopback finding is resolved.** Attempt 1 changed no file. Attempt 2 changes three files, all allowed for this order:
  - `anvil/sinks.py`: when the API answers with an HTTP error, the sink now closes that connection before passing the error on, so it no longer leaks a socket on every state write.
  - A new test, `tests/test_live_progress_sink_errors.py`, which checks this.
  - A matching line in `CHANGELOG.md`.

  This maps to R1.5 and scenario S3.
- **Rest of the spec:**
  - `anvil/runner.py` changes in exactly one place: it now passes the pipeline order to the recorder. It has no network code and no "retry".
  - State records gain only the new fields the spec allows, and sinks are called before the single `state.json` write.
  - Both sinks show the exit status as given, without a fixed list, so `runtime_refused` appears like any other final state.
  - The README section is 10 lines (the limit is 15), the decision record is present, and the attempt 2 files contain no em or en dash.
- **One open item for the approver or owner (R1.2):** a resumed run sends nothing to the sinks when it resumes. The first update comes just before the next remaining station. Sending one earlier with correct station rows would mean changing the runner beyond the one place the spec allows, so the spec contradicts itself here. The builder flagged it. I don't see it as a blocker: the resumed run finds its existing comment again and updates it on the next write.

The branch diff also touches files outside the allowed list (`status/*`, the work order file, `runs/`). Those come from line and operator commits, not from the builder.
{"model": "claude-opus-5-5"}
