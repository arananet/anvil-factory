Looking at this work order to judge if it's buildable as stated.

**Work order wo-gh-8**: Implement risk and surface routing for reviewer sets and station models based on a spec document.

**Analysis**:
- Clear scope: Implement 6 scenarios (S1-S6) for routing reviewers and models based on risk/surfaces
- References a spec file: `.openspec/specs/risk-routing/spec.md`
- Defined deliverables: routing logic, config, tests, docs, CHANGELOG
- Single coherent feature: risk-based routing system
- No harmful, deceptive, or unlawful intent

**Risk rating**: **Medium**
- Modifies CI/CD review routing logic
- Controls security reviewer selection (S2) - errors could skip necessary security review
- Blast radius contained to review process, not end-user systems
- Testable and reversible

**Surfaces touched**:
- `security`: Controls when security reviewers are included in review sets
- `deploy`: Modifies CI/CD pipeline infrastructure and routing behavior

```json
{
  "intake_outcome": {
    "outcome": "accepted"
  },
  "risk": "medium",
  "surfaces": ["security", "deploy"]
}
```
