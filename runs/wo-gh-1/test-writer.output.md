I've written comprehensive tests for the project design system feature covering all 5 scenarios from the spec.

**Test file created:** `/home/runner/work/anvil-factory/anvil-factory/tests/test_design.py`

**Coverage:**

- **S1: Scaffolding** - Tests that `anvil init`, `anvil new-project`, and `anvil onboard` create `design/DESIGN.md` and `design/tokens.json` only when absent, and never overwrite existing files
  
- **S2: Structure not style** - Verifies the scaffold contains required sections (brand identity, palette, typography, voice, art direction, tokens, components, layout, motion, quality bars) with placeholders and questions, but no factory-imposed colors or styles

- **S3: Packet injection** - Tests that interface-producing stations (builder, writer, media-producer, brief-writer, reviewer-design) receive a Project design section with token values and quality bars, while other stations (like scout) do not

- **S4: Reviewer-design station** - Validates that reviewer-design exists in the station catalog and is added to the parallel reviewer groups in sdlc-default, content-default, and content-short pipelines

- **S5: Missing design warnings** - Checks that projects without a design system produce warnings in run reports and that reviewer-design returns changes_requested verdict with a finding about the missing design system

The tests reference implementation functions that will be built by the builder station: `scaffold_design_system()`, `load_design_system()`, and `packet_design_section()`.
