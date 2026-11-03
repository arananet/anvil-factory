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
- Focus on the design system the project has defined. Do not impose external design opinions or preferences that are not documented in the project's design system.
- A design token marked as "TODO" or placeholder means the project hasn't defined that value yet. Flag missing values as findings only if the interface output actually uses undefined tokens.
- Findings should be specific and actionable: cite which quality bar was violated, which token was used incorrectly, or which rule was not followed.
- Your verdict must be one of: `pass`, `fail`, or `changes_requested`.
- Produce the output as a JSON object, not as chat text.

## Output Format

Return a JSON object with this structure:

{
  "station": "reviewer-design",
  "verdict": "pass | fail | changes_requested",
  "findings": [
    "Specific finding with reference to design system rule or quality bar",
    "Another finding if applicable"
  ]
}

The station field must equal "reviewer-design", the verdict must be one of pass, fail, or changes_requested, and findings must be a list of strings.

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


## Work order

- id: wo-gh-21
- kind: task
- title: Fix the excessive Astra route consumption
- source: github-issue
- description: Implement the spec in .openspec/specs/astra-consumption/spec.md in the factory. Pipeline for this order is sdlc-default (software domain, full reviewer set), selected by the run workflow.

SEQUENCING GATE: execute this order only from a main that already carries the wo-gh-16 parse contract merge. Before executing, verify that tools/claude_station.py on the run branch carries the wo-gh-16 loopback's final REVIEW_SUFFIX shape and that the station prompts carry their Output Format contract sections. If the merge is not in the branch history, stop and report instead of running. This order never modifies tools/claude_station.py, the review parsing contract, or the prompts' Output Format sections, and it preserves the capability program's changes where both touch the runner.

Build, per the spec scenarios:

S1, packet budget: the runner measures every station packet with a deterministic token estimator defined once (anvil/, standard library only), its constant visible in config and the estimate labelled an estimate wherever shown. Per station budgets come from project config (anvil.yaml) through anvil/config.py with factory defaults there, and apply to the stations routed to the Astra or Codex executor and to the interface stations (builder, writer, media-producer, brief-writer, reviewer-design). An over budget packet is trimmed in the declared order (design tokens compact instead of pretty printed; quality bars reduced to headings plus first lines; learnings limited to the most recent entries that fit) until it measures within budget; if it still exceeds, or config sets the policy to fail, the step fails before any model call with the measured size and the budget in the failure detail. An under budget packet reaches the executor byte unchanged. Per measured step the run report records measured tokens, budget and action (sent, trimmed, failed).

S2, evidence image policy: a deterministic standard library assembler combines a design review round's PNG captures into one contact sheet PNG no wider than the configured maximum (factory default 1600 px), scaling down proportionally and never up, failing loudly on a capture it cannot process. The reviewer-design packet references the contact sheet only; the full resolution originals stay byte unchanged in the run evidence. The work order model gains an optional evidence image list, default empty, existing work orders parsing unchanged; builder packets reference image evidence only when the order declares it.

S3, fresh session design review: the reviewer-design packet is assembled fresh with the station prompt, the Project design section, the spec the order implements, a diff summary the runner derives deterministically from git (files changed with added and removed line counts) and the contact sheet reference. It never contains the builder session transcript, other stations' outputs or whole worktree file contents. The packet declares a file access allowlist (files the order touches, design system files, the spec) as a contract section, and a deterministic runner check verifies no embedded content comes from outside the allowlist. Other reviewers keep their current packets in this order.

S4, stable prefix layout: _packet_text assembles stable material first (station prompt, Project design section when present, Verified learnings when present) and per run variable material last (work order block, upstream steps), so two runs of one station share a byte identical prefix up to the work order block. After this order's run, the operator records the gateway log cached values for the run's Astra requests on the issue, exactly as logged, claiming no caching saving beyond them.

S5, per station cost visibility: each executed step's run report entry records the configured model, the executed model where the runtime reports one (existing provenance), the measured packet tokens and the executor reported usage (input and output tokens) when reported, null when not. The report totals the measured packet tokens of the Astra bound stations per work order. Cost stays null unless the runtime reports a numeric cost.

Tests, mapped to the scenarios as the spec's Tests section states: estimator determinism and monotonicity; budget trim order, fail policy with no executor call, under budget byte identity, report fields; contact sheet dimensions, PNG format, originals unchanged, non PNG failure; packet layout stable prefix across two runs; scoped review packet contents and the allowlist check rejecting out of allowlist content. The full factory suite passes.

