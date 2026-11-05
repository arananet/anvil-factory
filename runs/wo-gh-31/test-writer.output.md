I made no changes this round, as the work order requires. The standing tree matches the spec, and the full suite passes: 586 tests, with 6 skipped.

I read the code and ran the checks myself. I did not look at how the reviewers or the dispatcher behaved in this run.

- **R1, map entry:** `anvil/config.py:27` has `"review-cheap": "claude-sonnet-5-5"`. The new test `test_review_cheap_resolves_to_sonnet` checks it.
- **R2, totality test:** `tests/test_tier_map_totality.py` is a new file. It builds the label set from `anvil.routing`: `MODEL_HIERARCHY`, the `MODEL_POLICY` values, and the model values and policy ceilings from the default routing config. It does not hardcode the labels. It asserts that every label resolves into `CONCRETE_MODELS`, and a separate test confirms the vocabulary includes `review-cheap`. A future unmapped label would therefore fail the suite.
- **R3, nothing else changed:**
  - `git diff HEAD` shows no changes under `tests/` or `anvil/`.
  - `test_unmapped_value_still_passes_through` shows that `resolve_model` passes an unknown value straight through. The dispatcher's rejection of non-concrete values is untouched, and I did not test that directly.
  - The CHANGELOG Unreleased entry is present.
  - A search for em and en dashes in the test file, `CHANGELOG.md` and `anvil/config.py` found none.

I found no gap against the spec.

The station rules ask for the output as a file, but this round bars file changes. I wrote no output file and left the deleted `runs/wo-gh-31/test-writer.output.md` as it was.
{"model": "claude-sonnet-5-5"}
