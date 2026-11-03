I've reviewed the existing spec at `.openspec/specs/astra-consumption/spec.md` and verified it against the work order. The spec is complete and comprehensively covers all requirements:

**Verification:**
- ✓ All five scenarios (S1-S5) from the work order are fully specified
- ✓ All guardrails are present, including the sequencing gate for wo-gh-16
- ✓ Tests map correctly to each scenario
- ✓ Purpose section provides the baseline metrics (45,000 input tokens per request, 70.14 USD Astra cost)
- ✓ Status is "proposed" (appropriate for a spec ready for implementation)
- ✓ All implementation details match: packet budgets, contact sheets, fresh session design review, stable prefix layout, and cost visibility

The spec is production-ready and requires no revision. The output file is already at the specified location.

**Output:** `.openspec/specs/astra-consumption/spec.md` (no changes needed)
