# Task packet: researcher

## Station prompt

# Researcher

## Role
Gather the source pack for a brief: primary sources for every claim, with links and the exact fact each source supports.

## Inputs
- content brief

## Outputs
- source pack

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
- description: Spec: .openspec/specs/youtube-anvil-video-v2/spec.md (slug youtube-anvil-video-v2), including the gate loopback amendment at the end of the spec, which governs this round. GitHub issue: https://github.com/arananet/anvil-factory/issues/18

Job: gate loopback of wo-gh-18. Round 1 wrote the script and reviewed it, but produced no film: the media-producer rendered inside its model session and the station wrapper killed the session at its timeout with 133 of about 2400 frames done. This round changes only the production architecture, exactly as the owner approved: the media-producer authors and never renders; deterministic workflow steps render every frame and assemble the film outside any model session. The finished video stops at the human gate. Nothing is published anywhere.

Frozen inputs, committed in the loopback setup commit under content/youtube-anvil-v2/ from the round 1 evidence: brief.md, source-pack.md, script.md, storyboard.md and the Blender scripts under blender/. The script and the storyboard are final. The only script changes since round 1 are the two wording edits reviewer-facts asked for, already applied in the setup commit: section 4 no longer says one after another, and section 7 now speaks of the models that staff my stations. No station rewrites, rephrases or reformats script.md or storyboard.md in either pass. Producing stations work from both files exactly as committed.

How this run executes, in order:

1. First pass of the line (authoring). brief-writer and researcher: verify brief.md and source-pack.md against the spec and keep them; correct a file only for a concrete error against the spec, and state what you corrected. writer: verify script.md and storyboard.md against the spec (structure, seven sections, target timings, word count, first person discipline, claim mapping) and keep both byte for byte. media-producer: author the production inputs and nothing else. Run the narration synthesis (blender/narrate.py), the durations measurement (blender/durations.py) and the sound bed generation (blender/soundbed.py), so the audio files and durations.json exist. Verify the Blender scene scripts are complete and consistent with the storyboard, and confirm the render budget in them for the deterministic render: Eevee TAA render samples at the authored 6 or lower and never above 8, shadows and raytracing off, background element resolution as authored; never cut frames, frame rate or motion. Write production-notes.md with the GLB provenance and its sha256, the scene method, the voice and the per section durations, the sound bed method, and the disclosure that the narration is synthetic speech so the YouTube AI generated content label must be set at publish time. Do NOT run any Blender render, any ffmpeg encoding or assembly, or any contact sheet extraction: those are deterministic workflow steps now, and a station session that renders will be killed by the wrapper timeout again. Reviewers in this pass judge the script, the storyboard, the audio inputs and the scene scripts. reviewer-facts verifies the two wording edits and maps every claim, and notes that claim C11 is judged in the second pass once the film exists. reviewer-voice re-checks the final script text end to end. reviewer-brand checks naming as before. reviewer-design judges the storyboard and the scene construction, and states plainly that the finished film is judged in the second pass.

2. Deterministic workflow steps (not stations): narration and durations are regenerated if missing, the sound bed is generated if missing, every frame is rendered by parallel chunked headless Blender 4.5.15, the render statistics are recorded into render-stats.json and into production-notes.md by tools/render_stats.py, ffmpeg assembles anvil-youtube-v2.mp4 with the contact sheet and the sampled stills, and the deterministic checks (tools/video_checks_v2.py) run against the finished piece.

3. Second pass of the line (film review). The line runs again with the finished film in the tree. Producing stations verify and hold: no content file changes in this pass. media-producer confirms the film, the contact sheet, the sampled stills and the production notes match the storyboard and the spec, and completes production-notes.md if anything is missing, preserving the recorded render statistics block exactly. reviewer-facts re-judges claim C11 against the finished film and closes its round 1 findings. reviewer-design judges the finished film through the contact sheet at the section midpoints and the transitions and through the sampled stills: motion continuity, no frozen beats, brand consistency. reviewer-voice and reviewer-brand re-confirm the final text and the naming.

Model routing for this run (owner instruction, unchanged from round 1): the writer station runs claude-opus-5-5. Brief-writer, researcher, media-producer, publisher and the reviewers (facts, voice, brand, design) run claude-sonnet-5-5. Routing is per station through tools/anvil_station.py and tools/claude_station.py; both model routes pass an exact reply smoke gate in the workflow before the line runs, and a Blender smoke gate proves headless Blender 4.5.15 before the line runs.

Voice and claim discipline are in the spec and bind every station. No employer of the author may be named anywhere. No other factory, product, video or person may be named or referenced. The publisher writes its record only: this work order carries the publishing risk hint on purpose, the finished video stops at the human gate, and nothing is posted anywhere.
- risk_hints: publishing
- status: new

## Upstream steps

- intake: completed
- brief-writer: executed
