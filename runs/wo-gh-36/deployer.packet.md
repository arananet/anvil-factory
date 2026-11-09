# Task packet: deployer

## Station prompt

# Deployer

## Role
Prepare and carry out the release step described by the project.

## Inputs
- approved change

## Outputs
- release record

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.


## Work order

- id: wo-gh-36
- kind: feature
- title: Practice skills base: quarantined best practices with scoped, deterministic resolution
- source: github-issue
- description: Implement the spec in .openspec/specs/practice-skills/spec.md. Owner's idea 2026-10-29 (capability program item 11), decided 2026-11-08: a skills system for ANVIL, a quarantined base of development best practices with scoped, deterministic resolution. Pipeline for this order is sdlc-default, selected by the run workflow.

STAGING: this order is filed and staged only. Execution starts on the owner's word, like issues 28 and 33.

Build, per the spec requirements:

R1, the base: brain/practices.md with one entry per practice (Id, Topic, Rule, Scope with Languages, Surfaces and Stations, Enforcement prompt or gate, Source, Status active or superseded). Proposals enter only through a propose operation in the brain module mirroring propose_learning, landing in brain/inbox/; promotion only through a promote operation mirroring promote_learning. CLI gains propose-practice and promote-practice next to promote-learning and check-brain.

R2, the consistency check: promotion refuses with the reason named when provenance does not verify to the learnings standard (cited run report exists and supports the practice, or an owner decision record under brain/decisions/), when an active practice with the same topic and overlapping scope exists without a Supersedes, or when the entry is malformed. Supersedes marks the replaced practice superseded so it stops resolving. check-brain extends to practices: malformed base fails, any active topic and scope conflict fails, absent base passes.

R3, deterministic resolution: before packets are built, the runner resolves applicable practices from the work order surfaces, the pipeline station list and language signals. Matching is conjunctive across scope dimensions, disjunctive within a dimension, empty dimension unrestricted. Standard library only, no model in the resolution.

R4, recording: report.json gains a practices field (resolved ids per station, topics excluded by override, active base count at run start); the routing record carries the same resolution.

R5, precedence: anvil.yaml may declare practice_overrides, a list of topics the project governs itself. Overridden topics resolve nothing from the base and the exclusion is recorded. Explicit topic names only, no inference from document content.

R6, enforcement split: Enforcement prompt practices are injected into a dedicated Practices section of the packets of the stations they resolved for, and nowhere else. Enforcement gate practices are never prompt text; the checks gate lists them by id and topic in its pre-review output. Authoring automated checkers for individual gate practices is out of scope.

R7, empty base: ship the mechanism with no promoted practices; fixtures live in tests only. Seeding a catalog is follow-on work through the same gate.

R8, compatibility and coordination: no practices base means behavior identical to today apart from the report field recording an empty resolution. If issue 33 (scoped learnings) has merged before this run executes, reuse its scope matching helper for R3; if not, implement matching in the brain module and record the parallel in the run report.

Guardrails: Python standard library only; no new dependency. Do not change pipeline membership, station prompts, or the learnings mechanisms' behavior. Do not create, modify, or delete any file under tests/ that exists at the base ref; new tests arrive as new files, and they must exercise the real brain module and runner paths (facade tests that never touch the mechanism fail the order). No em dash or en dash character in any produced file. The reviewer writes its review to the authoritative review file named in its packet; prose outside that file is not a review. Nothing in this order publishes or deploys anything.

GitHub issue: https://github.com/arananet/anvil-factory/issues/36
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed
- test-writer: executed
- builder: executed
- checks-gate: failed
- loopback: loopback
- reviewer-spec: skipped
- reviewer-security: skipped
- reviewer-tests: skipped
- reviewer-architecture: skipped
- reviewer-design: skipped
- reviewer-ux: skipped
- approver: completed
- triage-human: completed
