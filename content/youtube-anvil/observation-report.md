# Observation report: ANVIL YouTube video (wo-gh-17)

Station: observer. Date: 2026-10-31.

## What was released

Nothing was released. No URL exists for this piece.

## What actually happened

The content line executed the full pipeline from intake through publisher for a 60 to 90 second YouTube explainer about ANVIL. The publisher stopped at the human gate and wrote publish-record.md stating that nothing was posted anywhere. This matches the work order's explicit instruction: "the finished video stops at the human gate and nothing is posted anywhere."

The pipeline produced:

- anvil-youtube.mp4: 1920x1080, 80.17 seconds, H.264/AAC, within spec (60-90 second range)
- script.md: 189 words of spoken narration across five sections, within spec (150-200 word range)
- storyboard.md: per-section visual and framing notes
- production-notes.md: full provenance and disclosure for every asset
- Four sample frames extracted at 15%, 40%, 65% and 88% of the total duration
- Audio files for all five sections synthesized with edge-tts (voice en-US-ChristopherNeural)
- brief.md, source-pack.md and review records

## Pipeline results

Upstream stations all executed:

- brief-writer, researcher, writer (Opus 5.5), media-producer: completed their outputs
- Four parallel reviewers ran:
  - reviewer-facts: pass
  - reviewer-voice: pass
  - reviewer-brand: pass
  - reviewer-design: changes_requested
- approver: returned `loopback` due to the design findings
- triage-human: completed (gate ran)
- publisher: executed, wrote publish-record.md, stopped

## Open items recorded in the publish record

The publisher identified these items for the human:

1. **Design findings** (reviewer-design):
   - frame-3 (Proof section): dashboard crop clips the skin temperature chart at bottom and hydration chart at right; battery value wraps to two lines
   - Sampling gap: frames 1 and 2 are both from "The line" section (identical visual); no sample frame shows the Hook or Verified memory sections
   - No project design tokens existed to check against (design/DESIGN.md and design/tokens.json are unfilled templates)

2. **Brand/facts note**: the hook frame shows the Sentia site headline, which is first-party copy outside the closed claim list; a human should confirm this is acceptable

3. **Voice note**: set the YouTube AI-generated content label at upload (synthetic voice and AI-generated diagrams)

4. **Checker note**: tools/video_checks.py counts 237 words against 189 spoken words because it counts timing lines and headings; the narration is within range but the checker behavior is a question for the operator

## Technical conformance

The piece meets all deterministic spec requirements:

- S1: video is 1920x1080 with one video stream and one audio stream ✓
- S2: duration is 80.17 seconds, within 60-90 second range ✓
- S3: narration is 189 words, within 150-200 word range ✓
- S4: no forbidden strings found in the script files ✓
- S5: all visuals named in storyboard exist as assets ✓
- S6: four sample frames exist at 1920x1080 ✓

The reviewer findings (S7 facts, S8 design) were executed; facts passed, design requested changes.

## What happens next

Per the publish record: "To publish: fix the design findings (the writer or media-producer re-runs), get a new design pass and approver result, then a human gives explicit approval. After that the publisher can record the live URL here."

The piece remains unpublished until:
1. Design findings are addressed
2. reviewer-design re-runs and passes
3. A human explicitly approves publication

## Observation

The work order behaved exactly as specified. The risk hint `publishing` triggered the required human gate, the approver's loopback result prevented automatic publication, and the publisher stopped with the piece prepared for human review. The content line executed deterministically through all stations and left a complete audit trail. Nothing was posted anywhere.
