The review verdict is **pass**, and I wrote it to `runs/wo-gh-31/reviewer-spec.review.json`.

- **R1 (map entry):** `MODEL_TIER_MAP` in `anvil/config.py` maps `review-cheap` to `claude-sonnet-5-5`, the same as the other reviewer tiers.
- **R2 (totality test):** `tests/test_tier_map_totality.py` reads its labels from the routing module, not from a copy. It asserts that every one resolves into `CONCRETE_MODELS`, and that `review-cheap` is among them.
- **R3 (nothing else changed):** `resolve_model` still passes unmapped values through, so the dispatcher still fails loudly on them. A test covers that case.
- **Tests:** the new test file passes (4 of 4). The full suite passes too (586 tests, 6 skipped).
- **Other checks:** the CHANGELOG has an entry, and the three changed files have no em or en dashes.

I could not diff against the base ref, because this checkout has no `main` or `origin/main` ref. So I did not confirm that existing files under `tests/` are unmodified. I noted that caveat in the review file.
{"model": "claude-sonnet-5-5"}
