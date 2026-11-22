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
- Read the spec, the tests and the code you are about to change before you write. Follow the project's existing structure and conventions.
- **Design citation**: When authoring or revising design/DESIGN.md, include a "Design knowledge sources" note citing the knowledge entries you drew from by data kind and entry name (e.g., "Style: modern-minimal", "Palette: metrics-blue", "Guideline: accessibility - contrast ratio"). If the knowledge came from an operator-supplied pack, cite it as "operator-supplied pack entry" without naming the pack's origin.

### Visual Output Quality Verification

When your packet includes a Quality Charter section (visual runs only), you must verify each produced output against the run's reference anchors and charter criteria before the review step:

1. **Read the output**: Examine each visual deliverable you produce (images, UI components, rendered interfaces).

2. **Compare against anchors**: If reference anchors are provided, compare your output against them. Check how your output measures up to the anchor's quality bar across the charter criteria.

3. **Check charter criteria**: Evaluate your output against the observable criteria from the Quality Charter:
   - For physical products: materials, light, contact, scale
   - For games/illustrations: the stated standard from the project design system
   - For interfaces (web pages, apps, dashboards): hierarchy, typography, layout, color, states, character

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

## Definition of done
- Every spec scenario for this order is satisfied on the final tree, not only the ones a test happens to cover.
- The project check command passes on the final tree. You ran it and read the output. You did not edit, skip or delete a test to get there.
- You exercised the change the way a user would (ran it, opened it, called it) and it works.
- For anything a person will see, you looked at the rendered result at the sizes the spec names and it meets the stated bar, the project design system and the Craft skills in your packet.
- The change stays inside the write set the work order allows.

## Before you hand off
Re-read your whole diff as a reviewer would and fix what you find. Then write the builder report: what changed and which scenario each change serves, the exact verification commands with their real summary lines, and plainly what is unmet, unverified or left open. A gap you report is better than one a reviewer finds.

## Consumption discipline

Read the spec and the relevant upstream artifacts first. Search before opening files; read only the relevant ranges. Bound command output and summarize long test logs with failures and a path to the full log. Run focused checks while editing and the required project checks at handoff. Reuse valid upstream work. Keep the final handoff concise, with changed files, evidence and unresolved issues. Preserve the required output contract.


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


## Craft skills

Curated craft guidance resolved for this station and this work order. Order of authority: the work order and its spec, then the project design system and decisions, then promoted practices, then these skills. Where a skill conflicts with any of those, the skill yields. Apply what fits the work in front of you; a skill is a bar to meet, not a checklist to recite.

### Skill: architecture-fundamentals

Good architecture is the cheapest structure that makes the next change easy. Judge every structural choice by what it costs the next person who has to read or change it.

**Start from what exists**
- Read the project brain (brain/project.md, brain/decisions/) and the neighbouring code before you propose anything. Follow the existing structure and naming unless you can name the concrete problem that breaking it solves.
- A decision record that is already accepted is a constraint. If the work needs to break one, say so and record a new decision; do not quietly work around it.

**Boundaries**
- Give each module one reason to exist and a small interface that hides how it works. A module is deep when a lot of behaviour sits behind few entry points.
- Dependencies point one way: domain logic knows nothing about delivery (HTTP, CLI, UI) or storage; the edges depend on the core, never the reverse.
- Keep input and output at the edges. Parse and validate once at the boundary, then pass typed, trusted data inward. Pure functions in the middle are the ones you can test without a harness.
- One source of truth for every fact: a constant, a schema, a config value. A second copy is a future bug.

**Size the design to the problem**
- Choose the smallest stack and the fewest moving parts that ship the stated scope. Name what version one deliberately leaves out.
- Do not build for a requirement nobody has stated. No plugin system for one plugin, no abstraction with one implementation, no config flag for a value that never changes.
- Prefer boring, well documented technology already used in the project over a new dependency. Every new dependency needs a reason that a standard library or existing module cannot meet.

**State, failure and operation**
- Say where every piece of state lives, who owns it and how long it lives. Shared mutable state is the first place to look for a defect.
- Fail closed and loudly: an unknown input, a missing file or a malformed record is an error with a named reason, never a silent default.
- Make behaviour deterministic where it can be. Anything that can be decided by plain code should not be left to a model or to timing.
- Configuration comes from the environment or a config file, secrets never from the tree.

**Record the decision**
- When you make a choice that a reasonable engineer could have made differently, write down the context, the decision and the consequence in a few lines, where the project keeps decisions.
- State the trade off honestly: what this choice makes harder.

**Before you hand off, check**
- Can you describe each new module in one sentence without the word "and"?
- Does any new code reach across a boundary it should not?
- Is there a simpler structure that satisfies the same spec scenarios? If yes, use it.

### Skill: implementation-craft

