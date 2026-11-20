I passed the change on architecture fit. The review is written to `runs/wo-gh-41/reviewer-architecture.review.json`; the JSON parses and contains no em or en dashes. I reviewed the code and didn't re-run the tests. The spec and tests reviewers already ran the full suite: 760 tests, all passing with the GitHub identity variables unset.

**Why it fits:**
- **One owner for the record.** `RunAccounting` in `anvil/runner.py` is the only thing that writes the run record. Every `report.json` write in the runner now goes through `write_report_atomic`.
- **Same shape throughout.** The checkpoint and the final report are built the same way, so the cost rules stay unchanged as the order requires.
- **Report is plain data.** The swimlane renderer works from the report alone, and `tools/line_comment.py` and `anvil/line.py` (resume) read it as data without touching the runner's internal state.
- **Signal handling stays at the outer edge.** It installs only on the main thread, and the old handlers are put back afterwards.
- **Decision recorded honestly.** `brain/decisions/0013-continuous-run-accounting.md` says plainly that the line now stops at the station that overspent, timed out or hit the turn limit. It also states the cost: a reviewer timeout now means a re-run.
- **Guardrails kept.** Standard library only. No changes to `pipelines/`, `anvil.json` or existing test files, and the edits stay inside the allowed files. The `status/` changes in the diff come from the factory's own run commits, not from the builder.

**Non-blocking findings, for follow-up:**
- **Checkpoints are called from many places.** `acct.checkpoint` appears at about nine separate exit points inside the already very long `_run_pipeline`. Each early exit has to remember to save first, so one hook at the end of the station loop would be safer.
- **State is shared loosely.** `RunAccounting` reads live state through late-bound lambdas: `snapshot` is set once and then replaced later in the function. It also uses an `in_flight` dict that the station loop changes in place. This works and is tested, but who owns that state isn't obvious.
- **Decision record has an out-of-date line.** Decision 0013 still describes the `test_governed_delivery.py` conflict as open, but operator commit 5354c71 has already resolved it.
- **The `anvil runs` command doesn't show the new fields.** It reads through `anvil/observe.py`, which doesn't display `exit_status` or `termination_reason`. That file is outside this order's allowed files.
- **Old dead code.** `build_packet` in `anvil/runner.py` has unreachable code after `return text`. It was already there before this change.
{"model": "claude-opus-5-5"}
