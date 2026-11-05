I wrote the review to `runs/wo-gh-29/reviewer-architecture.review.json` with verdict `pass`. It rests on a quick read of the dispatch and Codex wrapper code and a grep for retired models and dashes. I did not run the test suite.

- **Dispatch layering:** `tools/dispatch_station.py` picks the runtime from the concrete model and fails loudly on anything unknown, which matches R3 and decision 0004.
- **Codex runtime:** `tools/codex_station.py` runs `codex exec` headlessly against the gateway route with the bare model id. The credential travels only in the child environment. The station fails if the CLI is missing.
- **Reviewer permissions:** Reviewers have no hard edit denylist, because Codex has no setting that drops `apply_patch`. Instead, a no-edit instruction plus a post-run check fails any reviewer that changed files other than its own review. I accepted that as a runtime equivalent and noted it in the review.
- **Provenance:** The dispatcher self-reports the model it dispatched, so `executed_model` comes from runtime evidence.
- **Standing wiring:** I found no `claude-sonnet-4-5` or `gpt-6-astra` in the checked wiring files, `brain/decisions/0004-model-migration.md` is present, and the checked tools files and decision record have no em or en dashes.

One non-blocking note: the `ANVIL_CODEX_WIRE_API` override should be mentioned in `docs/EXECUTION.md` if it isn't already.
{"model": "claude-sonnet-5-5"}
