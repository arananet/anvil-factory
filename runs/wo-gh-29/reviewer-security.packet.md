# Task packet: reviewer-security

## Station prompt

# Reviewer Security

## Role
Check the change for security risks and unsafe defaults.

## Inputs
- code change

## Outputs
- review

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.

## Output Format

Return a JSON object with this structure:

{
  "station": "reviewer-security",
  "verdict": "pass | fail | changes_requested",
  "findings": [
    "Specific finding with reference to design system rule or quality bar",
    "Another finding if applicable"
  ]
}

The station field must equal "reviewer-security", the verdict must be one of pass, fail, or changes_requested, and findings must be a list of strings.


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
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed
- test-writer: executed
- builder: executed
- checks-gate: failed
- loopback: loopback
- reviewer-spec: skipped

## Output contract

Your complete answer is exactly one review JSON object written to runs/wo-gh-29/reviewer-security.review.json. The free output transcript stays as provenance and is never parsed for a review.
