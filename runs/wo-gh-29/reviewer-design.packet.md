# Task packet: reviewer-design

## Station prompt

# Reviewer Design

## Role
Judge interface output against the project's own design system: its design tokens, component and layout rules, motion rules, and quality bars.

## Inputs
- design system (tokens, rules, quality bars from design/DESIGN.md and design/tokens.json)
- interface output (HTML, React components, CSS, user-facing pages, or other interface artifacts)

## Outputs
- review (JSON format with verdict and findings)

## Rules
- Work only from the inputs listed above and the work order in the packet.
- If the project has no design system (no design/DESIGN.md), your verdict MUST be `changes_requested` with a finding stating that no design system exists for the project.
- If the project has a design system, review the interface output against:
  - Design tokens: Are the correct colors, typography, spacing values being used?
  - Component and layout rules: Do components follow the documented patterns?
  - Motion rules: Does any animation or transition follow the motion guidelines?
  - Quality bars: Does the interface meet the stated quality bars for visual hierarchy, scale contrast, spacing rhythm, and responsive behavior?
- **Authority**: The project's own design system (design/DESIGN.md, design/tokens.json) is the authority for this project. The Design knowledge section in your packet (when present) is reference material that the design system may draw from. On any conflict between the project's design system and the knowledge base, the project's design system wins. A deviation from the knowledge base alone is never a finding; a deviation from the project's design system is.
- Focus on the design system the project has defined. Do not impose external design opinions or preferences that are not documented in the project's design system.
- A design token marked as "TODO" or placeholder means the project hasn't defined that value yet. Flag missing values as findings only if the interface output actually uses undefined tokens.
- Findings should be specific and actionable: cite which quality bar was violated, which token was used incorrectly, or which rule was not followed. When referencing the Design knowledge base in a finding or suggestion, name the specific knowledge entry (e.g., "metrics-blue palette", "data-dense style", "accessibility guideline for contrast").
- Your verdict must be one of: `pass`, `fail`, or `changes_requested`.
- Produce the output as a JSON object, not as chat text.

## Output Format

For visual runs (when Quality Charter is present in your packet), return a JSON object with dual-section structure:

{
  "station": "reviewer-design",
  "verdict": "pass | fail | changes_requested",
  "compliance": {
    "verdict": "pass | fail | changes_requested",
    "findings": [
      "Design system compliance findings (tokens, rules, component patterns)"
    ]
  },
  "quality": {
    "verdict": "pass | fail | changes_requested",
    "findings": [
      "Quality findings comparing output against reference anchors and charter criteria"
    ],
    "anchor": "path/to/anchor/file or 'charter floor only' when no anchors"
  }
}

For non-visual runs (no Quality Charter in packet), return the simple structure:

{
  "station": "reviewer-design",
  "verdict": "pass | fail | changes_requested",
  "findings": [
    "Specific finding with reference to design system rule or quality bar"
  ]
}

### Dual-Section Review (Visual Runs)

For visual runs:

1. **Compliance section**: Judge design system adherence - tokens, component patterns, layout rules, motion guidelines.

2. **Quality section**: Judge visual quality by comparing the output against reference anchors and charter criteria. This is a separate judgment from compliance.
   - When reference anchors are present: Compare the output against the anchors. Name gap categories from the charter criteria (materials, light, scale, contact for physical products; stated criteria for games/illustrations).
   - When no anchors: Judge against charter floor alone.
   - Cite the anchor used in comparison or state "charter floor only" when no anchors available.

The overall verdict is the stricter of the two section verdicts. An output can pass compliance but fail quality, and such a case must be reported as changes_requested or fail at the overall level.

**Same-Subject Identity Consistency (S7)**: When the work order declares an `identity_reference` for runs producing multiple related visual outputs, the quality section may extend beyond individual anchor evaluation to include same-subject identity consistency verification across deliverable outputs. Your packet will specify this requirement when applicable. You must verify that all outputs maintain identical subject identity traits enumerated in the work order (examples for physical products: finish, detail colors, mounting or attachment, proportions and markings; stated equivalents apply for other product types). Divergence in these traits constitutes a quality failure even when each output individually meets anchor criteria. Such failures must name the specific output and trait in your findings, with ruling and evidence recorded in the quality section. This verification is part of quality section judgment, not a separate verdict.

### Quality Criteria by Product Type

When judging quality section findings, name specific criteria gaps:

