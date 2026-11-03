# Astra Consumption: Packet Budgets, Evidence Policy, Scoped Design Review

Status: proposed
Slug: astra-consumption

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
The gateway request logs for 2026-10-28 to 2026-11-03 (3,099 requests audited) put numbers on what the factory costs to run: 119.80 USD in total, of which the Astra route (openai/gpt-6-astra through Codex, the route the UI and design stations use) accounts for 70.14 USD, 58.5 percent, across 753 requests with 33,756,128 input tokens logged, about 45,000 input tokens per request, and zero cached requests in the whole window.

The mechanics are structural, not a model problem. An agentic station session resends its accumulated context on every call, and what ANVIL places at the base of that context is the station packet. Packets are assembled by anvil/runner.py in _packet_text from the station prompt, the work order, the upstream steps list, the Verified learnings section (anvil/brain.py, packet_learnings_section) and, for interface stations, the Project design section (anvil/design.py, packet_design_section), which inlines the full design tokens as JSON plus the quality bars. Every station of every run pays for that material again, and reviewer-design receives the same general packet although its job needs only the design system, a summary of the change and the rendered evidence. Rendered evidence reaches design stations as multiple full resolution captures. The gateway logs do not split text tokens from image tokens, so what share of the Astra input is image evidence is an open question: this spec treats it as something to instrument (S5), not as a premise.

This spec fixes the consumption at the factory spine, so every project ANVIL runs inherits the fix: measure every packet, budget the expensive routes, give the design reviewer one downscaled contact sheet instead of the full resolution set, start the design review from a fresh and scoped packet, lay packets out so provider prefix caching can engage, and record per station cost signals in the run report so the effect is measurable against the audited baseline.

## Requirements

Guardrails that bind the whole order:

- This order changes the factory spine only: packet assembly and measurement in anvil/runner.py and its helpers, the design section rendering in anvil/design.py where S2 and S3 require it, config reading in anvil/config.py, the work order model where S2 requires it, and tests. Runtime code stays on the Python standard library only.
- This order does not touch the review parsing contract, the Output Format sections of the station prompts, or tools/claude_station.py and its REVIEW_SUFFIX. It is executed from a main that already carries the wo-gh-16 parse contract merge, and it preserves that merge exactly.
- The packet token estimator is a deterministic heuristic defined once, in one place, with its constant visible in config. It is an estimate used for budgeting and comparison, never presented as the provider's own tokenizer count.
- Nothing in this order claims a saving. Savings are what the post merge proof run measures against the baseline above.

### S1: Packet budget for the expensive routes
- The runner measures every station packet with the deterministic estimator before execution and records the measured size.
- A per station input budget applies to the stations routed to the Astra or Codex executor and to the interface stations (builder, writer, media-producer, brief-writer, reviewer-design). Budgets are read from project config (anvil.yaml) through anvil/config.py, with factory defaults defined in the same place; a project value overrides the default.
- An over budget packet is trimmed by rule, in this declared order, until it fits: first the design tokens render compact instead of pretty printed; then the quality bars are reduced to their headings plus the first line of each bar; then the learnings section is limited to the most recent entries that fit the remaining allowance.
- If the packet still exceeds the budget after the trim rules, or the project config sets the over budget policy to fail, the step fails before any model call, with the measured size and the budget in the failure detail. An over budget packet is never sent silently.
- The run report records, per measured step: the measured tokens, the budget, and the action taken (sent, trimmed or failed).

### S2: Evidence image policy
- When a run produces rendered captures for a design review round, a deterministic assembler in the factory (standard library only) combines the round's PNG captures into one contact sheet PNG whose width does not exceed a configured maximum (factory default 1600 px). Captures are scaled down proportionally and never scaled up.
- The reviewer-design packet references the contact sheet and only the contact sheet. The full resolution originals stay byte unchanged in the run evidence directory for humans.
- The assembler fails loudly on a capture it cannot process (for example a file that is not PNG) instead of silently dropping or converting it.
- Builder stations receive image evidence only when the work order declares it: the work order model gains an optional list of evidence image paths in scope, defaulting to empty, and existing work orders parse unchanged. Absent that declaration, builder packets carry no image references.

