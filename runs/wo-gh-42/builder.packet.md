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

EVIDENCE (the defects this order closes):
The C64 blueprint chain (project c64-retro-hardware) consumed about 24.5M tokens across five work orders for one showcase page. In wo-gh-6 (run 43668712644) the builder's single call measured 6,359,529 cache-inclusive tokens against the 6,000,000 run cap: one station ate the whole pool and the run died at the cap, because ANVIL's budget is one shared pool with a between-calls run threshold (token-efficiency) and no per-station partition. The same chain wasted review spend on incomplete attempts: in wo-gh-7 (run 43673692204) the builder station recorded failed with exit 1 while its artifacts existed, and what was complete had to be reconstructed by hand before anyone could judge the attempt. The comparison against other software factories (factory research of 2026-11-15, report section "Mechanisms ANVIL Does Not Have", mechanisms 19 to 25 for failure mode 4 and 26 to 32 for failure mode 5) shows the standard controls: mini-SWE-agent checks a per-instance cost limit before each query is paid for; Spotify runs deterministic verifiers before any review artifact exists, and on failure no pull request is opened; ZazenCodes joins on all expected files existing before the approver runs.

BUILD, per the spec requirements:
R1: anvil.yaml's efficiency section gains station_budgets (a map from station id to a token cap) and default_station_budget. Configuration loading validates the worst case per pipeline (named partitions plus the default applied to unnamed model stations) against max_run_tokens and fails naming any excess. The factory's own anvil.yaml ships sdlc-default partitions summing to exactly 15000000: intake 200000, spec-writer 600000, test-writer 3200000, builder 6400000, reviewer-spec 600000, reviewer-security 600000, reviewer-tests 600000, reviewer-architecture 600000, reviewer-design 600000, reviewer-ux 600000, approver 200000, triage-human 100000, deployer 300000, observer 400000. Deterministic stages (the checks gate) take no partition.
R2: before every station dispatch the spine makes (first attempt, correction re-dispatch, loopback re-dispatch), it reads the station's measured consumption for this run from the token-efficiency per-attempt usage artifacts and refuses the dispatch when the partition is exhausted. A refusal is recorded as a budget outcome (station, partition, consumed, refused at), stops forward progress for the round, and costs zero model calls. Unmeasured usage is never treated as zero: with require_usage set, an unmeasured station counts as exhausted until measured; without it, the check records that it proceeded on unmeasured usage.
R3: the station wrapper terminates a session whose measured usage crosses its partition, the station-timeout kill mechanism's shape, and records the outcome as budget_exceeded with the partial usage exposed, using wo-gh-39's honest record fields. Undone work is not resumed inside that dispatch.
R4: after the builder and the checks gate, before any reviewer dispatch, the runner evaluates a deterministic completeness precondition: (a) every expected artifact for the attempt exists and is non-empty (the builder report, already literal-validated by the station artifact contract's gate step; the test-writer's test files for the attempt; the run delta file list); (b) the checks gate verdict for the attempt is pass (including the deterministic preflight outcome when staged wo-gh-28 has landed; the checks verdict as it exists when it has not); (c) no pre-review station the pipeline expects is recorded failed without its artifact. A failed precondition returns the named gaps to the builder as a gate loopback (bounded by the existing max loopbacks) and dispatches zero reviewers. The outcome and gaps land in the run report in a field set of their own. The precondition consumes existing verdicts and artifacts; it does not re-run the suite and does not duplicate the artifact contract's literal validation.
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
- builder: executed
- checks-gate: passed
- reviewer-spec: executed
- reviewer-security: executed
- reviewer-tests: executed
- reviewer-architecture: executed
- reviewer-design: executed
- reviewer-ux: routed_out
- approver: completed
- approver: loopback
- builder: executed
- checks-gate: passed
- reviewer-spec: executed
- reviewer-security: executed
- reviewer-tests: executed
- reviewer-architecture: executed
- reviewer-design: executed
- reviewer-ux: routed_out
- approver: completed
- approver: loopback

