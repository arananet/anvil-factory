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

- .openspec/specs/station-budgets-completeness/spec.md: +1, -0
- brain/decisions/0014-station-budgets-completeness.md: +2, -1
- runs/wo-gh-42/builder.output.md: +61, -69
- runs/wo-gh-42/builder.output.md.usage.json: +13, -13
- runs/wo-gh-42/builder.packet.md: +3, -60
- runs/wo-gh-42/builder.transcript.md: +19, -2
- runs/wo-gh-42/checks-gate.pre-review.output.md: +6, -6
- runs/wo-gh-42/envelopes/builder.envelope.json: +11, -11
- runs/wo-gh-42/envelopes/checks-gate.envelope.json: +2, -2
- runs/wo-gh-42/envelopes/intake.envelope.json: +1, -1
- runs/wo-gh-42/envelopes/reviewer-architecture.envelope.json: +20, -17
- runs/wo-gh-42/envelopes/reviewer-security.envelope.json: +22, -17
- runs/wo-gh-42/envelopes/reviewer-spec.envelope.json: +18, -17
- runs/wo-gh-42/envelopes/reviewer-tests.envelope.json: +19, -17
- runs/wo-gh-42/envelopes/spec-writer.envelope.json: +11, -11
- runs/wo-gh-42/envelopes/test-writer.envelope.json: +11, -11
- runs/wo-gh-42/events.jsonl: +10, -0
- runs/wo-gh-42/evidence/screenshot-1440x900.png: +0, -0
- runs/wo-gh-42/evidence/screenshot-390x844.png: +0, -0
- runs/wo-gh-42/intake.output.md.usage.json: +13, -13
- runs/wo-gh-42/intake.packet.md: +3, -1
- runs/wo-gh-42/report.json: +224, -1358
- runs/wo-gh-42/reviewer-architecture.output.md: +15, -12
- runs/wo-gh-42/reviewer-architecture.output.md.usage.json: +13, -13
- runs/wo-gh-42/reviewer-architecture.packet.md: +3, -60
- runs/wo-gh-42/reviewer-architecture.review.json: +9, -6
- runs/wo-gh-42/reviewer-security.output.md: +11, -11
- runs/wo-gh-42/reviewer-security.output.md.usage.json: +13, -13
- runs/wo-gh-42/reviewer-security.packet.md: +3, -60
- runs/wo-gh-42/reviewer-security.review.json: +11, -6
- runs/wo-gh-42/reviewer-spec.output.md: +16, -14
- runs/wo-gh-42/reviewer-spec.output.md.usage.json: +13, -13
- runs/wo-gh-42/reviewer-spec.packet.md: +3, -60
- runs/wo-gh-42/reviewer-spec.review.json: +7, -6
- runs/wo-gh-42/reviewer-tests.output.md: +21, -11
- runs/wo-gh-42/reviewer-tests.output.md.usage.json: +13, -13
- runs/wo-gh-42/reviewer-tests.packet.md: +6, -59
- runs/wo-gh-42/reviewer-tests.review.json: +8, -6
- runs/wo-gh-42/routing.json: +3, -3
- runs/wo-gh-42/spec-writer.output.md: +27, -23
- runs/wo-gh-42/spec-writer.output.md.usage.json: +13, -13
- runs/wo-gh-42/spec-writer.packet.md: +3, -1
- runs/wo-gh-42/state.json: +11, -138
- runs/wo-gh-42/test-writer.output.md: +60, -39
- runs/wo-gh-42/test-writer.output.md.usage.json: +13, -13
- runs/wo-gh-42/test-writer.packet.md: +3, -1
- tests/test_station_budgets_completeness.py: +47, -0
- work_orders/wo-gh-42.json: +1, -1

## File access allowlist

