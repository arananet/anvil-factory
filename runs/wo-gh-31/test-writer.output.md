The `review-cheap` entry is added and the full suite passes: 586 tests run, 6 skipped, 0 failures. I ran it with `python -m unittest discover` because pytest isn't installed here.

- **Fix:** `MODEL_TIER_MAP` in `anvil/config.py` now maps `review-cheap` to `claude-sonnet-5-5`.
- **Regression test:** the new file `tests/test_tier_map_totality.py` builds its label list from `anvil.routing` instead of a hardcoded copy. It collects `MODEL_HIERARCHY`, the `MODEL_POLICY` values, and the model values and policy ceilings from the default routing table, which includes the reduced panel's `review-cheap`. It asserts each label resolves through `resolve_model` to a member of `CONCRETE_MODELS`. Two extra tests pin `review-cheap` to `claude-sonnet-5-5` and check that an unmapped value still passes through unchanged for the dispatcher to reject.
- **Changelog:** an Unreleased entry is added to `CHANGELOG.md`.

No existing file under `tests/` was touched, and neither the new test file nor the new changelog entry contains an em or en dash. I haven't checked the other changed files for those characters. Nothing is committed.
{"model": "claude-sonnet-5-5"}
