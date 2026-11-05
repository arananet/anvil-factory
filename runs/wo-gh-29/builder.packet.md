# Task packet: builder

## Station prompt

# Builder

## Role
Implement the spec so the scenario tests pass.

## Inputs
- spec
- tests

## Outputs
- code change

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.
- **Design citation**: When authoring or revising design/DESIGN.md, include a "Design knowledge sources" note citing the knowledge entries you drew from by data kind and entry name (e.g., "Style: modern-minimal", "Palette: metrics-blue", "Guideline: accessibility - contrast ratio"). If the knowledge came from an operator-supplied pack, cite it as "operator-supplied pack entry" without naming the pack's origin.

### Visual Output Quality Verification

When your packet includes a Quality Charter section (visual runs only), you must verify each produced output against the run's reference anchors and charter criteria before the review step:

1. **Read the output**: Examine each visual deliverable you produce (images, UI components, rendered interfaces).

2. **Compare against anchors**: If reference anchors are provided, compare your output against them. Check how your output measures up to the anchor's quality bar across the charter criteria.

3. **Check charter criteria**: Evaluate your output against the observable criteria from the Quality Charter:
   - For physical products: materials, light, contact, scale
   - For games/illustrations: the stated standard from the project design system

4. **Record the comparison**: Document your findings in the run evidence directory (runs/{work_order_id}/evidence/) as a JSON file named `{output_filename}.comparison.json` with this structure:

```json
{
  "output": "path/to/generated/output.png",
  "anchor_cited": "path/to/reference/anchor.png or null if none",
  "criteria_checked": ["materials", "light", "contact", "scale"],
  "gaps": [
    {
      "criterion": "materials",
      "description": "Surfaces read as plastic rather than the metal shown in anchor"
    }
  ],
  "statement": "Explicit statement: 'No gaps found at charter bar' or description of gaps identified"
}
```

5. **Evidence, not verdict**: Your comparison is evidence for reviewers, not a final verdict. Record what you observe; reviewers are not bound by your self-assessment.

This verification step only applies when the Quality Charter section is present in your packet. For non-visual work, this step does not apply.


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
