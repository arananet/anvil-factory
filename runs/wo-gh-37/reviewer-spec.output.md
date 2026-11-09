I reviewed the change against the spec and passed it. The review is in `runs/wo-gh-37/reviewer-spec.review.json`. The full suite ran 621 tests with no failures (8 skipped).

All five scenarios (S1–S5) are met:
- **S1:** the runner reads the artifact back from the run tree, and chat output no longer overwrites a builder report the station wrote. Missing, empty or unparseable review artifacts fail the station with the reason on record.
- **S2:** the pre-review checks gate rejects a builder report that lacks any required literal in full. The work goes back to the builder and no reviewer runs.
- **S3:** an uncounted expected reviewer turns `approved` into `human_required`, and the decision text names the station and the reason.
- **S4:** two new test files cover the three observed failure modes, and no existing test file was touched.
- **S5:** nothing under `pipelines/` changed, there is no new dependency, and no em or en dashes appear in changed or new files.

I noted three minor points in the review, none blocking:
- `work_orders/wo-gh-37.json` was rewritten with `risk` changed from low to medium and `surfaces` from `api` to `deploy`. This looks like intake output, but the `deploy` surface may change human-gate behavior, so it is worth confirming.
- The spec file has a one-line change in the working tree that should be confirmed as intended.
- Reviewer artifacts are validated when the runner collects them, not inside the checks-gate step. That matches the spec's "as they are collected" wording.
{"model": "claude-sonnet-5-5"}
