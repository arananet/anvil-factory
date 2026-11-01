# Production notes: ANVIL launch film v2 (wo-gh-18, gate loopback)

This is the authoring pass record. The media-producer authored the production inputs only. Frames, encoding, the contact sheet and the sampled stills are made by deterministic workflow steps outside any model session. The render statistics block below is written by tools/render_stats.py after the render.

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

## Film review pass verification (media-producer, hold)

No content file was changed in this pass. script.md and storyboard.md are unchanged from the setup commit. The render statistics block above is preserved exactly as recorded.

Confirmed against the finished film and the spec:

- anvil-youtube-v2.mp4: H.264 video 1920x1080 at 30 fps, one AAC audio stream, duration 83.83 s, inside the 60 to 90 second window.
- Frames on disk per section match durations.json: 302, 207, 194, 205, 173, 498 and 936, 2515 in total. ffprobe counts 2514 frames in the encoded stream, one fewer than planned; the duration still matches durations.json at 83.83 s.
- contact-sheet.png is 2560x1440. Fifteen sampled stills exist under frames/ (seven section midpoints, frame-cut stills for the transitions); the deterministic checks report each at 1920x1080.
- tools/video_checks_v2.py result in checks.txt: PASS, 0 failing checks.
- GLB sha256 daea8110b356865396b062bb1ca20944dd7103286758214cbc7804b43c50f523 matches the spec.

Observations from viewing the contact sheet, passed to reviewer-design for judgment and not corrected here, since content files are held in this pass:

- Some transition tiles show a nearly empty paper frame at the start of a section (for example the first frame of section 3) before elements enter.
- In the section 6 midpoint tile, the "Verified memory." caption and the "A human approves." caption appear on screen together, and they overlap in part.
- In the section 4 tile, the "Stations build" caption is partly covered by a station post.

The disclosure above stands: the narration is synthetic speech, so the YouTube AI generated content label must be set at publish time. Nothing is published by this run.
