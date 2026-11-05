I added `tests/test_model_migration_round4.py` with 14 tests. 7 of them fail against the current tree, so they are red ahead of the builder's fix. No existing test file was touched, and the new file has no em or en dashes.

**What the tests cover**

- **Tier resolution through `run_pipeline` (R10, S8, S10):**
  - The tests drive `sdlc-default` with a fake command runtime. `anvil.runner.route_reviewers` is patched to return a `RoutingRecord` whose `selected_models` are tier labels (`review-balanced`, `review-strong`).
  - They assert the runtime received the concrete model for the routed reviewers and that the recorded `configured_model` is concrete and equals what was handed over.
  - They assert every executing step, intake included, hands off a concrete model, and that a tier label set on the intake station itself is resolved.
  - A concrete routed model must pass through unchanged, and `executed_model` must stay null without a self-report.
- **Codex credential source (R11, S9):**
  - These use a headers fixture string.
  - They cover parsing `cf-aig-authorization` out of `ANTHROPIC_CUSTOM_HEADERS` when `CF_AIG_TOKEN` is unset, and a request authorised from that value.
  - They cover the `CF_AIG_TOKEN` variable path and that it wins over the header, case-insensitive and CRLF-tolerant matching, and `ANVIL_GATEWAY_OPENAI_URL` still being honoured.
  - They cover a loud failure naming `CF_AIG_TOKEN` when neither source is present, with the credential never in stdout, stderr or the error text.

**Current failures**

- **5 errors, all in the credential group:** `codex_station.gateway_openai_config` still raises "missing: CF_AIG_TOKEN" because it doesn't read the header.
- **2 failures, routed path:**
  - A step still records the unresolved label as `configured_model` (intake shows `default`).
  - A registry-level tier label (`reasoning-strong`) is likewise recorded unresolved.
- **Already passing:** The routed-reviewer hand-off assertions, for `reviewer-spec` and `reviewer-security`, already pass. The runner passes `handoff_model` to the runtime but records `configured_model` unresolved. The fix is to resolve the label once, after all overrides, and use it for both.

I didn't run the full suite, only the new file.
{"model": "claude-sonnet-5-5"}
