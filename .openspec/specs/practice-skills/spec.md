# Practice Skills Base

Status: proposed

## Purpose

ANVIL has no skills system. Best practices today live as prose inside station prompts, as verified learnings in the brain, or in the operator's head. There is no way to add a practice once and have it reach exactly the stations it applies to, and no protection against two practices contradicting each other inside the same packet. This spec adds a practice skills base to the factory brain: a quarantined, provenance checked set of development best practices with explicit scope, resolved deterministically per work order before any model sees them.

## Design

Three layers, as designed with the owner on 2026-10-29:

1. A quarantined practice base that reuses the brain's promotion pattern: proposals with provenance, promotion only after a consistency check, one rule per topic per scope.
2. Deterministic resolution before any model: the runner assembles the conflict free practice set for a work order by scope matching and records it in the run report.
3. Written precedence: the project's own constitution and design system beat the base, through an explicit override list, never through model judgment.

One split runs through the whole design: a practice that can be checked mechanically belongs to the checks gate, not to a prompt.

## Requirements

R1. Practice base and quarantine. Promoted practices live in brain/practices.md, one entry per practice, with fields: Id, Topic, Rule, Scope (Languages, Surfaces, Stations), Enforcement (prompt or gate), Source, and Status (active or superseded). Proposals enter only through a propose operation in the brain module that mirrors propose_learning, and land in brain/inbox/ and nowhere else. Promotion happens only through a promote operation that mirrors promote_learning. The CLI gains propose-practice and promote-practice commands alongside the existing learning commands.

R2. Consistency check at promotion. Promotion refuses, naming the reason, when: the provenance does not verify to the same standard the learnings gate uses (the cited run report exists and supports the practice, or the source is an owner decision record under brain/decisions/); another active practice with the same Topic and an overlapping scope exists and the proposal does not supersede it; or the entry is malformed. A proposal may carry a Supersedes field naming one active practice; on promotion that practice is marked superseded and stops resolving. Scope overlap means at least one shared value, or an unrestricted dimension, on every scope dimension. The existing check-brain validation is extended to practices: it fails on a malformed practices.md and on any pair of active practices with the same topic and overlapping scope, and it passes on a repository with no practices base.

R3. Deterministic resolution. Before any packet is built, the runner computes the practices that apply to the work order from its surfaces, its pipeline's station list, and the language signals in the work order and the project config. A practice applies when every non-empty scope dimension matches: conjunctive across dimensions, disjunctive within a dimension, an empty dimension unrestricted. Resolution is deterministic Python standard library code; no model takes part in it.

R4. Recording. report.json gains a practices field holding the resolved practice ids per station, the topics excluded by project override, and the number of active practices in the base at run start. The run's routing record carries the same resolution, so what each station was given is auditable from the run evidence alone.

R5. Precedence by explicit override. A project may declare practice_overrides in its anvil.yaml: a list of topics the project governs itself through its constitution or design system. Practices whose topic is overridden are excluded from resolution for that project, and the exclusion is recorded per R4. Overrides are explicit topic names only; nothing infers an override from document content.

R6. Enforcement split. A practice with Enforcement prompt is injected into the packets of the stations it resolved for, in a dedicated Practices section, and into no other packet. A practice with Enforcement gate is never injected as prompt text; the checks gate lists it by id and topic in its pre-review output, so reviewers can see what the gate is accountable for. Authoring an automated checker for an individual gate practice is out of scope for this order; the gate listing is the contract.

R7. Empty base by design. This order ships the mechanism with no promoted practices. Test fixtures live in the test suite only. Seeding a real best practice catalog is follow-on work that enters through the same proposal and promotion gate as any other practice.

R8. Backward compatibility and coordination. A project with no brain/practices.md behaves exactly as today, apart from the report field recording an empty resolution. If the scoped learnings work (issue 33) has merged before this order executes, its scope matching helper is reused for R3 instead of writing a second matcher; if it has not merged, matching is implemented in the brain module and the parallel is recorded in the run report.

## Scenarios

S1. A proposal written through the propose operation lands in brain/inbox/; brain/practices.md is unchanged.

S2. A proposal whose source is a run report that exists and supports it promotes successfully and the practice then resolves for a matching work order.

S3. Promotion is refused, naming the conflicting practice, when an active practice with the same topic and overlapping scope exists and the proposal carries no Supersedes.

S4. A proposal with Supersedes promotes; the replaced practice is marked superseded, no longer resolves, and check-brain passes.

S5. Resolution respects scope: a practice scoped to one language reaches the in-scope stations of a matching work order and not a work order of another language; a practice scoped to one station reaches only that station's packet.

S6. A gate enforced practice appears in the checks gate pre-review output and in no station packet; a prompt enforced practice appears in its stations' packets and is not presented as a gate item.

S7. A project whose anvil.yaml overrides a topic resolves no base practice on that topic, and report.json records the exclusion.

S8. With no practices base present, a run's packets are unchanged and report.json records an empty practices resolution; the verdict is the honest approver outcome for the reviews the run can count, and is not asserted to be approved.

S9. check-brain fails on a practices.md that was hand edited to hold two active practices with the same topic and overlapping scope.

## Scope limits

Python standard library only. No pipeline membership changes, no station prompt rewrites, no changes to how learnings are proposed, promoted, demoted or injected beyond the coordination note in R8. No practice content is authored by this order. No em dash or en dash characters in any produced file.
