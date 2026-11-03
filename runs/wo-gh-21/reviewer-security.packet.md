# Task packet: reviewer-security

## Station prompt

# Reviewer Security

## Role
Check the change for security risks and unsafe defaults.

## Inputs
- code change

## Outputs
- review

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.

## Output Format

Return a JSON object with this structure:

{
  "station": "reviewer-security",
  "verdict": "pass | fail | changes_requested",
  "findings": [
    "Specific finding with reference to design system rule or quality bar",
    "Another finding if applicable"
  ]
}

The station field must equal "reviewer-security", the verdict must be one of pass, fail, or changes_requested, and findings must be a list of strings.


## Work order

- id: wo-gh-21
- kind: task
- title: Fix the excessive Astra route consumption
- source: github-issue
- description: Implement the spec in .openspec/specs/astra-consumption/spec.md in the factory. Pipeline for this order is sdlc-default (software domain, full reviewer set), selected by the run workflow.

SEQUENCING GATE: execute this order only from a main that already carries the wo-gh-16 parse contract merge. Before executing, verify that tools/claude_station.py on the run branch carries the wo-gh-16 loopback's final REVIEW_SUFFIX shape and that the station prompts carry their Output Format contract sections. If the merge is not in the branch history, stop and report instead of running. This order never modifies tools/claude_station.py, the review parsing contract, or the prompts' Output Format sections, and it preserves the capability program's changes where both touch the runner.

Build, per the spec scenarios:

S1, packet budget: the runner measures every station packet with a deterministic token estimator defined once (anvil/, standard library only), its constant visible in config and the estimate labelled an estimate wherever shown. Per station budgets come from project config (anvil.yaml) through anvil/config.py with factory defaults there, and apply to the stations routed to the Astra or Codex executor and to the interface stations (builder, writer, media-producer, brief-writer, reviewer-design). An over budget packet is trimmed in the declared order (design tokens compact instead of pretty printed; quality bars reduced to headings plus first lines; learnings limited to the most recent entries that fit) until it measures within budget; if it still exceeds, or config sets the policy to fail, the step fails before any model call with the measured size and the budget in the failure detail. An under budget packet reaches the executor byte unchanged. Per measured step the run report records measured tokens, budget and action (sent, trimmed, failed).

S2, evidence image policy: a deterministic standard library assembler combines a design review round's PNG captures into one contact sheet PNG no wider than the configured maximum (factory default 1600 px), scaling down proportionally and never up, failing loudly on a capture it cannot process. The reviewer-design packet references the contact sheet only; the full resolution originals stay byte unchanged in the run evidence. The work order model gains an optional evidence image list, default empty, existing work orders parsing unchanged; builder packets reference image evidence only when the order declares it.

S3, fresh session design review: the reviewer-design packet is assembled fresh with the station prompt, the Project design section, the spec the order implements, a diff summary the runner derives deterministically from git (files changed with added and removed line counts) and the contact sheet reference. It never contains the builder session transcript, other stations' outputs or whole worktree file contents. The packet declares a file access allowlist (files the order touches, design system files, the spec) as a contract section, and a deterministic runner check verifies no embedded content comes from outside the allowlist. Other reviewers keep their current packets in this order.

S4, stable prefix layout: _packet_text assembles stable material first (station prompt, Project design section when present, Verified learnings when present) and per run variable material last (work order block, upstream steps), so two runs of one station share a byte identical prefix up to the work order block. After this order's run, the operator records the gateway log cached values for the run's Astra requests on the issue, exactly as logged, claiming no caching saving beyond them.

S5, per station cost visibility: each executed step's run report entry records the configured model, the executed model where the runtime reports one (existing provenance), the measured packet tokens and the executor reported usage (input and output tokens) when reported, null when not. The report totals the measured packet tokens of the Astra bound stations per work order. Cost stays null unless the runtime reports a numeric cost.

Tests, mapped to the scenarios as the spec's Tests section states: estimator determinism and monotonicity; budget trim order, fail policy with no executor call, under budget byte identity, report fields; contact sheet dimensions, PNG format, originals unchanged, non PNG failure; packet layout stable prefix across two runs; scoped review packet contents and the allowlist check rejecting out of allowlist content. The full factory suite passes.

Guardrails: runtime code stays on the Python standard library only. No em dash or en dash character in any produced file (project style rule). Nothing in this order's artifacts claims a consumption saving; after the merge, a proof run (one small real design touching order through the line) reports the Astra input tokens per request from the gateway logs against the audited baseline of about 45,000 per request.

