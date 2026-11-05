# Decision 0004: Runtime model migration to per-station models and Sol for design

Status: accepted

Adopted: 2026-11-03, by the owner's order.

## Decision

Move the factory's runtime off retired models claude-sonnet-4-5 (retires 2026-11-30) and openai/gpt-6-astra (retired 2026-11-03). Assign explicit models per station in anvil.yaml:

- builder: claude-opus-5-5 (non-UI work)
- spec-writer, test-writer: claude-sonnet-5-5
- All reviewers except design: claude-sonnet-5-5
- reviewer-design, reviewer-ux: openai/gpt-6.1-sol
- intake, scout, supervisor, observer, deployer: claude-sonnet-5-5

The builder uses openai/gpt-6.1-sol when the runner assigns the guided design model (UI surface work orders).

Runtime dispatch is by the effective model the runner assigned for each step. Anthropic models run through Claude Code print mode via the gateway Anthropic route. openai/gpt-6.1-sol runs through an agentic OpenAI runtime (Codex) via the gateway OpenAI route. Unknown models fail loudly with no fallback.

The executed model recorded in run reports comes from runtime evidence (what the runtime reports), never copied from the configured label.

## Why

Owner's order 2026-11-03 to retire Astra and use Sol for design stations, following executed benchmark evidence recorded on branch anvil/benchmark-record-wo-gh-22.

Benchmark results: Astra, Opus 5.5 and Sol tied at quality (reviewer recall 10 of 10 against planted violations; builder token compliance 12 of 12 each). Measured cost per task: Sol 0.038 USD, Opus 0.137 USD, Astra 0.198 USD (both arms, inside the 10 euro hard cap). Sol delivers equivalent quality at about one fifth of Astra's cost.

claude-sonnet-4-5 retires 2026-11-30 per Anthropic's published model lifecycle.

## Consequences

**Breaking invariant**: Configured and executed models must agree or the step fails. No silent model switching, no fallback chain. A model mismatch is a loud failure recorded in the run report.

**Runtime dispatch contract**: The runner passes the effective model to the runtime through a channel it controls (environment variable or command argument). The runtime selects Anthropic or OpenAI execution path based on the model family. This makes the configured model and the executed model the same value by construction.

**Review channel unchanged**: Review file validation, the one in-session correction, parser contract and producer mechanism stay identical for Claude and Codex executed reviewers. Wrapper validates review files the same way under both runtimes.

**Cost measurement**: claude-opus-5-5, claude-sonnet-5-5 and openai/gpt-6.1-sol carry no price table entries. No verifiable source was recorded, so no price is invented; their steps record cost measured false with the reason. An entry may be added only with a source a reviewer can check, labelled with that source and a current date.

**Design station model**: The UX module's guided design stations (reviewer-design, reviewer-ux, builder on UI surfaces) execute on openai/gpt-6.1-sol as the routing policy specifies. The model is visible per step in run reports.

**Field continuity**: Report field astra_measured_tokens_total keeps its name (the test suite pins it). Comments describing it are updated to say interface stations, reflecting the field's broader role.

**Live proof sequencing**: This run executes on the wiring it replaces (the branch starts from main with the old models), so this run's own executed model labels are the old ones. The new wiring's live proof is the operator's post-merge verification run plus the smoke script tools/model_route_smoke.py probing the four routes.
