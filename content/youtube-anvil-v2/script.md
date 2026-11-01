# ANVIL: a launch film, spoken by the factory

## Narration

### 1. Introducing
Target timing: 0:00 to 0:08

Introducing ANVIL. I am a software factory. Work comes in as an intake and leaves as reviewed, approved output.

### 2. One intake
Target timing: 0:08 to 0:15

Every job starts as one intake, and that intake is a feature, an idea, or an issue.

### 3. Spec first
Target timing: 0:15 to 0:20

Next, I write the spec. It comes first, before any code.

### 4. The line builds
Target timing: 0:20 to 0:28

Then my specialized stations work down the line, one after another, and no station ever approves its own work.

### 5. Five reviewers in parallel
Target timing: 0:28 to 0:34

Five of my reviewers then check the work in parallel, all at the same moment.

### 6. The human gate and the memory
Target timing: 0:34 to 0:51

Then a human approves before anything ships, and nothing passes my gate without that approval. I keep a verified memory too. A learning enters it only with provenance tied to a run record, and proposals I cannot verify wait in quarantine.

### 7. Proof and close
Target timing: 0:51 to 1:20

Sentia is a concept sensor patch product I designed and built end to end. It is live at sentia.info-693.workers.dev, where an interactive page takes its five layers apart. My models are routed per station through Cloudflare AI Gateway, and my work lives on GitHub. I am open source under Apache 2.0. My content line wrote, rendered and reviewed this video, and it stopped at the human gate.

## Notes for the media producer

- Feed each section's narration text to edge-tts exactly as written above, without the heading or the Target timing line.
- The timings are estimates at the default speech rate of en-US-ChristopherNeural, with a short pad per section. Measured durations win; the total should land near 80 seconds, inside the 60 to 90 second window.
- Section 3 is short on purpose. Its visual (the card unfolding into a complete spec before any station moves) needs about five seconds, so pad the section to at least that if the narration runs shorter.
- Section 7 carries the most claims and runs about 29 seconds, which gives the Patch One time to rise, separate into five layers and settle back during the slow orbit.
- The address sentia.info-693.workers.dev is spoken as written. If the voice reads it badly, record that in production-notes.md rather than changing the words.

## Claim trace (for reviewer-facts)

Every spoken claim maps to the closed list in the spec, as sourced in source-pack.md.

| Section | Spoken claim | Claim ID |
|---------|--------------|----------|
| 1 | I am a software factory; work comes in as an intake and leaves as reviewed, approved output. | C1 |
| 2 | Every job starts as one intake: a feature, an idea, or an issue. | C2 |
| 3 | I write the spec first, before any code. | C3 |
| 4 | Specialized stations work in a line; no station approves its own work. | C4 |
| 5 | Five reviewers check the work in parallel. Stated for the factory in general, with no tie to this video's own panel (source pack flag F1). | C5 |
| 6 | A human approves before anything ships; nothing passes the gate without that approval. | C6 |
| 6 | Verified memory: a learning enters only with provenance tied to a run record; unverifiable proposals wait in quarantine. | C7 |
| 7 | Sentia is a concept sensor patch product I designed and built end to end, live at sentia.info-693.workers.dev, with an interactive page that takes its five layers apart. | C10 |
| 7 | Models are routed per station through Cloudflare AI Gateway; the work lives on GitHub. | C8 |
| 7 | Open source under Apache 2.0. | C9 |
| 7 | My content line wrote, rendered and reviewed this video, and it stopped at the human gate. No reviewer count is given here (flag F1). | C11 |

Counts stated: five reviewers and five Sentia layers. The three intake kinds are listed by name without a count. No other number is spoken apart from the address and the license version.
