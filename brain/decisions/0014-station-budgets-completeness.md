# 0014: Per-station token partitions inside the run cap, and a completeness gate before review

Status: proposed 2026-11-21, work order wo-gh-42, spec station-budgets-completeness.

## Context

The run budget was one shared pool (`efficiency.max_run_tokens`), checked
between calls. In wo-gh-6 one builder call measured 6,359,529 tokens against
a 6,000,000 cap, and the run died at the cap. In wo-gh-7 reviewer spend was
launched on an attempt whose builder had failed, and what was complete had to
be rebuilt by hand.

## Decision

- `efficiency.station_budgets` (station id to tokens per run) and
  `efficiency.default_station_budget` (the partition for unnamed model
  stations) divide the run cap. They are validated at load against
  `max_run_tokens` for every pipeline the runner is given. The worst case is
  the named partitions plus the default for each unnamed model station. An
  absent default adds nothing, and the stations it would cover are bounded
  only by the run cap. The factory ships sdlc-default partitions summing to
  exactly 15000000.
- The spine refuses a dispatch whose station has spent its partition. It
  reads consumption from the per-attempt usage records summed over the
  station's steps. Unmeasured usage counts as exhausted under
  `require_usage` and is recorded as `proceeded_unmeasured` without it. The
  wrapper kills a streaming session whose usage reaches what is left of the
  partition (the station timeout's kill-and-record shape). Both end the run
  through the continuous run accounting exit path (decision 0013).
- A deterministic completeness precondition runs after the pre-review checks
  gate and before any reviewer. It needs the builder report, the
  test-writer's files and the attempt delta to exist and be non-empty, the
  gate verdict to be pass, and no earlier station to be failed without its
  artifact. A failure is a gate loopback with the named gaps.
- The precondition is live only in a project that configures partitions.
  The line's existing contract tests (protected for this order) pin the old
  review flow for projects with scripted stations that write no files. The
  factory's own anvil.yaml configures partitions, so factory runs get the
  gate.

## Consequences

- A heavy station can no longer starve every station behind it. But a
  partition sized below a station's real need now ends the run at that
  station, where the shared pool would have let it finish. Partitions must be
  resized from measured runs (the 2026-11-21 table covers the largest
  measured use per station across wo-gh-39, wo-gh-43 and wo-gh-41).
- The in-flight ceiling needs streamed usage. A station gets stream-json
  output whenever a partition applies. The copilot runtime cannot be stopped
  mid flight and has the pre-call check only.
- With every sdlc-default station named and the sum equal to the cap, no
  default can be set without failing validation for that pipeline. Other
  pipelines' unnamed stations stay unpartitioned until the owner names them.
- A project that wants the completeness gate must configure partitions.
  Turning it on for every project is a separate decision, and it needs the
  scripted contract tests updated.
