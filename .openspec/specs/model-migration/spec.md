# Model migration: per-station models, Sol for design stations

## Problem

The factory's execute wiring still runs on models the owner has retired by
decision. claude-sonnet-4-5 is the hardcoded model in the station runtime
wrapper (tools/claude_station.py) and the per-station model in anvil.yaml for
every executed station of the factory's own line, and it retires on
2026-11-30. The design model in the routing policy (anvil/routing.py
MODEL_POLICY) and its fallback in anvil/knowledge.py is openai/gpt-6-astra,
which the owner retired on 2026-11-03. Worse, the routing policy label and the
runtime disagree: guided design stations are labelled with the design model
while the wrapper executes every station on the same Claude model, so the
configured model and the executed model silently diverge.

## Decision basis

Owner's order, 2026-11-03: stop using Astra, use Sol for the design stations.
Evidence: the executed benchmark recorded for issue 22 (branch
anvil/benchmark-record-wo-gh-22). Astra, Opus 5.5 and Sol tied on quality
(reviewer recall 10 of 10 against the planted violations fixture; builder
token compliance 12 of 12 each), and measured cost per task was Sol about a
fifth of Astra (Sol 0.038 USD, Opus 0.137 USD, Astra 0.198 USD across both
arms, inside the owner's 10 euro hard cap).

## Requirements

R1. Per-station models in anvil.yaml. Every station the sdlc-default pipeline
executes on the factory's own line carries an explicit model:
- builder (non UI work): claude-opus-5-5
- spec-writer, test-writer: claude-sonnet-5-5
- reviewer-spec, reviewer-tests, reviewer-security, reviewer-architecture and
  every other non-design reviewer: claude-sonnet-5-5
- intake, scout, supervisor, observer, deployer: claude-sonnet-5-5
- reviewer-design, reviewer-ux: openai/gpt-6.1-sol
- Guided design stations (reviewer-design, reviewer-ux, builder on UI
  surfaces, design system authoring paths) resolve to openai/gpt-6.1-sol
  through the routing policy (R2), which the runner already applies as the
  configured model for guided stations.
No station in the standing wiring names claude-sonnet-4-5.

R2. Routing policy. MODEL_POLICY's designer entry is openai/gpt-6.1-sol, and
the fallback in anvil/knowledge.py matches it. Documentation that states the
current design model (docs/UX-MODULE.md) is updated to match. The string
gpt-6-astra appears nowhere in the standing wiring (anvil/, tools/,
stations/, pipelines/, anvil.yaml, docs stating current state). Historical
run records under runs/ and past per-order workflow files are records, not
wiring, and are not rewritten.

R3. Runtime dispatch by effective model. The station runtime executes each
station on the effective model the runner assigned (the runner's
configured_model for that step, including routing and guided overrides), and
that assignment reaches the runtime through a channel the runner controls.
Dispatch:
- Anthropic models (claude-opus-5-5, claude-sonnet-5-5): Claude Code in print
  mode with that model, through the gateway Anthropic route, as today.
- openai/gpt-6.1-sol: an agentic OpenAI runtime (Codex) pointed at the
  gateway OpenAI provider route, called with the bare model id gpt-6.1-sol.
- Any other model value fails the step loudly. There is no default model, no
  fallback chain and no silent model switching anywhere in the dispatch.
The executed model recorded in the run report comes from runtime evidence
(the runtime reports what it ran), never copied from the configured label.
Handing the configured model to the runtime is not recording it: executor and
runner record executed_model only from the runtime's self-report, and it is
null when the runtime reports none (agent-execution S8 holds unchanged). The
dispatch wrapper self-reports the model it actually dispatched through the
existing self-report channel. Every executor the runner can call (command,
HTTP, packet-only, and the suite's fake executors) accepts the model hand-off
consistently; no call site raises on it.

R4. Review channel invariants hold for every runtime. Reviewer stations,
design reviewers included, write exactly their own review file through the
scoped channel; the wrapper's review file validation and its one in-session
correction behave the same for Claude and Codex executed reviewers; the
parser contract and the producer mechanism are unchanged. Builder and
test-writer keep write access; every other station keeps the edit denylist
or its runtime equivalent.

R5. Builder on UI surfaces. When the runner assigns the guided design model
to the builder (work order carrying a UI surface), the builder executes on
openai/gpt-6.1-sol through the R3 dispatch. On non-UI work the builder
executes on claude-opus-5-5. The assignment is visible per step in the run
report (configured versus executed).

R6. Cost measurement. An entry for claude-opus-5-5, claude-sonnet-5-5 or
openai/gpt-6.1-sol may be added only with a verifiable source a reviewer can
check, labelled with that source and a current date, per the labeled price
rule of the cost measurement capability. Absent such a source the model stays
unpriced and its steps record measured false with the reason, as the cost
spec already provides. No source, date or price is invented or backdated.

R7. Decision record. brain/decisions/0004 records this switch following the
existing convention (records at brain/decisions/NNNN-slug.md, heading
"# Decision NNNN: title", "Status: accepted", "Adopted: <date>, by the
owner's order.", then Decision, Why, Consequences): the Sol switch, the
owner's order of 2026-11-03, the benchmark evidence from R-basis above, the
retirement of claude-sonnet-4-5 on 2026-11-30, and the rule that configured
and executed models must agree or the step fails.

R8. Route smoke script. tools/model_route_smoke.py probes, using only the
environment credentials the workflows already supply: the Anthropic route
with claude-sonnet-5-5 (text), the Anthropic route with claude-opus-5-5
(text), the OpenAI route with gpt-6.1-sol (text), and the OpenAI route with
gpt-6.1-sol (vision: a small image input answered about its content). It
prints one line per route and exits non-zero if any route fails. It never
prints credential values.

R9. Report field continuity. The run report field astra_measured_tokens_total
keeps its name (the suite pins it); comments that describe it are updated to
say interface stations. No test-pinned contract changes shape in this order.

## Scenarios

S1. A grep over the standing wiring (anvil/, tools/, stations/, pipelines/,
anvil.yaml, docs/) finds no claude-sonnet-4-5 and no gpt-6-astra.
S2. Unit tests prove dispatch selection: each Anthropic model selects the
Claude runtime with that model; openai/gpt-6.1-sol selects the OpenAI
runtime with the bare id; an unknown model fails loudly; the runner passes
the effective model to the runtime (a fake runtime records the model it was
handed, per station, including the guided override for reviewer-design and
for the builder on a UI surface work order, and the plain assignment for the
builder on a non-UI work order).
S3. Unit tests prove the review channel invariants under both runtimes: a
reviewer executed by either runtime contributes its review only from the
file it wrote; a missing or malformed file records the same failure classes
as today.
S4. The decision record 0004 exists with the required sections and states
the evidence and the owner's order date.
S5. The price table validates under the existing loader rules (every entry
labelled with source and date) and includes the three new models or records
why an entry is absent.
S6. The full factory suite stays green and every pipeline stays valid.
Historical records (runs/, past workflow files) are byte-identical to before
the change.
S7. tools/model_route_smoke.py exists, is executable by the workflows, and
its failure mode is a non-zero exit with the failing route named (its live
pass is proven by the operator's post-merge verification run, not by this
order's own run, which executes on the wiring it replaces).

R10. Tier resolution at hand-off. The runner resolves every model label to a
concrete model when it computes a step's effective model, after registry,
project config, routing and guided resolution. One total map covers every
label the runner can produce:
- review-balanced, review-strong: claude-sonnet-5-5
- fast-builder, reasoning-strong: claude-opus-5-5
- writing-strong, fast-reader, media-gen, default: claude-sonnet-5-5
- a value already concrete (claude-opus-5-5, claude-sonnet-5-5,
  openai/gpt-6.1-sol) passes through unchanged.
No label reaches the runtime unresolved, and configured_model in the report
is always a concrete model. The dispatcher still fails loudly on anything
that is not a known concrete model. Routing's tier vocabulary and its spec do
not change; resolution happens at hand-off only.

R11. OpenAI runtime environment. The OpenAI runtime (Codex) builds its
endpoint and credential from the gateway environment the workflows already
supply, with no new secrets and no OPENAI_* variables required:
- endpoint: the gateway OpenAI provider route derived from the gateway
  coordinates in ANTHROPIC_BASE_URL, or ANVIL_GATEWAY_OPENAI_URL when set
- credential: CF_AIG_TOKEN
- model: the bare id gpt-6.1-sol
It fails loudly only when that gateway environment is absent, naming the
missing variables and never printing their values.

S8. Unit tests prove every label in the R10 map resolves as listed, the map
is total over the labels the runner can produce, a routed reviewer's hand-off
to a fake runtime carries the concrete model, and configured_model in the
report is concrete for routed reviewers.
S9. A unit test proves the OpenAI runtime constructs its configuration from
CF_AIG_TOKEN and ANTHROPIC_BASE_URL alone, honours ANVIL_GATEWAY_OPENAI_URL
when set, and fails loudly when the gateway environment is absent.
S10. The agent-execution S8 provenance tests pass unmodified: executed_model
is null when the runtime reports none and equals the self-reported value when
it reports one, under every executor class.
S11. The price table contains no entry without a verifiable source and date;
the three new models are unpriced unless such a source is provided.