The build is finished when the spec scenarios pass on the final tree, the project checks are green, and a reviewer can follow the change without you in the room. Passing the new tests is the floor, not the goal.

**Before writing**
- Read the spec, the tests, and the code you are about to touch, including its callers. Find how the project already solves similar problems and do it the same way.
- Restate the change to yourself as a short list of scenario by scenario steps. If a scenario cannot be met from the inputs, stop and say which one and why.

**Write the change**
- Make the smallest change that fully satisfies the spec. Do not refactor nearby code, rename things or add features the spec did not ask for; note them as follow ups instead.
- Solve the general case the scenario describes. Never special case the test inputs, hard code an expected value, or detect that a test is running.
- Names say what a thing is or does. Functions do one thing at one level of abstraction. Prefer plain control flow to cleverness.
- Validate input at the boundary and fail with a message that names the offending value and the rule it broke. Do not swallow exceptions or return a quiet default for a real error.
- Handle the unhappy paths the spec lists and the obvious ones it does not: empty input, missing file, bad encoding, repeated call.
- Reuse an existing helper before writing a new one. If you must duplicate logic that has to stay in sync, say so in a comment at both sites.
- Comments explain why, not what. Remove debug output, dead code and leftover scaffolding before you finish.
- Stay inside the write set the work order allows. Protected paths and frozen surfaces are not yours to change.

**Verify before handoff**
- Run the project check command on the final tree and read the output. Fix what fails. Do not hand off a red suite and do not edit a test to turn it green.
- Exercise the change the way a user would: run the command, open the page, call the endpoint. Tests passing and the feature working are two different facts; confirm both.
- For anything visual, look at the rendered result at the sizes the spec names before you call it done, and produce the captures the order asks for.
- Re-read your full diff once as a reviewer would. Look for the unhandled case, the leftover TODO, the file you did not mean to touch.

**Report honestly**
- The builder report states what changed (files and the scenario each change serves), what you verified and how (the exact command and its real summary line), and what is not done or not verified.
- Every number and claim in the report must reproduce against the final tree. If a scenario is unmet or a check fails, say so plainly; a known gap reported is worth more than a clean report that review disproves.

### Skill: security-baseline

Assume every value that crosses a boundary is hostile until validated: request data, file contents, environment values from outside, model output, and anything read back from a place a user or another station could write.

**Input and output**
- Validate on the server side against an allow list of what is expected (type, length, range, format). Reject, do not repair.
- Never build a command, query, path or markup by joining strings with untrusted data. Use parameterized queries, argument lists instead of shell strings, and contextual output encoding.
- File paths from outside are resolved and checked to stay under the intended root. Reject parent references and absolute paths before use.
- Treat text produced by a model as untrusted input when it is parsed, executed or written to a path.
- On the web: encode on output, set a Content Security Policy where the stack allows, never put untrusted data into `innerHTML`, `eval` or inline handlers.

**Secrets**
- No secret, token or key in the tree, in a commit, in logs, in error messages or in a run artifact. Read secrets from the environment or the platform secret store at call time.
- Do not echo environment values or request headers into output. Redact before logging.

**Access**
- Check authorization on every request for the specific resource, on the server. Hiding a control in the interface is not access control.
- Default to deny. Grant the least privilege that works: narrow token scopes, read only where writing is not needed.
- State changing requests need protection against cross site request forgery where cookies authenticate; sessions and tokens expire.

**Dependencies and supply chain**
- Add a dependency only when the standard library or an existing one cannot do the job. Pin versions. Prefer widely used, maintained packages.
- Do not fetch and execute remote code at build or run time. Vendored third party material keeps its license and records its source and version.

**Failure and data**
- Fail closed: an error in a check means the check did not pass. Error responses do not leak stack traces, paths or internals.
- Collect and keep only the personal data the feature needs. Say where it is stored and for how long.
- Use the platform's vetted primitives for hashing, encryption and randomness. Never invent one.

**When reviewing**
- Trace each untrusted input in the change to every place it is used. A finding names the input, the sink and the consequence.
- Check what the change adds to the attack surface: new endpoints, new file writes, new permissions, new dependencies, new outbound calls.
- Missing validation, a secret in the tree, or a broadened permission is a finding even when the tests pass.

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

- id: wo-gh-42
- kind: feature
- title: Per-station token budgets with pre-call checks, and a deterministic completeness gate before the reviewer stage
- source: github-issue
- description: Implement the spec in .openspec/specs/station-budgets-completeness/spec.md. Pipeline for this order is sdlc-default (software domain, the factory repo itself), selected by the run workflow.

