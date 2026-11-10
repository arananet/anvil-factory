# Practices

Promoted practices for this project. An entry reaches this file only
through `anvil promote-practice`, which verifies its provenance and
refuses a second active rule for one topic in an overlapping scope.
Proposals wait in brain/inbox/ (quarantined) until promoted.
`anvil check-brain` validates every entry below.

## P-1: Traversal proof for platformer orders
Topic: Traversal proof for platformer orders
Rule: A platformer work order must carry a traversal proof that uses the project's real movement code, proving every platform and the goal reachable, before build and review spend.
Languages: 
Surfaces: 
Stations: checks-gate
Enforcement: gate
Source: decision brain/decisions/0005-review-layer-practice-seeding.md
Status: active

## P-2: Deterministic validation of builder reports with declared literals
Topic: Deterministic validation of builder reports with declared literals
Rule: A builder report whose work order declares required literals is validated deterministically against the final tree before any reviewer runs; a report that omits a declared literal in full returns the work to the builder without reviewer spend.
Languages: 
Surfaces: 
Stations: checks-gate
Enforcement: gate
Source: decision brain/decisions/0005-review-layer-practice-seeding.md
Status: active

## P-3: Capture evidence must exist before design review
Topic: Capture evidence must exist before design review
Rule: Rendered capture evidence must exist and be non-trivial in the run record before design review counts it as rendered evidence; a run without captures cannot pass on rendered evidence.
Languages: 
Surfaces: 
Stations: checks-gate
Enforcement: gate
Source: decision brain/decisions/0005-review-layer-practice-seeding.md
Status: active

## P-4: Fidelity to anchors and the committed asset pack
Topic: Fidelity to anchors and the committed asset pack
Rule: Judge rendered captures against both the project anchors and the committed asset pack; if the rendered game does not visibly use the pack art, fidelity fails.
Languages: 
Surfaces: 
Stations: reviewer-design
Enforcement: prompt
Source: decision brain/decisions/0005-review-layer-practice-seeding.md
Status: active

## P-5: Parallax depth must be demonstrated between layers
Topic: Parallax depth must be demonstrated between layers
Rule: Parallax depth must be demonstrated between layers in captures, by measured displacement or visible relative motion; a single panning plate is not depth.
Languages: 
Surfaces: 
Stations: reviewer-design
Enforcement: prompt
Source: decision brain/decisions/0005-review-layer-practice-seeding.md
Status: active

## P-6: Cross-set coherence check
Topic: Cross-set coherence check
Rule: Run an explicit cross-set coherence check on every review: same character, proportions, palette, motifs and light logic across all stages or scenes; style drift is a changes requested finding.
Languages: 
Surfaces: 
Stations: reviewer-design
Enforcement: prompt
Source: decision brain/decisions/0005-review-layer-practice-seeding.md
Status: active

## P-7: Genre coherence
Topic: Genre coherence
Rule: Judge the work against the genre declared in the project spec, never against imported standards from other genres; an old school 2D platformer is judged on genre craft: full-screen playable density, readable floors, big legible sprites.
Languages: 
Surfaces: 
Stations: reviewer-design
Enforcement: prompt
Source: decision brain/decisions/0005-review-layer-practice-seeding.md
Status: active

## P-8: Player basics checklist
Topic: Player basics checklist
Rule: Check the player basics on every review: it can be reached, it reads clearly, it moves with depth, it sounds right; a failure on any basic is a finding, not a taste note.
Languages: 
Surfaces: 
Stations: reviewer-ux
Enforcement: prompt
Source: decision brain/decisions/0005-review-layer-practice-seeding.md
Status: active

## P-9: Controls must not select text
Topic: Controls must not select text
Rule: Controls must not select text on touch or mouse interaction; text selection during play is a defect.
Languages: 
Surfaces: 
Stations: reviewer-ux
Enforcement: prompt
Source: decision brain/decisions/0005-review-layer-practice-seeding.md
Status: active

## P-10: Pause integrity and touch pause control
Topic: Pause integrity and touch pause control
Rule: Pause must survive visibility changes, and a touch pause control must exist; losing the pause state when the page hides and returns is a defect.
Languages: 
Surfaces: 
Stations: reviewer-ux
Enforcement: prompt
Source: decision brain/decisions/0005-review-layer-practice-seeding.md
Status: active

## P-11: Touch targets of at least 44 px
Topic: Touch targets of at least 44 px
Rule: Touch targets measure at least 44 px in both dimensions; a smaller target is a finding.
Languages: 
Surfaces: 
Stations: reviewer-ux
Enforcement: prompt
Source: decision brain/decisions/0005-review-layer-practice-seeding.md
Status: active

## P-12: Evidence must reproduce against the final tree
Topic: Evidence must reproduce against the final tree
Rule: An evidence file whose claims do not reproduce against the final tree is itself a finding; the reviewers' own rerun is the authority over any recorded evidence.
Languages: 
Surfaces: 
Stations: reviewer-tests
Enforcement: prompt
Source: decision brain/decisions/0005-review-layer-practice-seeding.md
Status: active

## P-13: Test accounting names baseline, additions and edits
Topic: Test accounting names baseline, additions and edits
Rule: Test accounting must name the baseline count, the added test files and the edited test files, with a justification for each edit; an unaccounted change is a finding.
Languages: 
Surfaces: 
Stations: reviewer-tests
Enforcement: prompt
Source: decision brain/decisions/0005-review-layer-practice-seeding.md
Status: active

## P-14: Cross-order spec conflict detection
Topic: Cross-order spec conflict detection
Rule: Before execution, check a new order's hard assertions (pinned counts, unconditional property pins, exact file sets) against standing contracts from prior orders on the same project; a collision is surfaced in the filing for an owner decision, never discovered by the checks gate mid-run.
Languages: 
Surfaces: 
Stations: intake, reviewer-spec
Enforcement: prompt
Source: decision brain/decisions/0005-review-layer-practice-seeding.md
Status: active

## P-15: Filing completeness for protected surfaces
Topic: Filing completeness for protected surfaces
Rule: When an order's substance touches protected paths, packet contents or existing tests, the filing must enumerate the complete authorized write set up front: protected_paths changes, named test adaptations and packet inclusions; an under-authorized filing is returned before the run fires.
Languages: 
Surfaces: 
Stations: intake, spec-writer
Enforcement: prompt
Source: decision brain/decisions/0005-review-layer-practice-seeding.md
Status: active
