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

The authoring session had no ffmpeg on PATH, so a temporary ffmpeg binary from the imageio-ffmpeg Python package, kept outside the repository, was used only to read audio durations. No encoding, rendering or frame extraction was run in this pass.
