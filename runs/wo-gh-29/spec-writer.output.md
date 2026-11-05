All three round 2 fixes are in. The full suite passes: 505 tests, OK, 3 skipped. The two S8 provenance tests and the rest of `tests/test_execution.py` pass unmodified. I changed no existing test file, and I added no new test files for these fixes.

1. **Provenance:** `configured_model` now goes into the runtime but is no longer recorded as the executed model.
   - `CommandExecutor` in `anvil/executor.py` no longer returns `"model": configured_model`. The executed model comes only from the runtime's self-report, so it is null when the runtime reports none.
   - `tools/dispatch_station.py` now self-reports the model it dispatched. On a successful run it appends a `{"model": ...}` line to the output file and stdout. That gives the Claude and Codex runtimes executed-model evidence without guessing. Review parsing still reads only the review file, so the parsing contract is untouched.
2. **Signature:** `HttpExecutor.execute` and `FailingExecutor.execute` now accept `configured_model`. The runner calls executors through a new `_call_executor` helper in `anvil/runner.py`. It passes the model only to executors that accept it, so the suite's existing fake executors, which lack the parameter, still work. No call site raises on the new argument.
3. **Prices:** I removed the `prices` block from `anvil.yaml`, which held the three invented entries. The new models are unpriced, and their steps record cost as unmeasured. I also changed the CHANGELOG sentence that claimed new price entries.

The example price entries in `docs/COST-MEASUREMENT.md` and `anvil/cost.py` still read `anthropic-pricing-2024-01` for a placeholder `model-name`. They are illustrative, not wired to any real model, so I left them alone.

I did not run the live routes, so the dispatch wrapper's self-report is verified only through the fakes. The live proof is still the post-merge run and the smoke script.
