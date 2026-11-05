I added the round 5 requirements to `.openspec/specs/model-migration/spec.md`, appended after S11. I didn't run any tests. The only check was that the file has no em or en dashes.

- **R12, agentic OpenAI runtime:**
  - **Invocation:** Codex CLI runs headlessly in the repo tree with the packet as the task. It uses the gateway OpenAI route from R11 with the bare id `gpt-6.1-sol`. The credential reaches it only through the environment.
  - **Permissions:** builder and test-writer may write. Every other station, reviewers included, writes only its own review file through the shell.
  - **Review and provenance:** review validation and the one in-session correction match the Claude wrapper. The wrapper self-reports `openai/gpt-6.1-sol`.
  - **Failure:** if the CLI is absent or can't be configured, the step fails loudly. A plain completion call is allowed only inside `tools/model_route_smoke.py`.
- **R13, test correction ruling:** the test-writer corrects exactly two assertions and the builder touches no test file.
  - `tests/test_model_migration_loopback.py` now expects builder `configured_model` to be `claude-opus-5-5`, not `fast-builder`.
  - `tests/test_model_migration_tiers.py` (S9) now expects the missing-credential error to name the sources actually checked. Its no-raise case is the one where a credential source is present.
- **S12 and S13:**
  - S12 covers the Codex wrapper unit tests, using fake runtimes in place of the CLI.
  - S13 requires the corrected assertions and the full suite to pass. It also names this run as the acceptance evidence: reviewer-design on Codex, a valid review file the runner counts, and `executed_model` `openai/gpt-6.1-sol` from self-report.

The existing R1 to R11 and S1 to S11 are unchanged.
{"model": "claude-sonnet-5-5"}
