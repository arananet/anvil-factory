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
- Your verdict must be one of: `approved`, `changes_requested`, or `comment`.
- Produce the output as a JSON object, not as chat text.

## Output Format

Return a JSON object with this structure:

```json
{
  "station": "reviewer-design",
  "verdict": "approved | changes_requested | comment",
  "findings": [
    "Specific finding with reference to design system rule or quality bar",
    "Another finding if applicable"
  ]
}
```

## Examples

### Example 1: No design system exists
```json
{
  "station": "reviewer-design",
  "verdict": "changes_requested",
  "findings": [
    "No design system exists for this project. The project must define design/DESIGN.md and design/tokens.json before interface output can be reviewed against design standards."
  ]
}
```

### Example 2: Interface violates quality bar
```json
{
  "station": "reviewer-design",
  "verdict": "changes_requested",
  "findings": [
    "Quality bar violation: Scale Contrast - The button text has only 2.8:1 contrast ratio against its background, failing the minimum 4.5:1 requirement stated in the quality bars.",
    "Token usage: The page uses hardcoded color '#FF5733' instead of the defined primary color token."
  ]
}
```

### Example 3: Interface meets design system
```json
{
  "station": "reviewer-design",
  "verdict": "approved",
  "findings": []
}
```


## Work order

- id: wo-gh-5
- kind: content
- title: Final pass on the ANVIL LinkedIn article: history section, Sentia closing, voice fixes, reviewer count, promo
- source: github-issue
- description: Spec: .openspec/specs/linkedin-article-final-pass/spec.md (slug linkedin-article-final-pass), approved and written before this run. GitHub issue: https://github.com/arananet/anvil-factory/issues/5

Job: the final pass on the ANVIL LinkedIn article. The input article is the revision produced by work order wo-gh-4, committed at content/linkedin-article/article.md in this checkout. Every station that needs it reads that file in full from the working tree. The writer station outputs the complete revised article as its output: full text, not a diff, not a summary, not an outline. The promo text ships at content/linkedin-article/promo-post.txt.

The brief-writer turns this description into the content brief. The researcher turns the facts below into the source pack. Nothing beyond these changes and the input article is invented.

The five changes, all facts verified:

1. INSERT a short history section titled "Not a new idea" between the intro and "The line". Use this text, supplied and approved by Edu, integrated verbatim or with only connective edits:

"The software factory is not a new idea. Back in 1968, Bob Bemer was already proposing one as the way to make programmers more productive: standardized tools, shared data, and management controls around the work. A year later Hitachi opened what is usually counted as the first software factory, an entire software organization run like a plant, set up to produce high quality software in quantity. In the 2000s the factory turned into an assembly kit, applications composed from reusable patterns, models and frameworks. In the 2010s and 2020s it became a delivery pipeline, people and process wrapped around continuous delivery, automated tests and security checks. The pattern is almost sixty years old. What changed is who, or what, works the line."

2. UPDATE the Sentia closing to the final state. The wo-gh-4 text ends the Sentia exam with round 4 stopped at the human gate and nothing deployed; that ending is stale and is replaced from the gate onward. The final state: round 4 of work order wo-gh-1 on arananet/sentia ended changes_requested, human required. Edu, the human at the gate, overrode his own gate and deployed that build himself, in his words at the gate: deploy it as is, accepting the minor deviations. Seeing it live, he then rejected the flat SVG art direction on sight: his verdict was that the design was ugly and that he expected isometric and 3D imagery. He ordered design v2 as a new work order, wo-gh-2 on arananet/sentia. V2 generated four product renders with Magnific (a hero render, an exploded view, an on-skin render and a network scene), each verified one by one; their shared caveat is that the patch rims read sage and mint rather than the brand's deep ink green. DESIGN.md was revised to put imagery first, and the page was recomposed around the renders, presentation layer only. Verdict: approved, with all 5 reviews counted and all passing, reviewer-design included. The suite recorded 56 pass, 0 fail, 1 skipped. Edu gave the gate word, and v2 is live at https://sentia.info-693.workers.dev, deployed 2026-10-29. The Sentia section ends with this closing sentence, word for word: "The design gate's first full pass came when the design system's ambition matched the product, not when the builder tried harder."

3. FIX reviewer-voice's four findings from the wo-gh-4 run. (a) The round 3 paragraph in the Sentia section ends with a sentence fragment, "A fourth round with those findings as acceptance criteria." Make it complete prose. (b) That same paragraph compresses its facts into two very long sentences; decompress them into readable prose without dropping facts. (c) The line "Suite: 38 pass, 0 fail, 1 skipped." in that paragraph reads as test output; rewrite it as prose. (d) In the Model routing section, "responses calls" is corrected to "response calls".

4. FIX the reviewer count in "The line" section. The SDLC reviewer group is five, not four: spec, security, tests, architecture, design. Update the reviewer walkthrough sentence ("Then four reviewers look at the result in parallel...") to five reviewers with the design reviewer's job stated (it checks the work against the project design system), and update the approver sentence ("An approver aggregates the four reviews into a single verdict.") to five reviews. Historical records elsewhere in the article (the Taskline example's four reviews, the design run's 2 of 4, the example run's 1 of 2) are facts of those runs and do not change.

5. PROMO: in content/linkedin-article/promo-post.txt, the claim "four reviewers in parallel" becomes "five reviewers in parallel". No other promo line changes unless a claim is now false; if another claim reads stale against the revised article, flag it in the run record instead of rewriting it.

Presentation rules for the writer:
- Preserve the input article's structure, section order and first person voice, with the single insertion in change 1. Image markers stay exactly where they are.
- No em dash characters and no en dash characters anywhere. Never mention the author's employer. The title, the credit section and the signature sign-off stay byte identical to the input article, including the final line: That's where I stand today. I reserve the right to change my mind tomorrow. In AI, that's not flip-flopping, it's keeping up.
- Publishing hold: the output is a draft for the author's review. The article must not state or imply that it, or anything else in this run, has been published.
- risk_hints: publishing
- status: new

## Upstream steps

- intake: completed
- brief-writer: executed
- researcher: executed
- writer: executed
- media-producer: executed
- reviewer-facts: executed
- reviewer-voice: executed
- reviewer-platform: failed
- reviewer-brand: executed

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

