# Task packet: media-producer

## Station prompt

# Media Producer

## Role
Produce the media the piece needs (images, audio or video) and record how each asset was made, so disclosure is a fact, not a guess.

## Inputs
- draft
- content brief

## Outputs
- media assets

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.


## Work order

- id: wo-gh-17
- kind: content
- title: ANVIL the video: a 60 to 90 second YouTube explainer produced by the content line
- source: github-issue
- description: Spec: .openspec/specs/youtube-anvil-video/spec.md (slug youtube-anvil-video), approved and written before this run. GitHub issue: https://github.com/arananet/anvil-factory/issues/17

Job: produce a 60 to 90 second YouTube explainer about ANVIL through the content line, and stop at the human gate. Nothing is published anywhere.

Pipeline: pipelines/content-video.json, a variant of content-default whose parallel review panel is reviewer-facts, reviewer-voice, reviewer-brand and reviewer-design.

Model routing for this run (owner instruction, 2026-10-31): the writer station runs claude-opus-5-5 and is the scriptwriter for this piece. The reviewers (facts, voice, brand, design) run claude-sonnet-5-5. Brief-writer, researcher, media-producer and publisher run claude-sonnet-5-5. Routing is per station through tools/anvil_station.py and tools/claude_station.py; both model routes pass an exact reply smoke gate in the workflow before the line runs.

File contract, all under content/youtube-anvil/:

- The brief-writer writes brief.md from this description and the spec.
- The researcher writes source-pack.md: the spec's closed claim list, each claim with its source (a repository file or the live Sentia site). No claim outside the spec's list may enter the pack.
- The writer writes script.md with this exact structure: a title line, then a ## Narration section holding five ### blocks, one per spec section in order, each block stating a Target timing line in M:SS form and then the spoken narration text for that section (150 to 200 words of narration in total across the five blocks), and storyboard.md (per section: the visual file, the on screen text exactly as the spec states it, and the framing note). The writer works from the brief, the source pack and the spec only.
- The media-producer executes the production contract in the spec: per section narration with edge-tts (voice en-US-ChristopherNeural), ffmpeg assembly to anvil-youtube.mp4 at 1920x1080 with the section titles burned in, four sample frames into frames/, and production-notes.md recording how every asset was made. The visual assets are already committed under assets/ by the operator (two diagrams generated for this piece with labels verified, and frames of the live Sentia site); the media-producer uses those and no others.
- The reviewers judge what exists at their step: reviewer-facts checks the script against the closed claim list only; reviewer-voice checks the owner's voice rules (natural grammar, no stacked fragments, no hype words, no em or en dashes); reviewer-brand checks naming and the forbidden names; reviewer-design judges the sample frames and the storyboard visuals for composition, legibility and palette consistency.
- The publisher writes its record only. This work order carries the publishing risk hint on purpose: the finished video stops at the human gate and nothing is posted anywhere.

Voice and claim discipline are in the spec and bind every station. No employer of the author may be named anywhere. No other factory, product, video or person may be named or referenced.
- risk_hints: publishing
- status: new

## Upstream steps

- intake: completed
- brief-writer: executed
- researcher: executed
- writer: executed

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