The reviewer writes its review to the authoritative review file named in its packet; prose outside that file is not a review.

GitHub issue: https://github.com/arananet/anvil-factory/issues/21

LOOPBACK (gate round 2, operator brief): round 1 executed the full line (Actions run 41581311619) and the verdict of record is no_reviews: all five reviewer stations wrote prose into their authoritative .review.json files, so the parser counted 0 of 5, failed closed and named each one; prose is not a review and round 1's outcome stands as recorded. The five raw reviewer outputs are on record in runs/wo-gh-21/ and their substantive findings, quoted and summarized below, are this loopback's scope. The implementation built the infrastructure (estimator, budget enforcement, contact sheet assembler, scoped packet builder, 17 mapped tests passing per reviewer-tests) but the reviewers found it is not wired into the executed run path and is not hardened. Fix exactly this, nothing else:

1. INTEGRATE S2 AND S3 INTO THE RUN PATH (reviewer-architecture findings 1 and 2, and reviewer-spec's integration shortfall). assemble_contact_sheet and build_reviewer_design_packet exist and pass unit tests but are never called by the run pipeline: when the runner prepares the reviewer-design step, it must assemble the round's contact sheet from the run's captures when captures exist and build the reviewer-design packet through the scoped builder, so a real run's reviewer-design packet is the fresh scoped packet of spec S3, not the standard packet. The WorkOrder evidence_images field is added but never read: builder packet assembly must consult it, including image references only when the order declares them and none otherwise.

2. FIX THE LAYER VIOLATION (reviewer-architecture finding 3). build_reviewer_design_packet imports from .stations inside the runner module, inverting the layer separation. Place the scoped packet assembly where the architecture allows and state the chosen placement in the builder output.

3. ALLOWLIST CHECK BY PROVENANCE (reviewer-architecture finding 4, reviewer-security finding 4). Pattern scanning of packet text cannot verify content provenance. The runner check must verify, deterministically, that each content block embedded in the reviewer-design packet carries a source inside the declared allowlist (tag content with its source path at assembly time and check the tags), so out of allowlist content fails the check even when its text mentions allowlisted names.

4. PNG ASSEMBLER AND PATH HARDENING (reviewer-security findings 1, 2, 3, 5, 6, in anvil/runner.py and anvil/model.py). Enforce input byte size and pixel dimension caps read from headers before any inflation of image data; verify PNG chunk CRCs; bounds check chunk lengths before reads; validate the contact sheet output path to resolve inside the run evidence directory; validate WorkOrder file path fields this order touches (including evidence image paths) to resolve inside the project tree.

5. MAKE S1 AND S5 VISIBLE IN THE REAL RUN REPORT. Round 1's runs/wo-gh-21/report.json contains no measured tokens, budget, action or usage anywhere, although the spec requires the run report to record them per measured step. After this loopback, the report must carry, per measured step: measured tokens, budget and action (sent, trimmed or failed); the executor reported usage or null; and the per work order total of measured packet tokens for the Astra bound stations as a present field (its value may be zero when no station in the run is Astra bound, but the field and the interface stations' measurements, reviewer-design included, must be there).

6. REVIEW CHANNEL DISCIPLINE (restated for every reviewer station in this round): your review is exactly one JSON object written to runs/wo-gh-21/<your station>.review.json and nothing else in that file. Prose, summaries and narrative belong in your .output.md only. A .review.json that is not one parseable JSON object is not counted, and round 1 ended with 0 of 5 counted for exactly that reason.

Guardrails unchanged: never modify tools/claude_station.py, the review parsing contract or the prompts' Output Format sections; standard library only; no em dash or en dash characters; S1, S4 and S5's already correct parts stay as they are except for item 5's report visibility.

LOOPBACK (gate round 3, operator brief, FINAL): rounds 1 and 2 both ended no_reviews for one reason only: the review producer defect. Across both rounds 0 of 10 reviewer .review.json files were countable because the stations could not write them and their chat prose was transcribed into the channel, which the parser correctly refuses. That defect is fixed on main by wo-gh-24 (merge 0ce8be45): each reviewer now writes exactly its own review file through a scoped channel, stdout is never transcribed, and the fix is proven with 5 of 5 counted reviews on live runs. This branch is synced to that main, so round 3's reviews count. The round 2 implementation stands (budget and report measurements were recorded in the round 2 run report; its 26 astra consumption tests pass) and the findings below, convergent across the round 2 prose of reviewer-spec, reviewer-security and reviewer-architecture, are this loopback's ENTIRE scope. Fix exactly this, nothing else:

