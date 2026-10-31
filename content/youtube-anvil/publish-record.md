# Publish record: ANVIL YouTube video (wo-gh-17)

Station: publisher (claude-sonnet-5-5). Result: NOT PUBLISHED. Nothing was posted anywhere.

## Where it went live

Nowhere. No URL exists for this piece.

## Why the publisher stopped

1. The human gate is required. The work order carries the risk hint `publishing`, and the gate rules map that hint to "required". The station rules say a required gate means stop and prepare the piece for the human.
2. The approver result is `loopback`, not approved. Four reviewers ran; three passed (facts, voice, brand). reviewer-design returned `changes_requested`. The gate envelope for triage-human shows `completed`, which records that triage ran. It does not record a human approving publication, and no such result is in the inputs.

## Open items for the human

- reviewer-design, frame-3 (Proof): the dashboard crop clips the skin temperature chart at the bottom edge and the hydration index chart at the right edge. The battery value wraps to two lines.
- reviewer-design, sampling: frame-1 and frame-2 are identical (both from "The line"). No sample frame shows the Hook or the Verified memory section.
- reviewer-design note: design/DESIGN.md and design/tokens.json are unfilled templates, so there were no project tokens to check against.
- reviewer-brand and reviewer-facts: the hook frame shows the Sentia site headline, which is first party copy outside the closed claim list. A human should confirm it is acceptable.
- reviewer-voice: set the YouTube AI-generated content label at upload. The voice is synthetic edge-tts and the diagrams are AI generated.
- Checker note: tools/video_checks.py counts 237 words against 189 spoken, because it counts timing lines and headings. The script file has 240 words in total, and the 189 narration words are within the 150 to 200 range. The checker question stays with the operator.

## Prepared for the human

Files under content/youtube-anvil/: anvil-youtube.mp4, script.md, storyboard.md, brief.md, source-pack.md, production-notes.md, review-brand.md, frames/, audio/.

To publish: fix the design findings (the writer or media-producer re-runs), get a new design pass and approver result, then a human gives explicit approval. After that the publisher can record the live URL here.
