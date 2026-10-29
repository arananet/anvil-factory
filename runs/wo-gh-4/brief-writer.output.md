I cannot write the brief to a file because the Write tool is disabled in this session. However, I'll provide the complete brief as output. In a normal execution, this would be written to `content/linkedin-article/brief.md`.

---

# Content Brief: ANVIL LinkedIn Article Update

## Audience

LinkedIn professionals interested in:
- AI-driven software development
- Coding agents and automation
- Software engineering processes
- Design systems and quality control
- Technical architecture decisions

Primary reader profile: Technical decision-makers, engineering leaders, and developers evaluating or building agent-based workflows.

## Angle

This is a progress report, not a launch piece. The original article described ANVIL's design and promise. This update proves what actually works: the factory has now run real work through the line, built improvements into itself, made hard technical choices about model routing, and faced honest failures on the way to honest successes.

The tone shifts from "here's what I built" to "here's what it did when I put it to work."

## Core Claims and Sources

### Claim 1: Per-project design systems are now built into the factory itself
**Source**: Verified fact 1 (work order wo-gh-1, GitHub Actions run 40778873024, PR #3 merged 2026-10-28)

**What to state**:
- Scaffolding creates design/DESIGN.md and design/tokens.json only when absent, never overwrites existing design systems
- When a project has a design system, station packets for interface-producing stations receive its tokens and quality bars
- A new station, reviewer-design, now sits in sdlc-default and both content pipelines to judge interface output against the project design
- When a pipeline includes interface-producing stations but the project has no design system, the run report carries a visible warning
- The factory dogfoods its own design folder
- The station catalog now holds 25 stations (correcting any earlier count of 24)

**Caveat to preserve**: The approval counted 2 of 4 reviews because reviewer-spec and reviewer-architecture returned prose that failed to parse as review JSON.

**Location in article**: New section on per-project design systems, positioned after "Composable stations, and the Core Four"

### Claim 2: Model routing is now policy, not hardcoded configuration
**Source**: Verified fact 2 (decided by Edu)

**What to state**:
- UI and design stations run GPT-6 Astra (model id openai/gpt-6-astra) through Cloudflare AI Gateway
- The non-UI builder runs Claude Opus 5.5
- Reviewers, the spec writer, and the test writer run Claude Sonnet 5.5
- Driver for the change: claude-sonnet-4-5 was deprecated on 2026-09-30 and retires from the Anthropic API on 2026-11-30
- Station models are now taken from each station's configuration instead of being hardcoded in a wrapper

**Location in article**: Within "Composable stations, and the Core Four" section where models are discussed, after the mention of "Different stations get different models"

### Claim 3: Getting to GPT-6 Astra required honest technical problem-solving
**Source**: Verified fact 3 (the Astra access story)

**What to state**:
- The gateway's classic provider endpoints do not fall back to Unified Billing and demand a stored BYOK key
- First Sentia runs stopped at the smoke gate with OpenAI 401 errors
- The unified endpoints on api.cloudflare.com do serve Cloudflare managed credentials
- This was verified live with chat completions and responses calls returning the exact control replies
- A dedicated CI token scoped to Workers AI Write only was minted and stored as a repository secret
- Its value never appeared in chat or in any file

**Location in article**: New subsection within the model routing discussion or as a technical note in the Sentia exam section

### Claim 4: The Sentia exam is a real test under real constraints across four rounds
**Source**: Verified facts 4 and 5 (work order wo-gh-1 on arananet/sentia, rounds 1-4)

**What to state**:

**Context**: Sentia is a mock startup whose launch page shipped correct and live but visually basic - the gap that motivated the design system work.

**Round 1**: Stopped at the Astra smoke gate, the 401 wall (see Claim 3).

**Round 2**: Executed but the builder wrapper crashed in tempdir cleanup. A second wiring bug left reviewer-design unrouted. The approval counted only 4 of 5 reviews and the verdict was changes_requested.

**Round 3**: Rejected. The Codex bubblewrap sandbox cannot run on GitHub hosted runners, so the builder could run no commands at all. Reviewers correctly rejected an empty change.

**Round 3 resolution**: With the sandbox bypassed on the throwaway runner (same posture the Claude stations already use), the line executed for real. The Astra builder created Sentia's design/DESIGN.md first, then elevated the page against it (presentation layer only). Security and architecture reviewers confirmed no behavior change.
- Suite: 38 pass, 0 fail, 1 skipped
- Reviews: 5 of 5 parseable, four passes
- reviewer-design (also running Astra) requested changes with three concrete findings against the builder's own design system: small width type below documented minimums, spacing values off documented rhythm, and palette drift
- Edu took the human gate decision: a fourth round with those findings as acceptance criteria

**Round 4** (GitHub Actions run 40814522329): Verdict changes_requested, human required.
- The builder fixed all four acceptance criteria in the diff: hero keeps 56px floor at small widths, body copy at documented 17px, off-rhythm spacing values gone, palette matches design file, 800ms reveal motion restored
- design/DESIGN.md itself gained the rhythm and motion rules
- Suite grew to 44 tests: 43 pass, 0 fail, 1 skipped (the skip is a git-diff scope test that needs a main ref in checkout; reviewers verified scope by hand)
- Reviews: 5 of 5, all parseable. reviewer-spec, reviewer-security, reviewer-tests, and reviewer-architecture passed
- reviewer-design requested changes again with four smaller findings: nav padding overriding documented horizontal gutters, footer prose at 13px against 17px body minimum, label size and tracking tokens, and white fills on two elements not in the physical patch
- Run stopped at the human gate again, decision is Edu's

**Critical**: Nothing has been deployed. The live Sentia page still serves the original design because the deployer never runs past a gate like this.

**Location in article**: New section as the closing proof, positioned before "Where to look"

### Claim 5: The example project now has an executed ending
**Source**: Verified fact 6 (work order wo-gh-3 on arananet/anvil-example-taskline, issue 3)

**What to update**:
- Change from "verdict reads no_reviews" to executed ending
- Verdict: approved, human not required
- Deployment: deployed_verified
- The builder diff was exactly the missing test, with the API file byte identical to main
- Caveat to preserve: The approval counted 1 of 2 reviews because the spec reviewer's answer did not parse

**Location in article**: "What the examples prove" section, update the paragraph about issue 3

### Claim 6: Test coverage has grown as the factory has grown
**Source**: Verified fact 7 (test counts recounted)

**What to update**:
- Ninety-four tests now cover the factory itself (up from eighty-nine, plus five design system tests)
- Six cover the example
- Nine cover the intake worker

**Location in article**: "Where to look" section, first paragraph

### Claim 7: The honest limits have shifted from "unproven" to "proven with known gaps"
**Source**: Synthesis of verified facts 1, 4, 5, 6 (the executed runs and their caveats)

**What to state**:
- Full executed model runs are no longer unproven - they have happened
- What the executed runs proved: The line can run real work, produce real changes, and reject work that fails quality gates
- What they exposed: Reviewer parse failures still happen (documented in multiple approvals), and multiple approvals have rested on a subset of the reviews produced rather than all reviews parsing successfully
- This is not theoretical anymore - these are the limits of the current implementation under real use

**Location in article**: "The honest limits" section, complete rewrite of the paragraph starting "What is not proven yet"

## Structure Preservation

The existing article structure is sound. New material fits as:
1. Keep all existing sections in their current order
2. Add per-project design systems section after "Composable stations, and the Core Four"
3. Integrate model routing policy within the existing model discussion in "Composable stations"
4. Include Astra access story as a technical aside (can be inline with model routing or within Sentia exam)
5. Add Sentia exam as new section before "Where to look"
6. Update "The honest limits" section with rewritten assessment
7. Update "What the examples prove" with new example ending
8. Update test counts in "Where to look"

## Presentation Rules

### Voice and tone
- Preserve first person voice throughout
- Maintain the plain-spoken, honest style of the original
- This is a progress report from someone who is building in public and reporting what actually happened

### Image markers (exact placement)
- [IMAGE: cover.png] at the top (existing)
- [IMAGE: diagram-1-the-line.png] in "The line" (existing)
- [IMAGE: diagram-6-station-catalog.png] in stations section (new)
- [IMAGE: diagram-3-station.png] in stations section (existing)
- [IMAGE: diagram-2-domains-modes.png] in "One core, software and content" (existing)
- [IMAGE: diagram-4-design-system.png] in new design system section (new)
- [IMAGE: diagram-5-model-routing.png] where routing policy is stated (new)

### Style constraints
- No em dash characters (—) anywhere
- No en dash characters (–) anywhere
- Never mention the author's employer
- The signature sign-off must remain byte identical: "That's where I stand today. I reserve the right to change my mind tomorrow. In AI, that's not flip-flopping, it's keeping up. 🥤"
- Credit section stays unchanged, naming only the two videos already credited

### Publishing hold
- This is a draft for author review
- Do not state or imply that this update, or anything in this run, has been published
- Use past tense for completed work, but never claim publication

## Quality Gates for Writer

The writer output must:
1. Trace every new claim to one of the seven verified facts above
2. Preserve all caveats about partial review counts
3. State clearly when a run is waiting at a human gate
4. Not claim any deployment that did not happen
5. Correct the station count to 25
6. Include all seven image markers in their specified locations
7. Follow all style constraints (no em/en dashes, employer never mentioned, sign-off byte identical)
8. Maintain the article's existing structure and voice while integrating the new material

## Risk Note

This brief includes a `risk_hints: publishing` flag. The writer must not treat this draft as published content. The article is a draft pending author review.

---

**Station output complete**: Content brief produced. The brief maps seven verified facts to seven claims, specifies where each fits in the existing article structure, and establishes the quality gates for the writer station. File writing is disabled, so this output appears as text rather than as `content/linkedin-article/brief.md`.
