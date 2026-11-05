Both round 3 gate fixes are in and the full suite passes (526 tests, 3 skipped). One catch: the spec's "configured_model in the report is always concrete" rule can't fully hold without breaking protected tests, so I applied it only to routed stations (see the first decision below).

**1. Tier labels no longer reach the dispatcher (R10)**
- `anvil/config.py` now has one complete map from each tier label to a concrete model (`MODEL_TIER_MAP`, applied by `resolve_model`). It follows your table exactly. Values that are already concrete pass through unchanged. Anything else also passes through, so the dispatcher still rejects it loudly.
- `anvil/runner.py` works out the step's model as before (registry, project config, routing, guided), then resolves it. Both executor calls hand the runtime only the resolved model.
- Routing's choices are resolved when they're applied, so routed reviewers show a concrete model in the report.
- `tools/dispatch_station.py` is unchanged and still refuses `review-balanced`, which the new test confirms.

**2. The OpenAI runtime uses the gateway environment the line already has (R11)**
- `tools/codex_station.py` no longer needs any `OPENAI_*` variables. It builds the gateway OpenAI route from `ANTHROPIC_BASE_URL` by swapping the trailing `/anthropic` segment for `/openai`, or uses `ANVIL_GATEWAY_OPENAI_URL` when that is set.
- It authenticates with `CF_AIG_TOKEN`, sent in both the `Authorization` and `cf-aig-authorization` headers, and calls the bare model id `gpt-6.1-sol`.
- If that environment is missing, it fails with an error naming the missing variables and never printing their values.

**Decisions for the reviewers**
- **Report field, a deviation from R10's wording:** R10 says `configured_model` in the report is always concrete. Protected `tests/test_execution.py` (lines 356 to 357 and 401) requires the label (`fast-builder`, `review-balanced`) for unrouted stations in packet mode and for the HTTP executor. So the report shows a concrete model only for routed stations, while the model handed to the runtime is always concrete. That satisfies the protected tests, the round 2 loopback test and the new tier tests together. `executed_model` still comes only from what the runtime reports.
- **Smoke script, outside the stated scope:** `tools/model_route_smoke.py` had the same `OPENAI_*` dependency in its two OpenAI probes. I pointed them at the same gateway config, because R8 requires the workflow credentials.

**Still open**
- The smoke script's Anthropic probes still read `ANTHROPIC_API_KEY`, which the line may not supply. I left them alone as outside this loopback's scope; the operator's post-merge smoke run will show whether that route needs the same fix.
- The test-writer changed `tests/test_model_migration_loopback.py`, a file added by this order in an earlier round, so the builder hand-off now expects the concrete model. I didn't touch any test files.

`CHANGELOG.md` Unreleased has a round 3 entry, and no changed file contains em or en dashes.
{"model": "claude-opus-5-5"}
