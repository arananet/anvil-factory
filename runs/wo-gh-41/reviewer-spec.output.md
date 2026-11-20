The review passes: the change meets the continuous-run-accounting spec. I wrote it to `runs/wo-gh-41/reviewer-spec.review.json` with 9 findings.

**What I ran:**
- The 19 new tests in `tests/test_continuous_run_accounting.py` all pass.
- The full factory suite ran 760 tests: OK, 6 skipped. I unset the GitHub CI identity variables (`GITHUB_ACTOR`, `GITHUB_ACTIONS`, `GITHUB_ACTOR_ID`) first, as the builder did. The builder reports that with them set, 5 approval identity tests fail; they fail the same way at the base ref and are not part of this change.
- No existing test file, nothing under `pipelines/`, and not `anvil.json` was modified or deleted since the merge base `5354c71`.
- No em or en dashes in the added lines.

**How each requirement is met:**
- **Checkpoint after every station (R1):** `report.json` is rewritten after every station, including every path that stops the run early. Each write goes to a temporary file that is then renamed over the old one, so a read mid-run always gets valid JSON. If a write fails, the previous file stays and the reason goes to stderr. The final report is the last checkpoint plus the verdict, decision and exit fields.
- **Save on every exit path (R2):**
  - The exit statuses match the spec's list of eight exactly.
  - Stations that never ran are listed as `not_run`.
  - A budget death records the tokens measured, the cap, the station in flight and that station's partial usage.
  - The cost rules are unchanged.
  - Crashes and SIGTERM/SIGINT still complete the record before the run is marked crashed.
- **No second run for paperwork (R3):** the swimlane and `tools/line_comment.py` render a killed run's record from the file alone, and old reports render as before. Resume treats a killed run's record as its accounting. A later run copies the earlier report into `history/` before its first checkpoint.

**Gaps that don't block the pass:**
- **Untested branches:** no test covers a budget death where the station in flight reported no usage. The code for it exists, and the builder says so. The pre-deploy checks-gate stop and the knowledge-pack intake stop have no dedicated tests either, but the spec doesn't require them.
- **`anvil runs` doesn't show the exit status yet:** it reads through `anvil/observe.py`, which this change doesn't touch.
- **Spec edited during this run:** the spec has uncommitted edits that move the "existing test files" baseline from the parent ref `4675a13` to the merge base `5354c71`. The code and the new tests are consistent with that revision.
{"model": "claude-opus-5-5"}
