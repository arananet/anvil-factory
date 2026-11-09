I wrote the tests in a new file, `tests/test_practice_skills.py`, and no existing test file was touched. Because the implementation doesn't exist yet, the module fails at import. The error is `ImportError: cannot import name 'parse_practices'` (from `anvil.brain`), so none of the 23 tests have run.

Every test calls the real brain module, the CLI or `run_pipeline`. Nothing is mocked. I checked that neither the file nor `brain.py`, `runner.py` and `cli.py` contains an em dash or en dash. The test file builds its dash checks from `chr()` codes so the file itself stays clean.

**Scenarios covered**
- **S1:** propose lands in `brain/inbox/` and leaves `practices.md` alone. The `propose-practice` and `promote-practice` commands work end to end.
- **S2:** a promotion succeeds with run-report provenance or with a decision record under `brain/decisions/`. It is refused for a missing report, a missing record, unsupported evidence, or a malformed proposal.
- **S3:** a same-topic, overlapping-scope conflict is refused and names the conflicting practice. Disjoint scopes coexist, and an unrestricted dimension counts as overlapping.
- **S4:** `Supersedes` marks the old practice superseded, it stops resolving, and `check-brain` passes. A `Supersedes` naming an unknown id is refused.
- **S5:** language, station and surface scoping, conjunctive across dimensions and disjunctive within one. Resolution is deterministic, and the runner picks up the config language signal.
- **S6:** a prompt practice appears only in its stations' packets. A gate practice appears only in the checks-gate pre-review output, by id and topic.
- **S7:** an overridden topic resolves nothing. Overrides match exact names only, and `report.json` and `routing.json` carry the same resolution.
- **S8:** with no base, packets have no Practices section and `report.json` records an empty resolution.
- **S9:** `check-brain` fails on a hand-edited conflict and on a malformed base, and passes with no base.
- **R7 and the dash rule:** a guard test that the factory ships no practices and that the produced files contain no dashes.

**Interface choices for the builder.** The spec doesn't fix function names or the language signal, so the names below are my choice. The module docstring in the test file records them. If you prefer different names, they're cheap to change.
- **Brain functions:** `propose_practice`, `promote_practice`, `parse_practices` and `resolve_practices(project, work_order, station_ids, config)`. The last one returns `{"resolved": {station: [ids]}, "excluded_topics": [...], "active_count": n}`.
- **Recording:** that same dict is `report["practices"]` and `routing.json["practices"]`.
- **Language signal:** a `languages` list in `anvil.yaml`. The spec also mentions language signals in the work order, but `WorkOrder` has no language field, so I tested only the config signal.
- **Config:** `practice_overrides` in `anvil.yaml`.
- **Proposal source format:** `Source` is `run <id>, artifact <path>, evidence <ev>` or `decision brain/decisions/<file>`.

The R8 note about reusing issue 33's matcher goes in the run report, so I didn't test it.
{"model": "claude-sonnet-5-5"}
