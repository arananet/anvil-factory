# Publish record: ANVIL the video v2 (wo-gh-18), polish round

**Status: NOT PUBLISHED. Nothing was posted anywhere. The piece is waiting at the human gate.**

## Why the publisher stopped
- The work order carries the `publishing` risk hint. `runs/wo-gh-18/report.json` records verdict `approved` and `human_required: true`. The gate rule reads: "Verdict approved, but the work order carries the risk hint 'publishing', so a human is required." `triage-human` shows "Human review: required". That is routing, not a human approval. No human approval is recorded, so I did not publish.
- No live URL exists, so none is recorded.

## State of the piece
- The deterministic steps have run. The tree holds a re-rendered film: `anvil-youtube-v2.mp4`, sha256 `a277ce32c3ac7c30de5679524f49b1017ff028cfea2d38277deed73c4b44ecac` (the previous round's film was `62a3137d...ff22`). `checks.txt` reports `RESULT: PASS (0 failing checks)`. `render-stats.json` and `frames/frame-proof-s1-title.png` exist.
- The review results recorded in `runs/wo-gh-18/` are still the authoring-pass results (scene script review). I found no second-pass (film review) output in the tree. reviewer-design has therefore not ruled on the four advisories against the finished stills, and reviewer-facts has not re-judged claim C11 against this film. I did not judge the film myself.

## The four polish advisories (all open until the second pass)
1. Section 4: "Stations build" title clear of the posts, caps, arms and tips.
2. Section 6: "Verified memory." and "A human approves." legible, not overlapping each other or the geometry, not one stacked column.
3. Section 1: "ANVIL" title in full ink and near full scale from early in the section.
4. Section 2: the card reads as the subject through the flight, including the midpoint, with no dead air elsewhere.

## For the human at the gate
- Approve only after the second pass records all four advisories closed, and only against the re-rendered film (sha256 above). Watch it end to end.
- The narration is synthetic speech. Set the YouTube AI-generated content label at upload.
- `design/DESIGN.md` and `design/tokens.json` are still placeholders, so brand consistency can only be checked internally.
- Audit item from reviewer-facts: media-producer reports the fixes were already in the tree and made no edits, and HEAD e9d346f is an empty commit. Confirm the fixes were committed before this round.
- Minor, carried over: `source-pack.md` cites setup commit 7344863 for the GLB, which does not resolve in this checkout. No spoken claim is affected.

## Next steps
1. Run the second pass on the finished film.
2. Confirm it. Require all four advisories ruled closed, each with its still.
3. A human records an explicit approval at the gate. After that, the publisher records the live URL and date here.