**Physical products**: materials, light, contact, scale
**Games/Illustrations**: Apply the project's stated standard from the design system

The station field must equal "reviewer-design", and both the overall verdict and section verdicts must be one of pass, fail, or changes_requested.

## Examples

Example 1: No design system exists
- verdict: changes_requested
- finding: "No design system exists for this project. The project must define design/DESIGN.md and design/tokens.json before interface output can be reviewed against design standards."

Example 2: Interface violates quality bar
- verdict: changes_requested
- findings:
  * "Quality bar violation: Scale Contrast - The button text has only 2.8:1 contrast ratio against its background, failing the minimum 4.5:1 requirement stated in the quality bars."
  * "Token usage: The page uses hardcoded color '#FF5733' instead of the defined primary color token."

Example 3: Interface meets design system
- verdict: pass
- findings: (empty list)


<!-- source: design/DESIGN.md -->
## Project design

### Design tokens

```json
{
  "colors": {
    "primary": "TODO",
    "secondary": "TODO",
    "accent": "TODO",
    "background": "TODO",
    "surface": "TODO",
    "text": "TODO",
    "text-secondary": "TODO",
    "error": "TODO",
    "warning": "TODO",
    "success": "TODO",
    "info": "TODO"
  },
  "typography": {
    "font-family-base": "TODO",
    "font-family-heading": "TODO",
    "font-family-mono": "TODO",
    "font-size-base": "TODO",
    "font-size-scale": "TODO",
    "line-height-base": "TODO",
    "line-height-heading": "TODO"
  },
  "spacing": {
    "unit": "TODO",
    "scale": [
      "TODO"
    ]
  },
  "layout": {
    "max-width": "TODO",
    "breakpoint-mobile": "TODO",
    "breakpoint-tablet": "TODO",
    "breakpoint-desktop": "TODO"
  },
  "motion": {
    "duration-fast": "TODO",
    "duration-base": "TODO",
    "duration-slow": "TODO",
    "easing-standard": "TODO",
    "easing-enter": "TODO",
    "easing-exit": "TODO"
  }
}
```

### Quality bars

for Product Pages

These bars apply to every product page or interface this project ships.

### Visual Hierarchy
- [ ] Clear content hierarchy with size, weight, and spacing
- [ ] Important actions are visually prominent
- [ ] Related elements are grouped

### Scale Contrast
- [ ] Minimum 4.5:1 contrast ratio for normal text
- [ ] Minimum 3:1 contrast ratio for large text (18pt+)
- [ ] Interactive elements have sufficient contrast

### Spacing Rhythm
- [ ] Consistent spacing scale used throughout
- [ ] Whitespace creates clear content boundaries
- [ ] Spacing adapts appropriately to different screen sizes

### Responsive Behavior
- [ ] Layout works on mobile, tablet, and desktop
- [ ] Touch targets are at least 44x44px on mobile
- [ ] Text is readable without zooming on any device
- [ ] No horizontal scrolling on standard viewports


## Spec

<!-- source: .openspec/specs/model-migration/spec.md -->
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
concrete model at the hand-off itself: after ALL overrides (registry, project
config, routing and guided) have produced the step's final model label, and
before both recording configured_model and passing the model to the runtime.
This holds for every station and every executing branch, intake included,
and in particular for the routed path where the routing record's
selected_models (tier labels) replace the initially computed model inside
run_pipeline. One total map covers every
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
- credential: CF_AIG_TOKEN when set; otherwise the bearer token carried by the
  cf-aig-authorization header inside ANTHROPIC_CUSTOM_HEADERS, which is how
  the standing workflows supply the gateway credential
- model: the bare id gpt-6.1-sol
It fails loudly only when neither credential source is present or the gateway
coordinates are absent, naming what is missing and never printing, logging or
writing any credential value.

S8. Unit tests prove every label in the R10 map resolves as listed and the
map is total over the labels the runner can produce. An integration test
drives run_pipeline with a routing record whose selected_models are tier
labels and a fake command runtime, and asserts the runtime received the
concrete model and the recorded configured_model is concrete. A test of the
map function alone does not satisfy this scenario.
S9. Unit tests prove the OpenAI runtime constructs its configuration from
ANTHROPIC_BASE_URL plus either CF_AIG_TOKEN directly or the
cf-aig-authorization value parsed from an ANTHROPIC_CUSTOM_HEADERS fixture
string, honours ANVIL_GATEWAY_OPENAI_URL when set, fails loudly when neither
credential source is present, and never emits the credential value.
S10. The agent-execution S8 provenance tests pass unmodified: executed_model
is null when the runtime reports none and equals the self-reported value when
it reports one, under every executor class.
S11. The price table contains no entry without a verifiable source and date;
the three new models are unpriced unless such a source is provided.