## Run context

Read the upstream work before you start; it is the input your station builds on.
The checks gate runs the project checks listed here; run them yourself before you hand off.

- Output of intake: runs/wo-gh-42/intake.output.md
- Output of spec-writer: runs/wo-gh-42/spec-writer.output.md
- Output of test-writer: runs/wo-gh-42/test-writer.output.md
- Output of builder: runs/wo-gh-42/builder.output.md
- Output of reviewer-spec: runs/wo-gh-42/reviewer-spec.output.md
- Output of reviewer-security: runs/wo-gh-42/reviewer-security.output.md
- Output of reviewer-tests: runs/wo-gh-42/reviewer-tests.output.md
- Output of reviewer-architecture: runs/wo-gh-42/reviewer-architecture.output.md
- Output of reviewer-design: runs/wo-gh-42/reviewer-design.output.md
- Output of builder: runs/wo-gh-42/builder.output.md
- Output of reviewer-spec: runs/wo-gh-42/reviewer-spec.output.md
- Output of reviewer-security: runs/wo-gh-42/reviewer-security.output.md
- Output of reviewer-tests: runs/wo-gh-42/reviewer-tests.output.md
- Output of reviewer-architecture: runs/wo-gh-42/reviewer-architecture.output.md
- Output of reviewer-design: runs/wo-gh-42/reviewer-design.output.md
- Project check: `python -m unittest discover -s tests -p 'test_*.py'`

## Loopback feedback (attempt 3 of 3)

The previous attempt was sent back by approver to builder. Resolve every finding below. Keep what already passed; do not start over.

Reason: Still open, needs an owner ruling (R4; S4, S5, S8): the spec at .openspec/specs/station-budgets-completeness/spec.md R4 has not been amended. It still says that before any reviewer dispatch 'the runner evaluates a completeness precondition', with no condition attached. The runner still applies the gate only where partitions are configured: anvil/runner.py:1652 sets completeness_active = any(station_budget_settings(config)), and the pre-review check at anvil/runner.py:2440 depends on that flag. A project with no efficiency.station_budgets and no default_station_budget skips completeness and sends incomplete attempts to review. The builder report (attempt 2, item 2) explicitly leaves this unfixed, because running the gate unconditionally breaks 22 protected existing tests. This is a real conflict between R4 and the protected-test guardrail (P-14), and the line cannot settle it. It stays open until the owner either amends R4 to scope completeness to projects with configured partitions, or

