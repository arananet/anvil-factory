I'll check the existing spec against the work order requirements.

The spec at `.openspec/specs/community-by-default/spec.md` already exists and is marked as **approved**. Let me verify it covers all work order requirements:

**Verification checklist:**
- ✓ Defines canonical location: templates/community/ and anvil/community.py
- ✓ Lists all seven community files with correct paths
- ✓ Covers greenfield door (scaffold.py)
- ✓ Covers brownfield door (onboard.py)  
- ✓ Specifies metadata plumbing (name, description, contact)
- ✓ Details each file's content requirements
- ✓ Includes test scenarios S1-S4 from work order (plus S5-S7 extras)
- ✓ States constraints (stdlib only, no em/en dash, no community files in this repo)
- ✓ Requires green test suite

**Assessment:**

The spec is complete, comprehensive, and approved. It fully captures the work order requirements with additional quality scenarios (S5-S7) covering contributor-facing content, suite validation, and dogfooding boundaries.

The spec is ready for implementation. No revision needed.
