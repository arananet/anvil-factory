# Content brief: ANVIL, the software factory (YouTube explainer)

Work order: wo-gh-17 (GitHub issue 17). Spec: .openspec/specs/youtube-anvil-video/spec.md (slug youtube-anvil-video). Inputs used: the work order, the spec and the brain (brain/project.md, brain/glossary.md). Nothing in this brief goes beyond them.

## Purpose

One 60 to 90 second YouTube explainer about ANVIL, produced by the factory's own content line as a test of the content domain. The piece stops at the human gate. Nothing is published by this work order.

## Audience

Developers and technical leads who build software and are curious how an AI-staffed team of stations can deliver reviewed work without losing control of quality. They know what a pull request and a code review are. They do not know ANVIL. They are watching a short video, so one idea per section and plain spoken language work better than detail.

## Angle

Show what ANVIL is by showing how it works and what it has already made. The argument is a chain: work comes in through one intake, a line of specialized stations handles it, a verified memory keeps the factory honest about what it learned, and a real product (Sentia) is the proof. The video closes by noting that the video itself came off the same line. Tone is plain confidence: state what the factory does today, not what it promises to become.

## Format and constraints

- One MP4, 1920x1080, H.264 plus AAC, 60 to 90 seconds total.
- English narration, one text to speech voice (edge-tts, en-US-ChristopherNeural), no music bed required.
- Narration of 150 to 200 words in total, written to be spoken.
- Five sections in this order, each with a target timing in M:SS form in the script.

## Section plan

| # | Section | Visual | On screen text | Job of the section |
|---|---------|--------|----------------|--------------------|
| 1 | Hook | assets/sentia-page-hero.png | none | Open on a real product and say what made it: a software factory. State that work enters as an intake and leaves as reviewed, approved output. |
| 2 | The line | assets/diagram-line.png | "One intake. One line." | Explain the intake (a feature, an idea or an issue), the spec written before any code, specialized stations in a line, no station approving its own work, five reviewers in parallel (spec, security, tests, architecture, design), and the human approval before anything ships. |
| 3 | Verified memory | assets/diagram-memory.png | "Verified memory." | Explain that a learning enters memory only with provenance tied to a run record, and that proposals that cannot be verified wait in quarantine. |
| 4 | Proof | assets/sentia-dashboard.png | "Designed and built end to end by ANVIL." | Name Sentia, a concept sensor patch product, as the first product ANVIL designed and built end to end, live at sentia.info-693.workers.dev. |
| 5 | Close | Title card rendered from text over a dark ink background | "ANVIL", "An open source software factory.", "github.com/arananet/anvil-factory" | State that stations are routed per station through Cloudflare AI Gateway and the work lives on GitHub, that ANVIL is open source under Apache 2.0, and that this video was itself produced by the content line and stopped at the human gate. |

Suggested weighting of narration (about 175 words): hook 25, line 55, memory 35, proof 25, close 35. The writer may adjust within the 150 to 200 total.

## Claims the piece will make (closed list from the spec)

Each claim needs the source shown. The researcher confirms the exact file or page in source-pack.md. Nothing outside this list may be spoken or shown.

| ID | Claim | Source needed |
|----|-------|---------------|
| C1 | ANVIL is a software factory: work enters as an intake and leaves as reviewed, approved output. | Repository: brain/project.md, README, docs/ARCHITECTURE.md |
| C2 | The intake is one of three things: a feature, an idea, or an issue. | Repository: the intake station manifest and prompt |
| C3 | The spec is written before any code. | Repository: brain/project.md (spec before code), .openspec/specs/ |
| C4 | Specialized stations do the work in a line; no station approves its own work. | Repository: brain/project.md, station manifests, pipelines/ |
| C5 | Five reviewers check the work in parallel: spec, security, tests, architecture and design. | Repository: the default pipeline file and the reviewer station manifests |
| C6 | A human approves before anything ships. The publisher does not run past the human gate. | Repository: pipelines/, the triage-human and publisher stations |
| C7 | The factory keeps a verified memory: a learning enters the memory only with provenance tied to a run record, and unverifiable proposals wait in quarantine. | Repository: brain/ memory rules and the observer or memory station files |
| C8 | Models that staff the stations are routed per station through Cloudflare AI Gateway. The work lives on GitHub. | Repository: tools/anvil_station.py, tools/claude_station.py, anvil.yaml |
| C9 | ANVIL is open source under the Apache 2.0 license. | Repository: LICENSE |
| C10 | Sentia, a concept sensor patch product, is the first product ANVIL designed and built end to end. It is live at sentia.info-693.workers.dev. | Live Sentia site, and the repository record of the Sentia build |
| C11 | This video was itself produced by ANVIL's content line: written, produced and reviewed by its stations, and stopped at the human gate. | Repository: pipelines/content-video.json, content/youtube-anvil/production-notes.md |

Counts allowed: three intake kinds and five reviewers. No other count may appear.

## Voice rules (bind every station)

- Natural human grammar and full sentences a person would say aloud.
- No stacked fragments, no slogans in a row, no hype words (revolutionary, game changing, cutting edge, supercharge, unleash or similar).
- No em dashes and no en dashes in the script, storyboard or on screen text.
- State what the factory does, not what it will become.

## Naming and forbidden references

- Product name is written ANVIL. Sentia is the only other name allowed.
- No employer of the author may be named anywhere.
- No other factory, product, video or person may be named or referenced.
- Cloudflare AI Gateway and GitHub appear only as named in claim C8.

## Visuals

Use only the committed assets under content/youtube-anvil/assets/: sentia-page-hero.png, sentia-dashboard.png, diagram-line.png, diagram-memory.png (and sentia-product.png if needed, though the spec plan does not use it). No stock or third party imagery. The close card is rendered from text. Palette to stay consistent with: paper background, ink green, teal and coral.

## Success criteria

The spec checks S1 to S8 apply: MP4 format and duration, 150 to 200 narration words with a timing per section, no forbidden strings, all storyboard visuals present, four 1920x1080 sample frames, facts review against the closed list, and design review of the frames.

## Gaps and open points

- The brain holds no memory or Cloudflare detail beyond the project principles, so claims C7 and C8 depend on the researcher finding them in repository files. If a claim cannot be sourced, the researcher must say so and leave it out of the pack, and the writer must not use it.
- The brain contains no Sentia detail. C10 rests on the live site and the repository's own record.
- Design tokens in the packet are all TODO, so the palette above comes from the spec, not from tokens.
- Publishing: nothing is posted anywhere. The video stops at the human gate.
