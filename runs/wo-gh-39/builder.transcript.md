I wrote the builder report to `runs/wo-gh-39/builder.output.md`. I made no code changes this attempt: the implementation from the earlier attempt on this branch already meets every scenario, and I re-checked it on the final tree.

**Test results:**
- **Full suite with the CI login details removed** (the way the checks gate now runs it): `Ran 736 tests` / `OK (skipped=6)`.
- **Full suite run raw in this Actions shell:** 5 approval tests fail. They also fail on the tree before this order. The cause is the CI host's GitHub identity leaking into the test run, and the operator's fix in commit 36c18c4 (`anvil/gates.py`) removes those variables before the gate's check runs. So the gate should be green this time, but I haven't watched it run.
- **The two new test files:** 26 tests, OK.

**Root cause, confirmed with `git show`:**
- At 93ae03fc the 1500s cap was hardcoded at `tools/claude_station.py:61` and `tools/codex_station.py:51`.
- At a011c14 it was at `tools/claude_station.py:63`.
- Neither had any override. The final tree resolves the timeout per station from configuration instead.

**What the implementation does:**
- **Order of precedence:** `ANVIL_STATION_TIMEOUT_SECONDS`, then `runtime.station_timeout_seconds` in `anvil.yaml`, then the default for the station's class.
- **Defaults:** 3600s for the eight producing stations, 1500s for all others.
- **Ceiling:** values above 7200 are clamped to 7200. Non-integer, zero or negative values are rejected with the source and value named.
- **Other limits raised to fit:** the executor timeout is always at least the largest station timeout plus 60s, `anvil.yaml` `timeout_seconds` is now 7200, and the job timeout is 360 minutes.
- **Timeout records:** a killed station records `timed_out` with the elapsed time, the timeout value, the reason, the model that ran and any partial usage. The model field is no longer null.

**Still open:**
- No live station has run past 1500 seconds; the evidence is scaled-down mechanism tests, as the spec allows.
- The way the executor finds the largest station timeout would need revisiting if per-station overrides are ever added. The spec doesn't ask for them.
- The branch diff also contains operator changes that this station didn't write: `anvil/gates.py`, `status/*` and `tools/model_route_smoke.py`.

Nothing in the diff touches `pipelines/`, `anvil.json` or existing tests, and no changed file contains an en dash or em dash.