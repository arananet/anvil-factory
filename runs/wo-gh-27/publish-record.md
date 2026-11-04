# Publish record: ANVIL film review pass (wo-gh-27)

**Status: NOT PUBLISHED. Nothing was posted anywhere. The film remains on the owner's hold.**

## Purpose of this pass

This is the dedicated film review pass that the wo-gh-18 polish round left incomplete. The polish round rendered a new film but failed to judge it: reviewer-design's counted review deferred all four polish advisories to a second pass, reviewer-facts left claim C11 open, and the publisher recorded the round INCOMPLETE.

This work order (wo-gh-27) executes that missing second pass: one dedicated film review over the already rendered film, run on the review-only pipeline (pipelines/content-film-review.json), with no authoring or rendering, judging the finished film on its evidence.

## Film under review

- File: `content/youtube-anvil-v2/anvil-youtube-v2.mp4`
- SHA256: `a277ce32c3ac7c30de5679524f49b1017ff028cfea2d38277deed73c4b44ecac`
- Size: 21,401,761 bytes
- Deterministic checks: 19 of 19 PASS (checks.txt)
- Render record: 2,515 of 2,515 frames (render-stats.json), 6 tolerated crashes, 0 failed
- Spoken script: unchanged from frozen script.md (checks S3 and S5 pass)

## Review results

### reviewer-design: Film review complete

All four polish advisories ruled **CLOSED** based on examination of the full-resolution proof stills:

1. **Section 4 - Title occlusion**: "Stations build" title clear of geometry. The title band sits clear of the full moving envelope of posts, caps, swing arms and tips, with no line geometry crossing its glyphs. (Proof stills: frame-mid-4.png, frame-cut-4-first.png, frame-cut-4-last.png)

2. **Section 6 - Caption stacking**: Both captions legible and properly separated. "Verified memory." and "A human approves." are both fully legible in the midpoint and final wide frames, overlap neither each other nor the archive or gate geometry, and do not read as one stacked block. (Proof stills: frame-mid-6.png, frame-cut-6-last.png, frame-cut-7-first.png)

3. **Section 1 - Opening title**: ANVIL title strong treatment throughout. The ANVIL title carries full ink color at full or near full scale from early in section 1, matching how it reads at the section's end. (Proof stills: frame-proof-s1-title.png, frame-mid-1.png, frame-cut-1-last.png)

4. **Section 2 - Card flight**: Card maintains subject prominence in flight. The card reads as the subject through its flight, including at the midpoint frame, with no dead air failure. (Proof stills: frame-mid-2.png, frame-cut-2-first.png, frame-cut-2-last.png)

**Verdict**: pass

### reviewer-facts: Claim C11 verified

Claim C11 verified successfully against this film:

- Measured SHA256: `a277ce32c3ac7c30de5679524f49b1017ff028cfea2d38277deed73c4b44ecac` (matches exactly)
- checks.txt: 19 of 19 PASS, including S7 contact sheet (2560x1800, 20 stills) and S3/S5 script integrity
- render-stats.json: 2,515 of 2,515 frames, 6 tolerated crashes, 0 failures

**Verdict**: pass

## Gate status

- approver: completed
- triage-human (human gate): completed
- The work order carries the `publishing` risk hint by design
- The video remains on the owner's hold

## What was published

**Nothing.** No files were uploaded, no URLs were created, no posts were made to any platform.

The only writes made by this pass are the run record files under `runs/wo-gh-27/`.

## What changed

No files under `content/` were modified by this pass. The film review examined the existing film and its evidence; no rendering or rewriting occurred.

## Next steps

The film review pass is complete. All four polish advisories are closed, and claim C11 is verified against the finished film. The video waits at the human gate for the owner's decision on publication.
