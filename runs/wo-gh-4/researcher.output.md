I cannot write the source pack to a file because the Write tool is disabled in this session. However, I'll provide the complete source pack as output. In a normal execution, this would be written to `runs/wo-gh-4/researcher.output.md`.

---

# Source Pack: ANVIL LinkedIn Article Update

This source pack provides primary sources for every claim in the content brief, with direct links and exact facts each source supports.

---

## Source 1: Per-project design systems implementation

**Claim**: The factory now scaffolds and validates per-project design systems, dogfooding its own design folder.

**Primary sources**:
- GitHub Actions run: https://github.com/arananet/anvil-factory/actions/runs/40778873024
- Pull request: https://github.com/arananet/anvil-factory/pull/3
- Merged: 2026-10-28
- Work order: wo-gh-1 on this repository

**Exact facts from source**:
- Scaffolding now creates `design/DESIGN.md` and `design/tokens.json` for a project only when absent, never overwrites existing files
- When a project has a design system, station packets for interface-producing stations include the project design section with tokens and quality bars
- New station `reviewer-design` added to catalog, now runs in sdlc-default pipeline and both content pipelines
- When interface-producing stations run and project has no design system, run report carries visible warning
- reviewer-design must not pass vacuously without a design system present
- Factory dogfoods its own design folder (verified: `/home/runner/work/anvil-factory/anvil-factory/design/DESIGN.md` and `design/tokens.json` exist in working tree)
- Station catalog count: 25 stations (verified by directory listing of `stations/` on main branch after merge)

**Stations in catalog** (verified 2026-10-29):
approver, blueprint, brief-writer, builder, deployer, intake, media-producer, observer, publisher, researcher, reviewer-architecture, reviewer-brand, reviewer-design, reviewer-facts, reviewer-platform, reviewer-security, reviewer-spec, reviewer-tests, reviewer-voice, scout, spec-writer, supervisor, test-writer, triage-human, writer

**Recorded caveat**:
The approval verdict for this work order counted 2 of 4 reviews, because reviewer-spec and reviewer-architecture returned prose that failed to parse as review JSON.

---

## Source 2: Model routing policy

**Claim**: Station models are now per-station configuration, with specific model assignments by role.

**Primary source**:
Policy decision by Edu (internal decision, no external link)

**Exact facts**:
- UI and design stations: GPT-6 Astra (model id `openai/gpt-6-astra`) via Cloudflare AI Gateway
- Non-UI builder: Claude Opus 5.5
- Reviewers, spec writer, test writer: Claude Sonnet 5.5
- Driver for change: `claude-sonnet-4-5` deprecated 2026-09-30, retires from Anthropic API 2026-11-30
- Implementation: Station models taken from each station's configuration file, not hardcoded in wrapper

**Supporting context**:
The deprecation dates for claude-sonnet-4-5 are Anthropic published facts. The model routing decisions and gateway configuration are internal architectural choices.

---

## Source 3: GPT-6 Astra access via Cloudflare AI Gateway

**Claim**: Reaching Astra required resolving authentication failures and switching to unified endpoints.

**Primary source**:
Cloudflare AI Gateway configuration work during Sentia rounds (internal work, no external link)

**Exact facts from source**:
- Gateway's classic provider endpoints do not fall back to Unified Billing
- Classic endpoints demand a stored BYOK (bring your own key)
- First Sentia runs stopped at smoke gate with OpenAI 401 authentication errors
- Unified endpoints on `api.cloudflare.com` serve Cloudflare managed credentials
- Access verified live: chat completions and responses calls returned exact control replies
- Dedicated CI token created: scoped to Workers AI Write only
- Token stored as GitHub repository secret
- Token value never appeared in chat transcript or in any file

**Security verification**:
The token scoping and secret storage follow GitHub Actions security best practices. No credentials in code or logs.

---

## Source 4: Sentia exam across four rounds

**Claim**: The Sentia mock startup page served as real-world test of design system work, spanning four rounds with concrete findings.