RELEASE (owner decision, 2026-11-21): this order is released for execution with the correction below. It was filed and staged on 2026-11-15 against a run cap of 6000000. Run configuration baseline now: the order is parented on factory main 72a84126a600fafb99446946694b5de809e01e66 (which carries wo-gh-41 continuous run accounting, the factory CI fix and the runtime refusal stop), whose anvil.yaml carries max_run_tokens 15000000, max_runtime_turns 100 and max_packet_tokens 48000, and whose anvil.json wires the checks command (python -m unittest discover -s tests -p 'test_*.py'). This order's partitions divide that existing 15000000 pool; they do not raise it.

CORRECTION OF 2026-11-21: the shipped partition table is replaced. The filed table summed to 6000000 and was too small for a large order: the approved run of wo-gh-41 used 725210 tokens in the test-writer against a filed partition of 600000. The new table sums to 15000000 and covers the largest consumption measured per station across the runs of wo-gh-39, wo-gh-43 and wo-gh-41. The spec carries the same correction.

OWNER RULING OF 2026-11-22 (after run 44912754341, verdict changes_requested on one finding): the completeness precondition of R4 applies only in a project whose configuration sets efficiency partitions (efficiency.station_budgets or efficiency.default_station_budget). That is the scope the build of that run implements, and it is the intended one: an unconditional precondition fails 22 existing protected tests (21 failures and 2 errors, measured by the builder). A project that configures no partitions keeps its present behavior. The factory's own anvil.yaml ships partitions, so the factory's own runs are gated. The spec on the run branch carries this ruling in R4 and in scenarios S4, S5 and S8 (commit eb22a19648b44a45f4fa464ab775f9ac2115806b). No code change is asked for by this ruling; an unconditional precondition is left to an order of its own.

EVIDENCE (the defects this order closes):
The C64 blueprint chain (project c64-retro-hardware) consumed about 24.5M tokens across five work orders for one showcase page. In wo-gh-6 (run 43668712644) the builder's single call measured 6,359,529 cache-inclusive tokens against the 6,000,000 run cap: one station ate the whole pool and the run died at the cap, because ANVIL's budget is one shared pool with a between-calls run threshold (token-efficiency) and no per-station partition. The same chain wasted review spend on incomplete attempts: in wo-gh-7 (run 43673692204) the builder station recorded failed with exit 1 while its artifacts existed, and what was complete had to be reconstructed by hand before anyone could judge the attempt. The comparison against other software factories (factory research of 2026-11-15, report section "Mechanisms ANVIL Does Not Have", mechanisms 19 to 25 for failure mode 4 and 26 to 32 for failure mode 5) shows the standard controls: mini-SWE-agent checks a per-instance cost limit before each query is paid for; Spotify runs deterministic verifiers before any review artifact exists, and on failure no pull request is opened; ZazenCodes joins on all expected files existing before the approver runs.

BUILD, per the spec requirements:
R1: anvil.yaml's efficiency section gains station_budgets (a map from station id to a token cap) and default_station_budget. Configuration loading validates the worst case per pipeline (named partitions plus the default applied to unnamed model stations) against max_run_tokens and fails naming any excess. The factory's own anvil.yaml ships sdlc-default partitions summing to exactly 15000000: intake 200000, spec-writer 600000, test-writer 3200000, builder 6400000, reviewer-spec 600000, reviewer-security 600000, reviewer-tests 600000, reviewer-architecture 600000, reviewer-design 600000, reviewer-ux 600000, approver 200000, triage-human 100000, deployer 300000, observer 400000. Deterministic stages (the checks gate) take no partition.
R2: before every station dispatch the spine makes (first attempt, correction re-dispatch, loopback re-dispatch), it reads the station's measured consumption for this run from the token-efficiency per-attempt usage artifacts and refuses the dispatch when the partition is exhausted. A refusal is recorded as a budget outcome (station, partition, consumed, refused at), stops forward progress for the round, and costs zero model calls. Unmeasured usage is never treated as zero: with require_usage set, an unmeasured station counts as exhausted until measured; without it, the check records that it proceeded on unmeasured usage.
R3: the station wrapper terminates a session whose measured usage crosses its partition, the station-timeout kill mechanism's shape, and records the outcome as budget_exceeded with the partial usage exposed, using wo-gh-39's honest record fields. Undone work is not resumed inside that dispatch.
R4: in a project whose configuration sets efficiency partitions, after the builder and the checks gate, before any reviewer dispatch, the runner evaluates a deterministic completeness precondition: (a) every expected artifact for the attempt exists and is non-empty (the builder report, already literal-validated by the station artifact contract's gate step; the test-writer's test files for the attempt; the run delta file list); (b) the checks gate verdict for the attempt is pass (including the deterministic preflight outcome when staged wo-gh-28 has landed; the checks verdict as it exists when it has not); (c) no pre-review station the pipeline expects is recorded failed without its artifact. A failed precondition returns the named gaps to the builder as a gate loopback (bounded by the existing max loopbacks) and dispatches zero reviewers. The outcome and gaps land in the run report in a field set of their own. The precondition consumes existing verdicts and artifacts; it does not re-run the suite and does not duplicate the artifact contract's literal validation.
R5: where the cost-measurement price table covers a station's executed model, the report's cost section shows per-station consumption in money next to the tokens (partition, consumed, priced amount), labelled as priced from the recorded table, never as an invoice; unpriced stations show tokens only and stay unmeasured in money.
R6: regression tests as new files under tests/: (a) a scripted builder partition below scripted consumption ends in the in-flight ceiling, a budget_exceeded outcome with partial usage, and untouched reviewer partitions; (b) an exhausted station is refused re-dispatch with zero model calls and the refusal recorded; (c) an over-cap configuration fails to load naming the excess, and the factory anvil.yaml loads with partitions summing to exactly 15000000; (d) a missing builder report or a failing checks verdict dispatches zero reviewers and returns the named gaps as a loopback, while a complete attempt with a passing verdict dispatches the reviewer stage.

