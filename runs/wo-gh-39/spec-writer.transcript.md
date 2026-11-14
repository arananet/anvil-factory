The spec for this order already existed at `.openspec/specs/station-timeout/spec.md` (status approved). I checked it against the work order line by line and changed nothing, because it already covers every item in the order.

I checked the spec's citations against the tree:
- **Old cap:** at `93ae03fc`, `TIMEOUT_SECONDS = 1500` is at `tools/claude_station.py` line 61 and `tools/codex_station.py` line 51. In the current tree it is at `tools/claude_station.py` line 63.
- **Neighbouring layers:** `anvil/executor.py` line 93 defaults the timeout to 300 seconds. `anvil.yaml` line 23 sets it to 1800. `.github/workflows/anvil-line.yml` line 66 has `timeout-minutes: 180`.
- **Dashes:** the spec has no em dash or en dash.

R1 to R11 each have a scenario S1 to S11 that names them. The spec also states out of scope and the allowed write set, including the protected paths.

I wrote the handoff to `runs/wo-gh-39/spec-writer.output.md`. That file had been deleted in the working tree.

Two choices are left for the builder or the owner, and the spec accepts either option in each:
- **R4:** clamp a value above 7200 to 7200, or reject it with an error that names 7200.
- **R5:** raise `runtime.timeout_seconds` in `anvil.yaml` to at least 7200, or derive the executor timeout from the station configuration.

The line numbers in S1 and S6 are as of the run base and will shift once edits land.