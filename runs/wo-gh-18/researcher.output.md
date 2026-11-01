I checked `brief.md` and `source-pack.md` against the spec and kept both unchanged. I found no concrete error in either, so I corrected nothing and the tree is still clean.

**What I checked**
- **Claims:** both files cover claims C1 to C11 in the spec's own wording. The brief's seven-section plan, on-screen texts and word budget (150 to 200) match the spec.
- **Voice rules:** the first-person rules, the banned third-person phrases and the closed list of allowed counts are all present in the brief.
- **Dashes:** neither file contains an em or en dash.
- **Asset:** `assets/patch-one.glb` is 386708 bytes, and its sha256 matches the spec's `daea8110…f50f523`.
- **Reviewer counts:** `pipelines/content-video.json` has four reviewers: facts, voice, brand and design. `pipelines/sdlc-default.json` and `pipelines/content-default.json` each have five. `anvil/model.py` lists six intake kinds. So flags F1 (C5) and F2 (C2) hold as written.

**For reviewer-facts**
- **C5:** "Five reviewers" is true of the default lines but not of this film's own four-reviewer panel. The script should keep section 5 about the factory in general. Section 7 should say nothing about a reviewer count.
- **C2:** "Issue" is an entry source rather than a kind in the code. The claim is a simplification, and the pack cites what supports each word.
- **C6:** the human gate is triggered by risk hints or a non-approved verdict. The claim is solid for published content, including this film.
- **C11:** the evidence for the rendered, produced and reviewed parts does not exist yet at this station. It gets judged in the second pass once the film is in the tree.
- **Provenance:** I did not verify the upstream Sentia commit `c9f9bf9` or `src/patch-one-glb.js`. That line rests on the spec's record. I also did not re-fetch the live Sentia site this pass. The pack's site facts come from its 2026-11-01 fetch.

I wrote no new files. I did not touch `script.md`, `storyboard.md` or anything under `blender/`, and I ran no render, encode or contact-sheet step.

{"model": "claude-sonnet-5-5", "runtime": "claude-code"}
