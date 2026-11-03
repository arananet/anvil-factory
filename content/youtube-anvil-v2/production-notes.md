# Production notes: ANVIL launch film v2 (wo-gh-18, polish loopback)

This is the polish round authoring pass record (the earlier sections below describe the unchanged production method). The media-producer authored the production inputs only. Frames, encoding, the contact sheet and the sampled stills are made by deterministic workflow steps outside any model session. The render statistics block below is written by tools/render_stats.py after the render.

## Asset provenance

- File: assets/patch-one.glb, 386708 bytes.
- sha256: daea8110b356865396b062bb1ca20944dd7103286758214cbc7804b43c50f523 (verified in this pass, matches the spec).
- Origin: the factory's own Blender product model of the Sentia Patch One, built by the Sentia project's product model run. Source repository arananet/sentia, branch anvil/run-take-apart-product-model, commit c9f9bf9fcdf23cbd2107d26b11077ba5740f7a44, decoded from src/patch-one-glb.js. First party material. No stock material and nothing downloaded from third parties is used anywhere in the film.

## Scene method

- Everything is built procedurally and deterministically by the Blender Python scripts under blender/. The scripts are the source of truth; no .blend file is an input.
- common.py: scene reset, render setup, paper colored world, one soft key light, emissive teal accents, shared materials, and the fixed seed (random seed 7, Cycles seed 7).
- scene_line.py: sections 1 to 6, the line scene following the storyboard (intake, spec card, stations, reviewers, human gate, verified memory).
- scene_proof.py: section 7, imports assets/patch-one.glb and animates its five scene root groups apart along the stack axis and back together during a slow orbit.
- film.py renders one section or one frame chunk; render_all.sh runs chunks of 60 frames with at most 4 Blender processes; frames that exist are skipped so an interrupted render resumes. assemble.py encodes, concatenates, mixes and writes the outputs.
- Verified in this pass: all scripts compile, sections 1 to 6 map to animators in scene_line.py, section 7 is in scene_proof.py, and film.py dispatches by section number.

## Render budget (as authored, confirmed)

- Eevee, 1920x1080, 30 fps, motion blur off.
- TAA render samples: 6 (authored default in common.setup_render), never above 8 and well under the spec ceiling of 16.
- Shadows off and raytracing off. Soft contact shadows are built as stacked translucent geometry.
- No volumetrics, no depth of field.
- Background element resolution as authored (resolution percentage 100 passed by render_all.sh).
- Frame count, frame rate and motion are not cut. Total planned frames: 2515 (83.833 s).

## Voice and durations

- Voice: en-US-ChristopherNeural via edge-tts, one file per section under audio/ (s1.mp3 to s7.mp3), default speech rate +0%, no rate adjustment needed.
- Narration text was fed exactly as written in script.md, without headings or target timing lines. The narration is 190 words.
- The address sentia.info-693.workers.dev is spoken as written; no change was made to the words.
- Durations measured with ffmpeg metadata (a lead of 0.15 s and a tail of 0.45 s per section; section 3 padded to at least 5 s):

| Section | Narration (s) | Visual (s) | Frames |
|---------|---------------|------------|--------|
| 1 Introducing | 9.48 | 10.08 | 302 |
| 2 One intake | 6.31 | 6.91 | 207 |
| 3 Spec first | 5.86 | 6.46 | 194 |
| 4 The line builds | 6.24 | 6.84 | 205 |
| 5 Five reviewers in parallel | 5.18 | 5.78 | 173 |
| 6 The human gate and the memory | 16.01 | 16.61 | 498 |
| 7 Proof and close | 30.60 | 31.20 | 936 |

- Total: 2515 frames, 83.833 s, inside the 60 to 90 second window. Written to durations.json.

## Sound bed method

- blender/soundbed.py, Python standard library only, fixed seed 7. No samples, no downloads.
- A soft pad and a gentle pulse under the narration, with a soft tick at each section change. Output audio/bed.wav, 44.1 kHz, mono, 16 bit, 84.33 s.
- Tick times (s): 0.00, 10.07, 16.97, 23.43, 30.27, 36.03, 52.63.
- The bed is mixed under the narration by assemble.py with ffmpeg so the narration stays clearly on top. The final mix levels are those set in assemble.py.

## Disclosure

The narration is synthetic speech (a neural text to speech voice). The YouTube AI generated content label must be set at publish time. Nothing is published by this run; the film stops at the human gate.

## Environment note

ffmpeg was on PATH in this pass. blender/durations.py was re-run and reproduced durations.json exactly (2515 frames, 83.833 s), and blender/soundbed.py was re-run and wrote audio/bed.wav (84.33 s). The narration files s1.mp3 to s7.mp3 were kept as synthesized. The GLB sha256 was re-verified against the spec, and all Blender scripts compile. No Blender render, no ffmpeg encoding and no frame extraction was run in this pass.

<!-- render-stats:start -->
## Render statistics (recorded by the deterministic workflow render step)

