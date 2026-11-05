I added `tests/test_model_migration_loopback.py` with 10 tests for the three loopback fixes. The full suite passes: 515 tests, OK, 3 skipped. The two S8 provenance tests in `test_execution.py` pass, unmodified.

I changed no existing test file and no production code. The tree already contained the executor, runner and price-table fixes, so these tests pin that behavior rather than drive new work.

- **Provenance (R3, S8):** one test runs a fake command runtime that records the model it receives. It checks the runtime gets `fast-builder` handed in, and `executed_model` stays null when the runtime reports nothing. A second test has the runtime report `self-reported-1`. It checks `executed_model` is that value and not the configured label.
- **Executor signature:** every executor class in `anvil/executor.py` must accept `configured_model` with a `None` default. An `HttpExecutor.execute(..., configured_model=...)` call must not raise `TypeError`. A legacy fake executor without that parameter must still run through `run_pipeline`.
- **No invented prices (R6, S5):** the two fabricated source labels must not appear in `anvil.yaml`. An entry for any of the three new models may exist only with an `http` source and a non-2024 date. The price table must still load. A model without an entry must produce `measured: false`, `cost: None` and a reason.

The new file contains no em or en dashes.

I did not check the existing `test_model_migration.py` price test against fix 3. It only asserts fields on entries that exist, so it passes with the entries removed.
{"model": "claude-sonnet-5-5"}