**Primary sources**:
- Repository: https://github.com/arananet/sentia
- Work order: wo-gh-1 on arananet/sentia
- Round 4 GitHub Actions run: https://github.com/arananet/sentia/actions/runs/40814522329

### Context
Sentia: mock startup whose launch page shipped correct and live but visually basic. This gap motivated the design system work.

### Round 1
**Outcome**: Stopped at Astra smoke gate (401 authentication errors, see Source 3)

### Round 2
**Outcome**: Verdict changes_requested, human not required

**Exact facts**:
- Builder wrapper crashed in tempdir cleanup
- Wiring bug: reviewer-design left unrouted
- Approval counted 4 of 5 reviews (one missing due to routing bug)
- Verdict: changes_requested

### Round 3
**Outcome**: Rejected

**Exact facts**:
- Codex bubblewrap sandbox cannot run on GitHub hosted runners
- Builder could run no commands
- Reviewers correctly rejected empty change

**Round 3 resolution** (same round, sandbox bypassed):
**Exact facts**:
- Sandbox bypassed on throwaway runner (same posture Claude stations use)
- Astra builder created `design/DESIGN.md` first, then elevated page against it
- Scope: presentation layer only
- reviewer-security and reviewer-architecture confirmed no behavior change
- Test suite: 38 pass, 0 fail, 1 skipped
- Reviews: 5 of 5 parseable
- Four reviewers passed
- reviewer-design (also running Astra) requested changes with three concrete findings:
  1. Small width type below documented minimums
  2. Spacing values off documented rhythm
  3. Palette drift
- Human gate decision by Edu: proceed to round 4 with those findings as acceptance criteria

### Round 4
**Source**: https://github.com/arananet/sentia/actions/runs/40814522329

**Outcome**: Verdict changes_requested, human required

**Exact facts**:
- Builder addressed all four acceptance criteria from round 3:
  1. Hero keeps 56px floor at small widths
  2. Body copy at documented 17px
  3. Off-rhythm spacing values removed
  4. Palette matches design file
  5. 800ms reveal motion restored
- `design/DESIGN.md` gained rhythm and motion rules
- Test suite: 44 tests (43 pass, 0 fail, 1 skipped)
  - Skip reason: git-diff scope test needs main ref in checkout
  - Reviewers verified scope by hand instead
- Reviews: 5 of 5, all parseable
  - reviewer-spec: passed
  - reviewer-security: passed
  - reviewer-tests: passed
  - reviewer-architecture: passed
  - reviewer-design: requested changes with four findings:
    1. Nav padding overriding documented horizontal gutters
    2. Footer prose at 13px against 17px body minimum
    3. Label size and tracking tokens
    4. White fills on two elements not in physical patch
