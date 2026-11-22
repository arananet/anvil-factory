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



## Diff summary

- CHANGELOG.md: +2, -1
- anvil/sinks.py: +8, -1
- runs/wo-gh-47/attempts/1/builder.output.md: +34, -56
- runs/wo-gh-47/attempts/1/checks-gate.pre-review.output.md: +28, -23
- runs/wo-gh-47/attempts/1/intake.output.md: +10, -0
- runs/wo-gh-47/attempts/1/spec-writer.output.md: +17, -18
- runs/wo-gh-47/attempts/1/test-writer.output.md: +35, -19
- runs/wo-gh-47/builder.output.md: +53, -33
- runs/wo-gh-47/builder.output.md.usage.json: +13, -13
- runs/wo-gh-47/builder.packet.md: +24, -116
- runs/wo-gh-47/builder.transcript.md: +16, -15
- runs/wo-gh-47/checks-gate.pre-review.output.md: +27, -17
- runs/wo-gh-47/envelopes/builder.envelope.json: +11, -11
- runs/wo-gh-47/envelopes/checks-gate.envelope.json: +9, -6
- runs/wo-gh-47/envelopes/intake.envelope.json: +1, -1
- runs/wo-gh-47/envelopes/spec-writer.envelope.json: +11, -11
- runs/wo-gh-47/envelopes/test-writer.envelope.json: +11, -11
- runs/wo-gh-47/events.jsonl: +13, -0
- runs/wo-gh-47/evidence/screenshot-1440x900.png: +0, -0
- runs/wo-gh-47/evidence/screenshot-390x844.png: +0, -0
- runs/wo-gh-47/intake.output.md: +10, -0
- runs/wo-gh-47/intake.output.md.usage.json: +12, -12
- runs/wo-gh-47/intake.packet.md: +2, -2
- runs/wo-gh-47/report.json: +409, -430
- runs/wo-gh-47/routing.json: +6, -13
- runs/wo-gh-47/spec-writer.output.md: +17, -18
- runs/wo-gh-47/spec-writer.output.md.usage.json: +13, -13
- runs/wo-gh-47/spec-writer.packet.md: +2, -2
- runs/wo-gh-47/state.json: +21, -57
- runs/wo-gh-47/test-writer.output.md: +35, -19
- runs/wo-gh-47/test-writer.output.md.usage.json: +13, -13
- runs/wo-gh-47/test-writer.packet.md: +2, -2
- work_orders/wo-gh-47.json: +2, -10

## File access allowlist

This packet may only embed content from:
- design/DESIGN.md
- design/tokens.json
- CHANGELOG.md
- anvil/sinks.py
- runs/wo-gh-47/attempts/1/builder.output.md
- runs/wo-gh-47/attempts/1/checks-gate.pre-review.output.md
- runs/wo-gh-47/attempts/1/intake.output.md
- runs/wo-gh-47/attempts/1/spec-writer.output.md
- runs/wo-gh-47/attempts/1/test-writer.output.md
- runs/wo-gh-47/builder.output.md
- runs/wo-gh-47/builder.output.md.usage.json
- runs/wo-gh-47/builder.packet.md
- runs/wo-gh-47/builder.transcript.md
- runs/wo-gh-47/checks-gate.pre-review.output.md
- runs/wo-gh-47/envelopes/builder.envelope.json
- runs/wo-gh-47/envelopes/checks-gate.envelope.json
- runs/wo-gh-47/envelopes/intake.envelope.json
- runs/wo-gh-47/envelopes/spec-writer.envelope.json
- runs/wo-gh-47/envelopes/test-writer.envelope.json
- runs/wo-gh-47/events.jsonl
- runs/wo-gh-47/evidence/screenshot-1440x900.png
- runs/wo-gh-47/evidence/screenshot-390x844.png
- runs/wo-gh-47/intake.output.md
- runs/wo-gh-47/intake.output.md.usage.json
- runs/wo-gh-47/intake.packet.md
- runs/wo-gh-47/report.json
- runs/wo-gh-47/routing.json
- runs/wo-gh-47/spec-writer.output.md
- runs/wo-gh-47/spec-writer.output.md.usage.json
- runs/wo-gh-47/spec-writer.packet.md
- runs/wo-gh-47/state.json
- runs/wo-gh-47/test-writer.output.md
- runs/wo-gh-47/test-writer.output.md.usage.json
- runs/wo-gh-47/test-writer.packet.md
- work_orders/wo-gh-47.json

## Work order

- id: wo-gh-47
- kind: feature
- title: Live progress sinks: a run seen while it runs, on the work order's issue and optionally on a GitHub Projects board
- source: github-issue
- description: Implement the spec in .openspec/specs/live-progress-sinks/spec.md. Pipeline for this order is sdlc-default (software domain, the factory repo itself), selected by the run workflow.

