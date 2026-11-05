I changed no test or source file this round. `tests/test_model_migration_verification.py` already holds the round 2 correction, so I only rewrote the output summary the re-fire had deleted, at `runs/wo-gh-30/test-writer.output.md`.

- **Policy the test encodes:** the builder is `claude-opus-5-5` on non-UI work and `openai/gpt-6.1-sol` on UI-surface work. `executed_model` must be self-reported and equal to the assignment. A test confirms the policy rejects the opposite value in each case.
- **Test run:** I ran `tests.test_model_migration_verification` and `tests.test_readme_showcase`. 28 tests passed and 3 were skipped. The readme showcase link test passes now that the `runs/` tree is back on main. I did not run the full suite.
- **Not covered:**
  - **Fake runtime:** the tests use a fake command runtime, so they check the runner's wiring and recording, not live Claude or Codex execution.
  - **Real-run evidence:** the design reviewers on Codex (S3) and the empty-change check (S6) depend on the real run's evidence.
  - **Full suite:** the suite on current main (S7) is the judge.
{"model": "claude-sonnet-5-5"}