R12. The OpenAI runtime is agentic. Station execution for openai/* models
runs the Codex CLI headlessly, in the repo working tree, with the packet as
the task. It is not a plain chat completion: a station on this runtime can
read the tree and run shell commands, so reviewers can write their review file
and the builder can edit. Contract, mirroring the Claude wrapper:
- configuration: Codex is configured against the gateway OpenAI provider route
  (endpoint and credential per R11), with the bare model id gpt-6.1-sol. The
  credential is handed to Codex through its environment key mechanism and is
  never printed, logged, or written to a tracked file.
- permissions: builder and test-writer may write. Every other station,
  reviewers included, runs without edit tools on the code under judgment but
  can write its own review file through the shell channel, as the producer
  contract requires.
- review validation and the one in-session correction behave exactly as in the
  Claude wrapper.
- provenance: the runtime self-reports the model it ran (openai/gpt-6.1-sol)
  through the existing self-report channel, so executed_model is runtime
  evidence, not a label copy (R3).
- failure: if the Codex CLI is absent or cannot be configured, the station
  fails loudly. There is no fallback to a bare completion for station
  execution. A plain completion call may exist only inside
  tools/model_route_smoke.py, which is a probe and not a runtime.

R13. Test correction ruling (operator, round 5). Two assertions in
migration tests encode superseded contracts and are corrected by the
test-writer, and only these:
- tests/test_model_migration_loopback.py: the builder step's configured_model
  is the resolved concrete model claude-opus-5-5, not the tier label
  fast-builder (R10).
- tests/test_model_migration_tiers.py (S9): the OpenAI runtime's missing
  environment error names the credential sources actually checked
  (CF_AIG_TOKEN and the ANTHROPIC_CUSTOM_HEADERS cf-aig-authorization header),
  and the no-raise case is the one where a credential source is present (R11).
No other existing assertion in any test changes. The builder changes no test
file.

S12. Unit tests prove the Codex wrapper builds a headless Codex invocation for
gpt-6.1-sol against the gateway OpenAI route with the credential only in the
child environment; builder and test-writer get write permission and every
other station does not; a reviewer's review file is validated with the one
in-session correction as under Claude; the wrapper self-reports
openai/gpt-6.1-sol; an absent Codex CLI fails loudly with no completion
fallback. Fake runtimes stand in for the CLI in tests.
S13. The corrected assertions of R13 pass and the full suite is green.
Acceptance evidence is the run itself: reviewer-design executes on the Codex
runtime, writes a valid review file the runner counts, and its step records
executed_model openai/gpt-6.1-sol from the runtime's self-report.


## Diff summary

- .openspec/specs/model-migration/spec.md: +48, -0
- CHANGELOG.md: +1, -0
- docs/EXECUTION.md: +12, -0
- runs/wo-gh-29/builder.output.md: +21, -15
- runs/wo-gh-29/builder.packet.md: +17, -0
- runs/wo-gh-29/checks-gate.pre-review.output.md: +32, -71
- runs/wo-gh-29/envelopes/builder.envelope.json: +1, -1
- runs/wo-gh-29/envelopes/checks-gate.envelope.json: +7, -45
- runs/wo-gh-29/envelopes/intake.envelope.json: +1, -1
- runs/wo-gh-29/envelopes/reviewer-architecture.envelope.json: +23, -4
- runs/wo-gh-29/envelopes/reviewer-security.envelope.json: +20, -4
- runs/wo-gh-29/envelopes/reviewer-spec.envelope.json: +20, -4
- runs/wo-gh-29/envelopes/reviewer-tests.envelope.json: +20, -4
- runs/wo-gh-29/envelopes/spec-writer.envelope.json: +1, -1
- runs/wo-gh-29/envelopes/test-writer.envelope.json: +2, -2
- runs/wo-gh-29/intake.output.md: +1, -1
- runs/wo-gh-29/intake.packet.md: +17, -0
- runs/wo-gh-29/reviewer-architecture.packet.md: +21, -5
- runs/wo-gh-29/reviewer-security.packet.md: +19, -3
- runs/wo-gh-29/reviewer-spec.packet.md: +18, -2
- runs/wo-gh-29/reviewer-tests.packet.md: +20, -4
- runs/wo-gh-29/routing.json: +2, -2
- runs/wo-gh-29/spec-writer.output.md: +14, -5
- runs/wo-gh-29/spec-writer.packet.md: +17, -0
- runs/wo-gh-29/test-writer.output.md: +19, -20
- runs/wo-gh-29/test-writer.packet.md: +17, -0
- tests/test_model_migration_loopback.py: +1, -1
- tests/test_model_migration_tiers.py: +19, -2
- tools/codex_station.py: +189, -44
- tools/model_route_smoke.py: +40, -0
- work_orders/wo-gh-29.json: +4, -4

## File access allowlist

This packet may only embed content from:
- design/DESIGN.md
- design/tokens.json
- .openspec/specs/model-migration/spec.md
- .openspec/specs/model-migration/spec.md
- CHANGELOG.md
- docs/EXECUTION.md
- runs/wo-gh-29/builder.output.md
- runs/wo-gh-29/builder.packet.md
- runs/wo-gh-29/checks-gate.pre-review.output.md
- runs/wo-gh-29/envelopes/builder.envelope.json
- runs/wo-gh-29/envelopes/checks-gate.envelope.json
- runs/wo-gh-29/envelopes/intake.envelope.json
- runs/wo-gh-29/envelopes/reviewer-architecture.envelope.json
- runs/wo-gh-29/envelopes/reviewer-security.envelope.json
- runs/wo-gh-29/envelopes/reviewer-spec.envelope.json
- runs/wo-gh-29/envelopes/reviewer-tests.envelope.json
- runs/wo-gh-29/envelopes/spec-writer.envelope.json
- runs/wo-gh-29/envelopes/test-writer.envelope.json
- runs/wo-gh-29/intake.output.md
- runs/wo-gh-29/intake.packet.md
- runs/wo-gh-29/reviewer-architecture.packet.md
- runs/wo-gh-29/reviewer-security.packet.md
- runs/wo-gh-29/reviewer-spec.packet.md
- runs/wo-gh-29/reviewer-tests.packet.md
- runs/wo-gh-29/routing.json
- runs/wo-gh-29/spec-writer.output.md
- runs/wo-gh-29/spec-writer.packet.md
- runs/wo-gh-29/test-writer.output.md
- runs/wo-gh-29/test-writer.packet.md
- tests/test_model_migration_loopback.py
- tests/test_model_migration_tiers.py
- tools/codex_station.py
- tools/model_route_smoke.py
- work_orders/wo-gh-29.json

## Work order

- id: wo-gh-29
- kind: feature
- title: Runtime model migration: per-station models, Sol for design stations, retire claude-sonnet-4-5 and gpt-6-astra
- source: github-issue
- description: Implement the spec in .openspec/specs/model-migration/spec.md in the factory. This order moves the factory's execute wiring off claude-sonnet-4-5 (retires 2026-11-30) and retires gpt-6-astra entirely. Owner's order 2026-11-03, from the executed benchmark in issue 22 (Astra, Opus 5.5 and Sol tied at recall 10 of 10 and builder compliance 12 of 12; cost per task Sol about a fifth of Astra).

Build, per the spec requirements:

R1: anvil.yaml carries an explicit model for every station the sdlc-default pipeline executes: builder claude-opus-5-5; spec-writer and test-writer claude-sonnet-5-5; reviewer-spec, reviewer-tests, reviewer-security, reviewer-architecture claude-sonnet-5-5; intake, scout, supervisor, observer, deployer claude-sonnet-5-5; reviewer-design and reviewer-ux openai/gpt-6.1-sol. No claude-sonnet-4-5 remains in the standing wiring.

R2: anvil/routing.py MODEL_POLICY designer becomes openai/gpt-6.1-sol; the fallback in anvil/knowledge.py matches; docs/UX-MODULE.md updated to state the new design model. gpt-6-astra appears nowhere in the standing wiring after this change.

R3: the station runtime dispatches on the effective model the runner assigned for the step (configured_model, including routing and guided overrides), passed to the runtime through a channel the runner controls (environment or argument; the runtime command template in anvil.yaml may gain a placeholder if needed). Anthropic models run through Claude Code print mode with --model set to the assigned model via the gateway Anthropic route. openai/gpt-6.1-sol runs through an agentic OpenAI runtime (Codex) pointed at the gateway OpenAI provider route with the bare model id gpt-6.1-sol. Any other model value fails the step loudly: no default, no fallback, no silent switching. The executed model in the run report comes from runtime evidence (what the runtime reports it ran), never copied from the configured label.

R4: review channel invariants under both runtimes. Reviewers (design included) write exactly their own review file through the scoped channel; wrapper review validation and the one in-session correction work the same for Claude and Codex executed reviewers; parser contract and producer mechanism unchanged. Builder and test-writer keep write access; other stations keep the edit denylist or runtime equivalent.

R5: the builder executes on openai/gpt-6.1-sol when the runner assigns the guided design model (UI surface work) and on claude-opus-5-5 otherwise, both visible per step in the report.

R6: price table entries for claude-opus-5-5, claude-sonnet-5-5 and openai/gpt-6.1-sol, each labelled with source and date recorded, or an entry omitted with the cost record honestly unmeasured; no invented prices.

R7: brain/decisions/0004 following the existing decision record convention (heading, Status: accepted, Adopted line with the owner's order, Decision, Why, Consequences): the Sol switch, the owner's order of 2026-11-03, the benchmark evidence (tie at recall 10 of 10 and compliance 12 of 12; Sol at about a fifth of Astra's per task cost; record on branch anvil/benchmark-record-wo-gh-22), the 2026-11-30 retirement of claude-sonnet-4-5, and the rule that configured and executed models must agree or the step fails.

R8: tools/model_route_smoke.py probing four routes with the workflow environment credentials (Anthropic route text for claude-sonnet-5-5 and claude-opus-5-5; OpenAI route text and vision for gpt-6.1-sol), one line per route, non-zero exit naming any failing route, never printing credential values.

R9: the report field astra_measured_tokens_total keeps its name; its comments are updated to say interface stations.

Tests covering S1 to S7 in the factory suite style: dispatch selection per model family, loud failure on unknown models, the effective model reaching a fake runtime per station (including the guided override cases), review channel invariants under both runtimes, decision record presence and sections, price table validation. Docs and CHANGELOG Unreleased updated.

Sequencing truth, stated for the reviewers: this run executes on the wiring it replaces (the branch starts from main as it stands), so this run's own executed models are the old ones; the new wiring's live proof is the operator's post-merge verification run plus the R8 smoke script. Judge this order on the wiring, the dispatch tests and the invariants, not on this run's executed model labels.

Guardrails: do not rewrite historical records (runs/ evidence, past per-order workflow files under .github/workflows/ stay byte-identical; this order's own new workflow file is the operator's, not the builder's, to change). Do not modify or delete any existing file under tests/ (the checks gate treats base ref test files as protected); new tests go in new files. The review parsing contract, the producer mechanism and the checks gate base ref behavior are frozen. Keep the full suite green and every pipeline valid. No em dash or en dash characters in any produced file.

GitHub issue: https://github.com/arananet/anvil-factory/issues/29

GATE LOOPBACK (round 2). Round 1 verdict: no_reviews. The implementation was built (anvil.yaml per-station models, routing and knowledge policy on openai/gpt-6.1-sol, tools/dispatch_station.py and tools/codex_station.py created, claude_station.py reading the model from the environment, executor and runner passing configured_model, decision record 0004, smoke script, 25 new tests in tests/test_model_migration.py passing) but the checks gate failed the run on the suite: 505 tests, FAILED (failures=2, errors=7, skipped=1), reviewers skipped in both attempts. The counted gate findings, verbatim in substance:

1. PROVENANCE REGRESSION (tests/test_execution.py, agent-execution S8, both FAIL). test_command_executor_never_guesses_a_model_s8: the builder step's executed_model came back as the configured tier label ('fast-builder') when the runtime reported no model; S8 requires null unless the runtime reports one. test_command_executor_records_a_self_reported_model_s8: when the runtime output reports a model ('self-reported-1'), executed_model must be that value, not the configured label. Round 1 conflated the hand-off with the record: passing configured_model INTO the runtime is the R3 requirement, but executed_model is recorded ONLY from runtime self-report evidence, exactly as before this order. Fix the runner/executor so both hold at once. The dispatch wrapper self-reports the model it actually dispatched through the existing self-report channel, so executed evidence exists for the new runtimes without guessing.

2. INCOMPLETE SIGNATURE CHANGE (7 errors). TypeError: HttpExecutor.execute() got an unexpected keyword argument 'configured_model'. Every executor class the runner can call must accept the model hand-off consistently (command, HTTP, and any other implementation), including the packet-only paths and the suite's fake executors' contracts. No call site may raise on the new argument.

3. INVENTED PRICES (spec R6 and S5). Round 1 added price entries labelled 'anthropic-pricing-2024-12' (dated 2024-12-15) and 'openai-pricing-2024-11' for models that did not exist under those names in 2024. Those sources are fabricated and the entries violate R6: no price is invented. Remove all three entries (claude-opus-5-5, claude-sonnet-5-5, openai/gpt-6.1-sol). The models stay unpriced; their steps record measured false with the reason, per the cost spec. Entries may return only with a verifiable source the reviewer can check, labelled with that source and a current date.

Loopback scope is exactly these three fixes on top of the standing round 1 tree. Do not revisit the parts no reviewer or gate faulted. HARD CONSTRAINTS unchanged: full suite green (the two S8 provenance tests and the whole test_execution module included, unmodified); do NOT modify or delete any existing file under tests/ (new tests only in new files); review parsing contract, producer mechanism and checks gate base ref behavior frozen; no em dash or en dash characters in any produced file.

GATE LOOPBACK (round 3). Round 2 verdict: no_reviews, but the failure class changed completely and the round 2 fixes are confirmed working: the checks gate PASSED (the S8 provenance regressions and the executor signature errors are gone), and the Claude stations executed on the new wiring with honest provenance (intake, spec-writer, test-writer and observer on claude-sonnet-5-5 self-reported; builder on claude-opus-5-5 self-reported). All five selected reviewers FAILED before executing, for exactly two reasons, both in the run envelopes:

1. TIER LABELS REACH THE DISPATCHER (reviewer-spec, reviewer-security, reviewer-tests, reviewer-architecture). Error of record: "dispatch_station: unknown model 'review-balanced'. Known models: claude-opus-5-5, claude-sonnet-5-5, openai/gpt-6.1-sol". The routing step assigns abstract tier labels (review-balanced, review-strong) as selected_models, the runner passes them through as the effective model, and the dispatcher rightly refuses them. The old wrapper ignored model labels entirely, so tiers never mattered until this order made the label load-bearing. The missing layer is tier resolution: a single concrete model map, applied by the runner when it computes the step's effective model (after registry, project config, routing and guided resolution), covering every label the runner can produce: review-balanced, review-strong, fast-builder, reasoning-strong, writing-strong, fast-reader, media-gen and default. Resolution follows R1: review-balanced and review-strong resolve to claude-sonnet-5-5 (every non-design reviewer runs claude-sonnet-5-5, security included); fast-builder and reasoning-strong resolve to claude-opus-5-5; writing-strong, fast-reader, media-gen and default resolve to claude-sonnet-5-5. The map is total: no label reaches the runtime unresolved, the report's configured_model is always a concrete model, and the dispatcher keeps failing loudly on anything that is not a known concrete model. Routing's own tier vocabulary and its spec do not change; resolution happens at hand-off. Unit tests prove each tier resolves per this table, that a routed reviewer's hand-off to a fake runtime carries the concrete model, and that configured_model in the report is concrete for routed reviewers.

2. THE OPENAI RUNTIME DEMANDS ENVIRONMENT THE LINE NEVER SUPPLIES (reviewer-design). Error of record: "codex_station: Missing OPENAI_BASE_URL or OPENAI_API_KEY environment variables". The standing execute workflows supply exactly the gateway environment the Anthropic route uses: ANTHROPIC_BASE_URL (which carries the gateway coordinates), ANTHROPIC_CUSTOM_HEADERS and the CF_AIG_TOKEN secret. No OPENAI_* variables exist anywhere in the line, and this order may not require new secrets. The OpenAI runtime must build its endpoint and credential from that same environment: the gateway OpenAI provider route derived from the gateway coordinates in ANTHROPIC_BASE_URL (or an explicit ANVIL_GATEWAY_OPENAI_URL when provided), authorized with CF_AIG_TOKEN, called with the bare model id gpt-6.1-sol. It fails loudly only when that gateway environment is absent. A unit test proves the runtime constructs its configuration from CF_AIG_TOKEN and ANTHROPIC_BASE_URL alone.

Noted for the record, not a defect: reviewer-ux was routed out by routing on intake's own assessment of this run (no UI surface in intake's outcome), which is the routing capability working as designed.

Loopback scope is exactly these two fixes on top of the standing tree. HARD CONSTRAINTS unchanged: full suite green with existing tests unmodified; new tests only in new files; review parsing contract, producer mechanism, routing tier vocabulary and checks gate base ref behavior frozen; no em dash or en dash characters in any produced file.

GATE LOOPBACK (round 4, final). Round 3 verdict: no_reviews again; gate passed; Claude stations again executed on the new models with honest provenance. Both round 3 items were attempted and both miss their target by one mechanism each. The errors of record:

1. TIER RESOLUTION NOT ON THE ROUTED PATH. reviewer-spec envelope, unchanged: "dispatch_station: unknown model 'review-balanced'", and the step's configured_model still records the tier. Round 3 added a resolution map (anvil/config.py) but the routed reviewer path never passes through it: in run_pipeline the routing override replaces configured_model with routing_record.selected_models (tier labels) after the initial computation, and the executor hand-off uses that value. Resolution must be applied at the hand-off itself: after ALL overrides (registry, project config, routing, guided) have produced the step's final model label, the runner resolves that label through the concrete map before recording configured_model and before passing the model to the runtime, for every station and every branch that executes (intake included). Proof requirement, stated plainly because round 3's tests passed while the wired path stayed broken: an integration test that drives run_pipeline with a routing record selecting tier models and a fake command runtime, asserting the runtime received the concrete model and the recorded configured_model is concrete. A test of the map function in isolation does not count.

2. CODEX CREDENTIAL SOURCE. reviewer-design envelope: "codex_station: gateway environment absent, missing: CF_AIG_TOKEN". The standing workflows never export CF_AIG_TOKEN as its own variable; the gateway credential travels inside ANTHROPIC_CUSTOM_HEADERS as the header 'cf-aig-authorization: Bearer <token>', which IS present in the runtime's environment (the Claude wrapper inherits the same environment). The OpenAI runtime must take the credential from that header when CF_AIG_TOKEN is not set: parse the cf-aig-authorization value out of ANTHROPIC_CUSTOM_HEADERS, use CF_AIG_TOKEN directly when it is set, and fail loudly only when neither is present. The credential value is never printed, logged or written to any file. Unit test with a headers fixture string proving the parse, plus the direct variable path.

This is the final loopback for this order. Scope is exactly these two mechanisms on the standing tree; nothing else changes. HARD CONSTRAINTS unchanged: full suite green with existing tests unmodified; new tests only in new files; review parsing contract, producer mechanism, routing tier vocabulary and checks gate base ref behavior frozen; no em dash or en dash characters in any produced file.

GATE LOOPBACK (round 5, final). Round 4 verdict: no_reviews; the in-run gate loopback was spent and the gate failed again, this time on three failures inside the line's own migration tests. Round 4's two mechanisms themselves LANDED: the run's steps record concrete configured models for every station (reviewers included), which is visible in the round 4 report. What remains is one operator ruling and one runtime substitution.

PART A: OPERATOR RULING ON TWO STALE TESTS (test correction round, the wo-gh-10 pattern). The following assertions encode superseded rounds' contracts and contradict the round 4 requirements of record, which stand:
1. tests/test_model_migration_loopback.py asserts the builder step's configured_model equals the tier label 'fast-builder'. Round 4 requires configured_model to be the resolved concrete model ('claude-opus-5-5'). The assertion is corrected to the concrete model.
2. tests/test_model_migration_tiers.py (S9) asserts the OpenAI runtime's missing environment error names 'CF_AIG_TOKEN' and that the runtime raises when only ANTHROPIC_BASE_URL is present. Round 4 replaced the credential source: the token is taken from ANTHROPIC_CUSTOM_HEADERS' cf-aig-authorization header when CF_AIG_TOKEN is unset, and the runtime fails only when neither source exists. The test is corrected to that contract: error naming follows the sources actually checked, and the no-raise case is the one where a credential source IS present.
The TEST-WRITER corrects exactly these assertions; the builder changes no test file, and no other assertion in any test changes. Implementation behavior per the round 4 brief is not reopened by this part.

PART B: THE OPENAI RUNTIME MUST BE AGENTIC (spec R3, unmet). Audit of the standing tools/codex_station.py: its call_openai_api is a plain chat completion (one prompt, one text reply, no tools). A reviewer executed through it cannot write its review file, cannot read the tree it judges, and its wrapper's review validation can never pass; a builder executed through it cannot edit anything. That is a stand-in, not the agentic runtime R3 requires, and it may not be presented as one. Replace the station execution for openai/* models with a real agentic Codex runtime, mirroring the Claude wrapper's contract exactly:
- The operator has staged the Codex CLI in this order's execute workflow (npm @openai/codex). The wrapper invokes it headlessly with the packet as the task, in the repo working tree.
- The wrapper configures Codex against the gateway OpenAI provider route (coordinates derived as in round 4, credential from CF_AIG_TOKEN or the cf-aig-authorization header in ANTHROPIC_CUSTOM_HEADERS, handed to Codex through its environment key mechanism, never printed or written to a tracked file), with the bare model id gpt-6.1-sol.
- Permissions mirror the Claude wrapper: builder and test-writer may write; every other station, reviewers included, runs without edit tools on the code under judgment but CAN write its own review file through the shell channel, exactly as the producer contract requires. Review validation and the one in-session correction behave as in the Claude wrapper.
- The runtime self-reports the model it ran (openai/gpt-6.1-sol) through the existing self-report channel, so executed_model is evidence, not a label copy.
- If the Codex CLI is absent or cannot be configured, the station fails loudly. There is no fallback to a bare completion for station execution. The plain completion call may survive only inside tools/model_route_smoke.py, which is a probe, not a runtime.
Acceptance evidence is this run itself: reviewer-design executes on the Codex runtime, writes a valid review file that the runner counts, and its step records executed_model openai/gpt-6.1-sol from the runtime's self-report.

This is the final loopback. HARD CONSTRAINTS unchanged: full suite green; existing tests change only through Part A's two named corrections, made by the test-writer; review parsing contract, producer mechanism, routing tier vocabulary and checks gate base ref behavior frozen; no em dash or en dash characters in any produced file.
- risk_hints: 
- status: new

## Rendered evidence

This run captured screenshots of the served project at the following breakpoints:

- `screenshot-1440x900.png` at `runs/wo-gh-29/evidence/screenshot-1440x900.png`
- `screenshot-390x844.png` at `runs/wo-gh-29/evidence/screenshot-390x844.png`

**Design review instruction:** When judging layout, scale, spacing, or visual hierarchy findings, cite the rendered evidence screenshots where applicable. The screenshots show what the page actually looks like at each breakpoint, not just what the source implies.


## Design knowledge

**Authority**: The project's own design system (design/DESIGN.md, design/tokens.json) is the authority for this project. The knowledge base below is reference material that the design system may draw from. On any conflict, the project's design system wins. A deviation from the knowledge base alone is not a finding; a deviation from the project's design system is.

**Note**: No product type slice matched. General guidelines only.

### Product Type: Undeclared

No specific product type declared. Using general guidelines only.

### UX Guidelines

**Accessibility:**
- Maintain minimum 4.5:1 contrast ratio for normal text, 3:1 for large text (18pt+)
- Touch targets must be at least 44x44px on mobile devices

**Feedback:**
- Loading states should appear after 300ms delay to avoid flashing
- Provide immediate visual feedback for user actions

**Forms:**
- Form fields should have clear labels and validation feedback
- Error messages should explain what went wrong and how to fix it

**Hierarchy:**
- Establish clear visual hierarchy using size, weight, and color
- Important actions should be visually prominent and easy to locate

**Motion:**
- Keep animation durations between 200-400ms for most transitions
- Provide reduced motion alternatives for users with vestibular sensitivity

**Responsive:**
- Test layouts at mobile (320-768px), tablet (768-1024px), and desktop (1024px+) breakpoints
- Avoid horizontal scrolling on standard viewports

**Spacing:**
- Use consistent spacing scale throughout (e.g., 4px, 8px, 16px, 24px, 32px)
- Group related elements together with whitespace separating distinct sections


## Quality Charter

Product type: physical_product

Observable criteria:

- **Materials**: Surfaces read as the materials the product is actually made of
- **Light**: One coherent light story, with shadows and reflections that agree with it
- **Contact**: Objects meet skin, surfaces and each other the way physical things do
- **Scale**: The object's size reads true against its context and human anatomy


## Reference Anchors

⚠️ **WARNING**: This run has no reference anchors.

The review will proceed under the charter floor alone.

