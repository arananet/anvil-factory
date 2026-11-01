I wrote the brief to `content/youtube-anvil-v2/brief.md`. I didn't commit it, and I didn't check the sources myself, so the researcher still has to do that.

The brief covers:
- **Audience and angle:** developers and technical leads, with ANVIL speaking as itself in first person from "Introducing ANVIL".
- **Voice and format rules:** the voice rules, plus the format rules for the video, narration and sound bed.
- **Section plan:** seven sections, each with its visual action, its exact on-screen text and what the narration has to do. It also carries a suggested word weighting of about 175 words.
- **Claims:** the spec's closed list of 11 claims, each with the repository file or live site that has to back it.

Three things the next stations should know:
- **Reviewer count:** the claim "five reviewers check the work in parallel" is on the spec's list. `pipelines/content-video.json` has four parallel reviewers (facts, voice, brand, design). I kept the claim as the spec words it. The brief tells the researcher to cite where five exist, such as the default software pipeline, and to flag any mismatch. I did not check that pipeline.
- **Sources outside the brain:** the brain files don't mention Cloudflare AI Gateway, Apache 2.0 or Sentia. Those claims have to come from the tools, `LICENSE` and the live Sentia site.
- **Design tokens:** they are all TODO in the packet. The brief takes the look from the spec (paper, ink green, teal) and leaves exact colors to the media-producer.

I left out the rejected first video and issue 17, because the spec says no other video may be referenced. I also didn't name the author's employer.

I read `LICENSE` and the pipeline file, and I confirmed that `tools/claude_station.py` mentions Cloudflare. I did not open the live site.

{"model": "claude-sonnet-5-5", "runtime": "claude-code"}
