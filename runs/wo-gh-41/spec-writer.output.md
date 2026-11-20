I rewrote the spec at `.openspec/specs/continuous-run-accounting/spec.md`. I kept the Purpose section and split each requirement into numbered clauses. Every scenario now names the requirement ids it proves, and the file has no em or en dashes. I didn't run the test suite, since this station only writes the spec.

**What changed**
- **Requirements:**
  - **R1.1 to R1.3:** the checkpoint now has three named fields: `checkpoint.last_completed_station`, `elapsed_ms` and `usage_so_far`. Writes are atomic, go through a sibling temporary file and leave none behind. The final report equals the last checkpoint plus the verdict, decision and exit fields.
  - **R2.1 to R2.4:** each exit path has its own `exit_status` from a closed set: `completed`, `budget_exceeded`, `station_timeout`, `turn_limit`, `checks_stopped`, `intake_stopped`, `error`, `signal`. Each also carries a `termination_reason`. Stations that never ran get the status `not_run`. A budget death records the consumption, the cap, and the station in flight with its partial usage.
  - **R2.5 (new):** if completing the record fails, the last checkpoint is never truncated.
  - **R3.1 to R3.3:** inspect, resume and the report tools read the record without running any station. The earlier report is copied into `runs/<id>/history/` (the existing mechanism) before the new run writes its first checkpoint. Reports written before this change must still render.
  - **R4.1 to R4.2:** the tests are new files only, and the full suite must pass.
- **Scenarios:** S1 to S5 now use real values (6,359,529 tokens against the 6,000,000 cap, `RuntimeError("injected")`, SIGTERM and SIGINT). Four are new:
  - **S6:** atomic writes.
  - **S7:** old reports still render, using `runs/wo-gh-20/report.json`.
  - **S8:** the turn limit, checks gate and intake stop paths.
  - **S9:** the suite passes and the existing test files are unchanged against 4675a131eb9aa88097741dc3cdc9772c3db17550.
- **New sections:**
  - **Allowed write set:** the order's surface, with no changes to protected paths.
  - **Out of scope:** resuming execution from a checkpoint, the wo-gh-42 work, the frozen surfaces, SIGKILL, and the C64 project.
  - **Builder report required literals.**

**Decisions for you**
1. **Names I chose:** the field names and the eight `exit_status` values are mine; the order didn't specify them. Please confirm them or rename them.
2. **Verdict versus exit status:** today the `verdict` field also carries `budget_exceeded`. The spec adds `exit_status` alongside it and leaves `verdict` alone. You need to decide whether `verdict` should keep doing that.
3. **Untrappable kills:** for SIGKILL or host loss, I treated the last checkpoint as the record and put completion out of scope. The order didn't address these.
4. **"Resuming":** I read this as "reading the record", not re-running from the last checkpoint. Automatic resume of execution is listed as out of scope.
5. **Decision record number:** I suggested 0013. The staged wo-gh-42 may also take that number, and both orders edit `anvil/runner.py`, so whichever lands second has to renumber and rebase.
{"model": "claude-opus-5-5"}