Rendered with Blender 4.5.15, Eevee, at 1920x1080 and 30 fps by the workflow's deterministic render step (parallel chunked headless Blender, at most 4 processes at once), outside any model station session.
Total frames rendered: 2515 frames.
Per section: section 1: 302 frames in 4178.6 s across 6 chunks, section 2: 207 frames in 3736.5 s across 4 chunks, section 3: 194 frames in 7361.7 s across 4 chunks, section 4: 205 frames in 3350.0 s across 4 chunks, section 5: 173 frames in 2841.0 s across 3 chunks, section 6: 498 frames in 7943.2 s across 9 chunks, section 7: 936 frames in 23423.5 s across 16 chunks.
Logged render time in total: 52834.5 s of Blender render time summed across chunks (chunks ran in parallel, so wall time was lower).
The full record is in render-stats.json next to this file.
<!-- render-stats:end -->

## Polish loopback: the four scene fixes (authoring pass, media-producer)

Scope: scene and layout only. script.md, storyboard.md, brief.md, source-pack.md, durations.json, audio/ and assets/patch-one.glb are frozen and were not edited by this station. No Blender render, no ffmpeg encoding and no frame extraction was run in this pass; the rendered film in the tree is still the previous round's film until the deterministic steps re-render it. Fixes below are authored in blender/scene_line.py and checked here by projecting the scene geometry through the authored cameras (arithmetic only, 35 mm lens, 1920x1080), not by viewing frames.

1. Section 4 title occlusion (scene_line.py, s4). The "Stations build" title moved from z 4.1 to z 5.28 at y 0 (band about z 4.9 to 5.7). The highest line geometry is the arm tips and caps at about z 4.38 at y -1.9; with the camera at z 3.0, 12.5 units off, the tip tops project to about y 297 px and the title glyph bottoms to about y 257 px, so there is about 40 px of clear paper, and the title top stays about 137 px below the frame top. The title still travels with the camera in x at the same linear speed, so it stays on screen the whole section. Wording, size and fade in timing are unchanged.
2. Section 6 caption stacking (scene_line.py, s6). Both captions are parented to the camera, 4 units in front, so no scene object can touch them. "A human approves." sits right of center and higher (about x 1300, y 130 px, 1.52 units wide); "Verified memory." sits left of center and lower (about x 600, y 215 px, 1.36 units wide), so they are staggered side by side with a horizontal gap, not one column. Projected tops of the archive, the quarantine pane and the gate beam are at y 383 px or lower in the midpoint frame and y 420 px or lower in the last frame, well under the caption band (y 85 to 255 px). "Verified memory." keys in at 0.40 to 0.47 of the section, so it is already fully on screen at the midpoint (0.50) and in the last frame. Wording unchanged.
3. Section 1 opening title (scene_line.py, s1). "ANVIL" uses the full ink material (INK) from frame 1 and is keyed at 0.97 of full scale at frame 1, full scale by 0.15 of the section, and 1.03 at the end, instead of pale gray at small scale until 0.85 to 0.90. The dolly in, the table rise, the post rise and the line assembly keys are untouched. Proof still: frame-proof-s1-title.png at 30 percent of the section.
4. Section 2 dead air (scene_line.py, s2). The card now enters in frame (-21, -1.4, 4.4) instead of far off frame and its X tilt runs 78, 68, 42, 14, 0 degrees across the flight, so its face is turned toward the camera at the midpoint (about 44 degrees tilt) instead of edge on. The camera rides about 5.5 to 6 units off the card with its target just ahead of it. Projected at the midpoint the card spans about x 278 to 818 and y 462 to 682 px (about 540 px wide), where the previous film showed it tiny and edge on. Frame count and section timing are unchanged. Audit of the other sampled frames from the geometry: the section 1 opening is no longer empty paper because the title is present from frame 1; section 3 first frame, section 4 first frame and the midpoints of sections 3, 4, 5 and 6 carry the card or piece, posts, gantry or archive in frame. The first frame of section 3 shows the small card with the dark posts behind it by design; reviewer-design judges it on the finished film.

Sheet sampling (blender/assemble.py, sheet mode). Every previous still name is kept. Added transition stills: frame-cut-2-last, frame-cut-3-first, frame-cut-4-last and frame-cut-5-first, so each of the six cuts (after sections 1 to 6) is sampled as a pair, the last frame of section a and the first frame of section a+1. Added early title proof: frame-proof-s1-title.png from section 1 at 30 percent (frame 91 of 302). The sheet has 20 tiles.

Render budget confirmed unchanged: common.setup_render keeps Eevee TAA render samples at 6 (never above 8), shadows off, raytracing off; 30 fps; no frames cut; render_all.sh and film.py untouched. Narration audio files, durations.json (2515 frames, 83.833 s) and the GLB sha256 (daea8110b356865396b062bb1ca20944dd7103286758214cbc7804b43c50f523) were checked and stand unchanged. No narration was re-synthesized. Scripts compile.

Disclosure stands: the narration is synthetic speech, so the YouTube AI generated content label must be set at publish time. Nothing is published by this run.

Film review pass: to be completed in the second pass against the re-rendered film, preserving the render statistics block exactly.
