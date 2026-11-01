# Observation report: wo-gh-18

## Release status

Not released. The publisher correctly blocked publication.

## What was released

Nothing. No video was published to YouTube or any other platform. The work stopped at the media-producer failure and never reached the human gate with an approvable artifact.

## What exists

### Completed artifacts
- `brief.md`: content brief (8.7 KB)
- `source-pack.md`: closed claim list with sources and GLB provenance (12.1 KB)
- `script.md`: seven section narration script, 189 words, first person voice opening with "Introducing ANVIL" (4.0 KB)
- `storyboard.md`: seven section visual direction with camera moves, action, on screen text and framing notes (6.2 KB)
- `audio/s1.mp3` through `audio/s7.mp3`: narration audio for all seven sections, voice en-US-ChristopherNeural
- `audio/bed.wav`: procedural sound bed
- `blender/`: Blender Python scene scripts (film.py, scene_line.py, scene_proof.py, common.py, assemble.py, narrate.py, soundbed.py, durations.py, render_all.sh)
- `durations.json`: measured section durations
- `assets/patch-one.glb`: committed Sentia product model

### Partial artifacts
- `frames/s1/`: 163 PNG frames from section 1 render at 1920x1080, 30 fps
- `frames/logs/`: four render logs for section 1 (render-s1-1.log, render-s1-61.log, render-s1-121.log, render-s1-181.log)

### Review outputs
- `reviews/reviewer-facts.md`: changes_requested. C11 claim unverifiable (no finished video exists), section 4 "one after another" goes slightly past claim list.
- `reviews/reviewer-voice.md`: pass on script voice. Open item: synthetic speech disclosure must go in production-notes.md when media-producer reruns.
- `reviews/reviewer-brand.md`: pass draft scope (script, storyboard, brief, source-pack, on screen text strings in Blender scripts). Final video and disclosure not reviewed.
- Design review output exists at `runs/wo-gh-18/reviewer-design.output.md` but not in `content/youtube-anvil-v2/reviews/`. Verdict: changes_requested. Artifacts missing, only section 1 frames exist, motion continuity unjudgeable.

## What does not exist

- `anvil-youtube-v2.mp4`: the assembled final video
- `production-notes.md`: render statistics, GLB hash, voice, durations, sound bed method, AI generated disclosure
- `frames/s2/` through `frames/s7/`: rendered frames for sections 2 through 7
- Contact sheet under `frames/`
- Sampled stills at section midpoints and transitions under `frames/`
- `runs/wo-gh-18/report.json`: approver output
- Human gate approval record
- `content/youtube-anvil-v2/reviews/reviewer-design.md`: design review in expected location

## Why publishing was blocked (all correct)

1. **Media-producer failed.** Only section 1 rendered (163 of approximately 181+ frames). Sections 2 through 7 have no frames. No MP4 was assembled. No production-notes.md was written.
2. **No approved draft.** The approver result was "loopback" not "pass", and `report.json` does not exist.
3. **No human gate approval.** The triage-human step is marked "completed" in the packet but no gate result file exists and no approval is recorded. A completed triage is not an approval.
4. **Open review findings.**
   - reviewer-facts: changes_requested. C11 ("My content line wrote, rendered and reviewed this video, and it stopped at the human gate") has no backing artifact. The video does not exist and no gate record exists. Section 4 "one after another" needs rewording to "work down the line".
   - reviewer-voice: pass with open item. AI generated speech disclosure must be written into production-notes.md when the media-producer reruns.
   - reviewer-brand: pass draft scope only. The final video and the disclosure were not reviewed.
   - reviewer-design: changes_requested. All visual artifacts except section 1 frames are missing. Motion continuity at midpoints and transitions cannot be judged. The finished MP4, contact sheet and sampled stills do not exist.
5. **Risk hint.** The work order carries the publishing risk hint. The spec states the video stops at the human gate and nothing is posted anywhere.
6. **Write tool disabled.** The publisher could not write its record file because the Write tool was disabled in its session. It correctly chose not to work around this with shell redirection since the block appeared deliberate.

## What needs to happen for release

1. Repair and rerun media-producer to:
   - Complete section 1 render (currently 163 frames, logs imply 181+)
   - Render sections 2 through 7
   - Assemble all sections into `anvil-youtube-v2.mp4`
   - Generate contact sheet and sampled stills (section midpoints and transitions)
   - Write `production-notes.md` with GLB hash, render statistics, voice, durations, sound bed method, and AI generated content disclosure
2. Rerun reviewer-design with the complete visual artifacts
3. Rerun reviewer-facts to verify C11 against the finished video and check rendered on screen text
4. Rerun reviewer-brand to check the final MP4 and the disclosure
5. Approver pass that writes `runs/wo-gh-18/report.json`
6. Explicit human gate approval that clears publishing

## Observed outcome

The factory's content line correctly halted production when the media-producer step failed. The publisher correctly refused to publish without an approved artifact, a human gate clearance, and with open review findings. The video was never released. No external publication occurred. The work remains at the factory boundary.

The first person voice and the Blender rendering approach address the two failures from the first video (issue 17), but the production execution did not complete.
