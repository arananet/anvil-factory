The spec at `.openspec/specs/model-tier-map/spec.md` already matches the work order, so I made no changes to it. This is a pure verification round.

- **Problem statement:** it matches the standing tree. `review-cheap` is in `MODEL_HIERARCHY`, and `MODEL_TIER_MAP` now maps it to `claude-sonnet-5-5` (`anvil/config.py:27`).
- **R1 to R3:** they cover the work order's items. R1 is the map entry, R2 is a totality test that reads its vocabulary from routing, and R3 says nothing else changes, with the dispatcher still failing loudly on unmapped values.
- **Dashes:** the spec has no em dash or en dash characters.
- **Not checked:** I did not look at the totality test or the CHANGELOG entry. The CHANGELOG entry is not part of this station's output.

Nothing is missing, so the next station can take it.

Git status showed `runs/wo-gh-31/spec-writer.output.md` as deleted. I recreated it with this report, since the station rules require the output to be a file. That is the only file I wrote.
{"model": "claude-sonnet-5-5"}
