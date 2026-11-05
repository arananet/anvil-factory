I wrote the review to `runs/wo-gh-31/reviewer-tests.review.json` with verdict `pass`. I did not run the full suite or check the dispatcher directly.

- **R1 (map entry):** `MODEL_TIER_MAP` in `anvil/config.py` maps `review-cheap` to `claude-sonnet-5-5`.
- **R2 (totality test):** `tests/test_tier_map_totality.py` is a new file. It builds the label list from `anvil.routing` instead of hardcoding it. It asserts every label resolves into `CONCRETE_MODELS`. I ran its 4 tests with `unittest` and they pass.
- **R3 (nothing else changed):** I did not diff against `main` (the `main` ref wasn't available), so I didn't confirm that existing test files are untouched. I found no changes to routing labels, the CHANGELOG Unreleased entry is present, and a dash grep found no em or en dashes in the changelog, config or new test.
- **Not verified:** I did not check the dispatcher's loud failure on unmapped values beyond the changelog claim and a test assertion that an unknown tier isn't in the map.
- **Environment:** `pytest` isn't installed here, which is why I used `unittest`. The review notes this too. The checks gate reported the full suite green.
{"model": "claude-sonnet-5-5"}
