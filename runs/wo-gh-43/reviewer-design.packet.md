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

<!-- source: .openspec/specs/attribution-default/spec.md -->
# ANVIL Attribution by Default

Status: filed for wo-gh-43
Slug: attribution-default

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
The owner rule, stated 2026-11-15: every project the factory ships carries an ANVIL attribution by default. An operator audit of the shipped projects on 2026-11-15 found the rule is not true today. Sentia carries a bespoke credit ("Sentia is a concept product, designed and built end to end by ANVIL, an open source software factory. Developed by Eduardo Arana.", the owner chosen wording of 2026-10-30), while Doom Fire, Mochi Smash, Platform25 and the live C64 page carry no attribution at all. Nothing in the factory produces the attribution: the scaffold does not seed it, the builder and publisher guidance do not state it, and the checks gate cannot see its absence. This spec makes the factory produce it by default, so future projects ship compliant and only the already shipped projects need retrofits, which are separate orders in their own repos.

## Requirements
- R1, the rule and the default wording. Every web project the factory scaffolds or onboards carries, by default, a visible attribution reading exactly "Made with ANVIL, an open source software factory." with a link to the ANVIL landing (https://anvil-landing-7x1.pages.dev) or to the factory repository. A project bespoke credit that names ANVIL as the builder counts as compliant and is never replaced by the default line; the Sentia credit quoted in the Purpose is the standing example. Placement is the page footer or an equivalent visible spot; on a game surface, a credits or footer element that does not break gameplay. No em dashes in the attribution text or in any text this order writes.
- R2, scaffold and onboard. anvil/scaffold.py (new_project) seeds the attribution requirement for web blueprints (blueprints/static-site.json, and blueprints/cloudflare-worker.json where it ships pages): the seeded first spec (site-shell) and the seeded project brain state the footer requirement, its default wording and the compliance rule of R1, so the first build of a new project includes it. anvil/onboard.py records the same requirement for an onboarded web project in its onboard output. Onboard never overwrites an existing project file, and this order does not change that: for onboarded projects the requirement is recorded, not forced into their pages.
- R3, station guidance. stations/builder/PROMPT.md and stations/publisher/PROMPT.md state the rule of R1: build the attribution in by default on web deliverables, keep a compliant bespoke credit when the project has one, place it per R1, and treat its absence at publish time as a defect. The only way a project ships without an attribution is an owner approved exception recorded in that project spec, named in the guidance.
- R4, deterministic check. The checks gate (anvil/gates.py, checks_gate) gains an attribution check for shipped web deliverables: given the deliverable HTML of a web project (dist/, public/ or the project root index, following the project layout), the check passes when the visible text carries an attribution naming ANVIL (the default line of R1, or a bespoke credit naming ANVIL as the builder), and fails the gate when no attribution naming ANVIL is present. The check applies only when the order ships a web deliverable; projects and orders without an HTML deliverable are unaffected. A recorded owner exception (R3) is honoured and passes with the exception named in the check output.
- R5, decision record. brain/decisions/0012-anvil-attribution-default.md records the rule as a long term factory decision, following the format of the existing decision records: context (the audit and its findings), the decision (R1 to R4 in brief), and consequences (future projects compliant by default, shipped projects retrofitted by their own orders, exceptions only by recorded owner approval).
- R6, tests. The factory test suite gains tests for the check of R4: pass on the default line, pass on a bespoke Sentia style credit, fail when no attribution exists, pass with a recorded exception, and not applicable to a non web deliverable. The full suite stays green under the project check command: python -m unittest discover -s tests -p 'test_*.py'.

## Authorised surface
anvil/scaffold.py, anvil/onboard.py, anvil/gates.py, a new anvil/ module for the check if the line prefers one, blueprints/static-site.json, blueprints/cloudflare-worker.json, stations/builder/PROMPT.md, stations/publisher/PROMPT.md, brain/decisions/0012-anvil-attribution-default.md, this spec, and tests/ for the new attribution tests only (per spec exception to the anvil.json protected_paths entry for tests/: new tests are written by the test-writer station, existing tests are not edited by the builder). anvil.json and pipelines/ stay untouched.

## Out of scope
- Retrofits of already shipped projects (Sentia, Doom Fire, Mochi Smash, Platform25, the live C64 page); each is its own order in its own repo.
- Forcing the attribution into the pages of an already onboarded project; onboard records the requirement only and never overwrites an existing project file.
- Any change to anvil.json, pipelines/, anvil.yaml (token cap stays 6,000,000, max_agent_calls 32, max_runtime_turns 40) or existing tests.
- Any gate change that affects orders or projects without an HTML deliverable.

## Exception record (R3, R4)
An owner approved exception is a line in the project spec of the form `Attribution exception: approved by <owner> on <YYYY-MM-DD>: <reason>`. The check honours only that exact line prefix, and names the quoted line in its output. (Form proposed by the spec writer because the order names the record but not its shape; the owner may change it before the build.)

## Compliance test for R4
Visible text means the text of the deliverable HTML with tags, script and style content, and comments removed. An attribution naming ANVIL is visible text that contains the exact default line, or contains the word "ANVIL" (case sensitive) in a sentence stating that ANVIL built or made the project (for example "built end to end by ANVIL"). The word in a comment, attribute or script only does not count. A deliverable file set passes when at least one HTML file in it carries the attribution; with several HTML files, the index page is the one checked.

## Scenarios
Each scenario names the requirement it proves.
- S1 (proves R1, R2), scaffold seeds the rule: a new static-site project scaffolded after this change carries the attribution requirement in its seeded site-shell spec and its seeded brain/project.md, each containing the exact default line, the landing URL https://anvil-landing-7x1.pages.dev, the footer placement, and the bespoke compliance rule. The same holds for blueprints/cloudflare-worker.json when it ships pages. An onboard run on a web project writes the same requirement into its onboard output and leaves every pre-existing project file byte-identical.
- S2 (proves R1, R4), check passes: a web deliverable whose footer reads "Made with ANVIL, an open source software factory." linked to https://anvil-landing-7x1.pages.dev passes the attribution check; a deliverable carrying the Sentia credit "Sentia is a concept product, designed and built end to end by ANVIL, an open source software factory. Developed by Eduardo Arana." also passes and is not flagged for replacement.
- S3 (proves R4), check fails: a web deliverable whose index.html has no attribution naming ANVIL (also: "ANVIL" present only inside an HTML comment) fails the checks gate, and the gate output names the missing attribution as the reason.
- S4 (proves R3, R4), exception honoured: a web deliverable with no attribution, from a project whose spec contains `Attribution exception: approved by Eduardo Arana on 2026-11-16: brand-neutral kiosk build`, passes, and the check output contains that exception line.
- S5 (proves R4, R6), non web unaffected and suite green: an order with no HTML deliverable runs the checks gate with no attribution failure and no attribution output; `python -m unittest discover -s tests -p 'test_*.py'` exits 0, including the new tests for S2, S3, S4 and this case.
- S6 (proves R3), station guidance: stations/builder/PROMPT.md and stations/publisher/PROMPT.md each contain the exact default line, the placement rule, the keep-bespoke rule, and the words "owner approved exception"; the publisher text treats a missing attribution as a defect.
- S7 (proves R5), decision record: brain/decisions/0012-anvil-attribution-default.md exists with the context, decision and consequences sections in the format of 0011-station-timeout.md, mentions the 2026-11-15 audit and the default line, and contains no em dash. No file written by this order contains an em dash (check: grep for U+2014 over the changed files returns nothing).
- S8 (proves R1), placement: on a game surface the attribution is in a credits or footer element outside the canvas and outside the input-handling region, so that removing it changes no gameplay behaviour; checked by the deliverable having the line in a footer or credits element that is not the game canvas container.


## Diff summary

- .openspec/specs/attribution-default/spec.md: +21, -5
- anvil/gates.py: +14, -0
- anvil/onboard.py: +5, -0
- anvil/scaffold.py: +12, -1
- blueprints/cloudflare-worker.json: +1, -0
- blueprints/static-site.json: +1, -0
- stations/builder/PROMPT.md: +1, -0
- stations/publisher/PROMPT.md: +1, -0

## File access allowlist

This packet may only embed content from:
- design/DESIGN.md
- design/tokens.json
- .openspec/specs/attribution-default/spec.md
- .openspec/specs/attribution-default/spec.md
- anvil/gates.py
- anvil/onboard.py
- anvil/scaffold.py
- blueprints/cloudflare-worker.json
- blueprints/static-site.json
- stations/builder/PROMPT.md
- stations/publisher/PROMPT.md

## Work order

- id: wo-gh-43
- kind: feature
- title: ANVIL attribution by default: every shipped web project credits the factory
- source: github-issue
- description: Implement the spec in .openspec/specs/attribution-default/spec.md. Pipeline for this order is sdlc-default (see anvil.json). Mode: brownfield, the factory improving itself. Domain: factory core, station guidance and project scaffolding.

OWNER RULE (stated 2026-11-15): every project the factory ships carries an ANVIL attribution by default. The owner audited the shipped projects and found the rule is not true today: Sentia carries a bespoke credit, and Doom Fire, Mochi Smash, Platform25 and the live C64 page carry none. This order makes the factory itself produce the attribution by default, so future projects ship compliant without a retrofit. Retrofits of already shipped projects are separate orders (the Doom Fire retrofit is filed in its own repo); this order changes only the factory.

DEFAULT WORDING AND COMPLIANCE:
- Default attribution text, exact: "Made with ANVIL, an open source software factory." with a link to the ANVIL landing https://anvil-landing-7x1.pages.dev (the factory repo link is an accepted alternative target).
- A project bespoke credit that names ANVIL as the builder counts as compliant. Precedent, Sentia: "Sentia is a concept product, designed and built end to end by ANVIL, an open source software factory. Developed by Eduardo Arana."
- Placement: the page footer or an equivalent visible spot. On a game surface, a credits or footer element that does not break gameplay.
- No em dashes in any text this order writes.

BUILD, per the spec requirements:
- R1, the rule and its wording, as above, recorded in the spec and in the decision record of R5.
- R2, scaffold and onboard: anvil/scaffold.py new_project seeds the attribution requirement for web blueprints (blueprints/static-site.json, and blueprints/cloudflare-worker.json where it ships pages), so the seeded site-shell spec and project brain carry the footer requirement from the first build. anvil/onboard.py records the same requirement for onboarded web projects in its onboard output, without overwriting any existing project file (onboard never overwrites).
- R3, station guidance: stations/builder/PROMPT.md and stations/publisher/PROMPT.md carry the rule, the default wording, the placement guidance and the exception path (an owner approved exception recorded in the project spec).
- R4, deterministic check: the checks gate (anvil/gates.py, checks_gate) verifies, for a shipped web deliverable, that the deliverable HTML carries an attribution naming ANVIL: the default line, or a bespoke credit naming ANVIL as the builder. The gate fails when no attribution is present. Web deliverables only: orders and projects without an HTML deliverable are unaffected. A recorded owner exception in the project spec or project configuration is honoured.
- R5, decision record: brain/decisions/0012-anvil-attribution-default.md captures the rule as a long term factory decision, in the format of the existing records.
- R6, tests: tests cover the check passing on the default line, passing on a bespoke Sentia style credit, failing when no attribution exists, and not applying to a non web deliverable. The full factory suite stays green: python -m unittest discover -s tests -p 'test_*.py'.

AUTHORISED SURFACE (full legitimate surface for this spec): anvil/scaffold.py, anvil/onboard.py, anvil/gates.py, a new anvil/ module for the check if the line prefers one, blueprints/static-site.json, blueprints/cloudflare-worker.json, stations/builder/PROMPT.md, stations/publisher/PROMPT.md, brain/decisions/0012-anvil-attribution-default.md, .openspec/specs/attribution-default/spec.md, and tests/ for the new attribution tests only (per spec exception to the anvil.json protected_paths entry for tests/: the new tests are written by the test-writer station; the builder does not edit existing tests). No other protected path changes: anvil.json and pipelines/ stay untouched.

TOKEN CAP: 6,000,000, the factory standing proven configuration in anvil.yaml (max_run_tokens 6000000, max_agent_calls 32, max_runtime_turns 40), left unchanged. Calibration basis: the comparable factory feature order wo-gh-39 (configurable station timeout, code plus tests) measured 1,504,285 tokens total and was approved; this order touches more files but the same order of magnitude, and the standing cap leaves headroom above the largest single station of every comparable factory run.

REQUIRED LITERALS in the builder report: "Made with ANVIL, an open source software factory.", "0012", ".openspec/specs/attribution-default/spec.md", "S1", "S2", "S3", "S4", "S5", and the full suite result line.

The run stops at the human gate. Nothing merges without the owner gate word reported back through the operator.

- risk_hints: checks gate changes can false-fail other projects runs; the spec confines the check to web deliverables, accepts bespoke ANVIL credits, and honours a recorded owner exception
- status: new

## Loopback feedback (attempt 2 of 3)

This is a re-review. The previous attempt was sent back by checks-gate to builder. Judge the work as it is now, and check that each finding below is resolved; do not pass a finding that is still open.

Reason: Gate checks failed; artifact validation: Builder report artifact /home/runner/work/anvil-factory/.anvil-worktrees/anvil-factory/wo-gh-43/runs/wo-gh-43/builder.output.md is missing. Required literal not found in full in the builder report: Made with ANVIL, an open source software factory. Required literal not found in full in the builder report: 0012

- # Checks Gate: pre-review
  Basis: builder_delta
  Attempt: 1
  
  # Protected Path Additions (Observed, Not Violations)
  Protected path addition (observed): tests/test_attribution_default.py (matches tests/)
  
  # Check Commands
  ## Command 1: python -m unittest discover -s tests -p 'test_*.py'
  Exit code: 1
  Output:
  ```
  ce for reviewers, not a final verdict. Record what you observe; reviewers are not bound by your self-assessment.\n\nThis verification step only applies when the Quality Charter section is present in your packet. For non-visual work, this step does not apply.\n\n## Definition of done\n- Every spec scenario for this order is satisfied on the final tree, not only the ones a test happens to cover.\n- The project check command passes on the final tree. You ran it and read the output. You did not edit, skip or delete a test to get there.\n- You exercised the change the way a user would (ran it, opened it, called it) and it works.\n- For anything a person will see, you looked at the rendered result at the sizes the spec names and it meets the stated bar, the project design system and the Craft skills in your packet.\n- The change stays inside the write set the work order allows.\n\n## Before you hand off\nRe-read your whole diff as a reviewer would and fix what you find. Then write the builder report: what changed and which scenario each change serves, the exact verification commands with their real summary lines, and plainly what is unmet, unverified or left open. A gap you repo

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

**Check the result against the method**
- Scenes carry at most four words on screen besides the subtitles; labels are large and bold.
- Analogies are drawn literally; magnitudes are shown by scale; the same elements persist and transform across scenes instead of being replaced.
- Key actions land on the spoken word they belong to, and every scene ends on a clear final image that holds.
- On pipeline output: voice is present, subtitles land on time, and hands, eyes and faces survive inspection.

**Provenance**
- Content method by Alan Daitch (@alandaitch), taught in an Instagram reel published around 2026-11-03: https://www.instagram.com/reel/DfSzHquzV1v/
- The method was extracted from the video itself. The full prompt the reel points to lives in its comments, which were not accessible when this skill was captured, so the skill carries the method as spoken and shown on screen and nothing more. The model named in the reel could not be verified from its audio, so the content layer names no model.
- Production pipeline from the reel "Cómo montar tu fábrica de reels con Claude code" by @unminutodeporques (Un minuto de porqués), published 2026-11-10: https://www.instagram.com/reel/DfkY1E1AYW_/
- Also extracted from the video itself; the tool names (Claude Code, ElevenLabs, HyperFrames, FFmpeg) were confirmed from on-screen text. The reference-rules document shown in that reel was not legible at playback resolution, so the only rules claimed from it are the three it names: the first-second hook, scene-change timing and sound-hit placement. The account sells a ready-made folder that packages the pipeline; this skill does not depend on it and stands on the method alone.

## Rendered evidence

This run captured screenshots of the served project at the following breakpoints:

- `screenshot-1440x900.png` at `runs/wo-gh-43/evidence/screenshot-1440x900.png`
- `screenshot-390x844.png` at `runs/wo-gh-43/evidence/screenshot-390x844.png`

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

Product type: game

Observable criteria:

- **Stated Standard**: Project must state observable criteria in design system


## Reference Anchors

⚠️ **WARNING**: This run has no reference anchors.

The review will proceed under the charter floor alone.

