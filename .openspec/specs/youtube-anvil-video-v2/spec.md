# YouTube video v2: ANVIL, a dynamic launch film rendered in Blender

## Purpose

Produce a second YouTube film about ANVIL through the factory's own content line. The first video (issue 17) was rejected by the owner at his gate: a narrated slideshow in third person is not a video. This piece fixes both failures at the root. The visuals are a real animated 3D sequence built and rendered in headless Blender by the line itself, and the narration speaks in a first person launch voice. The piece stops at the human gate. Nothing is published by this work order.

## The piece

- One MP4 at content/youtube-anvil-v2/anvil-youtube-v2.mp4, 1920x1080 (16:9), H.264 video with an AAC audio stream, 30 frames per second.
- Total duration between 60 and 90 seconds.
- English narration, one clean text to speech voice (the v1 setup), written to be spoken: 150 to 200 words in total.
- A light procedural sound design bed under the narration, generated inside the run. No third party music, no stock material of any kind.

## Voice: first person, launch register

- The narration's first words are exactly: Introducing ANVIL
- The presenter speaks as ANVIL, in first person (I, we), from the first line to the last. The factory is never narrated from outside in third person. That was the first video's central failure and it is a voice failure here.
- Natural human grammar. Full sentences a person would say out loud at a product launch: plain, confident, concrete.
- No stacked fragments, no slogans in a row, no hype words (no revolutionary, game changing, cutting edge, supercharge, unleash, or similar).
- No em dashes and no en dashes anywhere: not in the script, not in the storyboard, not in on screen text, not in the production notes.
- State what the factory does, not what it promises to become.

## Structure

Seven sections, in this order. The script states a target timing per section. The storyboard states, per section, the camera move, the action, any on screen text, and a framing note. Every section carries real motion from the render itself: the camera moves and the subjects move. A section whose visual is a still frame, or whose motion is faked by a zoom or pan over a still in post, fails the design review.

1. Introducing. In an empty paper space the factory line assembles itself as the camera dollies in: a long line table, station posts rising in sequence. On screen text in the scene: ANVIL.
2. One intake. A work order card flies in along the line and lands at its head. On screen text: One intake.
3. Spec first. The card unfolds and grows into a spec document that materializes completely before any station moves. On screen text: The spec comes first.
4. The line builds. The piece travels down the line while the camera tracks beside it; stations work in sequence and components attach to the piece as it passes. On screen text: Stations build.
5. Five reviewers in parallel. The piece halts at a review gantry; five reviewer posts around it light up in teal at the same moment and scan the piece. On screen text: Five reviewers in parallel.
6. The human gate and the memory. The line pauses at a gate and a hand rises to approve the piece through. Beside the line stands the memory archive: shelves where verified learnings slot in one by one, and a separate quarantine lane where unverified proposals wait behind glass. On screen text: A human approves. Verified memory.
7. Proof and close. The Sentia Patch One, the committed GLB asset, rises on a plinth, separates into its five layers in stack order and settles back together while the camera orbits slowly. Closing text in the scene: Sentia, then sentia.info-693.workers.dev, then Designed and built end to end by ANVIL.

## Claim list (closed)

The script may only assert claims from this list, phrased in first person. Each is true today and traceable to the factory repository or the live Sentia site.

- I am a software factory: work enters as an intake and leaves as reviewed, approved output.
- The intake is one of three things: a feature, an idea, or an issue.
- The spec is written before any code.
- Specialized stations do the work in a line, and no station approves its own work.
- Five reviewers check the work in parallel.
- A human approves before anything ships; nothing passes the human gate without that approval.
- I keep a verified memory: a learning enters it only with provenance tied to a run record, and proposals that cannot be verified wait in quarantine.
- The models that staff the stations are routed per station through Cloudflare AI Gateway, and the work lives on GitHub.
- I am open source under the Apache 2.0 license.
- Sentia is a concept sensor patch product that I designed and built end to end. It is live at sentia.info-693.workers.dev, including an interactive page where its five layers can be taken apart.
- This video was itself produced by my content line: written, rendered, produced and reviewed by my stations, and it stopped at the human gate.

No other factual claim may appear, spoken or on screen. In particular: no employer of the author may be named, no other factory, product, video or person may be named or referenced, and no counts beyond the ones in this list (three intake kinds, five reviewers, five Sentia layers) may be stated.

## Assets

Committed in the setup commit as run inputs under content/youtube-anvil-v2/assets/:

- patch-one.glb (386708 bytes, sha256 daea8110b356865396b062bb1ca20944dd7103286758214cbc7804b43c50f523): the factory's own Blender product model of the Sentia Patch One, built by the Sentia project's product model run. Source: repo arananet/sentia, branch anvil/run-take-apart-product-model at commit c9f9bf9fcdf23cbd2107d26b11077ba5740f7a44, decoded from src/patch-one-glb.js. First party material, and the same asset the live take apart page binds its interaction model to.

