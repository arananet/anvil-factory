I built both round 4 mechanisms and all 14 round 4 tests pass, but the full suite is not green. Two protected tests from earlier rounds directly contradict what the round 4 brief and spec ask for. Rewriting either one is forbidden, so I'm reporting the conflict instead of guessing which side gives way.

**Suite result:**
- **In this workflow environment:** 540 tests, 3 failures. This is the environment the checks gate runs in, so the gate will fail.
- **With `ANTHROPIC_CUSTOM_HEADERS` unset:** 542 tests, 1 failure. That count includes my two new supervisor tests.

## What changed
1. **Tier labels resolved at the hand-off** (`anvil/runner.py`). After every override has set the step's final label, the runner resolves it to a concrete model. When the step runs on the command runtime, which is the one that uses the model it is handed, that concrete model is also what gets recorded as `configured_model`. Packet mode and the HTTP executor still record the label, as the existing provenance tests require; the HTTP executor runs its own endpoint model anyway.
2. **The supervisor now passes a model too** (`anvil/supervisor.py`). It is another path that runs a station, and it never passed a model, so the dispatcher would have refused it. It now hands over the resolved model (`reasoning-strong` becomes `claude-opus-5-5`). Older executor test doubles without the new argument still work. Tests are in `tests/test_model_migration_supervisor_handoff.py`.
3. **Codex credential** (`tools/codex_station.py`). It uses `CF_AIG_TOKEN` when set. Otherwise it reads the token from the `cf-aig-authorization` header inside `ANTHROPIC_CUSTOM_HEADERS` (name matched case-insensitively, CRLF tolerated). If neither is present it fails loudly, naming the missing sources without printing any value.

## The two conflicts (need an operator decision)
1. **`tests/test_model_migration_loopback.py:61`** (round 2, protected). It requires a builder run on the command runtime to record `configured_model == "fast-builder"`. The round 4 spec and `tests/test_model_migration_round4.py` require that same kind of step to record the concrete model. The only differences between the two tests are the pipeline and the fixture, so no principled rule satisfies both. I followed the final brief, and this test fails in every environment.
2. **`tests/test_model_migration_tiers.py::test_missing_gateway_env_fails_loudly_without_values_s9`** (round 3, protected, 2 subtests). It expects a failure when `CF_AIG_TOKEN` is absent, but it doesn't clear `ANTHROPIC_CUSTOM_HEADERS` from its environment. The execute workflow sets that header for the whole job, and the checks gate passes its environment through to the suite. The new header fallback, which round 4 requires, therefore finds the real credential and the failure never happens. It passes wherever the header is unset, such as `factory.yml` CI.

**Decision needed:** one of these to reach a green gate:
- allow those two assertions to be changed (or the files replaced);
- or have the gate run the suite without the credential environment. That would change frozen gate behaviour, so I didn't do it.

Nothing is committed.
{"model": "claude-opus-5-5"}
