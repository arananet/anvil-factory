# 0015: Live progress sinks fed by the state record, GitHub as the zero setup default

Status: proposed 2026-11-22, work order wo-gh-47, spec live-progress-sinks.

## Context

A run could not be watched from outside. state.json and the report
checkpoints (decision 0013) stay on the machine that runs the line until the
run ends, and the runs of wo-gh-41 and wo-gh-42 showed only "In progress"
for 5 to 27 minutes. The existing export (events_url, otlp_endpoint) needs a
receiver someone must build and host. Owner direction of 2026-11-21: no
dependence on one vendor, and a person who copies ANVIL sees their runs
without standing anything up. Every work order is already a GitHub issue and
every run already holds a token that can write to it.

## Decision

- Progress sinks consume the run state record (anvil/run-state@1). The
  recorder calls them at every state write, before writing state.json, and
  records what they left (`sinks`, `export_errors`) in that same write. No
  event kind is added: the events contract, the webhook and the OTLP trace
  stay as governed delivery defined them, and the tests that compare webhook
  events with events.jsonl keep holding.
- The github-issue sink (one comment, created once and edited afterwards) is
  the default, enabled in the factory and in the scaffold: GitHub is where
  the work order already lives and the token is already there, so it is the
  zero setup choice. The github-project sink ships documented and off,
  because its token is one the workflow does not hold.
- Sink code lives in anvil/sinks.py beside the recorder; the runner gains no
  network code and only passes the pipeline order. A sink failure is an
  export error, never a verdict.

## Consequences

- API rate use: about one request per state write (one comment edit), plus a
  listing at the first call; a project board adds a request per phase change.
  A long run with many loopbacks spends that many requests of the token's
  hourly allowance. There is no batching or retrying, by scope.
- The comment is only as fresh as the last state write: during a long
  station it shows that station running and nothing finer.
- A second consumer of the state record means its fields are now read
  outside the engine; the record may only gain fields, as before.
- A run outside GitHub (no wo-gh id, no GITHUB_REPOSITORY, no token) shows
  nothing new; the sink records why in state.json and makes no call.