Everything else visual is built procedurally by the media-producer's Blender scripts inside the run. No stock material and nothing downloaded from third parties may be used.

## Production contract (media-producer station)

Working from content/youtube-anvil-v2/script.md and content/youtube-anvil-v2/storyboard.md as executed in this same run, and the committed asset:

1. Narration. Synthesize per section with edge-tts (install with pip if needed), voice en-US-ChristopherNeural, one file per section under content/youtube-anvil-v2/audio/. Measure each section with ffprobe. Each section's visual lasts its narration plus a short pad; the total must land between 60 and 90 seconds. Adjust the speech rate once if needed and record what was done. If the voice service is unreachable, record the failure in production-notes.md and stop; do not substitute a robotic local voice.
2. Scene. Write Blender Python under content/youtube-anvil-v2/blender/ that builds the whole film procedurally and deterministically: the line scene for sections 1 to 6 following the storyboard, and the proof scene for section 7, which imports assets/patch-one.glb and animates its five scene root groups apart along the stack axis and back together. The scripts are the source of truth; a .blend file is a build artifact, never an input. Fix every seed the API exposes.
3. Render. Blender 4.5.x headless, Eevee, 1920x1080, 30 fps, TAA render samples at most 16, no volumetrics, no depth of field, no motion blur. Paper colored world background, one soft key light, emissive teal accents, in the piece's visual language (paper, ink green, teal). Render each section to its own PNG sequence under content/youtube-anvil-v2/frames/s<N>/. Sections may render in parallel, at most 4 blender processes at once, and frames that already exist are skipped so an interrupted render resumes. If render time threatens the run, the levers, in this order, are: background element resolution first, then the sample count. Never the frame count and never the motion.
4. Sound bed. Generate a light procedural bed with Python (standard library only): a soft pad and a gentle pulse under the narration, with a soft tick at each section change. No samples, no downloads. Mix it with ffmpeg so the narration stays clearly on top, and record the method and the levels in production-notes.md.
5. Assembly. Encode each section's PNG sequence at 30 fps, concatenate the sections in storyboard order with hard cuts at the narration boundaries, mix the narration track and the bed, and write content/youtube-anvil-v2/anvil-youtube-v2.mp4 (H.264, AAC, 1920x1080, 30 fps).
6. Contact sheet. Extract one frame at each section midpoint, plus the last frame of a section and the first frame of the next for at least two transitions. Tile the sampled frames into content/youtube-anvil-v2/contact-sheet.png with every tile at least 640x360, and keep the individual sampled frames as 1920x1080 PNG stills under content/youtube-anvil-v2/frames/ named frame-mid-<section>.png and frame-cut-<section>.png.
7. Production notes. Write content/youtube-anvil-v2/production-notes.md recording: the GLB provenance and its sha256; how the scene was built; the render statistics (the Blender version, the total frames rendered, the render wall time in total and per section); the voice used and the per section durations; the total duration; the sound bed method; and the disclosure that the narration is synthetic speech, so the YouTube AI generated content label must be set at publish time (an owner note carried from the v1 review).

## Checks (scenarios)

- S1: ffprobe of the final MP4 reports width 1920, height 1080, one video stream at 30 fps and one audio stream.
- S2: ffprobe duration is between 60 and 90 seconds.
- S3: the narration word count in script.md is between 150 and 200 words, and script.md carries a target timing for each of the seven sections.
- S4: script.md, storyboard.md and production-notes.md contain no forbidden strings: no employer name, no em dash or en dash character.
- S5: first person discipline in the narration: it begins with the words Introducing ANVIL, it holds at least eight first person pronouns (I, we, my, our, me, us), and it contains none of these third person factory constructions: "ANVIL is a", "ANVIL is an", "ANVIL keeps", "ANVIL designed", "ANVIL built", "the factory is", "the factory keeps".
- S6: assets/patch-one.glb exists and its sha256 matches the value recorded in this spec.
- S7: contact-sheet.png exists and is at least 1280 pixels wide; at least nine sampled stills exist under frames/ and each is 1920x1080.
- S8: blender/ holds at least one Python build script, and production-notes.md carries the render statistics (a Blender 4.5 version string and a total frames figure).

The deterministic part of these checks (S1 to S8) is implemented in tools/video_checks_v2.py and run by the workflow after the line; its output is committed at content/youtube-anvil-v2/checks.txt.

The reviewers judge the rest: reviewer-facts maps every spoken and on screen claim to the closed list (S9). reviewer-voice judges the first person launch voice end to end, sentence by sentence (S10). reviewer-design judges the contact sheet at the section midpoints and at the transitions for motion continuity and the absence of frozen beats, and the sampled frames for brand consistency with the piece's visual language (S11).