RECONCILIATION WITH ACTIVE SPECS (read before building; these are decisions, not discoveries for the line to make):
The checks gate (spec checks-gate) already returns failing work to the builder with no reviewer spawned; R4 does not modify the gate, its verdicts, its loopback accounting or its S4 base ref behavior, and adds no second suite run: completeness is a runner-level launch precondition that consumes the gate's verdict. The station artifact contract's builder report validation is the base mechanism for R4(a), extended to the attempt's full expected artifact inventory, not duplicated. Token-efficiency R4's run threshold stays as the outer bound; R1 to R3 partition the pool inside it. Station-timeout (wo-gh-39) partitions wall-clock time; this order partitions tokens, sharing the kill-and-record mechanism shape and changing none of its keys. Continuous run accounting (wo-gh-41) landed on 2026-11-20: a refused dispatch and an in-flight ceiling kill end the run through the exit path that order added (exit_status budget_exceeded, a termination_reason naming the station and its partition, unrun stations recorded as not_run); this order adds no second way of ending a run, and tests/test_continuous_run_accounting.py is a protected existing test. The existing top level station_budgets key of anvil.yaml (astra-consumption, read by anvil.config.get_station_budget) caps a station's packet size; it is a different quantity, it stays where it is, and its behavior and tests (tests/test_astra_consumption.py) are frozen. The keys this order adds live inside the efficiency section, and the documentation names both and states the difference. Relationship to staged wo-gh-28 (deterministic preflight): preflight judges whether the changed code is alive; completeness judges whether the attempt's artifacts exist and the gate passed. Each works whether or not the other has landed, neither duplicates the other's checks, and execution order between the two orders is the owner's decision.

BUILDER REPORT REQUIRED LITERALS: the builder report (runs/wo-gh-42/builder.output.md) must contain each of these in full, unabbreviated: 72a84126a600fafb99446946694b5de809e01e66, station-budgets-completeness, 15000000, completeness. It must also state the base ref it verified the tree against, the partition table it shipped with its sum, the exact full factory test count from the suite run, and the names of the new test files added.

GUARDRAILS: authorized surface for this order: anvil/config.py, anvil.yaml (the efficiency keys and the factory's own partitions only), anvil/executor.py, anvil/runner.py, anvil/gates.py, anvil/telemetry.py, tools/claude_station.py (the in-flight ceiling), tools/dispatch_station.py if needed, the factory docs that describe budgets or the checks flow (docs/EXECUTION.md at minimum), CHANGELOG.md, one new decision record under brain/decisions/, and new test files under tests/. Pipeline files under pipelines/ are protected paths in anvil.json; the fix must hold without editing them. anvil.json itself is protected; do not edit it. Existing test files at the base ref are protected: do not modify or delete them; new tests arrive as new files. Frozen: the checks gate's verdicts and S4 behavior, the artifact contract's literal validation, token-efficiency's usage artifacts, the station-timeout keys, cost-measurement semantics, the review parse contract, the reviewer prompts. Python standard library only, no new dependency. No em dash or en dash character in any produced file. Nothing in this order merges, publishes or deploys anything; the run stops at the owner human gate.

GitHub issue: https://github.com/arananet/anvil-factory/issues/42


GitHub issue: https://github.com/arananet/anvil-factory/issues/42
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed
- test-writer: executed

## Run context

Read the upstream work before you start; it is the input your station builds on.
The checks gate runs the project checks listed here; run them yourself before you hand off.

- Output of intake: runs/wo-gh-42/intake.output.md
- Output of spec-writer: runs/wo-gh-42/spec-writer.output.md
- Output of test-writer: runs/wo-gh-42/test-writer.output.md
- Project check: `python -m unittest discover -s tests -p 'test_*.py'`

## Output contract

Write your builder report as a file to runs/wo-gh-42/builder.output.md. The checks gate reads that file back from the run tree before any reviewer runs; your chat reply is never accepted as the report.
