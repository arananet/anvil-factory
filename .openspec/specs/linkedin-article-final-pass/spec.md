# LinkedIn Article Final Pass

Status: approved
Slug: linkedin-article-final-pass

## Roles
- implementer: the content line stations (brief-writer, researcher, writer, media-producer) that produce the revised draft
- reviewer: the five content reviewers, who check the draft against this spec and the source pack
- qa: checks the scenarios below against the writer output
- product_owner: Edu, who owns the publishing decision at the human gate

## Purpose
The article revision produced by work order wo-gh-4 recorded the factory's progress but closed the Sentia exam one chapter early, carried four voice findings from its own reviewer-voice, and kept a stale reviewer count in its walkthrough of the line. Since that run, Edu decided the Sentia gate himself, rejected the deployed page's art direction, and ordered a design v2 that the line approved in full. He also supplied a short history of the software factory idea for the article's opening. This spec governs the final pass that lands all of it. The pass runs down the content line, executed, and stops at the human gate: the deliverable is a reviewed draft, never a publication.

## Requirements
- The input article lives at content/linkedin-article/article.md in this repository (the wo-gh-4 revision). The writer station reads it in full and produces the complete revised article as its output: full text, not a diff, not a summary, not an outline.
- A new section titled "Not a new idea" is inserted between the intro and "The line", carrying the history text supplied in the work order description, integrated verbatim or with only connective edits.
- The Sentia exam section closes with the final state from the work order description: the round 4 gate decision and deploy by Edu, his rejection of the flat SVG art direction, design v2 as work order wo-gh-2 on arananet/sentia, its approval with all five reviews counted and passing, and its live status. The section ends with the closing sentence given in the work order, word for word.
- Reviewer-voice's four findings from the wo-gh-4 run are fixed: the sentence fragment that ends the round 3 paragraph becomes complete prose, the two compressed sentences in that paragraph are decompressed into readable prose, the suite result line is written as prose rather than test output, and "responses calls" in the Model routing section reads "response calls".
- "The line" section counts five SDLC reviewers (spec, security, tests, architecture, design), in the reviewer walkthrough and in the approver aggregation sentence.
- The promo text at content/linkedin-article/promo-post.txt ships with its reviewer claim corrected to five reviewers in parallel. No other promo line changes unless a claim is now false; any other stale claim is flagged in the run record, not silently rewritten.
- Everything else is preserved: the title, the section order outside the one insertion, the first person voice, the image markers exactly as they are, the credit section naming only the two videos already credited, and the signature sign-off byte identical to the input article.
- Style law, checked by reviewers: no em dash and no en dash characters anywhere; the employer is never mentioned; the draft must not state or imply that it, or anything else in this run, has been published.

## Scenarios

### Scenario: The history section is in place
- S1: Given the revised article, when the opening is read, then a section titled "Not a new idea" sits between the intro and "The line" and carries the supplied history: Bemer's 1968 proposal, Hitachi's first software factory in 1969, the 2000s assembly kit, the 2010s and 2020s delivery pipeline, and the closing observation that what changed is who, or what, works the line.

### Scenario: The Sentia exam closes on the final state
- S2: Given the revised article, when the Sentia section is read to its end, then it states that round 4 ended changes_requested, that Edu overrode the human gate and deployed that build as is accepting the minor deviations, that he rejected the flat SVG art direction on sight and ordered design v2 (work order wo-gh-2 on arananet/sentia), that v2 generated four product renders with Magnific (hero, exploded view, on-skin, network scene) verified one by one with the shared caveat that the patch rims read sage and mint rather than deep ink green, that DESIGN.md was revised imagery first and the page recomposed around the renders, that the verdict was approved with all 5 reviews counted and all passing including reviewer-design, that the suite recorded 56 pass, 0 fail and 1 skipped, that Edu gave the gate word, and that v2 is live at https://sentia.info-693.workers.dev since 2026-10-29. The section's final sentence is the closing line given in the work order, word for word.

### Scenario: The voice findings are fixed
- S3: Given the revised article, when the round 3 paragraph of the Sentia section and the Model routing section are read, then no sentence fragment remains at the end of the round 3 paragraph, the paragraph's facts are carried in decompressed readable sentences, the round 3 suite result is stated in prose rather than as test output, and the Model routing section reads "response calls" where it previously read "responses calls".

### Scenario: The line counts five reviewers
- S4: Given the revised article, when "The line" section is read, then the reviewer walkthrough names five reviewers (spec, security, tests, architecture, design) and the approver sentence aggregates five reviews.

### Scenario: The promo matches the article
- S5: Given the package files, when promo-post.txt is read, then its parallel reviewer claim reads five reviewers, and every other claim in it still holds against the revised article.
