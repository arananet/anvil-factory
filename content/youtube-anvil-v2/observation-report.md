# Observation report: ANVIL the video v2 (wo-gh-18, gate loopback)

**Observation date: 2026-11-01**  
**Work order: wo-gh-18**  
**Change: gate loopback round, production re-architecture**  
**Pass: Second pass (film review) completed**

## What was released

**Nothing was published anywhere.** No video was uploaded, no URL exists, and no external service was contacted.

The publisher correctly stopped at the human gate and did not publish. This matches the work order's explicit instruction: "the finished video stops at the human gate, and nothing is posted anywhere."

## Why the publisher stopped

The publisher stopped because the human gate is required (from publish-record.md):

1. **Publishing risk hint**: The work order carries the `publishing` risk hint. The approver verdict is `approved` and all four reviews passed, but `report.json` records `human_required: true`.

2. **Human gate rule**: "Verdict approved, but the work order carries the risk hint 'publishing', so a human is required."

3. **No human approval recorded**: The `triage-human` step shows "completed" with detail "Human review: required". That is routing logic, not an actual human approval. No explicit human approval was found.

The publisher correctly interpreted the human gate requirement and did not publish. All three reasons are valid. The publisher followed the rules.

## What exists after this run

### Completed (both passes)

**Finished video**:
- `anvil-youtube-v2.mp4`: 21MB, 1920x1080, 30fps, h264+aac, 83.83s
- sha256: `62a3137df17fb512331e0cff3ed85fae0597cafa0530bd03cdcd0052f512ff22`

**Supporting evidence**:
- `contact-sheet.png`: 2560x1440, grid visualization at section midpoints and transitions
- 15 sampled stills (still-*.png)
- `render-stats.json`: 2515 frames rendered, Blender 4.5.15, render time recorded
- `ffprobe.json`: video stream analysis
- `production-notes.md`: complete production record including render statistics

**Audio files**:
- `audio/s1.mp3` through `s7.mp3` (narration, synthetic speech)
- `audio/bed.wav` (sound bed)
- `durations.json`: 2515 frames total, 83.833 seconds

**Review records**:
- `review-facts.md`: all claims C1-C11 mapped and verified, including C11 against finished film
- Reviewer outputs in `runs/wo-gh-18-pass1/`: facts, voice, brand, design all passed

**Content source files** (frozen from round 1):
- `brief.md`, `source-pack.md`, `script.md`, `storyboard.md`
- Blender scene scripts under `blender/` (8 scripts)

**Deterministic checks**:
- `checks.txt`: PASS (0 failing checks), 19 checks total covering resolution, framerate, duration, word count, first-person discipline, file integrity, contact sheet, stills, and render stats

## Architecture change verification

The production re-architecture succeeded completely:

1. **First pass (authoring)**: media-producer authored production inputs (narration, durations, sound bed, scene verification) but did NOT render. Duration: ~3.5 minutes.

2. **Deterministic workflow steps**: all frames rendered by parallel chunked headless Blender 4.5.15 outside any model session. Render logs committed under `frames/logs/`. No station session timeouts occurred.

3. **Second pass (film review)**: producing stations verified and held (no content changes). Reviewers judged the finished film. media-producer confirmed the film matches the storyboard and spec.

The round 1 timeout problem (media-producer session killed at 133/~2400 frames) cannot recur because rendering is now entirely outside model sessions.

## Observations on deterministic checks

All 19 checks in `checks.txt` passed:

- **Technical specs**: 1920x1080 ✓, 30fps ✓, h264+aac streams ✓, 83.83s duration ✓
- **Content compliance**: 195 words ✓, 14 timing marks ✓, first-person pronouns (12) ✓, no third-person ✓
- **Script/storyboard integrity**: script.md and storyboard.md unchanged ✓
- **Asset integrity**: GLB sha256 verified ✓
- **Evidence files**: contact sheet (2560x1440) ✓, 15 sampled stills ✓, render stats complete ✓
- **Production notes**: render stats recorded ✓, Blender version noted ✓

Zero failing checks. The finished video meets all technical and content requirements.

## Observations on reviews (second pass)

All four reviewers passed:

1. **reviewer-facts**: Re-judged claim C11 ("what the rendered result looks like") against the finished film. All claims C1-C11 now verified. Two wording edits from round 1 confirmed applied. Minor note: `source-pack.md` cites wrong commit for GLB (7344863 vs f6476d6), but no spoken claim affected. Pass.

