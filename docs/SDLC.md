# ANVIL and the SDLC

The default pipeline, sdlc-default, maps to the classic software development life cycle.

| SDLC phase | ANVIL stations | Artifact |
|---|---|---|
| Requirements | intake, spec-writer | Work order, OpenSpec spec |
| Design | spec-writer, reviewer-architecture (early read) | Spec, brain/decisions |
| Implementation | test-writer, builder | Tests first, then the code change |
| Verification | reviewer-spec, reviewer-security, reviewer-tests, reviewer-architecture, approver | Four review JSON files, one verdict |
| Release | triage-human, deployer | Triage decision, release record |
| Maintenance and observe | observer | Observation report, new work orders when needed |

Notes:
- Test writing sits before implementation on purpose. The tests come from spec scenarios, so verification starts in the design phase.
- Human triage sits between verification and release, not at the end. Risky work gets a human before it ships.
- Observation feeds maintenance: what the observer finds becomes a new work order, and the line runs again.
