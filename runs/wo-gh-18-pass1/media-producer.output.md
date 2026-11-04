The four polish fixes were already in the tree when this session started, so I made no edits to the scene scripts, `assemble.py` or `production-notes.md`. I read them against the polish amendment and found no concrete error. I did not view any frames, because the film in the tree is still the previous round's. The placement figures in `production-notes.md` are from projecting the scene geometry, not from stills.

- **Section 4:** the "Stations build" title sits at z 5.28, above the highest arm tips and caps at about z 4.38.
- **Section 6:** both captions are parented to the camera, staggered left and right, and clear of the archive, gate and quarantine geometry. "Verified memory." is fully keyed in by the midpoint.
- **Section 1:** "ANVIL" is full ink from frame 1 and reaches full scale by 0.15 of the section. The dolly and line assembly keys are untouched.
- **Section 2:** the card now enters in frame and tilts from 78 to 0 degrees, so it faces the camera at the midpoint. The camera rides beside it. Frame count and timing are unchanged.
- **Sheet sampling:** all existing still names are kept. All six cuts are now sampled as pairs, and `frame-proof-s1-title.png` is taken at frame 91 of 302. The sheet has 20 tiles.

I ran no Blender render, ffmpeg step or contact sheet extraction, and I re-synthesized no narration.

- **Render budget:** TAA render samples stay at 6, shadows and raytracing are off, and the frame rate is 30. No frames are cut.
- **Frozen inputs:** none changed in the working tree, and `git status` shows nothing modified under `content/`. durations.json is still 2515 frames. The GLB sha256 still ends `…c523`.
- **Scripts:** all compile, and I removed the `__pycache__` directories afterwards.

`production-notes.md` already records the four fixes and their scene locations, and its render statistics block is untouched. I wrote the station output to `runs/wo-gh-18/media-producer.output.md`. That file showed as deleted in the git status at the start.

The section 3 first frame shows a small card with dark posts behind it by design. I flagged it in the notes for reviewer-design to judge on the finished film.

{"model": "claude-sonnet-5-5", "runtime": "claude-code"}
