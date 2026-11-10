# Decision 0005: Seed the practice base with the review layer learnings

Status: accepted

Adopted: 2026-11-09, by the owner's order.

## Decision

Verified learnings from project runs live in the factory as scoped best practices consumed by the review layers (the deterministic checks gate and the reviewer stations), not as operator folklore or chat memory. The owner's direction of 2026-11-09, verbatim: "los learnings deben de ir a anvil pero en el sentido de las capas de a revisión. Ser coherente. Best practices". The coherence rule inside it: every project is judged against its own declared genre and spec, never against imported standards from other genres.

Under this record, the seed set below enters the practice base through propose-practice and promote-practice only. Each proposal cites this record as its Source; the per practice provenance recorded here is the evidence standard the promotion gate checks against.

## The seed set, with provenance

Checks gate layer:

- Traversal proof for platformer orders. Provenance: Dreamrun 3D wo-gh-6, where the jump apex of 2.08 stood against platform tops at 2.1, 2.2 and 2.4, verified from the shipped logic before the owner reported it in play.
- Deterministic validation of builder reports with declared literals. Provenance: Dreamrun 3D R7 and R8 report failures, and the factory fix wo-gh-37 (S2).
- Capture evidence must exist before design review. Provenance: Dreamrun 3D R3 (changes requested for missing rendered evidence) and ForYou Lab reviewer-design findings (no rendered evidence).

reviewer-design:

- Fidelity to anchors and the committed asset pack. Provenance: Dreamrun 3D wo-gh-5 spec (A5) and its reviewer-design check.
- Parallax depth must be demonstrated between layers. Provenance: owner verdict on the shipped Dreamrun 3D R6 build, 2026-11-09.
- Cross-set coherence check. Provenance: the coherence clause carried through Dreamrun 3D wo-gh-4 and wo-gh-5.
- Genre coherence. Provenance: owner correction, 2026-11-09 ("Es un 2d platform old school").

reviewer-ux:

- Player basics checklist. Provenance: owner playtest findings across Dreamrun 3D R6 and wo-gh-6.
- Controls must not select text. Provenance: Dreamrun 3D wo-gh-6 (C2).
- Pause integrity and touch pause control. Provenance: Dreamrun 3D reviewer-ux findings, R5 to R7.
- Touch targets of at least 44 px. Provenance: Dreamrun 3D R7 reviewer-ux quality pass.

reviewer-tests:

- Evidence must reproduce against the final tree. Provenance: Dreamrun 3D R8 and R9, where node-tests evidence claimed 159 of 159 against a final tree the reruns measured at 158 of 159.
- Test accounting names baseline, additions and edits. Provenance: Dreamrun 3D wo-gh-5 and wo-gh-6 test accounting practice.

Earned after the issue 36 amendment was written, added at the owner's merge and seed gate of 2026-11-09:

- Cross-order spec conflict detection (intake, reviewer-spec). Provenance: Dreamrun 3D R12, where the wo-gh-6 C2 pin (touch-action none, unconditional) collided with the wo-gh-7 H3 requirement (a scrollable title overlay) and the collision was discovered by the checks gate mid-run instead of at filing.
- Filing completeness for protected surfaces (intake, spec-writer). Provenance: three consecutive Dreamrun 3D loopbacks stopped by under-authorized filings: R12 (missing test adaptations), R13 (missing protected_paths authorization), with R14 closing the chain only after the complete write set was enumerated up front.

## Gate record

The practice skills mechanism (wo-gh-36) merged to main on 2026-11-09 under the owner's decision "Fusionar wo-gh-36 y sembrar los learnings" (merge approved, checks gate green, factory suite 649 tests with 0 failures). This record and the seeding it authorizes are recorded at runs/wo-gh-36/owner-acceptance.json and on issue 36.