RELEASE (owner decision, 2026-11-22): this order is released for execution. It was filed on 2026-11-21 and staged until wo-gh-42 landed, which it did on 2026-11-22 (merge 6191e8c1f235b4cd248a51203d40177834dc4ae2). Baseline now: factory main ae0bbfb2af95b41d96d8e2af7c9f8b787f54d83b, whose anvil.yaml carries max_run_tokens 15000000, max_runtime_turns 100, max_packet_tokens 48000 and the efficiency station partitions of wo-gh-42, and whose anvil.json wires the checks command (python -m unittest discover -s tests -p 'test_*.py'). First run of this order (45042545362) was stopped in the spec-writer by its token partition, since recalibrated (spec-writer 1200000, builder 5800000); the run branch carries that fix. The exit statuses now on main include runtime_refused; a sink must be able to show any exit status as a final state without knowing the list.

EVIDENCE (the defect this order closes):
A run cannot be watched. state.json is rewritten before every station and report.json is checkpointed after every station (wo-gh-41), but both stay on the disk of the machine that runs the line until the run ends. The five runs of wo-gh-41 on 2026-11-20 and the run of wo-gh-42 on 2026-11-21 each showed only "In progress" for 5 to 27 minutes; the owner asked what the line was doing and nobody could tell from outside. The existing export (observability.events_url and otlp_endpoint) needs a receiver someone must build and host. Owner direction of 2026-11-21: no dependence on one vendor for this, and a person who copies ANVIL must see their runs without standing anything up. Every work order is already a GitHub issue and every run already holds a token that can write to it.

BUILD, per the spec requirements:
R1: anvil.yaml accepts observability.sinks, an ordered and validated list of sink entries. A sink is called with the run state record (schema anvil/run-state@1) every time the recorder rewrites the state: at the start, before each station, after the last one, and when the run ends, crashes or is stopped early. No new event kind; events.jsonl is unchanged. A sink that raises, times out or is refused is recorded in export_errors under its type and the line goes on; each call is bounded by observability.timeout_seconds. No sinks configured means no additional network call. The sink code lives beside the recorder, outside anvil/runner.py.
R2: the github-issue sink, entry {"type": "github-issue"} with optional token_env (default GH_TOKEN). Active only when the work order id is wo-gh-<number>, GITHUB_REPOSITORY is set and the token variable is set; otherwise inactive with the reason recorded once and no network call. It creates one comment on the issue at its first call and edits that same comment on every later call, found again by a hidden marker carrying the run id. The comment shows the work order and pipeline, the run state, the verdict and exit status once known, one row per pipeline station in pipeline order (done, failed, running, pending, skipped, not run) with attempt and measured tokens, loopbacks used, tokens and priced cost so far, the time of the last update and the workflow run link when the environment gives one. Scalar facts only: no prompt, no station output, no path, no token value. The API base comes from GITHUB_API_URL when set.
R3: the github-project sink, entry {"type": "github-project", "owner": ..., "number": ...} with optional owner_type, status_field (default Status), token_env and columns. Phases and default option names: intake (Intake), spec (Spec), build (Build: test-writer and builder), checks (Checks), review (Review: reviewers and approver), human (Needs human), done (Done), failed (Failed). It sets the status of the issue's project item when the phase changes, adds the issue to the project when missing, and never alters the project's shape: a missing project, field or option is recorded by name and the sink goes inactive for the run. The workflow token cannot reach Projects; token_env names a variable holding one that can, and with it unset the sink is inactive and says so once.
R4: the factory's own anvil.yaml enables the github-issue sink; the scaffold for new projects enables it too; the github-project sink ships documented and off. The final ANVIL line report comment of the workflow is unchanged.
R5: sinks run in the line process and read their token there. Stations never receive it. No token value appears in state.json, events.jsonl, report.json, a comment or an export error.
R6: regression tests as new files under tests/, with a local HTTP collector in the manner of tests/test_governed_delivery.py: (a) one comment creation then only edits, the last showing every station done and the verdict; (b) the edit sent before the builder shows the builder running and later stations pending; (c) a collector answering 500 and an unreachable one leave verdict and report unchanged with one export error; (d) a non wo-gh id or a missing token gives zero network calls and one recorded reason; (e) the project sink sends a status change only when the phase changes, adds a missing item, and goes inactive naming a missing option; (f) no sink configured gives zero additional network calls; (g) a malformed sinks list fails loading naming the entry; (h) a token value in the environment appears in no file the run writes and in no request body.

RECONCILIATION WITH ACTIVE SPECS AND EXISTING TESTS (read before building; these are decisions, not discoveries for the line to make):
Governed delivery owns state.json, events.jsonl, the webhook and the OTLP trace; all four are frozen and this order only adds consumers of the state record. tests/test_governed_delivery.py asserts that the events POSTed to the webhook equal the events in events.jsonl and counts station.finished and loopback events against the report's steps: sinks must not add, remove or reorder events, which is why they are fed by the state and not by a new event. tests/test_review_producer.py asserts that the word "retry" does not occur in anvil/runner.py: keep network code and that word out of the runner. tests/test_continuous_run_accounting.py (wo-gh-41) asserts the report's shape after every exit path: a sink call on an exit path must not change what is written. wo-gh-42 (station partitions) may land before this order; its efficiency keys and this order's observability keys do not overlap. The runtime refusal stop (exit_status runtime_refused) is one more final state a sink must be able to show.

