I rewrote `.openspec/specs/station-timeout/spec.md` (status stays approved). The existing spec had no requirement ids and its scenarios didn't name requirements. It also had no out-of-scope section or write set. I haven't run anything against it; there are no tests for a spec, and the only check was a dash-character search, which found none.

**Requirements written (R1–R11):**
- R1: root cause with file and line, checked against the tree.
- R2: configurable timeout and resolution order.
- R3: defaults per station class.
- R4: 7200 ceiling and rejection of bad values.
- R5: executor timeout never below the largest station timeout.
- R6: job timeout raised to 360 minutes.
- R7: honest timeout record.
- R8: healthy behaviour unchanged.
- R9: scaled regression evidence.
- R10: decision record and docs.
- R11: required literals in the builder report.

**Scenarios written (S1–S11):** each one names its requirement and uses concrete values. They cover:
- a station configured at 100 against 200;
- a ceiling value of 9000, and the bad values "abc", "0" and "-5";
- a scaled station that works for 2 seconds against a 1-second legacy cap;
- a timeout record with elapsed time of at least 1000 ms.

The spec also states what is out of scope and the allowed write set. The write set authorizes new test files under the protected `tests/` path and forbids editing `anvil.json`, `pipelines/` and existing tests.

**Checks against the tree:**
- The `TIMEOUT_SECONDS = 1500` constant is at `tools/claude_station.py:63`. I did not check the historical `93ae03fc` lines for R1. They come from the work order and the original spec.
- `anvil.yaml` sets `runtime.timeout_seconds` to 1800.
- The job timeout is at line 66 of `anvil-line.yml`.

**Decisions left for the owner:**
- **Ceiling over the limit:** R4 lets the builder either clamp to 7200 or reject with an error naming 7200. The order allows both. Say so if you want only one.
- **Executor timeout:** R5 lets the builder either set `anvil.yaml` `runtime.timeout_seconds` to at least 7200 or derive it from the station configuration. Again the order allows both.
- **Docs search:** S10 requires that a search of `docs/` for "1500" finds no current-behaviour statement. I didn't list which docs mention 1500. A grep of `docs`, `README.md` and `CHANGELOG.md` for "1500" printed nothing, but `docs/EXECUTION.md` still needs the new behaviour documented.
{"model": "claude-sonnet-5-5"}
