I revised the spec in place at `.openspec/specs/continuous-run-accounting/spec.md`. An earlier attempt of this order had already written it, and I checked it line by line against the work order again: nothing in the order is missing. I changed only the clean-baseline check, because as written it could never pass. No tests were run, since this station only edits the spec.

**The problem:** S9 required that diffing against the parent ref `4675a131eb9aa88097741dc3cdc9772c3db17550` show no modified test files. Since that commit, main has picked up owner-authorized operator edits to existing tests. That includes commit `5354c71`, which changed `tests/test_governed_delivery.py` for this very order so a crashed run may leave a completed report. So S9 would fail no matter what the builder did. Against current main (`5354c7130e116658cc31dec270738ffaf2de67d6`), the only test difference on the branch is the new file `tests/test_continuous_run_accounting.py`.

**What I changed:**
- **R4.2:** "existing test file" now means a test file present on main at the run branch's merge base (`5354c71` at this revision). The operator test edits made after `4675a13` count as part of that baseline, not as changes by this order.
- **S9:** the check is now `git diff --diff-filter=MD` from that merge base to the built tree, and it must list nothing under `tests/`. The builder report must name the merge base as the base ref it checked against, alongside the parent ref `4675a13`.
- **Allowed write set:** `tests/test_continuous_run_accounting.py`, left on this branch by an earlier attempt, counts as new and may be revised. The rule against editing existing test files now points at the R4.2 merge base.

R1.1 to R1.3, R2.1 to R2.5, R3.1 to R3.3, R4.1 and scenarios S1 to S8 are unchanged. The spec still has no em or en dash characters.

**For the owner to decide:**
- **Parent ref:** the work order says the order is parented on `4675a13` and that test files "at the base ref" are protected. I read the base ref as current main, because of your operator commits. Please confirm.
- **Resuming from a checkpoint:** automatically restarting execution from the last checkpoint stays out of scope. Please confirm.
- **SIGKILL and host loss:** for these kills the last checkpoint is the only record. Please confirm that is acceptable.
- **Code already on the branch:** the earlier attempt left partial changes in `anvil/runner.py`, `anvil/line.py`, `tools/line_comment.py`, `docs/EXECUTION.md`, `CHANGELOG.md`, `brain/decisions/0013-continuous-run-accounting.md` and the new test file. Decide whether the builder reuses or redoes them.
{"model": "claude-opus-5-5"}
