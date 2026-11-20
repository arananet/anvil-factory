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

- .openspec/specs/continuous-run-accounting/spec.md: +4, -4
- runs/wo-gh-41/attempts/1/checks-gate.pre-review.output.md: +22, -26
- runs/wo-gh-41/attempts/2/checks-gate.pre-review.output.md: +22, -26
- runs/wo-gh-41/builder.output.md.usage.json: +14, -14
- runs/wo-gh-41/builder.packet.md: +35, -0
- runs/wo-gh-41/checks-gate.pre-review.output.md: +8, -9
- runs/wo-gh-41/envelopes/builder.envelope.json: +22, -5
- runs/wo-gh-41/envelopes/checks-gate.envelope.json: +6, -9
- runs/wo-gh-41/envelopes/intake.envelope.json: +1, -1
- runs/wo-gh-41/envelopes/reviewer-architecture.envelope.json: +1, -1
- runs/wo-gh-41/envelopes/reviewer-security.envelope.json: +1, -1
- runs/wo-gh-41/envelopes/reviewer-spec.envelope.json: +1, -1
- runs/wo-gh-41/envelopes/reviewer-tests.envelope.json: +1, -1
- runs/wo-gh-41/envelopes/spec-writer.envelope.json: +11, -11
- runs/wo-gh-41/envelopes/test-writer.envelope.json: +11, -11
- runs/wo-gh-41/events.jsonl: +16, -0
- runs/wo-gh-41/intake.output.md: +5, -7
- runs/wo-gh-41/intake.output.md.usage.json: +13, -13
- runs/wo-gh-41/reviewer-architecture.packet.md: +36, -1
- runs/wo-gh-41/reviewer-security.packet.md: +36, -1
- runs/wo-gh-41/reviewer-spec.packet.md: +36, -1
- runs/wo-gh-41/reviewer-tests.packet.md: +36, -1
- runs/wo-gh-41/routing.json: +1, -1
- runs/wo-gh-41/spec-writer.output.md: +18, -23
- runs/wo-gh-41/spec-writer.output.md.usage.json: +13, -13
- runs/wo-gh-41/state.json: +38, -32
- runs/wo-gh-41/test-writer.output.md: +42, -40
- runs/wo-gh-41/test-writer.output.md.usage.json: +13, -13
- tests/test_continuous_run_accounting.py: +29, -8

## File access allowlist

This packet may only embed content from:
- design/DESIGN.md
- design/tokens.json
- .openspec/specs/continuous-run-accounting/spec.md
- runs/wo-gh-41/attempts/1/checks-gate.pre-review.output.md
- runs/wo-gh-41/attempts/2/checks-gate.pre-review.output.md
- runs/wo-gh-41/builder.output.md.usage.json
- runs/wo-gh-41/builder.packet.md
- runs/wo-gh-41/checks-gate.pre-review.output.md
- runs/wo-gh-41/envelopes/builder.envelope.json
- runs/wo-gh-41/envelopes/checks-gate.envelope.json
- runs/wo-gh-41/envelopes/intake.envelope.json
- runs/wo-gh-41/envelopes/reviewer-architecture.envelope.json
- runs/wo-gh-41/envelopes/reviewer-security.envelope.json
- runs/wo-gh-41/envelopes/reviewer-spec.envelope.json
- runs/wo-gh-41/envelopes/reviewer-tests.envelope.json
- runs/wo-gh-41/envelopes/spec-writer.envelope.json
- runs/wo-gh-41/envelopes/test-writer.envelope.json
- runs/wo-gh-41/events.jsonl
- runs/wo-gh-41/intake.output.md
- runs/wo-gh-41/intake.output.md.usage.json
- runs/wo-gh-41/reviewer-architecture.packet.md
- runs/wo-gh-41/reviewer-security.packet.md
- runs/wo-gh-41/reviewer-spec.packet.md
- runs/wo-gh-41/reviewer-tests.packet.md
- runs/wo-gh-41/routing.json
- runs/wo-gh-41/spec-writer.output.md
- runs/wo-gh-41/spec-writer.output.md.usage.json
- runs/wo-gh-41/state.json
- runs/wo-gh-41/test-writer.output.md
- runs/wo-gh-41/test-writer.output.md.usage.json
- tests/test_continuous_run_accounting.py

## Work order

- id: wo-gh-41
- kind: feature
- title: Continuous run accounting: the run record is checkpointed after every station and completed on every exit path, budget death included
- source: github-issue
- description: Implement the spec in .openspec/specs/continuous-run-accounting/spec.md. Pipeline for this order is sdlc-default (software domain, the factory repo itself), selected by the run workflow.

STAGING: this order is filed and staged only. The spec and this work order record sit on the branch anvil/run-continuous-run-accounting, the issue carries no anvil label, and no run is fired. Execution starts on the owner's word. Run configuration baseline, unchanged by this filing: the order is parented on factory main 4675a131eb9aa88097741dc3cdc9772c3db17550 (the fixed spine merged by wo-gh-39), whose anvil.yaml carries max_run_tokens 6000000, max_runtime_turns 40 and max_packet_tokens 48000, and whose anvil.json wires the checks command (python -m unittest discover -s tests -p 'test_*.py').

