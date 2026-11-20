# Practice Enforcement Ladder: Corrections End as Checks

Status: draft (not filed)
Slug: practice-enforcement-ladder

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose

brain/practices.md on factory main holds fifteen active practices: three with Enforcement gate (P-1 to P-3) and twelve with Enforcement prompt. anvil/cli.py makes prompt the default (propose-practice --enforcement default "prompt"), so the cheapest path for a verified learning is one more sentence in a reviewer packet. A check in code gives the same answer every run; a sentence in a packet is advice a model may or may not apply. Several of the twelve are measurable by machine as written: P-11 (touch targets of at least 44 px), P-9 (controls must not select text), P-10 (pause survives visibility changes and a touch pause control exists).

This order turns the ladder around: a practice is a gate unless someone records why it cannot be, a gate practice must name the check that enforces it, and the three measurable practices above move from prompt to gate using the runtime verification driver.

## Requirements

### R1. Gate is the default
- anvil propose-practice defaults --enforcement to gate.
- A proposal with enforcement prompt must carry a Prompt-reason field: one line stating why no deterministic check can decide it. propose-practice refuses a prompt proposal without it; promote-practice refuses to promote one.
- anvil check-brain validates Prompt-reason on every prompt entry promoted after this order lands. The twelve existing prompt entries are listed by id in the check as grandfathered and are reported, not failed.

### R2. A gate practice names its check
- A practice with enforcement gate carries a Check field naming a check id. Check ids resolve to a registry in the factory (anvil/gates.py or a sibling), each entry a callable with a stable id.
- check-brain fails a gate practice whose Check does not resolve. The three existing gate practices (P-1 to P-3) receive their Check field in this order, pointing at the mechanism that already enforces them; where no code enforces one today, the builder report says so and the order adds the check.
- A run report's practices section records, per gate practice in scope, the check id and its outcome.

### R3. Three practices climb the ladder
- New gate practices supersede P-9, P-10 and P-11 through the existing supersedes mechanism, each with a check built on the runtime verification driver (order runtime-verification):
  - touch-target-min: every element the feature map marks as a control measures at least 44 px in both dimensions at the phone breakpoint.
  - no-text-selection: after pointer interaction on each control, the page selection is empty.
  - pause-integrity: with the game or app in its paused state, set_visibility hidden then visible leaves the declared paused state true; a control named as the touch pause control is visible at the phone breakpoint.
- Each check applies only where the practice's scope matches the project (surfaces, product type) and reports not applicable otherwise; not applicable is never a pass.
- The reviewer-ux packet stops carrying the superseded prompt text.

### R4. The ratio is visible
- The status page shows, per project, active practices by enforcement (gate, prompt) and the count of prompt entries carrying a Prompt-reason.

### R5. Regression tests
- New test files under tests/: (a) propose-practice with no --enforcement produces a gate proposal; (b) a prompt proposal without Prompt-reason is refused at propose and at promote; (c) check-brain fails a gate practice with an unresolvable Check and passes the shipped base; (d) each of the three checks fails on a fixture that violates it and passes on one that does not, using the fake driver; (e) a superseded prompt practice no longer appears in the reviewer-ux packet.

### Guardrails
- Depends on runtime-verification for R3; R1, R2 and R4 stand alone and may land first if the owner splits the order.
- Frozen: the promotion door (provenance verification, quarantine in brain/inbox, one active rule per topic and overlapping scope); the review parse contract; reviewer prompts other than the removal of superseded practice text from packets.
- Promotion of the three new practices stays the owner's word; this order files them as proposals with this spec as their source and does not promote them itself.
- Existing test files at the base ref are not modified or deleted. No em dash or en dash character in any produced file.

## Scenarios

- S1: Given no --enforcement flag, when a practice is proposed, then the proposal's enforcement is gate.
- S2: Given a prompt proposal without a Prompt-reason, when it is proposed or promoted, then the command refuses and names the missing field.
- S3: Given a gate practice whose Check names no registered check, when check-brain runs, then it fails naming the practice and the check id.
- S4: Given a built page with a 32 px control, when touch-target-min runs, then it fails naming the control and its measured size; given all controls at 44 px or more, then it passes.
- S5: Given a paused app that loses its paused state when the page is hidden and shown, when pause-integrity runs, then it fails; given one that keeps it, then it passes.
- S6: Given the three new practices promoted, when a reviewer-ux packet is built, then the text of P-9, P-10 and P-11 is absent and the run report shows the three check outcomes.