BUILDER REPORT: the builder report must contain each of these in full: ae0bbfb2af95b41d96d8e2af7c9f8b787f54d83b, live-progress-sinks, github-issue, github-project. It must also state the base ref it verified the tree against, the exact full factory test count from the suite run, and the names of the new test files added.

GUARDRAILS: authorized surface for this order: anvil/observe.py, a new module beside it for the sinks, anvil/config.py (validation of observability.sinks), anvil/scaffold.py (the default for new projects), anvil.yaml (the factory's own sink entry), docs/OPERATIONS.md, docs/EXECUTION.md, README.md (one short section on watching a run), CHANGELOG.md, one new decision record under brain/decisions/, and new test files under tests/. anvil/runner.py may change only where the recorder is constructed or told the pipeline order, and gains no network code. Do not touch any file under .github/workflows: the run's own token cannot push workflow changes and none are needed, because the line step already carries GH_TOKEN. Pipeline files under pipelines/ and anvil.json are protected paths. Existing test files at the base ref are protected: do not modify or delete them; new tests arrive as new files. A test that asserts something about this order's own run (which paths it changed, what its builder report says, a comparison against a fixed base ref) must skip unless ANVIL_WORK_ORDER_ID names this order: left unconditional, such a test fails for every order after this one, as the tree evidence of wo-gh-42 did. Frozen: the events contract, the OTLP trace, the existing fields of the run-state schema, the rule that export never decides a run, the station environment reduction, tools/line_comment.py. Python standard library only, no new dependency. No em dash or en dash character in any produced file. Nothing in this order merges, publishes or deploys anything; the run stops at the owner human gate.

GitHub issue: https://github.com/arananet/anvil-factory/issues/47
- risk_hints: 
- status: new

## Loopback feedback (attempt 2 of 3)

This is a re-review. The previous attempt was sent back by checks-gate to builder. Judge the work as it is now, and check that each finding below is resolved; do not pass a finding that is still open.

Reason: Completeness precondition failed: run delta file list for attempt 1 is empty: the builder changed no file

- completeness gap: run delta file list for attempt 1 is empty: the builder changed no file
- # Checks Gate: pre-review
  Basis: builder_delta
  Attempt: 1
  
  # Protected Path Additions (Observed, Not Violations)
  Protected path addition (observed): tests/test_live_progress_sinks.py (matches tests/)
  Protected path addition (observed): tests/test_live_progress_project_sink.py (matches tests/)
  
  # Check Commands
  ## Command 1: python -m unittest discover -s tests -p 'test_*.py'
  Exit code: 0
  Output:
  ```
  nitial branch. This default branch name
  hint: will change to "main" in Git 3.0. To configure the initial branch name
  hint: to use in all of your new repositories, which will suppress this warning,
  hint: call:
  hint:
  hint: 	git config --global init.defaultBranch <name>
  hint:
  hint: Names commonly chosen instead of 'master' are 'main', 'trunk' and
  hint: 'development'. The just-created branch can be renamed via this command:
  hint:
  hint: 	git branch -m <name>
  hint:
  hint: Disable this message with "git config set advice.defaultBranchName false"
  Switched to a new branch 'work-branch'
  ...................................................................................................................................................../opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/unittest/case.py:589: ResourceWarning: unclosed <socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 43177)>
    if method() is not None:
  ResourceWarning: Enable tracemalloc to get the object allocation traceback
  .../opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/unittest/case.py:589: Reso

## Practices

Promoted practices that resolved for this station. Follow each rule.

- P-4 (Fidelity to anchors and the committed asset pack): Judge rendered captures against both the project anchors and the committed asset pack; if the rendered game does not visibly use the pack art, fidelity fails.
- P-5 (Parallax depth must be demonstrated between layers): Parallax depth must be demonstrated between layers in captures, by measured displacement or visible relative motion; a single panning plate is not depth.
- P-6 (Cross-set coherence check): Run an explicit cross-set coherence check on every review: same character, proportions, palette, motifs and light logic across all stages or scenes; style drift is a changes requested finding.
- P-7 (Genre coherence): Judge the work against the genre declared in the project spec, never against imported standards from other genres; an old school 2D platformer is judged on genre craft: full-screen playable density, readable floors, big legible sprites.

## Rendered evidence

This run captured screenshots of the served project at the following breakpoints:

- `screenshot-1440x900.png` at `runs/wo-gh-47/evidence/screenshot-1440x900.png`
- `screenshot-390x844.png` at `runs/wo-gh-47/evidence/screenshot-390x844.png`

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