1. CRITICAL, WIRE THE S3 PROVENANCE CHECK INTO THE REVIEWER-DESIGN PREPARATION PATH (spec S3). verify_packet_allowlist_by_provenance (anvil/runner.py, line 275) is implemented and unit tested but never called anywhere: prepare_reviewer_design_step (line 387) builds the scoped packet through build_reviewer_design_packet and returns it unverified, so the deterministic provenance check the spec requires does not execute in a real run. Call the verifier in the preparation path, on the built packet, against exactly the allowlist the packet declares (today that list is constructed inside build_reviewer_design_packet, lines 361 to 368; surface it so the preparation path verifies against the same list, not a second reconstruction). A packet whose embedded content carries a provenance tag outside the allowlist must fail the step before any model call, with the violation as the failure detail. Add tests that drive the preparation path itself, not only the verifier in isolation: one packet with out of allowlist content failing through prepare_reviewer_design_step, and one clean packet passing through the same path.

2. RESOLVE THE .stations LAYER VIOLATION PROPERLY. build_reviewer_design_packet loads the reviewer-design prompt through a function-scoped import (anvil/runner.py, line 327: from .stations import load_registry, inside the function). Round 2 introduced that import and scoped it instead of removing the dependency; scoping is not a resolution and the reviewers flagged it again. The runner must not import from .stations at any scope for this. The scoped packet builder already accepts the station prompt as its prompt parameter: the caller in the run path resolves the reviewer-design prompt through the station registry the runner already works with and passes it in, and build_reviewer_design_packet never loads a registry itself (its prompt=None fallback may keep a plain default text, but no import). State the chosen placement in the builder output.

3. SECURITY RESIDUALS (reviewer-security, round 2):
(a) The provenance verifier's allowlist matching (line 299) accepts bare substring containment: a tagged source passes when it is a substring of an allowed path or an allowed path is a substring of it. Tighten to path boundaries: a source is allowed only when it equals an allowlist entry or lies beneath an allowlisted path at a path separator boundary. A source that merely shares a substring or a partial path segment with an entry must fail. Cover the shapes with tests: a sibling path sharing a prefix (design/DESIGN.md.bak), a partial segment match, and a parent traversal shape, each failing; exact entries and legitimately nested paths passing.
(b) _read_png (anvil/runner.py, line 114) inflates IDAT with zlib.decompress unbounded (line 195): the decompressed size is never validated against the size the IHDR dimensions imply, so a small crafted PNG can expand far beyond its declared dimensions in memory. Bound the inflation: decompress with an explicit maximum length derived from the expected raw size the assembler's own parsing implies (height rows of 1 filter byte plus width times 3 bytes), and fail loudly when the stream yields more than the expected size or a size different from it.
(c) _read_png accumulates IDAT chunk data (line 188) with no cap before decompression. Cap the accumulated compressed bytes while reading chunks (a bound tied to the expected raw size or a fixed cap well under the existing file size cap) and fail loudly when it is exceeded, before any inflation happens.

Guardrails unchanged: never modify tools/claude_station.py, the review parsing contract, the prompts' Output Format sections, or the wo-gh-24 producer mechanisms (the scoped review write channel, same-session correction, review_file_missing). S1, S2, S4 and S5 behavior stays exactly as round 2 left it, except that finding 1 wires the S3 check into the path as the spec always required. Standard library only. No em dash or en dash characters in any produced file. Every existing test keeps passing; new tests map to these three findings and say so in their names or docstrings.

Review channel discipline (round 3): the producer is fixed, so each reviewer's review is exactly one JSON object in its own runs/wo-gh-21/<station>.review.json, written through the channel its packet names. Round 3's verdict rests on counted reviews only; prose in .output.md remains provenance, never a verdict.
- risk_hints: 
- status: new

## Upstream steps

- intake: completed
- spec-writer: executed
- test-writer: executed
- builder: executed
- reviewer-spec: executed

## Output contract

Your complete answer is exactly one review JSON object written to runs/wo-gh-21/reviewer-security.review.json. The free output transcript stays as provenance and is never parsed for a review.
