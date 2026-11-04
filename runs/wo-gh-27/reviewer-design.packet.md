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

<!-- source: .openspec/specs/film-review-pass/spec.md -->
# Film Review Pass

Status: proposed
Slug: film-review-pass

## Roles
- implementer: executes the review described here (the reviewer stations)
- reviewer: the stations named below, judging the finished film on its evidence
- qa: checks the scenarios below against the run record
- product_owner: owns the purpose and accepts the result at the human gate

## Purpose

The wo-gh-18 polish round rendered a new film and then failed to judge it. The workflow (.github/workflows/anvil-execute-content-video-v2.yml on anvil/run-youtube-video-v2) runs the content line twice with the identical command, the same pipeline and the same work order, with no pass flag and no film evidence pack, so the second execution reproduced authoring behavior: the producing stations verified and held, and the reviewers judged the scene scripts again. reviewer-design's counted review states verbatim that it did not view the finished film and deferred each of the four polish advisories to a second pass. reviewer-facts left claim C11 open for the same reason. The run's own publisher and observer recorded the round INCOMPLETE. The formal verdict approved 4 of 4 covers the authoring pass only.

This spec defines the missing execution: one dedicated film review pass over the already rendered film, run on the review only pipeline (pipelines/content-film-review.json, added by the declared evidence wiring order, issue 26), with the film's evidence declared on the work order as evidence_images so the runner puts it in front of reviewer-design as a contact sheet and names each original in its packet.

## The film and its evidence

All paths are committed on the run branch under content/youtube-anvil-v2/, copied byte identical from anvil/run-youtube-video-v2 at 312e606:

- Film: anvil-youtube-v2.mp4, sha256 a277ce32c3ac7c30de5679524f49b1017ff028cfea2d38277deed73c4b44ecac, 21,401,761 bytes.
- Deterministic checks against this film: checks.txt, 19 of 19 PASS (the S7 line reads contact sheet 2560x1800 and 20 sampled stills, which distinguishes this film from the previous round's 2560x1440 and 15 stills).
- Contact sheet: contact-sheet.png (2560x1800, 20 sampled stills).
- Sampled stills: frames/frame-mid-1.png to frame-mid-7.png, frames/frame-cut-*.png transition stills, and frames/frame-proof-s1-title.png.
- Render record: render-stats.json (2,515 of 2,515 frames, 6 tolerated_crash chunk outcomes recorded by the wo-gh-25 wrapper, no failed chunks) and ffprobe.json.
- Production notes: production-notes.md. Previous round's publisher record: publish-record.md (records the INCOMPLETE state this pass closes).
- Frozen text: script.md and storyboard.md. The spoken script is unchanged by a word (checks S3 and S5 pass).

## Requirements

- One dedicated execution. The pass runs once, on pipelines/content-film-review.json, under its own work order (wo-gh-27). No authoring station executes in substance: there is no brief-writer, researcher, writer, media-producer or builder stage in the pipeline.
- Declared evidence. The work order declares as evidence_images the contact sheet plus the twelve named proof stills (three per advisory, listed in the scenarios). reviewer-design's packet carries the contact sheet assembled from the declared images and names each declared original; reviewer-design opens the originals at full resolution for its rulings.
- Per advisory rulings. reviewer-design rules on each of the four polish advisories separately, closed or not closed, and every ruling cites the still or stills that prove it. Its verdict is pass only if all four advisories are closed on the stills. A ruling that defers to scene scripts, to code, or to a future pass does not satisfy this spec: the film is the object under review.
- C11 re-judged. reviewer-facts verifies the film file on disk hashes to a277ce32c3ac7c30de5679524f49b1017ff028cfea2d38277deed73c4b44ecac, confirms checks.txt (19 of 19 PASS) and render-stats.json describe this film and not the previous round's, and rules claim C11 on that evidence.
- Nothing re-rendered, nothing rewritten. No station renders frames, encodes video, or changes any file under content/. The only writes are the run record under runs/wo-gh-27/ and the publisher's record, which the publisher writes into the run directory only.
- The gate holds. The work order carries the publishing risk hint on purpose. The video stays on the owner's hold: the publisher writes its record only, and nothing is posted or uploaded anywhere.

## Scenarios

### Scenario: Section 4 title occlusion advisory
- S4: reviewer-design examines frame-mid-4.png, frame-cut-4-first.png and frame-cut-4-last.png and rules whether the "Stations build" title band sits clear of the full moving envelope of the posts, caps, swing arms and tips in every cited still, with no line geometry crossing its glyphs.

### Scenario: Section 6 caption stacking advisory
- S6: reviewer-design examines frame-mid-6.png, frame-cut-6-last.png and frame-cut-7-first.png and rules whether the "Verified memory." and "A human approves." captions are both fully legible in the midpoint frame and the final wide frame, overlap neither each other nor the archive or gate geometry, and do not read as one stacked block in a single column.

### Scenario: Section 1 opening title advisory
- S1: reviewer-design examines frame-proof-s1-title.png, frame-mid-1.png and frame-cut-1-last.png and rules whether the opening ANVIL title carries the strong treatment from early in the section: full ink color and full or near full scale, matching how the same title reads at the end of the section.

### Scenario: Section 2 card flight advisory
- S2: reviewer-design examines frame-mid-2.png, frame-cut-2-first.png and frame-cut-2-last.png and rules whether the card reads as the subject through its flight, in particular at the midpoint frame, with no dead air failure of the kind the polish amendment targeted.

### Scenario: Claim C11 against this film
- S5: reviewer-facts recomputes the film's sha256, reads checks.txt and render-stats.json, and rules claim C11 against this film and this run record, stating the hash it measured.

### Scenario: The verdict covers the film
- S6: The run's counted reviews, read from their .review.json files, show reviewer-design's findings ruling on the stills (S4, S6, S1, S2) and reviewer-facts ruling on C11 (S5). A verdict whose counted findings judge scene scripts or defer the film does not satisfy this scenario, whatever its formal value.

## Tests

No code changes are made by this order, so there are no new unit tests. The scenarios are checked against the executed run record: runs/wo-gh-27/report.json, the counted .review.json files, and the diff the run commits (which must show no change under content/).


## Diff summary

- runs/wo-gh-27/envelopes/intake.envelope.json: +3, -3

## Evidence

Contact sheet: runs/wo-gh-27/contact-sheet.png

Declared evidence images:
- content/youtube-anvil-v2/contact-sheet.png
- content/youtube-anvil-v2/frames/frame-mid-4.png
- content/youtube-anvil-v2/frames/frame-cut-4-first.png
- content/youtube-anvil-v2/frames/frame-cut-4-last.png
- content/youtube-anvil-v2/frames/frame-mid-6.png
- content/youtube-anvil-v2/frames/frame-cut-6-last.png
- content/youtube-anvil-v2/frames/frame-cut-7-first.png
- content/youtube-anvil-v2/frames/frame-proof-s1-title.png
- content/youtube-anvil-v2/frames/frame-mid-1.png
- content/youtube-anvil-v2/frames/frame-cut-1-last.png
- content/youtube-anvil-v2/frames/frame-mid-2.png
- content/youtube-anvil-v2/frames/frame-cut-2-first.png
- content/youtube-anvil-v2/frames/frame-cut-2-last.png

## File access allowlist

This packet may only embed content from:
- design/DESIGN.md
- design/tokens.json
- .openspec/specs/film-review-pass/spec.md
- runs/wo-gh-27/envelopes/intake.envelope.json
