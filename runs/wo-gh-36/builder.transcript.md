I made no code change for this loopback. The two upstream fixes are in place and the mechanism from the first run already passes the corrected test.

- **Spec:** only scenario S8 changed in `.openspec/specs/practice-skills/spec.md`, and it now matches the addendum's sentence exactly.
- **Test:** in `tests/test_practice_skills.py`, the only change is the final assertion of the S8 test, which now expects `"no_reviews"` instead of `"approved"`. The seed fixture that carries `"approved"` was left alone.
- **Tests:** the practice-skills file passes (28 tests). The full suite passes too: 649 tests, 8 skipped. The one test that failed in the first run now passes.
- **What I changed:** I didn't touch anything under `tests/`, and nothing in the code. My only file is the builder report at `runs/wo-gh-36/builder.output.md`, which lists no blockers.
