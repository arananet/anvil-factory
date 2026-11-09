I wrote the review to `runs/wo-gh-36/reviewer-tests.review.json` with verdict `pass`.

- **Test change:** it is one line. The final assertion in `test_no_base_changes_nothing_but_the_report_field_s8` now expects `no_reviews`. All other assertions in that test and the seed fixture are unchanged.
- **Spec change:** it is one line. Scenario S8 uses the wording the addendum prescribes, and no other spec text changed.
- **Tests:** `python -m unittest tests.test_practice_skills` ran 28 tests, all OK. I used `unittest` because `pytest` isn't installed here. I did not run the full 649-test suite.
- **Scope:** no other existing test file is modified, and the changed files contain no em or en dashes.
{"model": "claude-sonnet-5-5"}
