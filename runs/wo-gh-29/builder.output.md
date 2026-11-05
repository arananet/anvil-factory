All three round 2 gate fixes are in, and the full suite passes: 515 tests, OK, 3 skipped. That includes all of `tests/test_execution.py` and its two S8 provenance tests, none of which I changed.

1. **Model provenance (S8):** `CommandExecutor` hands the assigned model to the runtime through the `ANVIL_CONFIGURED_MODEL` environment variable. It no longer copies that label into `executed_model`, which now comes only from what the runtime itself reports. If the runtime reports nothing, `executed_model` stays null. If it reports a model, that value is recorded. `tools/dispatch_station.py` now reports the model it actually dispatched through the existing channel (a `{"model": ...}` JSON line) after a successful run, so the new runtimes produce real evidence of what ran.
2. **Executor signature:** `HttpExecutor` and `FailingExecutor` now accept `configured_model=None`. The runner calls executors through a new helper, `_call_executor` in `anvil/runner.py`. It passes the model only to executors that accept it, so the suite's existing fake executors, which predate the hand-off, still work and no call site raises.
3. **Invented prices (R6, S5):** I removed all three made-up price entries from `anvil.yaml`. The three models stay unpriced, and their steps record cost as measured false with the reason. I updated the CHANGELOG and decision record 0004 to say this; 0004 still claimed the entries had been added.

New tests for these fixes are in a new file, `tests/test_model_migration_loopback.py`. No existing file under `tests/` was modified or deleted, and the produced files contain no em or en dashes.

The strings `anthropic-pricing-2024-01` in `anvil/cost.py` and `docs/COST-MEASUREMENT.md` were already on `main` as format examples, not prices from this order, so I left them alone. Nothing is committed yet, and approval belongs to the review stations.
{"model": "claude-opus-5-5"}
