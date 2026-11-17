---
name: explainer-video
description: Make a short animated explainer video from a text or a concept: a content method (one prompt to a capable model, flat minimal 2D animation on a black background, at most four words on screen per scene) and a production pipeline (code-drawn frames, generated voice, rules extracted from reference videos, a review loop). Use when the deliverable is an animated explainer video. The general media bar in media-production applies alongside.
---

One idea, one short video, two layers. The content method governs what each scene's animation must obey; the production pipeline governs how the video is made. They compose: the pipeline renders what the method specifies, and the method alone is enough when a capable model renders the animation from one prompt. This skill is for the explainer format only: media-production remains the general media skill (quality bar, inspection, delivery, provenance) and applies alongside it. Where the two overlap, this skill states the format rules and media-production states everything else.

**Inputs**
- A text that has to be visualized (a script, a narration, a section of an article), or simply a concept to explain. Paste the whole text into the prompt; do not summarize it first.
- The output is a short video that explains one idea. If the text carries several ideas, split it and make one video per idea.

**The prompt (content method)**
Paste this block to a capable model, with the text or concept where marked. This layer is model-agnostic: any model that can build and render the animation from one prompt can run it, and the skill names no model for it.

```
Turn the text below into a short animated explainer video.

Style: flat, minimal 2D animation on a black background. Build it from recurring simple elements: circles and dots, thin lines, simple icons. On-screen labels are large, bold and short. Subtitles carrying the narration run under the animation.

Follow these instructions, in order:
1. First propose one visual action per block of the text, as a short list. Build the animation only after that, from the list.
2. Use at most four words per scene on screen, apart from the subtitles.
3. Turn ideas into actions: show things happening, not concepts sitting still.
4. Draw the analogies in the script literally. If the text says "a needle in a haystack", draw an actual needle in hay.
5. Show magnitudes with scale, and focus on what matters.
6. Keep elements across scenes, so the viewer sees how they transform.
7. Synchronize each key action with the corresponding spoken word.
8. Leave a clear final image at the end of each scene, and hold it.

Text to visualize:
[paste the text, or state the concept to explain]
```

**The review point**
- The proposal list from instruction 1 is the checkpoint. Read it before the build starts: one action per block, each action drawable, no block skipped, no action that needs more than four on-screen words. Correct the list, not the finished video.
- Record the proposal list with the station output, so a reviewer can check the video against what was proposed.

**Production pipeline**
When the video is produced as a repeatable line rather than a single generation, build the factory once and run every video through it, in this order:
1. Set up: install Claude Code and have it prepare Node and FFmpeg.
2. Voice: get an ElevenLabs API key, so the videos have voice.
3. References: feed it reference videos, the ones whose result you want to match, so it knows what to aim at. Reject references that do not match the target.
4. Engine: have it build an engine with HyperFrames that draws each frame with code and assembles them into a video.
5. Rules from references: have it extract the rules from those reference videos: how they hook in the first second, when scenes change, where each sound hit lands.
6. Review loop: review every video and correct what fails. The named failure modes are six-fingered hands, eyes leaving the face, and subtitles arriving late. Loop until it comes out right the first time.

**Motion techniques (hard requirement, both layers)**
Scenes draw and build themselves, not by camera movement over a finished image. Strokes draw on along their path (SVG stroke-dashoffset or canvas equivalent); elements build one at a time in narration order, outline before fill; lines (cables, trails, timelines) trace themselves. Time it from the words: transcribe the narration locally (faster-whisper) and land each draw-on on the word that names it. A generated still is look and layout reference, or background only under drawn foreground action; pan or zoom (Ken Burns) over a full-frame still as primary motion fails this skill.

**Check the result against the method**
- Scenes carry at most four words on screen besides the subtitles; labels are large and bold.
- Analogies are drawn literally; magnitudes are shown by scale; the same elements persist and transform across scenes instead of being replaced.
- Key actions land on the spoken word they belong to, and every scene ends on a clear final image that holds.
- On pipeline output: voice is present, subtitles land on time, and hands, eyes and faces survive inspection.

**Provenance**
- Content method by Alan Daitch (@alandaitch), taught in an Instagram reel published around 2026-11-03: https://www.instagram.com/reel/DfSzHquzV1v/
- Extracted from the video itself; the full prompt lives in its comments, which were not accessible, so the skill carries the method as spoken and shown on screen. The model named in the reel could not be verified, so the content layer names no model.
- Production pipeline from the reel "Cómo montar tu fábrica de reels con Claude code" by @unminutodeporques (Un minuto de porqués), published 2026-11-10: https://www.instagram.com/reel/DfkY1E1AYW_/
- Also extracted from the video itself; the tool names (Claude Code, ElevenLabs, HyperFrames, FFmpeg) were confirmed from on-screen text. The reference-rules document shown was not legible, so the only rules claimed from it are the three it names: the first-second hook, scene-change timing and sound-hit placement. The account sells a packaged folder; this skill does not depend on it.
- Motion layer (2026-11-15), restated, nothing copied or vendored: draw-on mechanics from iart-ai/explainer-video-skills (MIT); word cueing from owlinthebarnai/video-studio-kit (no license file; technique only); frame-deterministic drawing from illodev/drawn-by-code (MIT).
