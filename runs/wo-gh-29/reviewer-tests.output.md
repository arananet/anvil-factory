I passed the tests for wo-gh-29 and wrote the review to `runs/wo-gh-29/reviewer-tests.review.json`.

- **Suite:** I ran the full suite and it passed: 560 tests, OK, 3 skipped.
- **Part A:** Both corrections are in place. `tests/test_model_migration_loopback.py` now expects `claude-opus-5-5` as the configured model. `tests/test_model_migration_tiers.py` now follows the credential sources actually checked, including the `ANTHROPIC_CUSTOM_HEADERS` `cf-aig-authorization` header.
- **Agentic runtime coverage:** The two new files, `tests/test_codex_agentic.py` and `tests/test_codex_reviewer_guard.py`, cover the Codex runtime and the reviewer write guard. They include tests for:
  - headless invocation of the Codex CLI;
  - gateway route and credential handling;
  - write permissions by station;
  - review validation and the single correction;
  - loud failure with no fallback;
  - self-reporting of the model.
- **Minor note:** The Part A correction to `tests/test_model_migration_tiers.py` also added two new test methods, which the ruling did not name. They only add coverage and don't weaken any assertion, so I did not treat them as a defect.
- **Dashes:** I found no em dash or en dash characters in the new or changed test files or in `tools/codex_station.py`.
{"model": "claude-sonnet-5-5"}
