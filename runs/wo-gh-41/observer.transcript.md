I couldn't observe a release, because none happened. The deployer stopped at `packet_ready` and wrote only its packet, with no release record. That is what the work order intends: nothing deploys until the owner approves at the human gate. My report is in `runs/wo-gh-41/observer.output.md` and lists the release record as the missing input.

What I could check on the branch before release:
- **Reviews:** the checks gate passed, the five reviewers that ran all returned pass, and the approver's verdict is approved.
- **Tests:** I re-ran `tests/test_continuous_run_accounting.py` and its 19 tests pass. The checks gate had already recorded the full suite at 760 tests OK, with 6 skipped.
- **Scope:** every changed file is inside the authorized surface, and nothing under `pipelines/` or in `anvil.json` changed.
- **Dashes:** the produced files I checked contain no em or en dash characters.
- **Uncommitted work:** the spec, the new test file and the run artifacts are still uncommitted.

**The new checkpointing has not run for real yet.** `runs/wo-gh-41/report.json` still belongs to the previous run (verdict `no_reviews`, no checkpoint fields), and this run has not updated it after any of its 14 stations. That is expected, since a run uses the factory's base runner rather than the code on the branch. Until a run happens after merge, only the scripted tests show the checkpointing and exit-path recording working. The report lists three things to watch then:
- report.json is written after every station and stays readable mid-run.
- A killed run (budget, timeout or SIGTERM) still leaves a complete record.
- Re-running a killed order keeps the old record in the run history.