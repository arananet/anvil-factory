I verified `brief.md` and `source-pack.md` against the spec and the repository. I found no concrete errors, so I corrected nothing and left both files byte for byte unchanged.

- **Claims:** C1 to C11 in the brief and the source pack use the spec's closed-list wording exactly. The pack cites nothing beyond that list.
- **Asset:** `assets/patch-one.glb` is 386708 bytes and its sha256 is `daea8110…f523`. Both match the spec.
- **Reviewer counts (C5):**
  - `pipelines/sdlc-default.json` has five reviewers.
  - `pipelines/content-default.json` has five reviewers: facts, voice, platform, brand and design.
  - `pipelines/content-video.json` has four: facts, voice, brand and design.

  Flag F1 already records this scope gap for reviewer-facts, so it needs no change.
- **Cited files:** `LICENSE` and `docs/MEMORY-GATE.md` exist, as C7 and C9 cite them.
- **Voice discipline:** neither file contains an em dash or an en dash. Neither names an employer, another product or a person.
- **Frozen inputs:** git shows no modifications to `brief.md`, `source-pack.md`, `script.md`, `storyboard.md`, `durations.json`, `audio/` or `assets/`.
- **Polish round:** this round changes only scene and layout. No claim, source or provenance line is affected.
- **Flag F5:** the evidence for the produced, rendered and reviewed parts of C11 is still downstream. Reviewer-facts has to judge C11 against the new film in the second pass.

I didn't re-fetch the live Sentia site or the upstream Sentia commit. Both rest on the pack's 2026-11-01 fetch and the spec's record, as the pack already says.

I ran no Blender, ffmpeg or contact sheet steps.

{"model": "claude-sonnet-5-5", "runtime": "claude-code"}