This packet may only embed content from:
- design/DESIGN.md
- design/tokens.json
- .openspec/specs/station-budgets-completeness/spec.md
- brain/decisions/0014-station-budgets-completeness.md
- runs/wo-gh-42/builder.output.md
- runs/wo-gh-42/builder.output.md.usage.json
- runs/wo-gh-42/builder.packet.md
- runs/wo-gh-42/builder.transcript.md
- runs/wo-gh-42/checks-gate.pre-review.output.md
- runs/wo-gh-42/envelopes/builder.envelope.json
- runs/wo-gh-42/envelopes/checks-gate.envelope.json
- runs/wo-gh-42/envelopes/intake.envelope.json
- runs/wo-gh-42/envelopes/reviewer-architecture.envelope.json
- runs/wo-gh-42/envelopes/reviewer-security.envelope.json
- runs/wo-gh-42/envelopes/reviewer-spec.envelope.json
- runs/wo-gh-42/envelopes/reviewer-tests.envelope.json
- runs/wo-gh-42/envelopes/spec-writer.envelope.json
- runs/wo-gh-42/envelopes/test-writer.envelope.json
- runs/wo-gh-42/events.jsonl
- runs/wo-gh-42/evidence/screenshot-1440x900.png
- runs/wo-gh-42/evidence/screenshot-390x844.png
- runs/wo-gh-42/intake.output.md.usage.json
- runs/wo-gh-42/intake.packet.md
- runs/wo-gh-42/report.json
- runs/wo-gh-42/reviewer-architecture.output.md
- runs/wo-gh-42/reviewer-architecture.output.md.usage.json
- runs/wo-gh-42/reviewer-architecture.packet.md
- runs/wo-gh-42/reviewer-architecture.review.json
- runs/wo-gh-42/reviewer-security.output.md
- runs/wo-gh-42/reviewer-security.output.md.usage.json
- runs/wo-gh-42/reviewer-security.packet.md
- runs/wo-gh-42/reviewer-security.review.json
- runs/wo-gh-42/reviewer-spec.output.md
- runs/wo-gh-42/reviewer-spec.output.md.usage.json
- runs/wo-gh-42/reviewer-spec.packet.md
- runs/wo-gh-42/reviewer-spec.review.json
- runs/wo-gh-42/reviewer-tests.output.md
- runs/wo-gh-42/reviewer-tests.output.md.usage.json
- runs/wo-gh-42/reviewer-tests.packet.md
- runs/wo-gh-42/reviewer-tests.review.json
- runs/wo-gh-42/routing.json
- runs/wo-gh-42/spec-writer.output.md
- runs/wo-gh-42/spec-writer.output.md.usage.json
- runs/wo-gh-42/spec-writer.packet.md
- runs/wo-gh-42/state.json
- runs/wo-gh-42/test-writer.output.md
- runs/wo-gh-42/test-writer.output.md.usage.json
- runs/wo-gh-42/test-writer.packet.md
- tests/test_station_budgets_completeness.py
- work_orders/wo-gh-42.json

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

## Practices

Promoted practices that resolved for this station. Follow each rule.

- P-4 (Fidelity to anchors and the committed asset pack): Judge rendered captures against both the project anchors and the committed asset pack; if the rendered game does not visibly use the pack art, fidelity fails.
- P-5 (Parallax depth must be demonstrated between layers): Parallax depth must be demonstrated between layers in captures, by measured displacement or visible relative motion; a single panning plate is not depth.
- P-6 (Cross-set coherence check): Run an explicit cross-set coherence check on every review: same character, proportions, palette, motifs and light logic across all stages or scenes; style drift is a changes requested finding.
- P-7 (Genre coherence): Judge the work against the genre declared in the project spec, never against imported standards from other genres; an old school 2D platformer is judged on genre craft: full-screen playable density, readable floors, big legible sprites.

## Craft skills

Curated craft guidance resolved for this station and this work order. Order of authority: the work order and its spec, then the project design system and decisions, then promoted practices, then these skills. Where a skill conflicts with any of those, the skill yields. Apply what fits the work in front of you; a skill is a bar to meet, not a checklist to recite.

### Skill: explainer-video

One idea, one short video, two layers. The content method governs what each scene's animation must obey; the production pipeline governs how the video is made. They compose: the pipeline renders what the method specifies, and the method alone is enough when a capable model renders the animation from one prompt. This skill is for the explainer format only: media-production remains the general media skill (quality bar, inspection, delivery, provenance) and applies alongside it. Where the two overlap, this skill states the format rules and media-production states everything else.

**Inputs**
- A text that has to be visualized (a script, a narration, a section of an article), or simply a concept to explain. Paste the whole text into the prompt; do not summarize it first.
- The output is a short video that explains one idea. If the text carries several ideas, split it and make one video per idea.

**The prompt (content method)**
Paste this block to a capable model, with the text or concept where marked. This layer is model-agnostic: any model that can build and render the animation from one prompt can run it, and the skill names no model for it.

