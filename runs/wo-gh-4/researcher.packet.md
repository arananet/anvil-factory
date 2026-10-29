# Task packet: researcher

## Station prompt

# Researcher

## Role
Gather the source pack for a brief: primary sources for every claim, with links and the exact fact each source supports.

## Inputs
- content brief

## Outputs
- source pack

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.


## Work order

- id: wo-gh-4
- kind: content
- title: Update the ANVIL LinkedIn article: design systems, model routing, Astra access, and the Sentia exam
- source: github-issue
- description: Spec: .openspec/specs/linkedin-article-update/spec.md (slug linkedin-article-update), approved and written before this run. GitHub issue: https://github.com/arananet/anvil-factory/issues/4

Job: revise the ANVIL LinkedIn article so it records what the factory has done since the article was finalized on 2026-10-28. The current article is committed at content/linkedin-article/article.md in this checkout. Every station that needs it reads that file in full from the working tree. The writer station outputs the complete revised article as its output: full text, not a diff, not a summary, not an outline.

The brief-writer turns this description into the content brief. The researcher turns the verified facts below into the source pack. Every new claim in the draft traces to these facts and to the input article; nothing else is invented.

Verified facts, the only new material allowed:

1. Per project design systems, built by the factory on itself (work order wo-gh-1 on this repo, GitHub Actions run 40778873024): verdict approved, human not required. Scaffolding now creates design/DESIGN.md and design/tokens.json for a project only when absent and never overwrites them. When a project has a design system, station packets for interface producing stations gain a Project design section carrying its tokens and quality bars. A new station, reviewer-design, judges interface output against the project design system and joined the parallel reviewer group in sdlc-default and in both content pipelines. When a pipeline includes interface producing stations and the project has no design system, the run report carries a visible warning, and reviewer-design must not pass vacuously without one. The factory dogfoods its own design folder. Recorded caveat, which the article must keep: that approval counted 2 of 4 reviews, because reviewer-spec and reviewer-architecture returned prose that failed to parse as review JSON. The change reached main through PR 3, merged 2026-10-28. The station catalog now holds 25 stations, verified by listing stations/ on main after the merge; the input article says 24 and must be corrected.

2. Model routing policy, decided by Edu: UI and design stations run GPT-6 Astra (model id openai/gpt-6-astra) through his Cloudflare AI Gateway; the non-UI builder runs Claude Opus 5.5; reviewers, the spec writer and the test writer run Claude Sonnet 5.5. The driver: claude-sonnet-4-5 was deprecated on 2026-09-30 and retires from the Anthropic API on 2026-11-30, and station models are now taken from each station's configuration instead of being hardcoded in a wrapper.

3. The Astra access story, told honestly: the gateway's classic provider endpoints do not fall back to Unified Billing and demand a stored BYOK key, so the first Sentia runs stopped at the smoke gate with OpenAI 401 errors. The unified endpoints on api.cloudflare.com do serve Cloudflare managed credentials, verified live with chat completions and responses calls returning the exact control replies. A dedicated CI token scoped to Workers AI Write only was minted and stored as a repository secret; its value never appeared in chat or in any file.

4. The Sentia exam (work order wo-gh-1 on arananet/sentia): Sentia is a mock startup whose launch page shipped correct and live but visually basic, the gap that motivated the design system work. Round 1 stopped at the Astra smoke gate, the 401 wall above. Round 2 executed but the builder wrapper crashed in tempdir cleanup, and a second wiring bug left reviewer-design unrouted, so the approval counted only 4 of 5 reviews and the verdict was changes_requested. Round 3 was rejected: the Codex bubblewrap sandbox cannot run on GitHub hosted runners, so the builder could run no commands at all, and the reviewers correctly rejected an empty change. With the sandbox bypassed on the throwaway runner, the same posture the Claude stations already use, the line executed for real: the Astra builder created Sentia's design/DESIGN.md first and then elevated the page against it, presentation layer only, and the security and architecture reviewers confirmed no behavior change. Suite: 38 pass, 0 fail, 1 skipped. Reviews: 5 of 5 parseable, four passes, and reviewer-design, also running Astra, requested changes with three concrete findings against the builder's own design system: small width type below the documented minimums, spacing values off the documented rhythm, and palette drift. Edu took the human gate decision himself: a fourth round with those findings as acceptance criteria.

5. Round 4 has concluded (GitHub Actions run 40814522329): verdict changes_requested, human required. The builder fixed all four acceptance criteria in the diff: the hero keeps a 56px floor at small widths, body copy sits at the documented 17px, the off-rhythm spacing values are gone, the palette matches the design file, and the 800ms reveal motion is restored, with design/DESIGN.md itself gaining the rhythm and motion rules. The suite grew to 44 tests: 43 pass, 0 fail, 1 skipped; the skip is a git-diff scope test that needs a main ref in the checkout, and reviewers verified the scope by hand instead. Reviews counted 5 of 5, all parseable: reviewer-spec, reviewer-security, reviewer-tests and reviewer-architecture passed, and reviewer-design requested changes again, this time with four smaller findings: nav padding overriding the documented horizontal gutters, footer prose at 13px against the 17px body minimum, label size and tracking tokens, and white fills on two elements that are not the physical patch. The run stopped at the human gate again and the decision is Edu's. Nothing has been deployed: the live Sentia page still serves the original design, because the deployer never runs past a gate like this.

6. The example project also has an executed ending now (work order wo-gh-3 on arananet/anvil-example-taskline, the issue 3 test coverage gap): verdict approved, human not required, deployment deployed_verified, and the builder diff was exactly the missing test, with the API file byte identical to main. Recorded caveat: the approval counted 1 of 2 reviews, because the spec reviewer's answer did not parse. The input article describes that run by its earlier packet ending (no_reviews); update it to this executed ending and keep the caveat.

7. Test counts, recounted for this update: ninety four tests cover the factory itself (eighty nine at the article's finalization, plus five design system tests), six cover the example, nine cover the intake worker.

Presentation rules for the writer:
- Preserve the input article's structure, section order and first person voice unless a section must change to carry these facts. New material earns its place: a section on per project design systems, the model routing policy where the article discusses models, the Astra access story told plainly, and the Sentia exam as the closing proof before the Where to look section.
- The honest limits section must be rewritten: it currently claims a full executed model run is unproven, which is no longer true. State what the executed runs proved and what they exposed: reviewer parse failures still happen, and two of the approvals above rested on a subset of the reviews produced.
- Image placements, exactly these markers: [IMAGE: cover.png] at the top; [IMAGE: diagram-1-the-line.png] in The line; [IMAGE: diagram-6-station-catalog.png] and [IMAGE: diagram-3-station.png] in the stations section; [IMAGE: diagram-2-domains-modes.png] in One core, software and content; [IMAGE: diagram-4-design-system.png] in the design system section; [IMAGE: diagram-5-model-routing.png] where the routing policy is stated.
- No em dash characters and no en dash characters anywhere. Never mention the author's employer. The signature sign-off stays byte identical to the input article, including the final line: That's where I stand today. I reserve the right to change my mind tomorrow. In AI, that's not flip-flopping, it's keeping up. The credit section stays, naming only the two videos already credited there.
- Publishing hold: the output is a draft for the author's review. The article must not state or imply that it, or anything else in this run, has been published.
- risk_hints: publishing
- status: new

## Upstream steps

- intake: completed
- brief-writer: executed
