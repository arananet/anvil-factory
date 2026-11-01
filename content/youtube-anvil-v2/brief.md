# Content brief: ANVIL, a launch film rendered in Blender

Work order: wo-gh-18 (GitHub issue 18). Spec: .openspec/specs/youtube-anvil-video-v2/spec.md (slug youtube-anvil-video-v2). Inputs used: the work order, the spec and the brain (brain/project.md, brain/glossary.md). Nothing in this brief goes beyond them.

## Purpose

One 60 to 90 second YouTube launch film about ANVIL, produced by the factory's own content line (pipelines/content-video.json) and rendered as a real animated 3D sequence in headless Blender 4.5. The piece stops at the human gate. Nothing is published by this work order.

## Audience

Developers and technical leads who build software and are curious how a line of AI-staffed stations can deliver reviewed work while a human stays in control. They know what a code review is. They do not know ANVIL. They watch a short film, so each section carries one idea, spoken in plain sentences while something visibly moves.

## Angle

A product launch told by the product. ANVIL speaks in first person (I, we) from its first words, which are exactly: Introducing ANVIL. The voice states what the factory does today, never what it promises to become. The visual argument is a chain that the camera follows physically: one intake enters, the spec is written first, stations build along a line, five reviewers act at once, a human approves, a verified memory sits beside the line, and a real product (Sentia) is the proof. The film closes by saying it came off the same line and stopped at the human gate.

## Voice rules (bind every station)

- First person, launch register, from the first line to the last. Never narrate the factory from outside in third person.
- Natural, full sentences a person would say aloud. No stacked fragments, no row of slogans.
- No hype words (no revolutionary, game changing, cutting edge, supercharge, unleash, or similar).
- No em dashes and no en dashes anywhere, including script, storyboard, on screen text and production notes.
- At least eight first person pronouns in the narration. None of: "ANVIL is a", "ANVIL is an", "ANVIL keeps", "ANVIL designed", "ANVIL built", "the factory is", "the factory keeps".
- Name nobody and nothing outside the claim list: no employer of the author, no other factory, product, video or person.

## Format and constraints

- One MP4 at content/youtube-anvil-v2/anvil-youtube-v2.mp4: 1920x1080, H.264 plus AAC, 30 fps, 60 to 90 seconds.
- English narration, edge-tts voice en-US-ChristopherNeural, 150 to 200 words in total across seven sections, each with a Target timing in M:SS form.
- Procedural sound bed generated in the run. No third party music or stock material.
- Only committed visual asset: assets/patch-one.glb (the Sentia Patch One, first party). Everything else is built by Blender scripts inside the run.
- Every section has real motion from the render: camera and subjects move. No still frames, no pan or zoom over a still.
- Visual language: paper background, ink green, emissive teal accents.

## Section plan

| # | Section | Visual action | On screen text (exact) | Job of the section |
|---|---------|---------------|------------------------|--------------------|
| 1 | Introducing | Empty paper space; the line table and station posts assemble in sequence as the camera dollies in | ANVIL | Open with "Introducing ANVIL" and say I am a software factory: work enters as an intake and leaves as reviewed, approved output. |
| 2 | One intake | A work order card flies along the line and lands at its head | One intake | Say the intake is one of three things: a feature, an idea, or an issue. |
| 3 | Spec first | The card unfolds into a spec document that completes before any station moves | The spec comes first | Say I write the spec before any code. |
| 4 | The line builds | The piece travels down the line, camera tracking beside it; stations work in sequence and attach components | Stations build | Say specialized stations do the work in a line and no station approves its own work. |
| 5 | Five reviewers in parallel | The piece halts at a gantry; five reviewer posts light up teal together and scan it | Five reviewers in parallel | Say five reviewers check the work in parallel. |
| 6 | Human gate and memory | A hand rises to approve the piece; shelves slot in verified learnings; a quarantine lane holds unverified proposals behind glass | A human approves. Verified memory. | Say a human approves before anything ships and nothing passes without it; a learning enters my memory only with provenance tied to a run record, and unverifiable proposals wait in quarantine. |
| 7 | Proof and close | Patch One rises on a plinth, separates into five layers in stack order, settles back; slow orbit | Sentia, then sentia.info-693.workers.dev, then Designed and built end to end by ANVIL | Say Sentia is a concept sensor patch product I designed and built end to end, live at sentia.info-693.workers.dev with an interactive page where its five layers come apart. Say station models are routed per station through Cloudflare AI Gateway and the work lives on GitHub, that I am open source under Apache 2.0, and that this video was produced by my content line and stopped at the human gate. |

Suggested narration weighting (about 175 words): 1: 22, 2: 18, 3: 15, 4: 28, 5: 18, 6: 36, 7: 38. The writer may adjust within the 150 to 200 total. Section 7 carries the most claims, so the writer should watch its pacing against the render time of the orbit.

## Claims the piece will make (closed list from the spec)

Nothing outside this list may be spoken or shown. Counts allowed: three intake kinds, five reviewers, five Sentia layers, and nothing else. Phrase each claim in first person.

| ID | Claim | Source needed |
|----|-------|---------------|
| C1 | I am a software factory: work enters as an intake and leaves as reviewed, approved output. | Repository: brain/project.md, README, docs/ARCHITECTURE.md |
| C2 | The intake is one of three things: a feature, an idea, or an issue. | Repository: intake station manifest and prompt |
| C3 | The spec is written before any code. | Repository: brain/project.md (spec before code), .openspec/specs/ |
| C4 | Specialized stations do the work in a line, and no station approves its own work. | Repository: brain/project.md, station manifests, pipelines/ |
| C5 | Five reviewers check the work in parallel. | Repository: pipeline files and reviewer station manifests (the count must be confirmed against a pipeline carrying five reviewers, and the researcher must flag any mismatch rather than adjust the claim) |
| C6 | A human approves before anything ships; nothing passes the human gate without that approval. | Repository: pipelines/, triage-human and publisher stations |
| C7 | I keep a verified memory: a learning enters it only with provenance tied to a run record, and proposals that cannot be verified wait in quarantine. | Repository: brain/ memory rules, brain/learnings.md header, observer station files |
| C8 | The models that staff the stations are routed per station through Cloudflare AI Gateway, and the work lives on GitHub. | Repository: tools/anvil_station.py, tools/claude_station.py, anvil.yaml |
| C9 | I am open source under the Apache 2.0 license. | Repository: LICENSE |
| C10 | Sentia is a concept sensor patch product that I designed and built end to end. It is live at sentia.info-693.workers.dev, including an interactive page where its five layers can be taken apart. | Live Sentia site; GLB provenance in the spec's Assets section |
| C11 | This video was itself produced by my content line: written, rendered, produced and reviewed by my stations, and it stopped at the human gate. | Repository: pipelines/content-video.json and this run's artifacts |

## Open points for the researcher

- Pipelines in this repository describe the review panel for this content variant as four reviewers (facts, voice, brand, design). The claim "five reviewers check the work in parallel" is on the spec's closed list as written. The researcher must cite where five parallel reviewers exist (for example the default software pipeline) and note the scope, so the reviewer-facts station can judge the wording. The brief does not add, drop or rephrase the claim.
- The brain files do not mention Cloudflare AI Gateway, Apache 2.0 or Sentia. The sources for C8, C9 and C10 are the tools, LICENSE and the live site, not the brain.

## What is missing from the inputs

Nothing blocks the brief. The design tokens in the packet are all TODO, so the visual language comes from the spec (paper, ink green, teal) and no color values are fixed here. The media-producer picks exact values and records them in production-notes.md.
