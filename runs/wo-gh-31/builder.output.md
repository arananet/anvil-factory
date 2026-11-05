The fix is in: `review-cheap` now resolves to `claude-sonnet-5-5`. The new tests and the full suite pass.

These changes were already in the working tree when I started. I checked them against the spec and didn't change anything:

- **R1:** `anvil/config.py:27` has the new entry `"review-cheap": "claude-sonnet-5-5"` in `MODEL_TIER_MAP`.
- **R2:** the new test file `tests/test_tier_map_totality.py` builds its list of tier labels from the routing module itself, not from a hardcoded copy. It reads `routing.MODEL_HIERARCHY`, the values in `routing.MODEL_POLICY`, and the model and ceiling values from the default routing table (from `routing.load_routing_config`). It then checks that each label resolves to one of `CONCRETE_MODELS`. With the `review-cheap` entry temporarily removed, 2 of its 4 tests fail, so it catches a missing label.
- **R3:** the test also confirms that an unknown value still passes through unresolved, so the dispatcher keeps failing loudly on it. `anvil/routing.py` and the existing files under `tests/` are unchanged.
- **CHANGELOG:** there is an Unreleased entry for the change.

**Checks:**
- The new tests pass (4 of 4).
- The full suite passes: 586 tests, 6 skipped. pytest isn't installed here, so I ran everything with `python -m unittest discover -s tests`.
- There are no em or en dashes in `anvil/config.py`, the new test, the work order, or the added changelog lines.

This is not a visual change, so there is no Quality Charter comparison file. Nothing is committed yet; approval belongs to the review station.
{"model": "claude-opus-5-5"}
