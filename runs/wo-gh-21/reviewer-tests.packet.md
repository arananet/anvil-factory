# Task packet: reviewer-tests

## Station prompt

# Reviewer Tests

## Role
Check that tests are real, mapped, and passing.

## Inputs
- spec
- tests

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
  "station": "reviewer-tests",
  "verdict": "pass | fail | changes_requested",
  "findings": [
    "Specific finding with reference to design system rule or quality bar",
    "Another finding if applicable"
  ]
}

The station field must equal "reviewer-tests", the verdict must be one of pass, fail, or changes_requested, and findings must be a list of strings.


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
- risk_hints: 
- status: new

## Upstream steps

- intake: completed
- spec-writer: executed
- test-writer: executed
- builder: executed
- reviewer-spec: executed
- reviewer-security: executed

## Output contract

Your complete answer is exactly one review JSON object written to runs/wo-gh-21/reviewer-tests.review.json. The free output transcript stays as provenance and is never parsed for a review.
