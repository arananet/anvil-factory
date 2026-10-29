# LinkedIn Article Update

Status: approved
Slug: linkedin-article-update

## Roles
- implementer: the content line stations (brief-writer, researcher, writer, media-producer) that produce the revised draft
- reviewer: the five content reviewers, who check the draft against this spec and the source pack
- qa: checks the scenarios below against the writer output
- product_owner: Edu, who owns the publishing decision at the human gate

## Purpose
The ANVIL LinkedIn article was finalized on 2026-10-28 and the factory has moved since. It built per project design systems into itself through an executed run, adopted a per station model routing policy, found a working route to GPT-6 Astra after its first route failed at the smoke gate, and put the design system to a real exam on the Sentia launch page across four executed rounds. This spec governs the article revision that records all of that. The revision itself runs down the content line, executed, and stops at the human gate: the deliverable is a reviewed draft, never a publication.

## Requirements
- The input article lives at content/linkedin-article/article.md in this repository. The writer station reads it in full and produces the complete revised article as its output: full text, not a diff, not a summary, not an outline.
- Every new claim in the revision traces to the verified facts in the work order description (issue 4). The researcher station turns those facts into the source pack; the writer invents nothing beyond them.
- The station catalog count is 25, verified by listing stations/ on main after PR #3 merged. Any earlier count in the input article is corrected.
- The structure, voice and section order of the input article are preserved unless a section must change to carry the new facts. New material earns its place: a design system section, the model routing policy where the article discusses models, the Astra access story told honestly, and the Sentia exam as the closing proof.
- Image placements use exactly these markers: [IMAGE: cover.png], [IMAGE: diagram-1-the-line.png], [IMAGE: diagram-6-station-catalog.png], [IMAGE: diagram-3-station.png], [IMAGE: diagram-2-domains-modes.png], [IMAGE: diagram-4-design-system.png], [IMAGE: diagram-5-model-routing.png].
- Style law, checked by reviewers: no em dash and no en dash characters anywhere in the text; the employer is never mentioned; the signature sign-off is byte identical to the input article; the credit section remains, naming only the two videos already credited there.
- Where an approval rested on a subset of the reviews produced, the article says so. Where a run is still waiting at a human gate, the article says that too, and claims no deploy that did not happen.

## Scenarios

### Scenario: Design systems enter the article
- S1: Given the revised article, when the design system section is read, then it states that scaffolding creates design/DESIGN.md and design/tokens.json only when absent and never overwrites them, that the project design system is injected into station packets, that reviewer-design sits in sdlc-default and both content pipelines, that a missing design system is a visible run warning, that the factory dogfoods its own design folder, and that the design run's approval counted 2 of 4 reviews because two reviewers returned prose that failed to parse.

### Scenario: Model routing is stated as policy
- S2: Given the revised article, when the model discussion is read, then it states that UI and design stations run GPT-6 Astra (openai/gpt-6-astra) through the Cloudflare AI Gateway, that the non-UI builder runs Claude Opus 5.5, that reviewers, the spec writer and the test writer run Claude Sonnet 5.5, and that the driver includes the retirement of claude-sonnet-4-5 from the Anthropic API on 2026-11-30 after its deprecation on 2026-09-30, with station models taken from configuration rather than hardcoded.

### Scenario: The Astra access story is honest
- S3: Given the revised article, when the access story is read, then it states that the gateway's classic provider endpoints do not fall back to Unified Billing and demand a stored BYOK key, that the first Sentia runs stopped at the smoke gate on OpenAI 401 errors, that the unified endpoints on api.cloudflare.com do serve Cloudflare managed credentials and were verified live, and that a dedicated CI token scoped to Workers AI Write was minted and stored as a repository secret without its value appearing in chat or files.

### Scenario: The Sentia exam closes with round 4's real verdict
- S4: Given the revised article, when the Sentia section is read, then it recounts the four rounds (smoke gate stop, wrapper crash and unrouted design reviewer, sandbox rejection, real execution with reviewer-design requesting changes on three findings), and closes with round 4: verdict changes_requested with a human required, the four acceptance criteria fixed in the diff, the suite at 44 tests with 43 pass, 0 fail and 1 skip, reviews counted 5 of 5 with four passes, reviewer-design requesting changes again on four smaller findings, and no deployment claimed.

### Scenario: The honest limits are current
- S5: Given the revised article, when the honest limits section is read, then it no longer claims that a full executed model run is unproven; it states what the executed runs proved and what they exposed, including reviewer parse failures and approvals that rested on a subset of reviews.

### Scenario: The example run record is current
- S6: Given the revised article, when the examples section is read, then the issue 3 example run is described with its executed ending: verdict approved, deployment deployed_verified, and the caveat that the approval counted 1 of 2 reviews.
