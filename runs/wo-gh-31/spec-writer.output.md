The spec already exists at `.openspec/specs/model-tier-map/spec.md`. It was staged in commit 9873716, and it matches the work order. I checked it against the code, and I made no changes.

- **Problem statement:** `anvil/routing.py:30` lists `review-cheap` in `MODEL_HIERARCHY`. `anvil/routing.py:119` assigns it to the reduced panel. `MODEL_TIER_MAP` (`anvil/config.py:26`) has no entry for it, and `resolve_model` (`anvil/config.py:44`) passes unmapped labels through unchanged.
- **R1 to R3:** These cover the work order's three items, which are the map entry, the totality test that reads its vocabulary from routing, and nothing else changing.
- **Dashes:** The spec file has no em dash or en dash characters.
- **Brain:** `brain/` has nothing that bears on this change.

Nothing is missing, so the next station can take it.

The CHANGELOG entry from the work order is not part of this station's output, so I left it for the implementation station.
{"model": "claude-sonnet-5-5"}
