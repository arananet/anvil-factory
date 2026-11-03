The four scene fixes and the extended sheet sampling were already in the committed tree (commit 141c924). I authored nothing new in the scene scripts; this pass was verification plus the production-notes update. I ran no Blender render, no ffmpeg and no frame extraction, so none of this has been seen in a rendered frame.

I checked each fix by projecting the scene geometry through the authored cameras with a 35 mm lens at 1920x1080. The projection is in `/tmp/proj.py` and is not committed.

1. **Section 4 title:** it sits at z 5.28, about 40 px above the highest arm tip and cap in the frame (title bottom y≈257, tips y≈297). It still travels with the camera in x.
2. **Section 6 captions:** both are parented to the camera, so scene geometry can't touch them.
   - **Placement:** "A human approves." sits at about x 1300, y 130. "Verified memory." sits at about x 600, y 215. They are side by side, staggered, with a horizontal gap.
   - **Clearance:** archive, quarantine and gate tops are at y 383 or lower at the midpoint and y 420 or lower in the last frame, clear of the caption band.
   - **Timing:** the second caption is fully in by 0.47, so it is on screen at the midpoint (0.50) and in the last frame.
3. **Section 1 title:** "ANVIL" uses the full ink material from frame 1, starts at 0.97 scale and is full scale by 0.15 of the section. The dolly and the line assembly keys are untouched.
4. **Section 2 card:** it now enters in frame, and its tilt runs 78°, 68°, 42°, 14°, 0°, so at the midpoint it is about 44° and faces the camera. At the midpoint it projects to about x 278–818, y 462–682, roughly 540 px wide. The card sits left of center on purpose, to leave room ahead of its motion. The section 3 first frame is still a small card with dark posts behind it, and I left it. The notes pass it to reviewer-design to judge on the finished film.

**Sheet sampling:** `assemble.py` keeps all 15 existing still names. It adds `frame-cut-2-last`, `frame-cut-3-first`, `frame-cut-4-last` and `frame-cut-5-first`, so every cut is sampled as a pair. It also adds `frame-proof-s1-title.png` at frame 91 of 302, about 30 percent. The sheet is now 20 tiles.

**Render budget and frozen inputs:**
- **Budget:** unchanged, at 6 TAA samples (never above 8), shadows and raytracing off, 30 fps, no frames cut.
- **Frozen inputs:** `script.md`, `storyboard.md`, the audio files, `durations.json` and the GLB hash `daea8110…` stand unchanged. Both scripts compile.

`production-notes.md` now records the four fixes with their scene locations, the sampling change and the budget confirmation. I replaced the previous round's stale film-review section, which described the old film, with a note that the second pass completes it. The render statistics block is byte-identical to before.

`source-pack.md` shows as modified in git, but that edit isn't mine. It changes one provenance line, replacing a commit hash that isn't resolvable in this checkout. I left it for the researcher station's record.

{"model": "claude-sonnet-5-5", "runtime": "claude-code"}
