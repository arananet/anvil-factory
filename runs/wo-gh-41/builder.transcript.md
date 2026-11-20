The continuous-run-accounting build for wo-gh-41 is ready for review, and this attempt needed no code change. The implementation from the earlier attempts is already on the branch and meets scenarios S1 to S9. The report is at `runs/wo-gh-41/builder.output.md` and contains all the required literals.

- **The earlier blocker is gone:** a protected test asserted that a crashed run leaves no report, which this order directly contradicts. Your commit 5354c71 removed that assertion and is merged into the branch, so the conflict no longer exists.
- **Full suite:** `Ran 760 tests ... OK (skipped=6)` when run with `GITHUB_ACTOR`, `GITHUB_ACTIONS` and `GITHUB_ACTOR_ID` unset. That is 741 tests at the base ref plus 19 new.
- **Full suite in the raw CI environment:** 5 failures. All are approval-identity tests (3 in `test_autonomous_line`, 2 in `test_governed_delivery`) that refuse their `--by` test identities because this runner sets `GITHUB_ACTOR`. They fail the same way at the base ref, and the 19 new tests pass in both environments.
- **New tests:** 19 in `tests/test_continuous_run_accounting.py`, which is the only test file the order adds. No existing test file is modified or deleted relative to the base ref 5354c71.
- **Write set:** the changes stay inside the authorized surface. Nothing under `pipelines/` changed, and `anvil.json` is untouched.
- **Run end to end:** I scripted a run where the builder crosses the token cap. The runtime received no call after the builder. The record has exit status `budget_exceeded`, the 6,359,859 tokens measured against the 6,000,000 cap, and the builder's partial usage. Every later station is listed as not run, and `tools/line_comment.py` renders the record.

Gaps, also stated in the report:
- No test covers a budget death where the runtime reports no usage for the station in flight. The code records a reason in that case, but a fake runtime can't cross the cap without reporting usage.
- The checks-gate stop before deploy is implemented but not tested; only the stop before review has a test.
- The `anvil runs` inspect command reads through `anvil/observe.py`, which is outside the allowed files, so it is unchanged. The resume path is updated.