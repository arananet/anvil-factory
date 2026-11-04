# Review: reviewer-facts, wo-gh-18 polish loopback, authoring pass

Verdict: pass.

- Frozen inputs: git shows no change to brief.md, source-pack.md, script.md, storyboard.md, durations.json, audio/ or assets/patch-one.glb against HEAD.
- Spoken claims: script.md maps to C1 to C11 only, with the same wording as the previous round. Narration is 190 words, matching production-notes.md. (checks.txt reports 195 words because it counts the whole script file, not only the narration.)
- On-screen text in blender/scene_line.py (ANVIL, One intake, The spec comes first, Stations build, Five reviewers in parallel, A human approves., Verified memory.) stays inside the claim list. Nothing else is named or counted.
- Polish edits change placement, scale, timing and flight only. They add no factual claim.
- Render budget: common.py keeps TAA samples at 6, shadows and raytracing off, as production-notes.md states.
- Open: C11 is judged against the finished film in the second pass. Also, source-pack.md still cites setup commit 7344863 for the asset. This does not affect any claim.
