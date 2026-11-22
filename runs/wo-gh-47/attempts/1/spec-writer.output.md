I revised `.openspec/specs/live-progress-sinks/spec.md`. The spec this order points at already existed, but it didn't meet the definition of done: its scenarios didn't name requirements. Checking it against the code at base `10168fa` also turned up gaps the builder would otherwise have run into. I wrote the spec only; nothing was built or run.

**What changed**
- **Requirements, now numbered:** R1.1–R1.10 (configuration and validation, when sinks are called, the order of sink call and file write, new state fields, failures, inactive sinks, timeout, no sinks means no calls, events unchanged, where the code lives), R2.1–R2.6 (github-issue), R3.1–R3.6 (github-project), R4.1–R4.5 (what ships enabled), R5.1–R5.3 (tokens) and R6.1–R6.3 (tests).
- **Scenarios, rewritten with concrete values:** S1–S14, plus new S15 and S16. Each one names its requirements, and items (a) to (h) of the order are mapped to them. S10 covers `runtime_refused` and an unknown future exit status, both shown as is.
- **New sections:** base ref, terms, out of scope, allowed write set, the builder report contents, and how the spec fits with the existing specs and tests.

**Decisions I made in the spec, from what the code shows**
1. **The state record gains four fields:** `stations` (the pipeline order), `total_tokens` on each step, `exit_status`, and a `sinks` status list. Today's record has none of these, and the comment can't show pending rows, tokens per station or the exit status without them. Adding fields is allowed by the order.
2. **Why a sink is inactive goes in the new `sinks` field, not `export_errors`.** With the scaffold enabling github-issue, every scaffolded run without GitHub variables would otherwise add a note to `export_errors`. Real failures still go to `export_errors`.
3. **Crashes reach the sinks without touching the runner.** `mark_crashed` keeps its signature, reads `anvil.yaml` itself, and finds the existing comment again by its run id marker.
4. **Sinks are called first, then state.json is written.** This way a failure from the final call still ends up in the file.
5. **Loading fails if a sink's `token_env` would reach a station.** Only GH_TOKEN-style names are on the built-in deny list in `anvil/executor.py`, which is frozen. A custom Projects token variable would otherwise leak into stations.

**Left for you to decide**
- **Board columns:** while deployer or observer runs, the card stays where it was. At the end, any result other than approved, or a human gate, goes to Failed. That includes `gate_failed`, `no_reviews` and the dry-run `packet_ready`. I also dropped the earlier draft's "unless columns names it", so `columns` only maps phases to column names.
- **Tests run by hand:** existing test files run scaffolded projects with ids like `wo-gh-12`. If someone runs the suite with GH_TOKEN and GITHUB_REPOSITORY exported, the new default sink would comment on the real issue. CI and the line's checks step are safe because neither carries GH_TOKEN. Existing tests can't be changed under this order.
- **No retry or throttling:** an unreachable API costs up to `timeout_seconds` per state write.
- **The Projects board can't work in the factory yet:** that needs a workflow change to supply a Projects token, which this order forbids. It ships documented and off.

Nothing in the order is missing from the spec.
{"model": "claude-opus-5-5"}
