I wrote the source pack to `content/youtube-anvil-v2/source-pack.md`. It covers claims C1 to C11 and nothing else. Each claim has its repo file or live-site source and the specific fact that source supports. The pack has no em or en dashes and no personal names.

**GLB asset:** the file is 386708 bytes and its sha256 matches the spec's value. The pack gives the provenance exactly as the spec records it. The scene has five root nodes in stack order: Top cover, Comfort foam, Sensing and processing board, Adhesive layer, Release liner. I could not check the upstream Sentia commit, because the `gh` call was unauthenticated here. That line rests on the spec.

**Live site:** `sentia.info-693.workers.dev` and `/take-apart` both returned HTTP 200 on 2026-11-01. The take-apart page is the interactive study of the five layers, and the site footer credits ANVIL with designing and building it.

**Flags for reviewer-facts:**
- **C5, five reviewers:** the factory's default software line and default content line have five parallel reviewers. This film's own pipeline, `content-video.json`, has four, and the README says four too. The pack doesn't change the claim. It advises keeping section 5 about the factory in general and giving no reviewer count in section 7, where the video itself is described.
- **C2, intake kinds:** the code has six kinds: idea, feature, bug, incident, task and content. "Issue" is a way work comes in, not a kind. The three-kinds claim is a simplification, and the pack cites what supports each word.
- **C6, human gate:** in code the gate is triggered by risk hints or a non-approved verdict, and publishing is one of the hints. The claim holds for anything that gets published, including this film. It isn't supported as a statement about every work order.
- **C11, this video's own line:** the artifacts that show it was written, rendered and reviewed don't exist yet. The pack can only cite the pipeline and the work order.
- **C10, site content:** the live site names a person and gives many product specs, none of which are on the claim list. The pack warns the writer to keep them out.

{"model": "claude-sonnet-5-5", "runtime": "claude-code"}