- Still open, needs an owner ruling (R4; S4, S5, S8): the spec at .openspec/specs/station-budgets-completeness/spec.md R4 has not been amended. It still says that before any reviewer dispatch 'the runner evaluates a completeness precondition', with no condition attached. The runner still applies the gate only where partitions are configured: anvil/runner.py:1652 sets completeness_active = any(station_budget_settings(config)), and the pre-review check at anvil/runner.py:2440 depends on that flag. A project with no efficiency.station_budgets and no default_station_budget skips completeness and sends incomplete attempts to review. The builder report (attempt 2, item 2) explicitly leaves this unfixed, because running the gate unconditionally breaks 22 protected existing tests. This is a real conflict between R4 and the protected-test guardrail (P-14), and the line cannot settle it. It stays open until the owner either amends R4 to scope completeness to projects with configured partitions, or authorizes updating the 22 tests so the gate can run unconditionally (a one-line runner change). I cannot pass an open loopback finding.
- Resolved (R4(a), S4, reviewer-tests finding): the missing-builder-report case can now fail. test_s4_missing_builder_report_dispatches_zero_reviewers requires a gap naming runs/wo-sbc/builder.output.md. The new test_s4_missing_report_alone_blocks_review_when_checks_pass covers a successful builder with a source change, test-writer files and passing checks but an empty report, and expects exactly one gap naming the report path and zero reviewer calls. The new test_s4_completeness_gaps_names_a_missing_or_empty_report calls completeness_gaps directly. I repeated the mutation independently: in a copy of the tree I replaced 'if not _nonempty_file(report):' with 'if False:' and ran tests.test_station_budgets_completeness.CompletenessGate, which gave FAILED (failures=5).
- Defect fix verified (R4(a)): _nonempty_file now treats a file with only whitespace as empty. That matches the artifact contract's rule (read_bytes().strip()), and validate_builder_report and the gate step are unchanged, so S9 (consumes, never re-runs) still holds.
- R1/S3, R2/S2/S7, R3/S1, R5/S6, R7, R8, S9 to S11: no regressions since attempt 1. The partition table still sums to 15000000, and the pre-call check, in-flight ceiling, cost section, docs, CHANGELOG and decision 0014 are all present. The gap the builder disclosed still stands: the in-session correction-refusal path (wrapper exit 12) has no test through the runner. S2's 'a correction or a loopback' allows this, so it is not a blocker.
- Evidence: 'python -m unittest tests.test_station_budgets_completeness' gave Ran 28 tests, OK. The full suite, run as 'env -u GITHUB_ACTIONS -u GITHUB_ACTOR -u GITHUB_ACTOR_ID python -m unittest discover -s tests -p test_*.py', gave Ran 799 tests, OK (skipped=6), which matches the builder report (771 base plus 28 new). 'git diff --name-only 72a84126a600fafb99446946694b5de809e01e66 -- tests pipelines anvil.json' is empty, so no protected path changed. No em dash or en dash appears in the changed or new files.
- Loopback finding R4 / S4, S5, S8 (completeness scoped to configured partitions) is still open. anvil/runner.py:1652 sets completeness_active = any(station_budget_settings(config)) and anvil/runner.py:2440 gates the precondition on it, so a project with no efficiency partitions skips completeness. The builder report lists this as open pending an owner ruling. It conflicts with the protected-test guardrail and the builder cannot resolve it. This is not a security defect: completeness is a review-spend control, not an access control. But this re-review cannot pass a finding that is still open. It needs the owner ruling: amend R4, or authorize updates to the 22 protected tests.
- The S4 missing-builder-report test gap that reviewer-tests raised looks addressed. tests/test_station_budgets_completeness.py adds test_s4_missing_report_alone_blocks_review_when_checks_pass (line 571) and test_s4_completeness_gaps_names_a_missing_or_empty_report (line 593). Reviewer-tests owns the mutation re-check.
- Attempt 2 delta, security review: _nonempty_file (anvil/runner.py:1176) now reads the file and strips it, so whitespace-only counts as empty, matching gates.validate_builder_report. The paths are internal: the configured report path, plus test-writer delta entries joined under the project root from the local working-tree snapshot. The function only reads them for an emptiness check. Their content is never echoed, executed or written. OSError fails closed to 'empty'. Low-severity nit: read_bytes loads the whole file to test for emptiness. A bounded read would avoid memory cost on a very large delta file. Not a blocker.
- Change since attempt 1 in anvil/executor.py: it surfaces a budget_exceeded record (elapsed_ms, reason, configured_model) from the wrapper's last usage record. These are the same honest fields as the timeout record. No environment value, header or secret is copied.
- Unchanged and still acceptable: no new dependency (standard library only), no new endpoint, outbound call or permission. tools/claude_station.py:323 starts the CLI from an argument list without a shell. Budget configuration is allow-list validated and rejects bad values. With require_usage set, an unmeasured station is refused. Streamed model output is parsed defensively and used only for arithmetic.
- Attempt 1 low-severity follow-ups, carried forward and disclosed in the builder report, not blockers. (1) The in-flight ceiling fails open to the pre-call check and the run cap when the CLI streams no usage events. Record 'ceiling unmeasured' in that case. (2) If an outside timeout kills the wrapper, the CLI child (start_new_session=True) is orphaned. Forward SIGTERM to the child's process group.
- Evidence: python -m unittest tests.test_station_budgets_completeness gives 'Ran 28 tests ... OK'. No em dash or en dash in the changed or new files under anvil, tools, docs/EXECUTION.md, CHANGELOG.md, anvil.yaml, decision 0014 or the new test file. The diff against 72a84126a600fafb99446946694b5de809e01e66 touches no file under pipelines/, no anvil.json and no existing test.
- RESOLVED (my attempt 1 finding, R4(a), S4, test-design 'make the test able to fail'): the missing builder report case can now fail. test_s4_missing_builder_report_dispatches_zero_reviewers now requires a gap naming runs/wo-sbc/builder.output.md, not just any gap containing 'builder'. New test_s4_missing_report_alone_blocks_review_when_checks_pass: the builder changes src/feature.py, the test-writer writes its file, checks pass (gate_verdict pass), the report is empty or whitespace only. It asserts exactly one gap, that gap names the report path, and zero reviewer calls. New test_s4_completeness_gaps_names_a_missing_or_empty_report calls the real completeness_gaps on a missing, empty, whitespace-only and real report.
- Mutation check repeated by me on a copy of the final tree: replacing `if not _nonempty_file(report):` (anvil/runner.py:1206) with `if False:` makes `python -m unittest tests.test_station_budgets_completeness.CompletenessGate` report 'Ran 8 tests ... FAILED (failures=5)'. Before the fix the same mutation passed all 6 tests. The finding is closed.
- Mock scope is acceptable: test_s4_missing_report_alone_blocks_review_when_checks_pass stubs anvil.runner.validate_builder_report, the gate's frozen literal validation. That is a collaborator, not the unit under test. In the real flow that validation already rejects an empty report before completeness runs, so the stub is the only way to reach completeness with a passing gate. The direct completeness_gaps test covers the same rule without any mock. The tests also found a real defect, now fixed: _nonempty_file treated a whitespace-only file as present (anvil/runner.py:1176-1182, now read_bytes().strip(), the same rule as gates.validate_builder_report).
- Suite reproduces (P-12): on the final tree, `env -u GITHUB_ACTIONS -u GITHUB_ACTOR -u GITHUB_ACTOR_ID python -m unittest discover -s tests -p 'test_*.py'` gives 'Ran 799 tests ... OK (skipped=6)'. `python -m unittest tests.test_station_budgets_completeness` gives 'Ran 28 tests ... OK'. Both match the builder report.
- Test accounting (P-13) is complete. Baseline: 771 (measured in attempt 1 on the base 72a84126a600fafb99446946694b5de809e01e66). Added: one file, tests/test_station_budgets_completeness.py, now 28 tests (attempt 1 had 26; attempt 2 adds 2 and tightens 1 in that new file). 771 + 28 = 799. Edited existing tests: none. `git diff --name-only 72a84126a600fafb99446946694b5de809e01e66 -- tests pipelines anvil.json` is empty, so the protected test_continuous_run_accounting.py and test_astra_consumption.py are untouched. The 29th 'def test_' match in the file is fixture text (test_x inside the TEST_FILE string at line 246), not a test.
- Mapping is still complete: S1 to S11 each have named tests, and the module docstring map lists the S4 tests. No em or en dash appears in the test file or the builder report.
- STILL OPEN, not passed by this station (approver finding R4 / S4, S5, S8): completeness still runs only when completeness_active = any(station_budget_settings(config)) (anvil/runner.py). The builder did not change this and says so plainly. Running the gate unconditionally would break 22 protected existing tests. This is a conflict between the spec and the guardrails that only the owner can settle, by amending R4 or authorizing edits to those tests. No test change can close it inside this order. The tests do cover the behaviour where it is active, so the test verdict is pass, but the R4 ruling stays with the approver and the owner gate.
- Remaining test gaps (disclosed, non-blocking): the in-session correction refusal (wrapper exit 12) has no test through the runner. S2 is tested on the loopback path, which the scenario's 'a correction or a loopback' allows. The in-flight ceiling (S1) has only been run against a stand-in claude CLI.

## Output contract

Write your builder report as a file to runs/wo-gh-42/builder.output.md. The checks gate reads that file back from the run tree before any reviewer runs; your chat reply is never accepted as the report.
