# Task packet: observer

## Station prompt

# Observer

## Role
Watch the released change and report what actually happened.

## Inputs
- release record

## Outputs
- observation report

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.


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
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed
- test-writer: executed
- builder: executed
- checks-gate: passed
- reviewer-spec: failed
- reviewer-security: failed
- reviewer-tests: failed
- reviewer-architecture: failed
- reviewer-design: failed
- reviewer-ux: routed_out
- approver: completed
- triage-human: completed
- deployer: packet_ready
