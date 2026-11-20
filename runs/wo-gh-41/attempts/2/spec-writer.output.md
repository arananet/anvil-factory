I revised the spec in place at `.openspec/specs/continuous-run-accounting/spec.md`. The earlier attempt of this order had already written it, so I made two small changes and kept everything else. I checked the work order against the spec line by line and found nothing missing. No tests were run, since this station only changes the spec.

**Changed:**
- **R4.1:** it now lists the S6 tests (atomic write and failed rename), the S8 tests (turn limit, checks gate stop, intake stop) and a SIGINT test next to the SIGTERM one. It also requires every scenario, S1 to S8, to be proved by a test method that names the scenario id in its name or docstring. Before this change, S6 and S8 were not tied to any test.
- **S6 and S8:** both now name R4.1 as well.
- **Allowed write set:** the decision record is now the specific file `brain/decisions/0013-continuous-run-accounting.md`. The earlier attempt already created it on this branch. The builder may revise it but may not add or edit any other decision record.

**Unchanged and already in line with the order:**
- R1.1 to R1.3 (checkpoint after every station, atomic writes, no added station or model call)
- R2.1 to R2.5 (every exit path completes the record, with a closed list of exit statuses)
- R3.1 to R3.3 (inspect and resume read the record, history is kept, old reports still render)
- R4.2 (the full suite passes and no existing test file is changed)
- Scenarios S1 to S5, S7 and S9, plus the guardrails, out of scope list and builder report required literals

I confirmed that `runs/wo-gh-20/report.json`, which S7 uses as its example of an old report, exists and has none of the new keys. The spec contains no em or en dashes.

**For the owner to decide:**
- **Resuming from a checkpoint:** the spec leaves automatically restarting execution from the last checkpoint out of scope, as the order implies. Confirm that is what you want.
- **SIGKILL and host loss:** for these kills the last checkpoint is the only record. Confirm that is acceptable.
- **Code already on the branch:** the earlier attempt left partial changes in `anvil/runner.py`, `anvil/line.py`, `docs/EXECUTION.md` and `CHANGELOG.md`. Decide whether the builder reuses or redoes them.
{"model": "claude-opus-5-5"}
