Both parts are written, but the full suite is red on purpose: 557 tests run and the 10 failures are all in the new Codex file. Part A is fixed and passing. The Part B tests are written ahead of the builder's work, and today's `tools/codex_station.py` still makes a plain chat completion, so they fail against it.

**Part A: the two stale tests corrected**
- **`tests/test_model_migration_loopback.py`:** the builder step's `configured_model` is now asserted as `claude-opus-5-5` instead of `fast-builder`.
- **`tests/test_model_migration_tiers.py` (S9):** I replaced the missing-environment test.
  - The error is now expected to name `CF_AIG_TOKEN` and `ANTHROPIC_CUSTOM_HEADERS` / `cf-aig-authorization`, plus `ANTHROPIC_BASE_URL` when only the token is set.
  - The runtime must not raise when a credential source is present.
  - Two new cases cover the header-parse path and the direct token taking priority over the header.
- **One change beyond the two named assertions:** the shared test helper now also clears `ANTHROPIC_CUSTOM_HEADERS`, so the tests don't pick up a real credential from the host.
- Both modules pass: 23 tests OK.

**Part B: `tests/test_codex_agentic.py` (new, 13 tests, covering S12)**
- A fake `codex` executable on `PATH` stands in for the CLI and records its arguments, working directory and environment.
- **Invocation:** the tests expect a headless `exec` run in the repo tree, with the packet as the task and the bare model id `gpt-6.1-sol`.
- **Endpoint and credential:** the gateway route must end in `/openai`. The credential (from `CF_AIG_TOKEN` or the header) must appear only in the child's environment, never in arguments, stdout, stderr or the output file.
- **Permissions:** builder and test-writer must get the same arguments as each other, and different ones from the other stations.
- **Review file:** reviewers' files are validated, with one in-session correction and no second one.
- **Failure cases:** a missing CLI or a missing gateway environment must fail loudly. `codex_station.py` must contain no `chat/completions` or `urlopen`.
- **Self-report:** the dispatcher must emit `{"model": "openai/gpt-6.1-sol"}` on success, and not when the CLI is absent.

The runtime-shape assertions follow the spec's R12 wording and my guess at the fake-CLI interface. If the builder uses a different Codex argument layout, those tests may need adjusting to the real contract.

I haven't touched any file outside `tests/`, and the new files contain no em or en dashes.
{"model": "claude-sonnet-5-5"}
