There was nothing to observe: wo-gh-47 has not been released. The deployer stopped at `packet_ready` without producing a release record, and `report.json` has `deployment_status: null`. The work order expects this, because nothing in this order merges or deploys. I wrote the observation report to `runs/wo-gh-47/observer.output.md`. It says the release record is missing and summarises what the run records show.

**The run itself:** the verdict was `approved` with one loopback, after the first builder attempt changed no file. All five counted reviewers passed and `reviewer-ux` was routed out. The run used 3,657,038 measured tokens and recorded no export errors.

**Things the owner should look at before merging:**
1. **Human gate:** the work order says the run stops at the owner gate. Instead, `triage-human` shows `completed` in 0.028 ms, `human_required` is `false`, and the line went on to the deployer and observer stations. Nothing was deployed, but the run did not stop where the work order says it should.
2. **Uncommitted changes:** these exist only in the working tree, not on the run branch:
   - an edit to `anvil/sinks.py` (closes the failed HTTP response before re-raising the error)
   - an edit to `CHANGELOG.md`
   - the new file `tests/test_live_progress_sink_errors.py`

   `CHANGELOG.md` names that test file, so the committed branch alone would refer to a file it does not contain.
3. **Files outside the allowed scope:** the changes against the base ref include files under `status/`, which the order does not authorise. Two earlier ANVIL runs of this order committed them, and they look like status pages the line generates rather than builder work.
4. **Test suite here:** 833 tests ran, with 6 failures, 1 error and 14 skipped. The same 7 tests fail the same way on a clean checkout of the base ref `ae0bbfb`. They come from the GitHub and `ANVIL_*` variables set in this environment, not from this change. The line's own checks-gate run exited 0.

R4 holds: the factory `anvil.yaml` and the scaffold for new projects both turn on the `github-issue` sink.

To observe a released change, this station needs a deployer release record, and that can only exist after the owner merges.