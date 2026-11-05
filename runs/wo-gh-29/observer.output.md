I wrote the observation report to `runs/wo-gh-29/observer.output.md`. There was nothing released to observe, and I don't consider this run ready to release. The deployer record is only `packet_ready`, so the report describes what the run record shows rather than post-release behavior.

- **Checks gate:** it passed in round 2. 515 tests ran with exit code 0 and 3 skipped, and the round 1 failures (S8 provenance, executor signature) no longer appear.
- **Reviewers:** none produced a review, so the verdict is `no_reviews`. The approver and triage-human steps show `completed` anyway, but with no reviews behind them that is not an approval.
  - **Four reviewers failed on tier labels:** reviewer-spec, reviewer-tests and reviewer-architecture were given `review-balanced`, and reviewer-security was given `review-strong`. The new dispatch wrapper rejected both as unknown models. Routing is probably passing tier labels where concrete models are needed, and that needs fixing before a rerun.
  - **reviewer-design failed on a missing environment:** the Codex step exited because `OPENAI_BASE_URL` and `OPENAI_API_KEY` were not set. So this run doesn't show whether the Sol route works. The R8 smoke script and the operator's post-merge run are the remaining proof.
- **Stale files:** the observer envelope and `report.md` in the working tree are left over from an earlier attempt. The observer envelope shows `failed` with `ANVIL_CONFIGURED_MODEL environment variable not set`. `report.md` shows the checks gate as failed. I noted this in the report and did not touch either file.

The report contains no em or en dashes.
{"model": "claude-sonnet-5-5"}
