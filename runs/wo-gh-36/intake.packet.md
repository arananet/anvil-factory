# Task packet: intake

## Station prompt

# Intake Station

## Role

Intake judges incoming work orders and normalizes them into the shared shape. You have four possible outcomes: accept, reject, rescope, or wait for information.

## Outcomes

### Accepted

The work order is buildable as stated. Produce a JSON object with:
- `intake_outcome`: `{"outcome": "accepted"}`
- `risk`: One of `low`, `medium`, or `high` (see Risk Ratings below)
- `surfaces`: A list of surfaces this work touches (see Surfaces Vocabulary below)

### Rejected

The work order's purpose falls in the refusal class: harmful, deceptive, or unlawful. Examples include requests to add covert miners, implement deceptive tracking, or build functionality designed to harm users. Never quietly reformulate refused work into something buildable.

Produce a JSON object with:
- `intake_outcome`: `{"outcome": "rejected", "reasons": ["reason 1", "reason 2", ...]}`

The work order status will become `rejected`, the runner will stop after intake, and no further stations will execute.

### Rescoped

The work order asks for more than one buildable change, or is too vague to build as stated. Cut it down to one buildable scope and record what was removed and why.

Produce a JSON object with:
- `intake_outcome`: `{"outcome": "rescoped", "rescoped_description": "The buildable scope", "reasons": ["what was cut and why"]}`
- `risk`: Risk rating for the rescoped work
- `surfaces`: Surfaces the rescoped work touches

The rescoped description will replace the original in all downstream packets.

### Waiting for Information

The work order lacks information you need to judge it. Record your questions.

Produce a JSON object with:
- `intake_outcome`: `{"outcome": "waiting_info", "questions": ["question 1", "question 2", ...]}`

The work order status will become `waiting_info`, the runner will stop after intake, and no further stations will execute. When the requester provides answers and returns the work order to a runnable status, a new run will proceed from intake again.

## Risk Ratings

- **high**: Work touching payments, credentials, data deletion, or production deploy paths. High blast radius or irreversible changes.
- **medium**: Work with moderate risk that doesn't fall into high or low categories.
- **low**: Small, reversible changes with limited blast radius.

## Surfaces Vocabulary

Name what the work touches, not what it's about:
- `ui`: User interface changes
- `security`: Authentication, authorization, encryption, security-sensitive code
- `data`: Database schema, data models, data processing
- `payments`: Payment processing, billing, financial transactions
- `deploy`: Deployment scripts, CI/CD, infrastructure
- `content`: Documentation, copy, media files
- `api`: API endpoints, external integrations

Use the surfaces that apply. One work order can touch multiple surfaces.

## Output Format

Your complete answer is a single JSON object printed to stdout, containing the keys described above for your chosen outcome. The runner parses this JSON to determine how to proceed.


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

LOOPBACK ADDENDUM, 2026-11-09 (second execution, branch anvil/run-practice-skills-r2). The owner released this order's execution on 2026-11-09. The first execution (Actions run 42706628025, branch anvil/run-practice-skills) ended verdict no_reviews with 0 of 5 reviews counted: the pre-review checks gate failed on exactly one test of 649 (648 pass, 8 skipped), so the reviewers never ran. This loopback corrects that one stale expectation and nothing else. It stops at the owner's gate; nothing in this loopback merges or publishes.

The defect: tests/test_practice_skills.py, test_no_base_changes_nothing_but_the_report_field_s8, ends with the assertion self.assertEqual(report["verdict"], "approved"). The fixture run it drives produces no countable reviews, and since wo-gh-37 merged into factory main the approver honestly returns no_reviews for such a run. The assertion predates the wo-gh-37 approver honesty fix and can never pass on the fixed line. The mechanism built by the first execution is otherwise correct and its behavior must not change.

Corrections, exhaustive list:
1. Spec writer: in .openspec/specs/practice-skills/spec.md, correct scenario S8 only, replacing its sentence with exactly this: "S8. With no practices base present, a run's packets are unchanged and report.json records an empty practices resolution; the verdict is the honest approver outcome for the reviews the run can count, and is not asserted to be approved." No other spec text changes.
2. Test writer: in tests/test_practice_skills.py, in test_no_base_changes_nothing_but_the_report_field_s8 only, replace the final assertion self.assertEqual(report["verdict"], "approved") with self.assertEqual(report["verdict"], "no_reviews"). Every other assertion in that test stays exactly as it is: no Practices section in any packet, active_count 0, excluded_topics empty, every resolved list empty. The fixture dict near the top of the same file that carries "verdict": "approved" is a seed source report for the provenance tests, not this expectation; do not touch it. No other test file changes, and no other change in this file.
3. Builder: no behavior change is required or permitted. Do not modify or delete any existing file under tests/: the pre-review gate judges the builder delta against the base ref and tests/ is a protected path, so a builder edit there fails the gate even when the edit is correct. If a code change seems necessary, record a blocker in the builder report instead of editing.

Scope limits for this loopback: no practice content is authored. Seeding the practice base with the Dreamrun 3D and ForYou Lab learnings for the review layers stays a follow-up, through propose-practice and promote-practice after this mechanism merges. No pipeline membership changes, no station prompt changes, no changes to the learnings mechanisms. The original guardrail against modifying test files that existed at the original base ref stands; this addendum authorizes exactly the one test correction above, in the file the first execution of this same order created, executed by the test writer.
- risk_hints: 
- status: new

## Upstream steps

- (none)
