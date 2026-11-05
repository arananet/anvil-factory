I wrote the round 3 tests in a new file, `tests/test_model_migration_tiers.py`. They don't pass yet, because the tier resolver and the OpenAI gateway change aren't implemented. I ran the file once: 14 failures and 3 errors across its 11 tests, which is the expected state before the fix. I have not run the full suite.

The tests cover these spec items:
- **R10/S8, tier resolution:** each of the 8 labels reaches the runtime as the concrete model from the table in the brief. Concrete models pass through unchanged, and no station gets an unresolved label. Routed reviewers are handed `claude-sonnet-5-5`, and the report's `configured_model` for them is concrete.
- **R10, dispatcher:** the dispatcher still fails loudly on a tier label.
- **S10, provenance:** `executed_model` stays null when the runtime reports none.
- **R11/S9, OpenAI runtime:**
  - The runtime builds its config from `CF_AIG_TOKEN` and `ANTHROPIC_BASE_URL` alone.
  - It honours `ANVIL_GATEWAY_OPENAI_URL` when set.
  - It fails without printing credential values when the gateway env is missing.
  - It does not need any `OPENAI_*` variables.

To check the OpenAI runtime, the tests assume `call_openai_api(prompt, model)` stays the entry point. They also assume it swaps the trailing `/anthropic` in the base URL for `/openai` and sends the model as bare `gpt-6.1-sol`.

I made one edit outside the new file. In `tests/test_model_migration_loopback.py`, two assertions expected the runtime to receive `fast-builder`. They now expect `claude-opus-5-5`. That file belongs to this order, so it isn't one of the protected existing tests.

There is also a conflict the builder will have to resolve. Protected `tests/test_execution.py` asserts that the report's `configured_model` is the raw label (`fast-builder`, `review-balanced`) in packet mode. It asserts the same for the unrouted builder under the HTTP executor. R10 says `configured_model` is always concrete, so both can't hold everywhere. My report test only covers routed reviewers under a command executor, as the brief describes. The builder can't edit `test_execution.py`. They need to resolve at hand-off and for routed selections, and keep the label in the report where those tests require it.

The coverage table and this note are in `runs/wo-gh-29/test-writer.output.md`. Neither the tests nor the note contains em or en dashes.
{"model": "claude-sonnet-5-5"}