Guardrails: runtime code stays on the Python standard library only. No em dash or en dash character in any produced file (project style rule). Nothing in this order's artifacts claims a consumption saving; after the merge, a proof run (one small real design touching order through the line) reports the Astra input tokens per request from the gateway logs against the audited baseline of about 45,000 per request.

The reviewer writes its review to the authoritative review file named in its packet; prose outside that file is not a review.

GitHub issue: https://github.com/arananet/anvil-factory/issues/21

LOOPBACK (gate round 2, operator brief): round 1 executed the full line (Actions run 41581311619) and the verdict of record is no_reviews: all five reviewer stations wrote prose into their authoritative .review.json files, so the parser counted 0 of 5, failed closed and named each one; prose is not a review and round 1's outcome stands as recorded. The five raw reviewer outputs are on record in runs/wo-gh-21/ and their substantive findings, quoted and summarized below, are this loopback's scope. The implementation built the infrastructure (estimator, budget enforcement, contact sheet assembler, scoped packet builder, 17 mapped tests passing per reviewer-tests) but the reviewers found it is not wired into the executed run path and is not hardened. Fix exactly this, nothing else:

1. INTEGRATE S2 AND S3 INTO THE RUN PATH (reviewer-architecture findings 1 and 2, and reviewer-spec's integration shortfall). assemble_contact_sheet and build_reviewer_design_packet exist and pass unit tests but are never called by the run pipeline: when the runner prepares the reviewer-design step, it must assemble the round's contact sheet from the run's captures when captures exist and build the reviewer-design packet through the scoped builder, so a real run's reviewer-design packet is the fresh scoped packet of spec S3, not the standard packet. The WorkOrder evidence_images field is added but never read: builder packet assembly must consult it, including image references only when the order declares them and none otherwise.

2. FIX THE LAYER VIOLATION (reviewer-architecture finding 3). build_reviewer_design_packet imports from .stations inside the runner module, inverting the layer separation. Place the scoped packet assembly where the architecture allows and state the chosen placement in the builder output.

3. ALLOWLIST CHECK BY PROVENANCE (reviewer-architecture finding 4, reviewer-security finding 4). Pattern scanning of packet text cannot verify content provenance. The runner check must verify, deterministically, that each content block embedded in the reviewer-design packet carries a source inside the declared allowlist (tag content with its source path at assembly time and check the tags), so out of allowlist content fails the check even when its text mentions allowlisted names.

4. PNG ASSEMBLER AND PATH HARDENING (reviewer-security findings 1, 2, 3, 5, 6, in anvil/runner.py and anvil/model.py). Enforce input byte size and pixel dimension caps read from headers before any inflation of image data; verify PNG chunk CRCs; bounds check chunk lengths before reads; validate the contact sheet output path to resolve inside the run evidence directory; validate WorkOrder file path fields this order touches (including evidence image paths) to resolve inside the project tree.

5. MAKE S1 AND S5 VISIBLE IN THE REAL RUN REPORT. Round 1's runs/wo-gh-21/report.json contains no measured tokens, budget, action or usage anywhere, although the spec requires the run report to record them per measured step. After this loopback, the report must carry, per measured step: measured tokens, budget and action (sent, trimmed or failed); the executor reported usage or null; and the per work order total of measured packet tokens for the Astra bound stations as a present field (its value may be zero when no station in the run is Astra bound, but the field and the interface stations' measurements, reviewer-design included, must be there).

6. REVIEW CHANNEL DISCIPLINE (restated for every reviewer station in this round): your review is exactly one JSON object written to runs/wo-gh-21/<your station>.review.json and nothing else in that file. Prose, summaries and narrative belong in your .output.md only. A .review.json that is not one parseable JSON object is not counted, and round 1 ended with 0 of 5 counted for exactly that reason.

Guardrails unchanged: never modify tools/claude_station.py, the review parsing contract or the prompts' Output Format sections; standard library only; no em dash or en dash characters; S1, S4 and S5's already correct parts stay as they are except for item 5's report visibility.
- risk_hints: 
- status: new

## Upstream steps

- intake: completed
- spec-writer: executed
- test-writer: executed
- builder: executed
- reviewer-spec: executed
- reviewer-security: executed
- reviewer-tests: executed
- reviewer-architecture: executed

## Output contract

Your complete answer is exactly one review JSON object written to runs/wo-gh-21/reviewer-design.review.json. The free output transcript stays as provenance and is never parsed for a review.
