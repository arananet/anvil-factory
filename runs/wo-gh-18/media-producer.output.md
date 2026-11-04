I made no changes this pass. The four polish fixes, the sheet sampling and the production notes were already committed on this branch, so I checked them against the spec instead of rewriting them. I did not render, encode or extract frames.

**The four fixes in `blender/scene_line.py`**
1. **Section 4 title:** "Stations build" now sits at z 5.28, up from 4.1. The highest arm tips and caps reach about z 4.38. The notes' projection puts about 40 px of clear paper between them and the glyphs. The title still travels with the camera.
2. **Section 6 captions:** both captions are parented to the camera, so no scene geometry can touch them. "A human approves." sits upper right and "Verified memory." sits lower left, so they are side by side and not one column. "Verified memory." is fully keyed in by 0.47 of the section, so it is on screen at the midpoint and the last frame. The wording is unchanged.
3. **Section 1 title:** "ANVIL" uses the full ink material from frame 1. It is at 0.97 of full scale at frame 1 and full scale by 0.15 of the section. The dolly and the line assembly keys are untouched.
4. **Section 2 flight:** the card starts in frame, and its tilt runs 78, 68, 42, 14, 0 degrees across the flight. That makes it about 44 degrees at the midpoint instead of edge on. The camera rides about 5.5 to 6 units off with its target just ahead of the card. Frame count and timing are unchanged.

**Sheet sampling in `blender/assemble.py`**
- All existing still names are kept. It adds `frame-cut-2-last`, `frame-cut-3-first`, `frame-cut-4-last` and `frame-cut-5-first`, so every cut is sampled as a pair.
- It adds `frame-proof-s1-title.png`, taken at frame 91 of 302 (30%). The sheet has 20 tiles.

**Frozen inputs and render budget**
- `git diff` against HEAD shows no change to `brief.md`, `source-pack.md`, `script.md`, `storyboard.md`, `audio/`, `durations.json` or `assets/`. I did not compare `script.md` and `storyboard.md` against the previous round's commit; the writer station owns that check.
- Eevee TAA render samples stay at 6 (the cap is 8), with shadows and raytracing off. The frame rate and frame count are unchanged.
- Both scene scripts compile.

**Things to know**
- The working tree already holds a re-rendered film. `anvil-youtube-v2.mp4`, `checks.txt`, `contact-sheet.png`, `ffprobe.json` and `render-stats.json` are modified, and 20 stills including `frame-proof-s1-title.png` exist. The only uncommitted change in `production-notes.md` is the workflow rewriting the render statistics block. I left that block untouched.
- The notes' authoring section still says the film in the tree is the previous round's. That is out of date. Since the notes are meant to be completed in the second pass, I left it alone. I did not view the new frames or confirm the film shows the fixes. The geometry claims above come from the notes' projections, which I did not recompute. Judging the finished film is reviewer-design's job in the second pass.
- `reviewer-design` should judge the section 3 first frame, which the notes flag as the small card with dark posts behind it by design.

{"model": "claude-sonnet-5-5", "runtime": "claude-code"}
