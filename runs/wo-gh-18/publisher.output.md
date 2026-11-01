I did not publish the video, and nothing was posted anywhere. I wrote the record at `content/youtube-anvil-v2/publish-record.md`. It says "NOT PUBLISHED" and I haven't committed it.

I stopped for three reasons:

- **Human gate required:** the work order carries the `publishing` risk hint, which makes the gate required. The `triage-human` envelope says "completed", but the inputs contain no explicit human approval to publish.
- **No finished film:** there is no `anvil-youtube-v2.mp4`, contact sheet, sampled stills or `render-stats.json` in the tree. The render, assembly, `tools/video_checks_v2.py` and film review steps haven't run, so the reviewers' passes cover the authoring inputs only. reviewer-facts still has to judge claim C11 against the finished film.
- **Missing report file:** `runs/wo-gh-18/report.json`, which both envelopes point to, isn't in the tree.

reviewer-facts and reviewer-design both passed for the authoring pass. The audio inputs and `durations.json` are present.

The record also lists a few items for the human at the gate:

- The narration is synthetic speech, so the YouTube AI-generated content label must be set at upload.
- `design/DESIGN.md` and `design/tokens.json` are still placeholders, so brand consistency can only be checked internally.
- `source-pack.md` cites setup commit 7344863 for the GLB, but the loopback setup commit is f6476d6. No spoken claim is affected.

Once the film is rendered and reviewed and a human approves explicitly, the publisher can record the live URL in the same file.

{"model": "claude-sonnet-5-5", "runtime": "claude-code"}