EVIDENCE (the defect this order closes):
In the C64 blueprint chain (project c64-retro-hardware), work order wo-gh-6 (run 43668712644) exhausted its budget: the builder's single call measured 6,359,529 cache-inclusive tokens against the 6,000,000 run cap, and the run died with status budget_exceeded before the builder wrote its report. The branch held finished product but no builder report and no complete run record: 0 of 6 reviewers counted, and the run's own accounting did not exist. Work order wo-gh-7 then spent a second run (5,697,863 tokens measured) largely to write the paperwork wo-gh-6 never wrote, the builder report and the comparison records for work that already existed. The comparison against other software factories (factory research of 2026-11-15, report section "Mechanisms ANVIL Does Not Have", mechanisms 7 to 12 for failure mode 2) shows the standard shape elsewhere: mini-SWE-agent saves its trajectory in a finally block after every step and converts limit exceptions into recorded exit outcomes; Attractor checkpoints after every node and resumes from the last checkpoint; OpenHands treats an append-only event log as the run record.

BUILD, per the spec requirements:
R1: the runner writes the run record (runs/<work-order-id>/report.json with its step records) after every station completes, fails or is skipped, in the final report's shape plus a checkpoint field set (last completed station, elapsed milliseconds, measured usage so far). Writes are atomic (sibling temporary file, then rename), so a mid-run read always sees a valid report complete as of the last finished station. Checkpointing adds no station and no model call.
R2: every termination path completes the record before the process exits: normal completion, a verdict, budget exhausted (exit status budget_exceeded), a station timeout (using wo-gh-39's honest timeout records), the runtime turn limit, a checks gate stop, an intake stop, an uncaught exception in spine code, and the trappable external signals (SIGTERM, SIGINT). The completed record names the exit status, the termination reason, every station that ran with its outcome and executed model, every station that never ran as not run, and the cost section under cost-measurement semantics. A budget death is a complete recorded outcome carrying the measured consumption that crossed the cap and the station in flight, with its partial usage when exposed.
R3: inspecting or resuming after a killed run reads the checkpointed record as the run's accounting; tools/line_comment.py and the swimlane render a killed run's record with no station executing. A later run of the same work order preserves the killed run's record in the run history and never overwrites it.
R4: regression tests as new files under tests/, driving scripted runs through the runner with a fake runtime: (a) a run killed at the token cap mid-builder leaves a complete, parseable record (exit status budget_exceeded, per-station outcomes, the builder's measured partial usage, unrun stations named not run); (b) the same completeness holds for a station timeout death and for an injected uncaught error, each with its own exit status and reason; (c) a healthy scripted run checkpoints after each station and its final report equals the last checkpoint plus the verdict sections; (d) SIGTERM leaves a completed record naming the signal.

RECONCILIATION WITH ACTIVE SPECS (read before building; these are decisions, not discoveries for the line to make):
No active spec conflicts. The token-efficiency spec already requires per-attempt usage artifacts and that a budget stop preserves the report; this order generalizes that preservation to every exit path and makes it a runner property, using those artifacts as inputs. Cost-measurement semantics are frozen and reused as they stand (totals are sums of measured steps; unmeasured stays unmeasured with its reason). The station artifact contract's executed model honesty and the station-timeout record fields are inputs, unchanged.

BUILDER REPORT REQUIRED LITERALS: the builder report (runs/wo-gh-41/builder.output.md) must contain each of these in full, unabbreviated: 4675a131eb9aa88097741dc3cdc9772c3db17550, continuous-run-accounting, checkpoint, budget_exceeded. It must also state the base ref it verified the tree against, the exact full factory test count from the suite run, and the names of the new test files added.

GUARDRAILS: authorized surface for this order: anvil/runner.py, anvil/line.py, anvil/telemetry.py, anvil/cost.py, anvil/executor.py, anvil/cli.py (the resume and inspect paths), tools/line_comment.py, anvil/statuspage.py if it reads run reports, the factory docs that describe run reports or resume (docs/EXECUTION.md at minimum), CHANGELOG.md, one new decision record under brain/decisions/, and new test files under tests/. Pipeline files under pipelines/ are protected paths in anvil.json; the fix must hold without editing them. anvil.json itself is protected; do not edit it. Existing test files at the base ref are protected: do not modify or delete them; new tests arrive as new files. Frozen: cost-measurement semantics, the station-timeout record fields, the review parse contract, the reviewer prompts. Python standard library only, no new dependency. No em dash or en dash character in any produced file. Nothing in this order merges, publishes or deploys anything; the run stops at the owner human gate.

GitHub issue: https://github.com/arananet/anvil-factory/issues/41


GitHub issue: https://github.com/arananet/anvil-factory/issues/41
- risk_hints: 
- status: new

## Loopback feedback (attempt 3 of 3)

This is a re-review. The previous attempt was sent back by checks-gate to builder. Judge the work as it is now, and check that each finding below is resolved; do not pass a finding that is still open.

Reason: Gate checks failed

- # Checks Gate: pre-review
  Basis: builder_delta
  Attempt: 2
  
  # Protected Path Additions (Observed, Not Violations)
  Protected path addition (observed): tests/test_continuous_run_accounting.py (matches tests/)
  
  # Check Commands
  ## Command 1: python -m unittest discover -s tests -p 'test_*.py'
  Exit code: 1
  Output:
  ```
  ch'
  ...................................................................................................................................................../opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/unittest/case.py:589: ResourceWarning: unclosed <socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 36915)>
    if method() is not None:
  ResourceWarning: Enable tracemalloc to get the object allocation traceback
  .../opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/unittest/case.py:589: ResourceWarning: unclosed <socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 36783)>
    if method() is not None:
  ResourceWarning: Enable tracemalloc to get the object allocation traceback
  .......................F............................................................s....................................ss.........................................................................................................................................................s......s......................................................................................................s................................................................................

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

- `screenshot-1440x900.png` at `runs/wo-gh-41/evidence/screenshot-1440x900.png`
- `screenshot-390x844.png` at `runs/wo-gh-41/evidence/screenshot-390x844.png`

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

