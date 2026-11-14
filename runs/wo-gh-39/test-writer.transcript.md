The new tests are written and fail now, for the right reasons. The full project check shows 17 failures and errors: 12 are the new tests, 5 are in other test files.

`tests/test_station_timeout.py` (19 tests) was already on the branch from an earlier run of this station. I checked it against the approved spec and ran it, and I did not change it. I wrote `runs/wo-gh-39/test-writer.output.md` with the scenario-to-test map, the run results and the baseline count. I did not edit any existing test.

- **Scenario coverage:** each scenario S1 to S10 has at least one test named after it. S11 (builder report literals) is not covered, because the builder report does not exist yet.
- **New tests, red state:** 12 of the 19 fail (7 failures, 5 errors), all for the right reason.
  - `anvil.config` has no `station_timeout_seconds`, `STATION_TIMEOUT_CEILING` or `effective_executor_timeout`.
  - `TIMEOUT_SECONDS = 1500` is still in `tools/claude_station.py`.
  - `anvil.yaml` still has `runtime.timeout_seconds: 1800`.
  - A killed station is still not recorded as `timed_out`.
  - The decision record, changelog entry and docs are missing.
- **New tests, already passing:** the other 7 hold against the base. One is S6, because `anvil-line.yml` already has `timeout-minutes: 360`, from an operator commit.
- **Project check:** `Ran 729 tests ... FAILED (failures=12, errors=5, skipped=6)`. The 17 failures and errors are the 12 new tests plus 5 in `test_autonomous_line.py` and `test_governed_delivery.py`.
  - I opened only one of those 5, and it fails because the runner's authenticated GitHub actor is `arananet` and the test passes `--by ana`. It is unrelated to this work order, and I did not run any of the 5 at the base ref.
  - The baseline is 710 existing tests (729 minus the 19 new).