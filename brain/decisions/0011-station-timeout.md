# 0011: The station timeout is configuration, with a ceiling

Status: accepted 2026-11-14, work order wo-gh-39, spec station-timeout.

## Context

The station wrapper killed every station at a hardcoded 1500 seconds
(`TIMEOUT_SECONDS = 1500`, tools/claude_station.py line 63 at a011c14, and
earlier also tools/codex_station.py line 51 at 93ae03fc). Producing stations
that needed longer were killed after their work was on disk, and the kill was
recorded as a bare failure with executed_model null and usage unmeasured.
Nothing in the repository could override the value; raising the job timeout
did not move it.

## Decision

- The per station timeout resolves from ANVIL_STATION_TIMEOUT_SECONDS, then
  runtime.station_timeout_seconds in anvil.yaml (handed to the wrapper by the
  command executor through the same variable), then the class default:
  3600 seconds for the eight producing stations, 1500 for every other station.
  The resolution lives in anvil/config.py, one place for the wrapper and the
  executor.
- The hard ceiling is 7200 seconds. A larger value is clamped to 7200 with a
  note on stderr rather than rejected, so a misconfigured project still runs
  and a runaway station still dies at the ceiling. A non numeric or non
  positive value is rejected with the value named.
- The timeout bounds the whole station invocation, a reviewer's correction
  attempt included, so the executor bound below is a real bound.
- The command executor timeout is raised to the largest station timeout in
  effect plus 60 seconds, so the wrapper is the binding cap and writes its
  record first. The factory anvil.yaml sets runtime.timeout_seconds to 7200;
  the anvil-line job allows 360 minutes.
- A killed station records status timed_out, the station, the measured
  elapsed milliseconds, the timeout value and its source as the reason, the
  dispatched model, and the partial usage the runtime printed before the kill
  (or unmeasured with a reason). The run record step carries status timed_out
  and executed_model set to the dispatched model.

## Consequences

- One override value applies to every station alike; there is no per station
  override. A project that wants a long builder but short reviewers relies on
  the class defaults.
- executed_model for a timed out station is the model that was dispatched,
  not a runtime self report: the runtime was killed before it could report.
  This is weaker evidence than for a station that finished.
- Clamping repairs a value instead of refusing it; the stderr note is the only
  signal. The trade is chosen so that an over ceiling value cannot stop the
  line, while it can never extend a station past 7200 seconds.
- A reviewer whose first attempt uses most of its timeout has less time left
  for its correction attempt than before, when each attempt had its own cap.
- Consumers outside the spine that look only for status failed (anvil/line.py
  for a pipeline without an approver, the OpenTelemetry export, the status
  page) do not yet treat timed_out as failed; see the builder report of
  wo-gh-39.
- The evidence is scaled mechanism tests (seconds, not hours); no live run
  past 1500 seconds is claimed.
