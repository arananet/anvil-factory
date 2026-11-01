# Observation report: ANVIL the video v2 (wo-gh-18, gate loopback)

**Observation date: 2026-11-01**  
**Work order: wo-gh-18**  
**Change: gate loopback round, production re-architecture**

## What was released

**Nothing was published anywhere.** No video was uploaded, no URL exists, and no external service was contacted.

The publisher correctly stopped at the human gate and did not publish. This matches the work order's explicit instruction: "the finished video stops at the human gate, and nothing is posted anywhere."

## Why the publisher stopped

The publisher gave three reasons for stopping (from publish-record.md):

1. **Publishing risk hint**: The work order carries the `publishing` risk hint, making the human gate required. No explicit human approval for publishing was found in the inputs.

2. **Finished film does not exist**: No `anvil-youtube-v2.mp4`, contact sheet, sampled stills, or `render-stats.json` exist in the tree. Only the first (authoring) pass completed.

3. **Missing report artifact**: The `runs/wo-gh-18/report.json` file referenced by the approver and triage envelopes is not present.

All three reasons are valid. The publisher followed the rules.

## What exists after this run

### Completed (first pass outputs)
- Audio files: `audio/s1.mp3` through `s7.mp3` (narration), `audio/bed.wav` (sound bed)
- `durations.json`: measured section timings, 2515 frames total, 83.833 seconds
- `production-notes.md`: authoring pass record with asset provenance, scene method, render budget, voice details, and disclosure
- `review-facts.md`: reviewer-facts findings, both wording edits verified, claims C1-C10 mapped, C11 deferred to second pass
- `publish-record.md`: publisher's record of stopping at the gate
- Frozen inputs from round 1 (committed in f6476d6): `brief.md`, `source-pack.md`, `script.md`, `storyboard.md`, Blender scripts under `blender/`

### Not completed (deterministic workflow steps and second pass)
- No rendered frames
- No `anvil-youtube-v2.mp4` film
- No `render-stats.json`
- No contact sheet or sampled stills
- No second pass reviewer results (film review)
- No final approver decision after film review

## Architecture change verification

The production re-architecture goal was achieved: the media-producer authored inputs only and did not render. Per `production-notes.md`:

> "This is the authoring pass record. The media-producer authored the production inputs only. Frames, encoding, the contact sheet and the sampled stills are made by deterministic workflow steps outside any model session."

The session timeout problem from round 1 (133 of ~2400 frames before timeout) cannot recur because no station session renders frames anymore.

## Observations on compliance

1. **Voice and claim discipline**: The publisher noted that no employer, other factory, product, video, or person was named. The script uses first person throughout. Reviewer-facts verified all claims.

2. **Frozen inputs**: The script and storyboard were kept byte for byte as committed. The only changes from round 1 were the two approved wording edits (section 4: removed "one after another"; section 7: "models that staff my stations").

3. **Risk hint respected**: The `publishing` risk hint correctly triggered the human gate requirement. The publisher did not bypass it.

4. **Disclosure ready**: Production notes state the narration is synthetic speech, requiring the YouTube AI-generated content label at publish time.

## State for next steps

The work is staged at the human gate. Per the publisher's next steps:

1. Run the deterministic render, assembly, and `tools/video_checks_v2.py` workflow steps
2. Run the second pass (film review) with finished film present
3. Wait for explicit human approval at the gate
4. After approval, the publisher can record the live URL

## Observed outcome

The change did what it was designed to do: separate authoring from rendering so that model sessions never time out on render work. The first pass completed successfully. The publisher correctly stopped before publishing, exactly as the work order specified.

**Status: HELD AT HUMAN GATE, NOTHING PUBLISHED**