```
Turn the text below into a short animated explainer video.

Style: flat, minimal 2D animation on a black background. Build it from recurring simple elements: circles and dots, thin lines, simple icons. On-screen labels are large, bold and short. Subtitles carrying the narration run under the animation.

Follow these instructions, in order:
1. First propose one visual action per block of the text, as a short list. Build the animation only after that, from the list.
2. Use at most four words per scene on screen, apart from the subtitles.
3. Turn ideas into actions: show things happening, not concepts sitting still.
4. Draw the analogies in the script literally. If the text says "a needle in a haystack", draw an actual needle in hay.
5. Show magnitudes with scale, and focus on what matters.
6. Keep elements across scenes, so the viewer sees how they transform.
7. Synchronize each key action with the corresponding spoken word.
8. Leave a clear final image at the end of each scene, and hold it.

Text to visualize:
[paste the text, or state the concept to explain]
```

**The review point**
- The proposal list from instruction 1 is the checkpoint. Read it before the build starts: one action per block, each action drawable, no block skipped, no action that needs more than four on-screen words. Correct the list, not the finished video.
- Record the proposal list with the station output, so a reviewer can check the video against what was proposed.

**Production pipeline**
When the video is produced as a repeatable line rather than a single generation, build the factory once and run every video through it, in this order:
1. Set up: install Claude Code and have it prepare Node and FFmpeg.
2. Voice: get an ElevenLabs API key, so the videos have voice.
3. References: feed it reference videos, the ones whose result you want to match, so it knows what to aim at. Reject references that do not match the target.
4. Engine: have it build an engine with HyperFrames that draws each frame with code and assembles them into a video.
5. Rules from references: have it extract the rules from those reference videos: how they hook in the first second, when scenes change, where each sound hit lands.
6. Review loop: review every video and correct what fails. The named failure modes are six-fingered hands, eyes leaving the face, and subtitles arriving late. Loop until it comes out right the first time.

**Motion techniques (hard requirement, both layers)**
Scenes draw and build themselves, not by camera movement over a finished image. Strokes draw on along their path (SVG stroke-dashoffset or canvas equivalent); elements build one at a time in narration order, outline before fill; lines (cables, trails, timelines) trace themselves. Time it from the words: transcribe the narration locally (faster-whisper) and land each draw-on on the word that names it. A generated still is look and layout reference, or background only under drawn foreground action; pan or zoom (Ken Burns) over a full-frame still as primary motion fails this skill.

**Check the result against the method**
- Scenes carry at most four words on screen besides the subtitles; labels are large and bold.
- Analogies are drawn literally; magnitudes are shown by scale; the same elements persist and transform across scenes instead of being replaced.
- Key actions land on the spoken word they belong to, and every scene ends on a clear final image that holds.
- On pipeline output: voice is present, subtitles land on time, and hands, eyes and faces survive inspection.

**Provenance**
- Content method by Alan Daitch (@alandaitch), taught in an Instagram reel published around 2026-11-03: https://www.instagram.com/reel/DfSzHquzV1v/
- Extracted from the video itself; the full prompt lives in its comments, which were not accessible, so the skill carries the method as spoken and shown on screen. The model named in the reel could not be verified, so the content layer names no model.
- Production pipeline from the reel "Cómo montar tu fábrica de reels con Claude code" by @unminutodeporques (Un minuto de porqués), published 2026-11-10: https://www.instagram.com/reel/DfkY1E1AYW_/
- Also extracted from the video itself; the tool names (Claude Code, ElevenLabs, HyperFrames, FFmpeg) were confirmed from on-screen text. The reference-rules document shown was not legible, so the only rules claimed from it are the three it names: the first-second hook, scene-change timing and sound-hit placement. The account sells a packaged folder; this skill does not depend on it.
- Motion layer (2026-11-15), restated, nothing copied or vendored: draw-on mechanics from iart-ai/explainer-video-skills (MIT); word cueing from owlinthebarnai/video-studio-kit (no license file; technique only); frame-deterministic drawing from illodev/drawn-by-code (MIT).

## Rendered evidence

This run captured screenshots of the served project at the following breakpoints:

- `screenshot-1440x900.png` at `runs/wo-gh-42/evidence/screenshot-1440x900.png`
- `screenshot-390x844.png` at `runs/wo-gh-42/evidence/screenshot-390x844.png`

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

