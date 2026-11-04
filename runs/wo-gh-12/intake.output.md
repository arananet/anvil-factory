Looking at the work order and spec to make an intake judgment.

This is a closing and repair run with a well-defined scope: fix 10 specific test failures across 4 categories (prompt contract violation, routing surface rule defects, test simulation fix, and registry expectation update). The work is buildable as stated with clear success criteria (green gate suite) and explicit constraints about protected paths.

The work order asks to:
- Fix implementation defects (prompt contract, routing logic)  
- Fix test defects (simulation, registry expectation)

All focused on completing the reviewer-ux feature integration. This is a coherent unit of repair work, not multiple separate changes.

**Risk assessment**: Medium - this touches internal review tooling and test infrastructure with moderate complexity, but has limited blast radius and doesn't involve production deployment, credentials, or data deletion.

**Surfaces touched**: The work modifies a prompt file (documentation/content), routing logic, and test code. From the surfaces vocabulary, `content` is the clearest match for the PROMPT.md changes.

```json
{
  "intake_outcome": {"outcome": "accepted"},
  "risk": "medium",
  "surfaces": ["content"]
}
```
