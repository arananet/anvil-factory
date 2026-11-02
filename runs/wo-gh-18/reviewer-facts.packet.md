# Task packet: reviewer-facts

## Station prompt

# Facts Reviewer

## Role
Check every claim in the draft against the source pack. A claim with no source is a finding, not a detail.

## Inputs
- draft
- source pack

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
- description: Spec: .openspec/specs/youtube-anvil-video-v2/spec.md (slug youtube-anvil-video-v2), including the gate loopback amendment (production re-architecture) and, at the end of the spec, the polish loopback amendment, which governs this round. GitHub issue: https://github.com/arananet/anvil-factory/issues/18

Job: polish loopback of wo-gh-18. The previous round produced the film and the line approved it; reviewer-design passed the film and left four advisories for the human gate, the publisher record carried them to the gate, and the owner ordered all four fixed. This round changes only scene and layout: on screen text placement, sizes and timing, and section 2's flight and camera choreography. The spoken script does not change by a single word.

Frozen inputs, committed on this branch and entering this round unchanged: brief.md, source-pack.md, script.md, storyboard.md, the narration audio under audio/, durations.json and assets/patch-one.glb. No station rewrites, rephrases or reformats script.md or storyboard.md in either pass; both are verified byte for byte against the previous round. Claim C11 is re-judged against the new film in the film review pass.

How this run executes, in order:

1. First pass of the line (authoring). brief-writer and researcher: verify brief.md and source-pack.md against the spec and keep them; correct a file only for a concrete error against the spec, and state what you corrected. writer: verify script.md and storyboard.md are byte identical to the previous round and keep both byte for byte. media-producer: author the scene fixes and nothing else. Work in the Blender scripts under content/youtube-anvil-v2/blender/ (scene_line.py for sections 1, 2, 4 and 6) and in the sheet sampling in blender/assemble.py, exactly as the polish amendment specifies: (1) section 4: place the "Stations build" title band clear of the full moving envelope of the posts, caps, swing arms and tips, so no sampled frame shows line geometry crossing its glyphs; (2) section 6: reposition the "Verified memory." and "A human approves." captions (placement, size or the second caption's timing) so that in the midpoint frame and the final wide frame both are fully legible, overlap neither each other nor the archive or gate geometry, and do not read as one stacked block in a single column; (3) section 1: give the opening "ANVIL" title the strong treatment from the first part of the section, full ink color and full or near full scale reached early, matching how the same title reads at the end of the section, while the dolly in and the line assembly keep their motion; (4) section 2: tighten the card's flight rotation profile and the camera path and target so the card reads as the subject through the whole flight, in particular at the midpoint, and audit the other sections' sampled frames for the same dead air failure. Extend the sheet sampling in assemble.py as the amendment specifies: every existing still name kept, the transition pairs completed for the cuts after sections 1 to 6, and one early title proof still from section 1 at about 30 percent of the section, named frame-proof-s1-title.png. Verify the narration audio files and durations.json stand unchanged; do not re-synthesize the narration (the deterministic workflow step regenerates anything missing). Confirm the render budget in the scene scripts is unchanged: Eevee TAA render samples at the authored 6 and never above 8, shadows and raytracing off; never cut frames, frame rate or motion. Record the four fixes and their scene locations in production-notes.md, preserving the recorded render statistics block exactly (the workflow's statistics step rewrites that block after the render). Do NOT run any Blender render, any ffmpeg encoding or assembly, or any contact sheet extraction: those are deterministic workflow steps, and a station session that renders will be killed by the wrapper timeout again. Reviewers in this pass judge the scene scripts against the four advisories and the frozen inputs. reviewer-design states plainly that the finished film is judged in the second pass.

2. Deterministic workflow steps (not stations): narration and durations are regenerated if missing, the sound bed is generated if missing, every frame is rendered by parallel chunked headless Blender 4.5.15, the render statistics are recorded into render-stats.json and into production-notes.md by tools/render_stats.py, blender/assemble.py assembles anvil-youtube-v2.mp4 with the contact sheet and the sampled stills, and the deterministic checks (tools/video_checks_v2.py) run against the finished piece.

3. Second pass of the line (film review). The line runs again with the finished film in the tree. Producing stations verify and hold: no content file changes in this pass. media-producer confirms the film, the contact sheet, the sampled stills and the production notes match the storyboard and the spec, and completes production-notes.md if anything is missing, preserving the recorded render statistics block exactly. reviewer-design judges the finished film through the new contact sheet and the sampled stills and rules on each of the four polish advisories separately, closed or not, citing the still or stills that prove each ruling; its pass requires all four closed. reviewer-facts re-verifies claim C11 against the new film in the tree and confirms the render statistics and the checks describe that film. reviewer-voice and reviewer-brand re-confirm the frozen final text and the naming.

Model routing for this run (owner instruction, unchanged): the writer station runs claude-opus-5-5. Brief-writer, researcher, media-producer, publisher and the reviewers (facts, voice, brand, design) run claude-sonnet-5-5. Routing is per station through tools/anvil_station.py and tools/claude_station.py; both model routes pass an exact reply smoke gate in the workflow before the line runs, and a Blender smoke gate proves headless Blender 4.5.15 before the line runs.

Voice and claim discipline are in the spec and bind every station. No employer of the author may be named anywhere. No other factory, product, video or person may be named or referenced. The publisher writes its record only: this work order carries the publishing risk hint on purpose, the finished video stops at the human gate, and nothing is posted anywhere.
- risk_hints: publishing
- status: new

## Upstream steps

- intake: completed
- brief-writer: executed
- researcher: executed
- writer: failed
- media-producer: failed
