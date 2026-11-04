# Observation Report: wo-gh-27 Film Review Pass

**Observer station** | **Date**: 2026-11-04  
**Work order**: wo-gh-27 - Film review pass for wo-gh-18 polish film

## What was supposed to happen

This pass was designed to complete the film review that wo-gh-18 left incomplete. The polish round rendered a new film but never judged it due to running the content line twice with identical commands. This pass would:

1. Review the existing film against four design advisories (S1, S2, S4, S6)
2. Verify claim C11 against the finished film
3. Record results without publishing anything
4. Make no changes to files under `content/`

## What actually happened

### Execution completed successfully

All upstream stations executed and produced their required outputs:

- **reviewer-design**: Examined proof stills at full resolution and ruled on all four polish advisories
- **reviewer-facts**: Verified claim C11 by measuring SHA256 and confirming checks
- **approver**: Completed gate
- **triage-human**: Completed gate  
- **publisher**: Wrote publish record to `runs/wo-gh-27/`

### Review findings

**reviewer-design verdict: pass**

All four polish advisories closed based on still examination:

1. ✓ Section 4 title occlusion: "Stations build" title clear of geometry (frames: mid-4, cut-4-first, cut-4-last)
2. ✓ Section 6 caption stacking: Both captions legible and properly separated (frames: mid-6, cut-6-last, cut-7-first)
3. ✓ Section 1 opening title: ANVIL title strong treatment throughout (frames: proof-s1-title, mid-1, cut-1-last)
4. ✓ Section 2 card flight: Card maintains subject prominence in flight (frames: mid-2, cut-2-first, cut-2-last)

Review file: `runs/wo-gh-27/reviewer-design.review.json` written correctly as structured JSON.

**reviewer-facts verdict: pass**

Claim C11 verified successfully:
- Measured SHA256: `a277ce32c3ac7c30de5679524f49b1017ff028cfea2d38277deed73c4b44ecac` ✓ matches expected
- checks.txt: 19 of 19 PASS including S7 contact sheet (2560x1800, 20 stills) and S3/S5 script integrity ✓
- render-stats.json: 2,515 of 2,515 frames, 6 tolerated crashes, 0 failures ✓

Review file: `runs/wo-gh-27/reviewer-facts.review.json` written correctly as structured JSON.

### Release status

**Nothing was published.** Confirmed by:
- Publisher's explicit record: "NOT PUBLISHED. Nothing was posted anywhere."
- No upload URLs in publish record
- No external platform posts
- Video remains on owner's hold per the `publishing` risk hint

### File changes

Verified constraints:
- ✓ No files under `content/` were modified (git diff shows only `runs/wo-gh-27/envelopes/intake.envelope.json`)
- ✓ Film file unchanged: `content/youtube-anvil-v2/anvil-youtube-v2.mp4` (21,401,761 bytes, SHA256 verified)
- ✓ All writes confined to `runs/wo-gh-27/` directory

### Channel discipline

Both reviewer stations followed the fixed producer protocol:
- ✓ reviewer-design wrote structured JSON to `reviewer-design.review.json`
- ✓ reviewer-facts wrote structured JSON to `reviewer-facts.review.json`
- ✓ Both files contain valid verdict and findings structure
- ✓ Narrative prose confined to separate `.output.md` files

## Discrepancies

None. All stations executed as specified, all constraints were respected, and the pass produced exactly the review results it was designed to produce.

## Current state

The wo-gh-27 film review pass is **COMPLETE**:
- All four polish advisories from wo-gh-18 are now **CLOSED** based on evidence
- Claim C11 is **VERIFIED** against the finished film  
- The film review that wo-gh-18 left incomplete is now **FINISHED**
- The video waits at the human gate for the owner's publication decision

The film under review (`anvil-youtube-v2.mp4`, SHA256 a277ce32...4b44ecac) has passed all design and facts checks and is ready for publication when the owner releases the hold.