2. **reviewer-voice**: Re-confirmed final script text end to end. First person discipline maintained. Voice consistency verified. Pass.

3. **reviewer-brand**: Re-confirmed naming compliance. No employer, factory, product, video, or person named. "ANVIL" used correctly. Pass.

4. **reviewer-design**: Judged finished film via contact sheet and sampled stills. Motion continuity verified, no frozen beats, brand consistency checked. Advisory items flagged for human review (see below). Pass.

**Approver verdict**: approved (all 4 reviews counted as pass).

## Advisory items for human review

reviewer-design flagged these items for the human at the gate to confirm against the final contact sheet and stills. They are advisory and did not block the pass verdict:

1. "Stations build" — a station post runs through the word "Stations"
2. "Verified memory." and "A human approves." overlap in one frame
3. The first-frame "ANVIL" title is small and low contrast on the paper background
4. One contact sheet cell is nearly empty

The publisher also noted that `design/DESIGN.md` and `design/tokens.json` are still placeholders, so brand consistency can only be checked internally.

## Observations on compliance

1. **Voice and claim discipline**: First person throughout. No employer, factory, product, video, or person named. All claims mapped and verified. Script kept byte for byte from round 1 final (with two approved wording edits applied in setup commit).

2. **Frozen inputs**: Script and storyboard unchanged from committed versions. No station rewrote, rephrased, or reformatted either file in either pass.

3. **Risk hint respected**: The `publishing` risk hint correctly triggered the human gate requirement. The approver verdict is `approved`, but `human_required: true` in `report.json`. The publisher did not bypass the gate.

4. **Disclosure ready**: Production notes state the narration is synthetic speech, requiring the YouTube AI-generated content label at publish time.

5. **Model routing**: writer ran claude-opus-5-5. All other producing stations ran claude-sonnet-5-5. Both models passed the exact-reply smoke gate before the line ran.

6. **Render budget**: Eevee TAA render samples at 6 (within authored budget, under the spec limit of 8). Shadows and raytracing off. Background element resolution as authored. No frame, framerate, or motion cuts.

## State verification against publish record

The publisher's `publish-record.md` accurately reflects the actual state:

- **Video exists**: Confirmed. sha256 matches: `62a3137df17fb512331e0cff3ed85fae0597cafa0530bd03cdcd0052f512ff22`
- **Video properties**: Confirmed. 1920x1080, 30fps, h264+aac, 83.83s
- **Supporting files**: Confirmed. Contact sheet, sampled stills, render stats, ffprobe, production notes all present
- **Deterministic checks**: Confirmed. `checks.txt` reports PASS (0 failing checks)
- **Approver verdict**: Confirmed. `report.json` shows `verdict: "approved"`, all 4 reviews passed
- **Human gate**: Confirmed. `human_required: true` in `report.json`
- **Not published**: Confirmed. No YouTube URL, no publish logs, no external service contact

The publish record is accurate. No discrepancies observed.

## Observed outcome

The gate loopback completed successfully:

1. **Architecture goal achieved**: Rendering moved outside model sessions. No session timeouts. First pass (authoring): ~3.5 minutes. Deterministic render: completed in parallel chunks.

2. **Authoring pass (pass 1)**: brief-writer, researcher, writer, media-producer, and all four reviewers executed successfully. Audio files and production inputs authored. No rendering in station sessions.

3. **Deterministic workflow steps**: 2515 frames rendered by headless Blender 4.5.15 in parallel chunks. ffmpeg assembled the film with contact sheet and stills. All checks passed.

4. **Film review pass (pass 2)**: Producing stations verified and held. Reviewers judged the finished film. All four reviews passed. Approver verdict: approved.

5. **Human gate**: Publisher correctly stopped. No explicit human approval found. Nothing published anywhere.

The work order stated: "the finished video stops at the human gate, and nothing is posted anywhere." This is exactly what happened. The publisher followed the rules.

**Status: HELD AT HUMAN GATE, NOTHING PUBLISHED**

## Next steps (from publish record)

1. A human reviews the film end to end and records an explicit approval at the gate, or sends it back with changes.
2. After approval, the publisher records the live URL and publish date in `publish-record.md`.
3. At YouTube upload time, the AI-generated content label must be set (narration is synthetic speech).
