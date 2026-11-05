I checked the existing code and made no changes, as this round requires. The fix already in place meets the spec. The builder rules say to write my output to a file in the repo, but this round forbids touching files, so this report is in chat only.

**R1, the missing map entry: done.** `anvil/config.py:27` maps `"review-cheap"` to `"claude-sonnet-5-5"`. The other non-design reviewer labels (`review-balanced`, `review-strong`) also map to Sonnet, which matches the owner's policy.

**R2, the totality test: done.** `tests/test_tier_map_totality.py` is a new file. It builds the label list from the routing module at run time instead of keeping its own copy. It pulls from:
- `routing.MODEL_HIERARCHY`
- `routing.MODEL_POLICY` values
- the default routing table that `routing.load_routing_config()` returns, including the reduced panel's `"review-cheap"` at `anvil/routing.py:119`
- policy ceilings

It then checks that `resolve_model` turns each label into a member of `CONCRETE_MODELS`. It also checks that `review-cheap` is actually in that list, so the test can't pass on an empty list. A label added to routing later without a map entry will fail the suite.

**R3, nothing else changed: holds.**
- `resolve_model` still returns unknown values unchanged, so the dispatcher still fails loudly on them. The test `test_unmapped_value_still_passes_through` covers this.
- Routing's vocabulary and rules are unchanged.
- No existing file under `tests/` was modified.
- The CHANGELOG has an Unreleased entry.
- None of the three files contains an em dash or en dash.

**Tests:**
- `python -m unittest tests.test_tier_map_totality` ran 4 tests, all passing.
- The full suite (`python -m unittest discover -s tests`) ran 586 tests, all passing with 6 skipped.
- pytest isn't installed here, so I used unittest.

**Gaps:** I found none against the spec. This round's own run started on the fixed code, so its `review-cheap` reviewers should now resolve to a real model when handed off. Whether they actually do is something only this run's reviewers can confirm.

`git status` shows `runs/wo-gh-31/builder.output.md` as deleted. That was already the case at the start of this session and isn't something I did.
{"model": "claude-opus-5-5"}
