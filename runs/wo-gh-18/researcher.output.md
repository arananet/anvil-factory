I verified `brief.md` and `source-pack.md` against the spec and kept both unchanged. I found no concrete error, so I made no corrections and wrote no files. The source pack stays at `content/youtube-anvil-v2/source-pack.md`.

**What I checked against the spec**
- **Claim list:** The pack covers C1 to C11 in the spec's wording, with no extra claims and no counts beyond three intake kinds, five reviewers and five Sentia layers.
- **Dashes:** Neither file contains an em dash or en dash.
- **GLB:** The file is 386708 bytes and its sha256 is `daea8110b356865396b062bb1ca20944dd7103286758214cbc7804b43c50f523`. Both match the spec and the pack.
- **C5 and F1:** Five parallel reviewers exist in `pipelines/sdlc-default.json` and `pipelines/content-default.json`. `pipelines/content-video.json` has four: facts, voice, brand and design. The pack states this scope and does not change the claim.
- **C2 and F2:** `anvil/model.py` lists six kinds, and "issue" is not one of them. The pack flags this and leaves the claim as written.
- **C9:** `LICENSE` is Apache 2.0 and `pyproject.toml` says `Apache-2.0`.

**Not re-verified this pass**
- The live Sentia site fetch (2026-11-01) and the upstream commit `c9f9bf9` of the Sentia repository. The pack already records that the upstream commit was not checked.
- The pack says the GLB was committed in `7344863`. My `git log` here shows only `fddea15` as the adding commit, so I couldn't confirm that hash. The spec doesn't use it, so I left it.

**Handoffs**
- **C11 (F5):** The pack can only cite the pipeline and the work order. reviewer-facts judges C11 in the second pass, once the film exists.
- **No new sources:** The pack adds nothing for the two script wording edits. Section 4's edit drops a phrase and section 7's rewords the C8 claim, and both are covered by existing sources.

{"model": "claude-sonnet-5-5", "runtime": "claude-code"}
