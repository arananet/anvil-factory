I reviewed the change and wrote a `pass` verdict to `runs/wo-gh-37/reviewer-security.review.json`. I did this by reading the diff of `anvil/` and `tools/`. I didn't run the test suite or the new test files.

- **No new attack surface:** the diff adds no dependency, network call, shell invocation or `eval`. It uses only the standard library.
- **Approver fails closed:** an expected reviewer that failed or wasn't counted now gives `human_required`, with the uncounted stations named. Before, it could approve silently on the remaining votes.
- **Builder report check:**
  - Each required literal must appear in full in the report.
  - Captured chat output is rejected when literals are required.
  - A stale `builder.output.md` is deleted before each builder attempt.
- **Residual risk, accepted:** a builder can write the literals into its report without doing the work and still pass this check. The reviewers stay the semantic control.
- **Wider reviewer file guard:** a reviewer may now also change single-level files named `runs/<wo>/<station>.*`. Every other changed path still fails the guard. The prefix is built from packet values, not model output, so the risk is low.
- **Work order input:** required literals go into the builder prompt with control characters stripped. They can come from a GitHub issue, which is untrusted, but that's the same trust level as the existing description field.
- **Protected paths:** `pipelines/` and the existing tests are untouched. The protected-path gate and the review parse contract are unchanged.

I found nothing that needs changes.
{"model": "claude-sonnet-5-5"}
