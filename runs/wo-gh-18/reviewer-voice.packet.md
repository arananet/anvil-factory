# Task packet: reviewer-voice

## Station prompt

# Voice Reviewer

## Role
Check the draft sounds like the author: natural grammar, no filler cadence, the house rules in the brain, and the AI generated disclosure present when the piece or its media is AI generated.

## Inputs
- draft
- brain

## Outputs
- review

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.


## Work order

- id: wo-gh-18
- kind: content
- title: ANVIL the video v2: a dynamic Blender rendered launch film produced by the content line
- source: github-issue
- description: Spec: .openspec/specs/youtube-anvil-video-v2/spec.md (slug youtube-anvil-video-v2), approved and written before this run. GitHub issue: https://github.com/arananet/anvil-factory/issues/18

Job: produce a 60 to 90 second YouTube launch film about ANVIL through the content line, rendered as a real animated 3D sequence in headless Blender, and stop at the human gate. Nothing is published anywhere. This is the second attempt: the first video (issue 17) was rejected by the owner because it was a narrated slideshow in third person. Both failures are fixed at the root here: real Blender animation, first person voice.

Pipeline: pipelines/content-video.json, the content variant whose parallel review panel is reviewer-facts, reviewer-voice, reviewer-brand and reviewer-design.

Model routing for this run (owner instruction, 2026-10-31): the writer station runs claude-opus-5-5 and is the scriptwriter for this piece. The reviewers (facts, voice, brand, design) run claude-sonnet-5-5. Brief-writer, researcher, media-producer and publisher run claude-sonnet-5-5. Routing is per station through tools/anvil_station.py and tools/claude_station.py; both model routes pass an exact reply smoke gate in the workflow before the line runs, and a Blender smoke gate proves headless Blender 4.5.15 before the line runs.

File contract, all under content/youtube-anvil-v2/:

- The brief-writer writes brief.md from this description and the spec.
- The researcher writes source-pack.md: the spec's closed claim list, each claim with its source (a repository file or the live Sentia site), plus the provenance of the committed GLB asset exactly as the spec records it. No claim outside the spec's list may enter the pack.
- The writer writes script.md with this exact structure: a title line, then a ## Narration section holding seven ### blocks, one per spec section in order, each block stating a Target timing line in M:SS form and then the spoken narration text for that section (150 to 200 words of narration in total across the seven blocks), and storyboard.md (per section: the camera move, the action, the on screen text exactly as the spec states it, and the framing note). The narration speaks as ANVIL in first person from its first words, which are exactly: Introducing ANVIL. The writer works from the brief, the source pack and the spec only.
- The media-producer executes the production contract in the spec: per section narration with edge-tts (voice en-US-ChristopherNeural); Blender Python scene scripts under blender/ that build the film procedurally and deterministically; per section Eevee renders at 1920x1080 and 30 fps into frames/s<N>/ PNG sequences (parallel sections and resumable frames as the spec allows); a procedural sound bed generated with Python standard library only; ffmpeg assembly to anvil-youtube-v2.mp4; the contact sheet and sampled stills under frames/; and production-notes.md recording the GLB provenance and hash, the render statistics (Blender version, total frames, render wall time), the voice, the per section durations and the sound bed method. The only committed visual asset is assets/patch-one.glb, the factory's own Sentia product model; everything else visual is built by the Blender scripts inside the run.
- The reviewers judge what exists at their step: reviewer-facts checks the script and every on screen text against the closed claim list only; reviewer-voice checks the first person launch voice end to end and the owner's voice rules (natural grammar, no stacked fragments, no hype words, no em or en dashes); reviewer-brand checks naming and the forbidden names; reviewer-design judges the contact sheet and the sampled frames for motion continuity at section midpoints and transitions, the absence of frozen beats, composition and brand consistency.
- The publisher writes its record only. This work order carries the publishing risk hint on purpose: the finished video stops at the human gate and nothing is posted anywhere.

Voice and claim discipline are in the spec and bind every station. No employer of the author may be named anywhere. No other factory, product, video or person may be named or referenced.
- risk_hints: publishing
- status: new

## Upstream steps

- intake: completed
- brief-writer: executed
- researcher: executed
- writer: executed
- media-producer: failed
- reviewer-facts: executed
