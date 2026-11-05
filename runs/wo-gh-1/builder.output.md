## Implementation Complete

I've successfully implemented the project design system feature according to the spec. All tests pass (94/94).

### What was built:

**S1: Scaffolding** 
- Created `anvil/design.py` with `scaffold_design_system()` function
- Updated `init_project()`, `new_project()`, and `onboard_project()` to scaffold design files
- Design files are created only when absent, never overwrite existing files
- Factory repo now has its own design system (dogfooding)

**S2: Scaffold structure**
- `design/DESIGN.md` template with sections: brand identity, art direction, tokens, component/layout rules, motion rules, quality bars
- `design/tokens.json` template with placeholder token structure (colors, typography, spacing, layout, motion)
- No factory-imposed styles—only placeholders and questions

**S3: Packet injection**
- `packet_design_section()` function computes design section once per run
- Interface stations (builder, writer, media-producer, brief-writer, reviewer-design) receive Project design section in packets
- Section includes token values and quality bars
- Non-interface stations receive no design section

**S4: reviewer-design station**
- Created `stations/reviewer-design/` with station.json and PROMPT.md
- Contract judges interface output against project design system
- Added to parallel reviewer groups in sdlc-default, content-default, and content-short pipelines
- All existing reviewers retained

**S5: Warnings and findings**
- RunReport now includes warnings list
- Missing design system produces warning when interface stations are present
- reviewer-design returns changes_requested verdict with finding when no design system exists

**Additional work:**
- Updated CHANGELOG.md
- Created `docs/DESIGN-SYSTEM.md` documentation
- Updated station count in tests (24→25 stations)
- Fixed test bug (case-sensitivity issue)
- Updated supervisor tests to include reviewer-design
- All 94 tests passing
