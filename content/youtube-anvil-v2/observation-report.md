# Observation report: ANVIL the video v2 (wo-gh-18, polish round)

**Observation date: 2026-11-04**  
**Work order: wo-gh-18**  
**Change: Polish loopback round**  
**Pass: First pass (authoring) and deterministic steps completed. Second pass (film review) did NOT run.**

## What was released

**Nothing was published anywhere.** No video was uploaded, no URL exists, and no external service was contacted.

The publisher correctly stopped because the workflow is incomplete: the second pass (film review) did not run, so the four polish advisories have not been ruled on against the finished film.

## Why the publisher stopped

From `publish-record.md`, the publisher identified multiple blocking conditions:

1. **Incomplete workflow**: "I found no second-pass (film review) output in the tree. reviewer-design has therefore not ruled on the four advisories against the finished stills, and reviewer-facts has not re-judged claim C11 against this film."

2. **Advisories still open**: All four polish advisories remain unresolved until the second pass rules on them against the finished film.

3. **Human gate requirement**: The work order carries the `publishing` risk hint and `triage-human` requires human review. No explicit human approval is recorded.

The publisher made the correct decision. Publishing requires the second pass to confirm all four advisories are closed, followed by human approval.

## What exists after this run

### Completed

**Finished video** (re-rendered):
- `anvil-youtube-v2.mp4`: 21,401,761 bytes, 1920x1080, 30fps, h264+aac, 83.83s
- sha256: `a277ce32c3ac7c30de5679524f49b1017ff028cfea2d38277deed73c4b44ecac`
- This is a NEW render. Previous round sha256: `62a3137d...ff22`

**Supporting evidence**:
- `contact-sheet.png`: 2560x1800 (note: dimension changed from previous 2560x1440)
- 20 sampled stills (increased from 15 in previous round), including new `frame-proof-s1-title.png`
- Transition pair stills for cuts after sections 1-6 (newly complete)
- `render-stats.json`: 2515 frames rendered, Blender 4.5.15
- `ffprobe.json`: video stream analysis
- `production-notes.md`: records the four scene fixes with locations

**Audio files** (unchanged):
- `audio/s1.mp3` through `s7.mp3` (narration, verified unchanged)
- `audio/bed.wav` (sound bed)
- `durations.json`: 2515 frames total, 83.833 seconds

**Review records** (first pass only):
- First-pass reviews in `runs/wo-gh-18/`: facts, voice, brand, design (all reviewed scene scripts, not the finished film)
- NO second-pass film review outputs found in the tree

**Content source files** (verified unchanged):
- `brief.md`, `source-pack.md`, `script.md`, `storyboard.md` all byte-identical to previous round
- Blender scene scripts under `blender/`: modified per the four polish fixes

**Deterministic checks**:
- `checks.txt`: PASS (0 failing checks), 19 checks total

### Not completed

**Second pass (film review)**: Did not run. No station judged the finished film against the four polish advisories. This is the blocking issue.

## The four polish advisories (status: OPEN)

The publish record lists all four advisories. None have been ruled on against the finished film:

1. **Section 4**: "Stations build" title clear of the posts, caps, arms and tips.
2. **Section 6**: "Verified memory." and "A human approves." legible, not overlapping each other or the geometry, not one stacked column.
3. **Section 1**: "ANVIL" title in full ink and near full scale from early in the section.
4. **Section 2**: The card reads as the subject through the flight, including the midpoint, with no dead air elsewhere.

**Expected**: reviewer-design rules on each advisory separately (closed or not) citing the still or stills that prove each ruling. All four must be closed before approval.

**Actual**: No film review pass ran, so no rulings exist.

## Observations on deterministic checks

All 19 checks in `checks.txt` passed:

- **Technical specs**: 1920x1080 ✓, 30fps ✓, h264+aac streams ✓, 83.83s duration ✓
- **Content compliance**: 195 words ✓, 14 timing marks ✓, first-person pronouns (12) ✓, no third-person ✓
- **Script/storyboard integrity**: script.md and storyboard.md clean (unchanged from previous round) ✓
- **Asset integrity**: GLB sha256 verified (daea8110b3568653...) ✓
- **Evidence files**: contact sheet (2560x1800) ✓, 20 sampled stills ✓, still size correct ✓
- **Production notes**: render stats recorded ✓, Blender version noted ✓, 8 Blender scripts ✓

Zero failing checks. The deterministic portion of the workflow completed successfully.

## Observations on first-pass reviews

All four first-pass reviewers passed (scene script review, not film review):

