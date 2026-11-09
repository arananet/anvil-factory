I added `tests/test_station_artifact_contract.py`, with 13 tests mapped to S1–S4. Seven of them fail today, as expected before implementation. The other six pass, including the healthy-path and no-declared-literals baselines and the empty-captured-output case (S4a). The three-step expected-reviewer rewrite for S4b is covered below.

I didn't run the rest of the factory suite, so S5 isn't checked beyond the baseline tests in this file. I didn't change any existing test, pipeline file or source file. The new file has no em or en dashes.

**The 7 failing tests**
- **S1:** a reviewer with a missing or empty review file should be recorded `failed`. Its step detail should name `reviewer-tests.review.json` and say why. Today the step shows `executed`.
- **S2:** an abbreviated sha256 or an empty builder report should fail the pre-review `checks-gate` and loop back to the builder. No reviewer should run. Today the gate passes and reviewers launch.
- **S4c:** the builder chat-summary case is bounced the same way as the S2 abbreviated case.
- **S3 (end to end):** an expected reviewer that wrote no review file must not give a silent `approved`. The decision text must name it.
- **S3 (unit):** this test calls `aggregate_explained(reviews, expected=[...], uncounted={station: reason})`.

**Interface assumptions in the tests**
- `required_literals` is a top-level work order field, passed as a dict to `run_pipeline`.
- `aggregate_explained` takes the new `expected` and `uncounted` keyword arguments. That signature is my guess, because the spec doesn't fix it. If the implementer picks a different one, only that unit test needs adjusting.
- For a healthy run, the approver rule must still start with "All counted reviews passed." because today's text carries a count suffix.

**Fixture notes**
- `sdlc-default` routes `reviewer-ux` out for non-UI work, so S3 and S4b use `reviewer-architecture` as the target. The ux failure from the issue can't be reproduced through default routing.
- S4b accepts either outcome the spec allows, review collected or failed with the scope reason. It also asserts the review is counted. That is stricter than the spec's "or", so say if you'd rather it allow the scope-failure outcome.
{"model": "claude-sonnet-5-5"}
