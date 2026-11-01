# Publish record: ANVIL the video v2 (wo-gh-18)

**Status: NOT PUBLISHED. Nothing was posted anywhere.**

## Why the publisher stopped
- The work order carries the `publishing` risk hint, so the human gate is **required**. The `triage-human` envelope says "completed", but no explicit human approval of publishing is in the inputs. The rules say a required gate means stop, so I did not publish.
- The finished film does not exist in the tree. There is no `anvil-youtube-v2.mp4`, contact sheet, sampled stills or `render-stats.json`. This run's inputs are the first (authoring) pass only. The deterministic render and the second (film review) pass have not run yet.
- `runs/wo-gh-18/report.json`, the artifact the approver and triage envelopes point to, is not in the tree.
- No live URL exists, so none is recorded.

## State of the inputs (first pass)
- reviewer-facts: pass. Both wording edits are verified and every claim maps to C1 to C11. C11 is judged in the second pass.
- reviewer-design: pass for the storyboard and scene scripts. The finished film is judged in the second pass.
- Audio inputs are present: `audio/s1.mp3` to `s7.mp3`, `audio/bed.wav` and `durations.json`.

## For the human at the gate
- Review the finished film once the deterministic render and the second pass have produced it.
- The narration is synthetic speech. Set the YouTube AI-generated content label at upload.
- `design/DESIGN.md` and `design/tokens.json` are still placeholders. Brand consistency can only be checked internally.
- Minor, noted by reviewer-facts: `source-pack.md` cites setup commit 7344863 for the GLB, while the loopback setup commit is f6476d6. No spoken claim is affected.

## Next steps
1. Run the render, assembly and `tools/video_checks_v2.py` workflow steps.
2. Run the second pass and get its reviewer and approver results.
3. Wait for an explicit human approval at the gate.
4. After that the publisher can record the live URL here.
