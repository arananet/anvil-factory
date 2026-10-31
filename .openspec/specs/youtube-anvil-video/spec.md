# YouTube video: ANVIL, the software factory

## Purpose

Produce one short YouTube explainer about ANVIL through the factory's own content line, as a test of the content domain. The piece stops at the human gate. Nothing is published by this work order.

## The piece

- One MP4 at content/youtube-anvil/anvil-youtube.mp4, 1920x1080 (16:9), H.264 video with an AAC audio stream.
- Total duration between 60 and 90 seconds.
- English narration, one clean text to speech voice, no music bed required.
- Narration length between 150 and 200 words, written to be spoken.

## Structure

Five sections, in this order. The script states a target timing per section and the storyboard states the visual and any on screen text per section.

1. Hook. Visual: assets/sentia-page-hero.png, a real frame of the live Sentia site. On screen text: none.
2. The line. Visual: assets/diagram-line.png. On screen text: "One intake. One line."
3. Verified memory. Visual: assets/diagram-memory.png. On screen text: "Verified memory."
4. Proof. Visual: assets/sentia-dashboard.png, a real frame of the live Sentia dashboard. On screen text: "Designed and built end to end by ANVIL."
5. Close. Visual: a title card the media-producer renders over a dark ink background. On screen text: "ANVIL" and "An open source software factory." and "github.com/arananet/anvil-factory".

## Claim list (closed)

The script may only assert claims from this list. Each is true today and traceable to the factory repository or the live Sentia site.

- ANVIL is a software factory: work enters as an intake and leaves as reviewed, approved output.
- The intake is one of three things: a feature, an idea, or an issue.
- The spec is written before any code.
- Specialized stations do the work in a line; no station approves its own work.
- Five reviewers check the work in parallel: spec, security, tests, architecture, and design.
- A human approves before anything ships. The publisher does not run past the human gate.
- The factory keeps a verified memory: a learning enters the memory only with provenance tied to a run record, and proposals that cannot be verified wait in quarantine.
- The models that staff the stations are routed per station through Cloudflare AI Gateway. The work lives on GitHub.
- ANVIL is open source under the Apache 2.0 license.
- Sentia, a concept sensor patch product, is the first product ANVIL designed and built end to end. It is live at sentia.info-693.workers.dev.
- This video was itself produced by ANVIL's content line: written, produced and reviewed by its stations, and stopped at the human gate.

No other factual claim may appear, spoken or on screen. In particular: no employer of the author may be named, no other factory, product, video or person may be named or referenced, and no counts beyond the ones in this list (three intake kinds, five reviewers) may be stated.

## Voice rules

- Natural human grammar. Full sentences a person would say out loud.
- No stacked fragments, no slogans in a row, no hype words (no revolutionary, game changing, cutting edge, supercharge, unleash, or similar).
- No em dashes and no en dashes anywhere in the script, the storyboard, or on screen text.
- Plain confidence: state what the factory does, not what it promises to become.

## Assets

Committed in the setup commit as run inputs under content/youtube-anvil/assets/:

- sentia-page-hero.png and sentia-dashboard.png: frames of the live Sentia site (the deployed production tree), first party material.
- sentia-product.png: the live Sentia hero product image, fetched from the live site.
- diagram-line.png and diagram-memory.png: diagrams generated for this piece with a text capable image model; every label was verified by reading the generated image back before it was committed.

No stock material and nothing downloaded from third parties may be used. The media-producer may crop or scale the committed assets and may render title cards and section titles from text; it may not substitute other imagery.

## Production contract (media-producer station)

Working from content/youtube-anvil/script.md and content/youtube-anvil/storyboard.md as executed in this same run, and the committed assets:

1. Synthesize the narration per section with edge-tts (install with pip if needed), voice en-US-ChristopherNeural, one file per section. If that voice service is unreachable, record the failure in production-notes.md and stop; do not substitute a robotic local voice.
2. Measure each section's narration with ffprobe and time each section's visual to its narration plus a short pad. The total must land between 60 and 90 seconds; adjust the speech rate once if needed and record what was done.
3. Assemble content/youtube-anvil/anvil-youtube.mp4 with ffmpeg: every visual scaled and padded to 1920x1080, 30 fps, the section's on screen text burned in as a title at the section start, narration concatenated in section order.
4. Extract four sample frames at roughly 15, 40, 65 and 88 percent of the total duration into content/youtube-anvil/frames/frame-1.png through frame-4.png.
5. Write content/youtube-anvil/production-notes.md recording how each asset was made (including the operator supplied assets and their provenance), the voice used, the per section durations, the total duration, and every command class used. Disclosure is a fact from this file, not a guess.

## Checks (scenarios)

- S1: ffprobe of the final MP4 reports width 1920, height 1080, one video stream and one audio stream.
- S2: ffprobe duration is between 60 and 90 seconds.
- S3: the narration word count in script.md is between 150 and 200 words, and script.md carries a target timing per section.
- S4: script.md, storyboard.md and production-notes.md contain no forbidden strings: no employer name, no em dash or en dash character.
- S5: every visual named in storyboard.md exists as a file under content/youtube-anvil/assets/, and the close card is rendered from text as specified.
- S6: at least four sample frames exist under content/youtube-anvil/frames/ and each is 1920x1080.
- S7: the reviewers judge the executed script against the closed claim list; any claim outside the list is a facts failure.
- S8: reviewer-design judges the sample frames for composition, legibility of burned in titles, and consistency with the piece's own frames (paper background, ink green, teal and coral palette of the committed assets).

The deterministic part of these checks (S1 to S6) is implemented in tools/video_checks.py and run by the workflow after the line; its output is committed at content/youtube-anvil/checks.txt.
