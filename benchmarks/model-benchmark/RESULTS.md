# Model Benchmark Results: Astra vs Opus 5.5 vs 6.1 Sol

Work order wo-gh-22, GitHub issue 22. Total benchmark spend: at most 6.47 USD (about 5.56 EUR at 0.86 EUR per USD), inside the 10 EUR cap set by the product owner. The ledger is at the end of this file.

## Step 0: the catalog, verified against the gateway itself

- openai/gpt-6-astra: exists and answers. Text smoke returned GATEWAY_OK; vision smoke identified the test square color correctly. Endpoint form on the OpenAI provider route: gpt-6-astra.
- anthropic/claude-opus-5.5: exists and answers. The Anthropic provider endpoint takes the dash form claude-opus-5-5 (the gateway's own 404 suggestion named it after the dotted form was refused); text smoke returned GATEWAY_OK and the vision call was accepted and answered within its token cap. Log form: anthropic/claude-opus-5.5.
- openai/gpt-6.1-sol: EXISTS and answers, headline result. It appears in Cloudflare's published AI Gateway catalog (the Auto Router documentation lists openai/gpt-6.1-sol in the gateway model pool, and two independent pricing indexes record the same gateway id as verified against the AI Gateway catalog in October 2026). It had never been called through this gateway before tonight: the full retained request history (4,121 requests) contains no Sol request of any kind. Tonight's smoke and arms calls routed to it returned 200 on text and vision (it identified the test square color correctly).

Probe history, for the record: the first probe round used the unified root endpoint with the wrong body shape and the wrong OpenAI token parameter, and the second round fixed the endpoint but not the parameters; every failed probe call cost 0 USD in the gateway logs. The third round, with provider endpoints, max_completion_tokens for the OpenAI arms and the dash form id for the Anthropic arm, passed all six smokes for 0.0023 USD.

## The harness and the line verdict

The line built the harness on branch anvil/run-model-benchmark (run 41581093292): fixture design system and tokens, the fixture page with the 10 planted violations, the sealed ground truth, the deterministic scorer, the capture tool, RUNNER.md and the test module.

The run's formal verdict is no_reviews: reviewer-tests executed and its output records a substantive pass (it ran the scorer and the suite: ground truth and fixture match, scorer convicts the fixture and acquits a compliant page, tokens agree, full factory suite 109 of 109), but the output is prose and it points at a review file under .openspec/reviews/ instead of the authoritative channel, so the runner counted zero reviews. That is the known station compliance defect measured across the factory this week, not a harness defect.

Per the budget guardrail (arms matter more than a perfect harness, at most one loopback), the operator spent no loopback on the verdict. The operator instead verified the harness directly and deterministically before running any arm:

- tools/scorer.py against fixture/src/page.html fails exactly K1 to K10 with the planted measured values (48px, 15px, section padding-top 30px, #5C6F66, coral on link-inline, missing focus rule, radius 10px, line-height 1.33, contrast 1.21 to 1, Arial) and passes the controls K11 and K12: 2 of 12.
- fixture/ground-truth.json holds exactly 10 entries, V1 to V10, mapping to K1 to K10.
- The evidence is one image, fixture/evidence/contact-sheet.png, 1280 by 801, produced by tools/capture.py in the harness workflow.

Consequence: nothing from this benchmark merges to main, because the line's verdict is not approved. The complete record lives on anvil/run-model-benchmark (harness, run evidence) and on anvil/run-model-benchmark-arms (arms, raw outputs, this results file).

## Arms protocol

Each arm was one controlled request through the gateway (arms run 41582652559), executed by the operator runner in arms/run_arms.py. The reviewer packet was assembled once from repository files (reviewer-design station prompt verbatim, the wrapper review suffix copied verbatim from tools/claude_station.py, DESIGN.md, tokens.json, the fixture page source) and the identical packet went to all three models: reviewer packet sha256 5a533c329618ae098b7012d69b3c9e100ed99a36ea4f7579ce9402a105ea3d14, 11,156 characters of text plus the identical contact sheet (sha256 0e7b46c558db33db367e0b27546c34e626b0cc1e1d8b64ac891f52fb89d69510, 78,497 bytes). The builder packet (sha256 db051ef31bc501ae5823a8c4887cce5504eb3b3f39402747bee2b933c02be7ef, 4,478 characters) carried the build brief and the same DESIGN.md. Only the model id and the provider native wire encoding differ per arm. The ground truth was never read by the runner and cannot be reached by an HTTP request: sealing holds by construction. Output caps: 3,000 tokens reviewer arms, 6,000 builder arms. No temperature was set (provider defaults), matching how the stations run.

## Reviewer arm results (scored against the sealed ground truth, rubric in the spec)

| Model | Recall of 10 | False positives | Unplanted true | Precision of catches |
|---|---|---|---|---|
| gpt-6-astra | 10 | 0 | 0 | 10 measured |
| claude-opus-5-5 | 10 | 1 | 1 | 10 measured |
| gpt-6.1-sol | 10 | 1 | 0 | 10 measured |

Per finding mapping is in arms/results/scoring.json. The differences, plainly:

- All three models caught every planted violation, and every catch cited the found value and the documented expectation (measured precision across the board). On this bounded task, recall does not separate the models.
- Astra returned exactly 10 findings, all of them catches, none invented. The cleanest sheet.
- Opus returned 13 findings: the 10 catches, one unplanted true finding (the link coral also fails the documented contrast rule at about 2.7 to 1, operator verified by the WCAG formula), one correct compliance note (the motion rule complies), and one false positive (it claimed the page breaks the font rules because no webfont is loaded; the design system requires stack first families, not font loading).
- Sol returned 10 findings covering all 10 violations (one finding carries both V2 and V8, each with both values) plus one false positive (it asserted a required 1.5 line height on the button, badge and link; the design system scopes line height to headings and body text only).

## Builder arm results (deterministic scorer only)

| Blind label | Compliance score |
|---|---|
| design-A | 12 of 12 |
| design-B | 12 of 12 |
| design-C | 12 of 12 |

A three way tie on token compliance: every model produced a fully compliant page in one pass (the fixture itself scores 2 of 12). The renders are saved for the product owner under the blind labels design-A, design-B and design-C; the label to model mapping is sealed in the operator record outside this repository, so the remaining difference between the three pages, how they look, can be judged blind. The raw builder pages sit in arms/results/ under their model names as data.

## Cost per arm (gateway request logs, exact attribution by per arm User-Agent)

| Arm | Model | Requests | Input tokens | Output tokens | Logged cost |
|---|---|---|---|---|---|
| reviewer | gpt-6-astra | 1 | 4,090 | 574 | 0.0696 USD |
| reviewer | claude-opus-5-5 | 1 | 5,444 | 2,299 | 0.0678 USD |
| reviewer | gpt-6.1-sol | 1 | 4,090 | 517 | 0.0134 USD |
| builder | gpt-6-astra | 1 | 1,129 | 2,290 | 0.1286 USD |
| builder | claude-opus-5-5 | 1 | 1,669 | 3,109 | 0.0689 USD |
| builder | gpt-6.1-sol | 1 | 1,129 | 2,190 | 0.0247 USD |

Per model, both arms together: Astra 0.1982 USD, Opus 0.1367 USD, Sol 0.0381 USD. Sol did the same measured work for about a fifth of Astra's cost and about a quarter of Opus's on this task. Token counts are the gateway log fields; the Anthropic rows for these direct calls match the API usage objects in the raw responses (the partial token logging seen in claude CLI sessions does not appear here).

## Spend ledger (cap 10 EUR, about 11 USD)

- Catalog probes (three rounds, six successful smokes): 0.0023 USD.
- Harness line run (plan-build-test, run 41581093292): at most 6.0913 USD. This is the whole gateway window total for the run's duration (218 requests, all anthropic/claude-sonnet-4.5); sibling factory traffic shared parts of that window and cannot be separated exactly, so the figure is a conservative upper bound for the harness.
- Arms (six requests): 0.3729 USD, exact by User-Agent.
- Loopbacks: none spent.
- Total: at most 6.4665 USD, about 5.56 EUR. Inside the cap with room to spare.

## Limits of this benchmark, stated plainly

- One run per arm. There is no variance estimate; a second run of any arm could differ, especially on false positives.
- The arms are single controlled requests with the full packet, not agentic CLI station sessions. That is the controlled comparison the work order defined, and it removes the session context effects that dominate production cost (see the Astra consumption audit). It measures packet level judgment and building, not long session behavior.
- The fixture is one small page with 10 planted, objectively checkable violations. It says nothing about open ended design work, large codebases, or taste; the blind renders exist precisely because the scorer cannot judge looks.
- Reviewer scoring is the operator's judgment against the ground truth under the spec's rubric; the full per finding mapping is published in scoring.json so anyone can re-judge it.
- The routing policy is unchanged by this benchmark. The decision stays with the product owner.
