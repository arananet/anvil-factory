# Spec writer handoff: wo-gh-39

Spec file: .openspec/specs/station-timeout/spec.md (already present at the run base, status approved). I re-read the work order line by line against it and changed nothing, because nothing in the order is missing from it.

Checks run against the tree:
- git show 93ae03fc: tools/claude_station.py line 61 and tools/codex_station.py line 51 both read `TIMEOUT_SECONDS = 1500`. Matches R1.
- Current tree: tools/claude_station.py line 63 `TIMEOUT_SECONDS = 1500`, used at the subprocess call (line 272) and in the timeout message (line 276). Matches R1.
- anvil/executor.py line 93 defaults timeout_seconds to 300; anvil.yaml line 23 sets 1800; .github/workflows/anvil-line.yml line 66 has timeout-minutes: 180. Matches R5 and R6.
- The spec contains no em dash or en dash.

Requirement ids covering the order: R1 (S1) diagnosis, R2 (S2) configurable resolution, R3 (S3) defaults, R4 (S4) 7200 ceiling, R5 (S5) executor coordination, R6 (S6) job timeout 360, R7 (S7) honest timeout record, R8 (S8) healthy behaviour unchanged, R9 (S9) scaled regression evidence, R10 (S10) decision and docs, R11 (S11) builder report literals.

Out of scope and the allowed write set are stated in the spec, including the protected paths (anvil.json, pipelines/, existing tests/ files).

Left open for the owner:
- R4 allows clamping or rejecting above 7200. The builder picks one; the spec accepts either.
- R5 allows either raising anvil.yaml runtime.timeout_seconds to at least 7200 or deriving the executor timeout from station configuration. The builder picks one.
- Line numbers cited in S1 and S6 are as of the run base and shift once edits land.
{"model": "claude-sonnet-5-5"}
