# Publish record: ANVIL the video v2 (wo-gh-18)

**Status: NOT PUBLISHED. Nothing was posted anywhere. The piece is waiting at the human gate.**

## Why the publisher stopped
- The work order carries the `publishing` risk hint. `runs/wo-gh-18/report.json` records verdict `approved` and `human_required: true`. The human gate rule reads: "Verdict approved, but the work order carries the risk hint 'publishing', so a human is required." The `triage-human` step shows "completed" with detail "Human review: required". That is routing, not a human approval. No human approval is recorded, so I did not publish.
- No live URL exists, so none is recorded.

## State of the piece (second pass)
- The finished film is in the tree: `content/youtube-anvil-v2/anvil-youtube-v2.mp4`, sha256 `62a3137df17fb512331e0cff3ed85fae0597cafa0530bd03cdcd0052f512ff22`. It is 1920x1080, 30 fps, h264 video plus audio, 83.83 s.
- Supporting evidence: `contact-sheet.png`, sampled stills, `render-stats.json`, `ffprobe.json`, `production-notes.md`.
- Deterministic checks: `checks.txt` reports `RESULT: PASS (0 failing checks)`.
- Approver: approved, with all four reviews counted as pass (facts, voice, brand, design).
- reviewer-facts closed claim C11 against the finished film.

## For the human at the gate
- Watch the finished film end to end before approving.
- reviewer-design flagged these items to confirm against the final contact sheet and stills. They are advisory and do not block the pass verdict:
  - "Stations build": a station post runs through the word "Stations".
  - "Verified memory." and "A human approves." overlap in one frame.
  - The first-frame "ANVIL" title is small and low contrast on the paper background.
  - One contact sheet cell is nearly empty.
- The narration is synthetic speech. Set the YouTube AI-generated content label at upload.
- `design/DESIGN.md` and `design/tokens.json` are still placeholders, so brand consistency can only be checked internally.
- Minor, from reviewer-facts:
  - `source-pack.md` cites setup commit 7344863 for the GLB, while the loopback setup commit is f6476d6. No spoken claim is affected.
  - `ffprobe.json` shows 2514 frames and `render-stats.json` shows 2515 rendered frames on disk.

## Next steps
1. A human reviews the film and records an explicit approval at the gate, or sends it back with changes.
2. After approval, the publisher records the live URL and publish date here.
