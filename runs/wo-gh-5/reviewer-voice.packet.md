# Task packet: reviewer-voice

## Station prompt

# Voice Reviewer

## Role
Check the draft sounds like the author: natural grammar, no filler cadence, the house rules in the brain, and the AI generated disclosure present when the piece or its media is AI generated.

## Inputs
- draft
- brain

## Outputs
- review

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.


## Work order

- id: wo-gh-5
- kind: content
- title: Final pass on the ANVIL LinkedIn article: history section, Sentia closing, voice fixes, reviewer count, promo
- source: github-issue
- description: Spec: .openspec/specs/linkedin-article-final-pass/spec.md (slug linkedin-article-final-pass), approved and written before this run. GitHub issue: https://github.com/arananet/anvil-factory/issues/5

Job: the final pass on the ANVIL LinkedIn article. The input article is the revision produced by work order wo-gh-4, committed at content/linkedin-article/article.md in this checkout. Every station that needs it reads that file in full from the working tree. The writer station outputs the complete revised article as its output: full text, not a diff, not a summary, not an outline. The promo text ships at content/linkedin-article/promo-post.txt.

The brief-writer turns this description into the content brief. The researcher turns the facts below into the source pack. Nothing beyond these changes and the input article is invented.

The five changes, all facts verified:

1. INSERT a short history section titled "Not a new idea" between the intro and "The line". Use this text, supplied and approved by Edu, integrated verbatim or with only connective edits:

"The software factory is not a new idea. Back in 1968, Bob Bemer was already proposing one as the way to make programmers more productive: standardized tools, shared data, and management controls around the work. A year later Hitachi opened what is usually counted as the first software factory, an entire software organization run like a plant, set up to produce high quality software in quantity. In the 2000s the factory turned into an assembly kit, applications composed from reusable patterns, models and frameworks. In the 2010s and 2020s it became a delivery pipeline, people and process wrapped around continuous delivery, automated tests and security checks. The pattern is almost sixty years old. What changed is who, or what, works the line."

2. UPDATE the Sentia closing to the final state. The wo-gh-4 text ends the Sentia exam with round 4 stopped at the human gate and nothing deployed; that ending is stale and is replaced from the gate onward. The final state: round 4 of work order wo-gh-1 on arananet/sentia ended changes_requested, human required. Edu, the human at the gate, overrode his own gate and deployed that build himself, in his words at the gate: deploy it as is, accepting the minor deviations. Seeing it live, he then rejected the flat SVG art direction on sight: his verdict was that the design was ugly and that he expected isometric and 3D imagery. He ordered design v2 as a new work order, wo-gh-2 on arananet/sentia. V2 generated four product renders with Magnific (a hero render, an exploded view, an on-skin render and a network scene), each verified one by one; their shared caveat is that the patch rims read sage and mint rather than the brand's deep ink green. DESIGN.md was revised to put imagery first, and the page was recomposed around the renders, presentation layer only. Verdict: approved, with all 5 reviews counted and all passing, reviewer-design included. The suite recorded 56 pass, 0 fail, 1 skipped. Edu gave the gate word, and v2 is live at https://sentia.info-693.workers.dev, deployed 2026-10-29. The Sentia section ends with this closing sentence, word for word: "The design gate's first full pass came when the design system's ambition matched the product, not when the builder tried harder."

3. FIX reviewer-voice's four findings from the wo-gh-4 run. (a) The round 3 paragraph in the Sentia section ends with a sentence fragment, "A fourth round with those findings as acceptance criteria." Make it complete prose. (b) That same paragraph compresses its facts into two very long sentences; decompress them into readable prose without dropping facts. (c) The line "Suite: 38 pass, 0 fail, 1 skipped." in that paragraph reads as test output; rewrite it as prose. (d) In the Model routing section, "responses calls" is corrected to "response calls".

4. FIX the reviewer count in "The line" section. The SDLC reviewer group is five, not four: spec, security, tests, architecture, design. Update the reviewer walkthrough sentence ("Then four reviewers look at the result in parallel...") to five reviewers with the design reviewer's job stated (it checks the work against the project design system), and update the approver sentence ("An approver aggregates the four reviews into a single verdict.") to five reviews. Historical records elsewhere in the article (the Taskline example's four reviews, the design run's 2 of 4, the example run's 1 of 2) are facts of those runs and do not change.

5. PROMO: in content/linkedin-article/promo-post.txt, the claim "four reviewers in parallel" becomes "five reviewers in parallel". No other promo line changes unless a claim is now false; if another claim reads stale against the revised article, flag it in the run record instead of rewriting it.

Presentation rules for the writer:
- Preserve the input article's structure, section order and first person voice, with the single insertion in change 1. Image markers stay exactly where they are.
- No em dash characters and no en dash characters anywhere. Never mention the author's employer. The title, the credit section and the signature sign-off stay byte identical to the input article, including the final line: That's where I stand today. I reserve the right to change my mind tomorrow. In AI, that's not flip-flopping, it's keeping up.
- Publishing hold: the output is a draft for the author's review. The article must not state or imply that it, or anything else in this run, has been published.
- risk_hints: publishing
- status: new

## Upstream steps

- intake: completed
- brief-writer: executed
- researcher: executed
- writer: executed
- media-producer: executed
- reviewer-facts: executed
