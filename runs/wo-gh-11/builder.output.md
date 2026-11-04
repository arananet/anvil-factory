## Implementation Complete

I've successfully implemented the design knowledge base and UX module per the spec. Here's what was delivered:

### Core Implementation

**Knowledge Module** (`anvil/knowledge.py`):
- Built-in knowledge loader with validation
- Operator-supplied pack loading and validation
- Deterministic product type slice matching
- Packet injection for design stations
- Project product type detection from brain/design files

**Built-in Dataset** (`design-knowledge/`):
- 5 styles (modern-minimal, data-dense, friendly-conversational, technical-precise, editorial-spacious)
- 4 palettes across 3 product types (dashboard, mobile-app, marketing-site)
- 4 font pairings (classic-readable, modern-geometric, technical-mono, editorial-contrast)
- 14 UX guidelines grouped by concern (accessibility, spacing, hierarchy, responsive, motion, forms, feedback)
- 4 product type notes (dashboard, mobile-app, marketing-site, documentation)

### Station Updates

**Contracts Updated**:
- `reviewer-design`: Authority statement (project design system wins) and citation requirements
- `builder`: Citation requirements for design authoring
- `writer`: Citation requirements for design authoring

**Catalog Updated**:
- All three design stations marked as "guided design station" with designation
- `design_model: "openai/gpt-6-astra"` from routing policy

### Documentation

- **CHANGELOG.md**: Unreleased entry documenting the UX module
- **docs/UX-MODULE.md**: Complete documentation covering knowledge base layer, packs, authority rule, and guided stations

### Test Coverage

✅ All 20 design knowledge tests pass (S1-S10 scenarios covered)
✅ Full test suite green: 302 tests passing
✅ All 8 pipelines remain valid
✅ No workflow files modified (per standing note)

The implementation fulfills all requirements from work order wo-gh-11 and spec `.openspec/specs/design-knowledge/spec.md`.