### S3: Fresh session, scoped design review
- reviewer-design runs as its own fresh session. Its packet contains: the station prompt, the Project design section, the spec the order implements, a diff summary of the change under review produced deterministically by the runner from git (files changed with added and removed line counts), and the contact sheet reference from S2.
- The reviewer-design packet does not contain the builder session's transcript, other stations' outputs, or whole worktree file contents.
- The packet declares a file access allowlist as a contract section: the files the order touches, the design system files and the spec. A deterministic runner check verifies that the packet embeds no file content from outside that allowlist.
- Other reviewer stations keep their current packets in this order. Scoping them the same way is follow up work, named here so it is not mistaken for part of this order.

### S4: Stable prefix packet layout
- _packet_text assembles every packet with the stable material first, in this order: the station prompt, the Project design section when present, the Verified learnings section when present. The per run variable material comes last: the work order block, then the upstream steps list.
- Byte property: for the same station and the same project, the packets of two different runs are identical up to the first variable section.
- After this order's own execution run, the operator checks the gateway logs for the run's Astra requests and records the cached token or cached flag values exactly as the logs show them in the run evidence summary on the issue, whether caching engaged or not. No artifact of this order claims a caching saving beyond what that check shows.

### S5: Per station cost visibility in the run report
- Each executed step's run report entry records: the configured model, the executed model where the runtime reports one (the existing provenance), the measured packet tokens (S1), and the usage the executor returned for that step (input and output tokens) when the runtime reports usage. When the runtime reports no usage, the usage entry is null, never an estimate.
- The run report totals the measured packet tokens of the Astra bound stations per work order, so a work order's Astra exposure is visible in the report itself.
- Cost stays null unless a numeric cost is reported by the runtime, following the executor's existing rule. Attribution of gateway log cost to individual sessions is operator reporting, not a report field this order invents.

## Scenarios

### Scenario: An over budget packet is trimmed by rule or fails loudly
- S1: Given a design station packet whose measured size exceeds its configured budget, when the runner prepares the step, then the packet is trimmed in the declared order (compact tokens, reduced quality bars, learnings limited) until it measures within budget, or the step fails before any model call with the measured size and the budget in the failure detail; and the run report shows the measured tokens, the budget and the action taken. An under budget packet reaches the executor byte unchanged.

### Scenario: A design review round sends one contact sheet, originals preserved
- S2: Given a run that produced several full resolution PNG captures for a design review round, when reviewer-design is prepared, then its packet references exactly one contact sheet PNG whose width is at most the configured maximum, the original captures remain byte unchanged in the run evidence, a non PNG capture in the round makes the assembler fail loudly, and a builder packet in the same run references images only if the work order declared evidence images in scope.

### Scenario: The design review starts fresh and scoped
- S3: Given a change under review, when the reviewer-design packet is assembled, then it contains the design section, the spec, a git derived diff summary and the contact sheet reference; it contains no builder transcript, no other station outputs and no whole file contents; and the deterministic allowlist check passes, meaning no embedded content comes from a file outside the declared allowlist (the files the order touches, the design system files, the spec).

### Scenario: Packets share a stable prefix across runs
- S4: Given two runs of the same project, when the packets for the same station are compared, then they are byte identical from the start up to the first variable section (the work order block), the variable material appears only after the stable material, and the operator's post run gateway log check is recorded on the issue with the cached values exactly as logged, with no caching saving claimed beyond them.

### Scenario: The run report shows what each station cost to feed
- S5: Given an executed run, when its report is read, then every executed step shows its configured model, its executed model where reported, its measured packet tokens and its executor reported usage or null; the report totals the measured packet tokens of the Astra bound stations for the work order; and no cost figure appears anywhere in the report unless the runtime reported a numeric cost.

## Tests
- Estimator: the same input always yields the same count, an empty packet counts zero, and the count grows with input size.
- Budget: an over budget fixture packet is trimmed in the declared order and then measures within budget; with the policy set to fail, preparation raises before execution and the executor is never called; an under budget packet reaches the executor byte unchanged; the report entries carry measured tokens, budget and action.
- Contact sheet: fixture PNG captures of known sizes produce one PNG sheet whose width is at most the configured maximum; the originals are byte unchanged; a non PNG input fails loudly.
- Packet layout: two packets for one station across two runs share the expected stable prefix and differ only from the work order block on; the design and learnings sections appear before the work order block.
- Scoped review: a reviewer-design packet built over a fixture change contains the diff summary and the design section, contains no content from a fixture file outside the allowlist, and the allowlist check rejects a packet that embeds such content.
- The full factory suite passes.