1. **reviewer-facts**: Verified the scene script changes against the spec. No claims affected by scene changes. Pass.
2. **reviewer-voice**: Re-confirmed script.md and storyboard.md byte-identical to previous round. Pass.
3. **reviewer-brand**: Re-confirmed naming compliance. Pass.
4. **reviewer-design**: Reviewed scene script changes against the four advisories. Noted the finished film must be judged in the second pass. Pass.

**Approver verdict** (first pass): approved, with `human_required: true`.

These reviews are valid but insufficient for publishing. The spec requires the second pass to judge the finished film.

## Production observations

From `production-notes.md` and the publisher's audit item:

1. **media-producer reported no edits**: "The scene fixes specified in the polish amendment were already present in the tree when I executed. I made no edits to any Blender scripts or assembly configuration."

2. **HEAD is an empty commit**: `e9d346f` states "Empty commit: the crash tolerant render wrapper from wo-gh-25 is already staged at fb44bc3d; no content changes."

3. **Publisher's audit request**: "Confirm the fixes were committed before this round."

**Observation**: The four scene fixes were committed before this round ran. media-producer correctly verified them and held. The deterministic workflow re-rendered the film with those fixes already in the scripts.

## Minor notes

1. **Source pack citation**: `source-pack.md` cites setup commit 7344863 for the GLB, which does not resolve in this checkout. The publisher notes no spoken claim is affected. (Carried over from previous round.)

2. **Design system placeholders**: `design/DESIGN.md` and `design/tokens.json` are still placeholders. Brand consistency can only be checked internally. (Carried over from previous round.)

## State verification against publish record

The publisher's `publish-record.md` accurately reflects the actual state:

- **Video exists**: Confirmed. sha256 matches: `a277ce32c3ac7c30de5679524f49b1017ff028cfea2d38277deed73c4b44ecac`
- **Video is new**: Confirmed. Different sha256 from previous round.
- **Deterministic checks passed**: Confirmed. `checks.txt` reports PASS (0 failing checks).
- **New sampled stills**: Confirmed. `frame-proof-s1-title.png` exists, transition pairs complete.
- **Second pass did not run**: Confirmed. No film review outputs in the tree.
- **Four advisories open**: Confirmed. No rulings against the finished film.
- **Not published**: Confirmed. No YouTube URL, no publish logs, no external service contact.

The publish record is accurate. No discrepancies observed.

## Observed outcome

The polish round is **INCOMPLETE**. Here's what happened:

1. **First pass (authoring)**: brief-writer, researcher, writer, media-producer, and all four reviewers executed successfully. media-producer verified the four scene fixes were already in the tree and made no edits. Reviewers passed the scene scripts.

2. **Deterministic workflow steps**: 2515 frames rendered by headless Blender 4.5.15 with the scene fixes applied. ffmpeg assembled the new film with contact sheet and 20 sampled stills. All checks passed. New film sha256: `a277ce32...ecac`.

3. **Second pass (film review)**: **DID NOT RUN**. Producing stations did not verify and hold. Reviewers did not judge the finished film. The four advisories were not ruled on.

4. **Publisher**: Correctly stopped and did not publish. The workflow is incomplete and the human gate requires explicit approval.

The work order specifies: "The line runs again with the finished film in the tree. Producing stations verify and hold: no content file changes in this pass. media-producer confirms the film... reviewer-design judges the finished film... and rules on each of the four polish advisories separately, closed or not."

This did not happen. The second pass must run before this round can be considered complete.

**Status: INCOMPLETE - SECOND PASS REQUIRED**

## Blocking issues

1. **Second pass did not run**: The film review pass must execute with the finished film in the tree.
2. **Four advisories unresolved**: reviewer-design must rule on each advisory separately, citing stills.
3. **Claim C11 not re-verified**: reviewer-facts must re-judge C11 against the new film.
4. **No human approval**: After the second pass confirms all advisories closed, a human must explicitly approve.

## Next steps (from publish record)

1. **Run the second pass** on the finished film (sha256 `a277ce32...ecac`).
2. **Confirm it**: Require all four advisories ruled closed, each with its still.
3. **Human approval**: A human records an explicit approval at the gate.
4. **Then publish**: After approval, the publisher records the live URL and date.

Until the second pass runs and confirms all four advisories are closed, the polish round remains incomplete and nothing can be published.

---

**Observer verdict: The workflow stopped after the deterministic render step. The second pass (film review) did not run, leaving the four polish advisories unresolved. The publisher correctly refused to publish an incomplete workflow. This is not a release; it is a blocking state requiring the second pass to execute.**
