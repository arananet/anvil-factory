# Builder report: wo-gh-36, practice skills base

Spec: .openspec/specs/practice-skills/spec.md
Tests: tests/test_practice_skills.py (written by test-writer; not modified)

## Result

27 of 28 scenario tests pass. One fails, and the cause is in the test, not the mechanism (see "Open item").
Full suite: 649 tests, 1 failure (the same test), 8 skipped. At the base ref the suite had 622 tests and 1 error (the new test file failing to import), so nothing regressed.

## Changes

### anvil/brain.py (additions only; learnings functions unchanged apart from check_brain)
- R1: `propose_practice` writes a `Kind: practice` proposal to brain/inbox/ and nothing else. `promote_practice` is the only writer of brain/practices.md. Each entry has a `## P-<n>: <topic>` heading with Topic, Rule, Languages, Surfaces, Stations, Enforcement, Source, an optional Supersedes, and Status.
- R2: `promote_practice` refuses with a named reason when:
  - the proposal is malformed (no Topic, no Rule, or Enforcement not prompt or gate);
  - the existing base is invalid;
  - provenance fails. `run ..., artifact ..., evidence ...` goes through the existing `validate_provenance`, the same standard as learnings. `decision brain/decisions/<file>` must name an existing file under brain/decisions/;
  - Supersedes names an unknown or inactive practice;
  - an active practice has the same topic and an overlapping scope. The refusal names that practice id.
  On refusal nothing changes on disk. Supersedes rewrites the old entry's Status to superseded.
- R2: `check_practices` reports malformed headings or fields, duplicate ids, and active topic and scope conflicts. `check_brain` adds these to its problems and gains a `practices` count key. A missing practices.md adds nothing, so it passes.
- R3: `resolve_practices(project, work_order, station_ids, config)` is pure standard library code with no model involved:
  - matching is conjunctive across languages, surfaces and stations, disjunctive within one dimension, and an empty dimension is unrestricted;
  - values are lowercased;
  - ids are ordered by practice number;
  - only active, well formed entries count.
- R5: `practice_overrides` topics are excluded by exact name only and listed in `excluded_topics`.
- R6: `packet_practices_section` renders `## Practices` from prompt enforced practices only. `gate_practices_section` lists gate enforced practices by id and topic only, never the rule text.

### anvil/runner.py
- R3: the resolution is computed once at run start, before any packet is built. Inputs are the work order surfaces, the pipeline's topological station order, and the language signal: `languages` in anvil.yaml plus a work order `languages` attribute when one exists. If intake output sets new surfaces, the resolution is recomputed before any downstream packet.
- R6: the Practices section is passed into `_packet_text` and `prepare_packet` (all trim variants keep it) and into the prebuilt reviewer-design packet. A station with no resolved prompt practices gets no section.
- R6: in the pre-review phase, the checks-gate output gains a `## Gate practices` listing.
- R4: `RunReport` gains a `practices` field, which defaults to the empty resolution. routing.json is extended with the same `practices` dict right after the routing record is written. `anvil/routing.py` is unchanged.

### anvil/cli.py
- R1: new `propose-practice` command (`--topic --rule --enforcement --languages --surfaces --stations --source --supersedes`) and new `promote-practice` command. The check-brain summary line now includes the active practice count.

## R7, empty base
No brain/practices.md is shipped. `anvil check-brain .` on the factory: PASS, 0 active practices. Fixtures exist only inside the tests.

## R8, compatibility and coordination
- Issue 33 (scoped learnings) has not merged at this ref: brain.py has no scope matcher. Matching is implemented in the brain module (`_scope_overlaps`, `_scope_matches`), so there are now two matchers in parallel. Folding them together is follow-on work once issue 33 lands.
- With no practices base, the packets of a full sdlc-default run are byte-identical to the base ref's packets. I checked this by hashing every packet.md from the same run on the base ref (stashed) and on this change. The only difference is the report's `practices` field holding `{"resolved": {<station>: []...}, "excluded_topics": [], "active_count": 0}`.

## Open item: S8 verdict assertion
`test_no_base_changes_nothing_but_the_report_field_s8` asserts `report["verdict"] == "approved"`, but the run's verdict is `no_reviews`. The test's fake executor prints its review JSON to stdout. Under the producer channel rule (wo-gh-24), the runner never transcribes executor output into a review file. I ran the same pipeline on the base ref without this change and it also gives `no_reviews` ("Counted 0 reviews, expected 5."). So the assertion does not match today's behavior, and I did not change runner review handling to satisfy it, because that would break an existing contract. Everything else in that test passes: no Practices section, an empty resolution, and active_count 0. The fix belongs to the test-writer: have the fake executor write `runs/<id>/<station>.review.json`, or assert that the verdict equals the baseline verdict.

## Guardrails
- Standard library only; no new dependency.
- No pipeline, station prompt, or learnings behavior changed.
- No file under tests/ created, modified or deleted by this station.
- No em dash or en dash in changed files.
- Nothing published or deployed.
{"model": "claude-opus-5-5"}