- Run stopped at human gate
- Decision pending (Edu's call)

**Critical deployment fact**:
Nothing deployed. Live Sentia page still serves original design. Deployer never runs past a gate in this state.

---

## Source 5: Example project executed ending

**Claim**: The anvil-example-taskline test coverage gap now has an executed ending with deployment verification.

**Primary sources**:
- Repository: https://github.com/arananet/anvil-example-taskline
- Issue: https://github.com/arananet/anvil-example-taskline/issues/3
- Work order: wo-gh-3 on arananet/anvil-example-taskline

**Exact facts from source**:
- Previous state (in current article): verdict reads `no_reviews` (packet mode, no execution)
- Current state: verdict `approved`, human not required
- Deployment: `deployed_verified`
- Builder diff: exactly the missing test
- API file: byte identical to main
- Test coverage gap resolved

**Recorded caveat**:
The approval counted 1 of 2 reviews, because spec reviewer's answer did not parse as valid review JSON.

**Context update for article**:
The article currently describes this run stopping with `no_reviews`. Update to reflect the executed ending, deployment verification, and preserved caveat about partial review count.

---

## Source 6: Test coverage growth

**Claim**: Test counts have grown as the factory has evolved.

**Primary source**:
Verified fact 7 from work order packet (test counts recounted for this update)

**Exact counts**:
- Factory itself: 94 tests (up from 89 at article finalization, +5 design system tests)
- Example project: 6 tests
- Intake worker: 9 tests

**Context for article**:
Current article states "Eighty nine tests cover the factory itself, six cover the example, nine cover the intake worker". Update factory count to ninety-four and note the five additional design system tests.

**Location in article**: "Where to look" section, first paragraph

---

## Source 7: Honest limits reassessment

**Claim**: Full executed model runs are no longer unproven, but parse failures and partial review counts remain documented issues.

**Primary sources**:
Synthesis of Sources 1, 4, 5, and 6 above (the executed runs and their recorded caveats)

**What the executed runs proved**:
- The line runs real work end to end
- Models can produce real changes
- Quality gates reject work that fails validation
- Deployment verification works (example project)
- Human gates hold when configured (Sentia, content publishing)

**What the executed runs exposed**:
- Reviewer parse failures still occur (documented in multiple approvals)
- Multiple approvals rested on subset of reviews:
  - Design system work: 2 of 4 reviews counted
  - Example project: 1 of 2 reviews counted
  - Sentia rounds: reviewer routing bugs in round 2
- These are not theoretical limits anymore: documented under real use

**Context for article rewrite**:
Current article states "What is not proven yet is the last mile: a full run where a real model does the building and the reviewing on a real change, end to end."

This is no longer accurate. Rewrite to:
1. State that full executed runs have now happened
2. List what they proved
3. List what they exposed (parse failures, partial counts)
4. Position this as current implementation limits under real use, not theoretical gaps

**Location in article**: "The honest limits" section, complete rewrite

---

## Image placement specifications

These image markers must appear exactly as specified:

1. `[IMAGE: cover.png]` - top of article (existing, preserve)
2. `[IMAGE: diagram-1-the-line.png]` - in "The line" section (existing, preserve)
3. `[IMAGE: diagram-6-station-catalog.png]` - in stations section (new)
4. `[IMAGE: diagram-3-station.png]` - in stations section (existing, preserve)
5. `[IMAGE: diagram-2-domains-modes.png]` - in "One core, software and content" (existing, preserve)
6. `[IMAGE: diagram-4-design-system.png]` - in new design system section (new)
7. `[IMAGE: diagram-5-model-routing.png]` - where routing policy stated (new)

No external image URLs. These are internal references to image files that will accompany the article.

---

## Preserved constraints

### Attribution and credits (do not modify)
- Credit section naming the two videos (Eric Risco, Dan/disler): preserve byte-identical
- Final signature: "That's where I stand today. I reserve the right to change my mind tomorrow. In AI, that's not flip-flopping, it's keeping up. 🥤" - preserve byte-identical

### Style rules
- No em dash characters (—) anywhere
- No en dash characters (–) anywhere  
- Never mention author's employer
- First person voice throughout

### Publishing hold
- This is a draft for author review
- Do not state or imply publication has occurred
- Use past tense for completed work, but never claim publication

---

## Traceability matrix

Every new claim in the article draft must trace to one of these seven sources:

| Claim in brief | Source number | Verification |
|---------------|---------------|--------------|
| Design systems scaffolding | Source 1 | PR #3, Actions run 40778873024 |
| Station count: 25 | Source 1 | Directory listing verified |
| Model routing policy | Source 2 | Internal policy decision |
| Astra access story | Source 3 | Gateway configuration work |
| Sentia rounds 1-4 | Source 4 | Actions run 40814522329 |
| Example executed ending | Source 5 | Issue 3, wo-gh-3 |
| Test count: 94 | Source 6 | Verified fact 7 |
| Honest limits update | Source 7 | Synthesis of 1, 4, 5, 6 |

No claims outside these seven sources are permitted in the draft. Existing article content is preserved where not contradicted by new facts.

---

**Station output complete**: Source pack produced with primary sources, exact facts, links, and traceability matrix for all seven claims in the content brief.
