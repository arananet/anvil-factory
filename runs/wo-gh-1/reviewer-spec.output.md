Review complete. The implementation passes all scenarios:

**S1 - Scaffolding**: All three entry points (`anvil init`, `anvil new-project`, `anvil onboard`) scaffold design/DESIGN.md and design/tokens.json when absent. The `scaffold_design_system()` function checks file existence before writing, never overwriting.

**S2 - Structure not style**: The scaffold contains all required sections (brand identity with palette/typography/voice, art direction, tokens, component/layout rules, motion rules, quality bars). Uses "TODO" placeholders throughout with no factory colors or fonts prescribed.

**S3 - Packet injection**: The `packet_design_section()` function targets exactly the five interface-producing stations (builder, writer, media-producer, brief-writer, reviewer-design) and no others. Tokens and quality bars are extracted and injected into packets per run.

**S4 - Design reviewer**: Station exists at `stations/reviewer-design/` with agent kind and correct contract. Added to parallel reviewer groups in all three pipelines (sdlc-default, content-default, content-short) with all existing reviewers preserved.

**S5 - Warnings and findings**: Run reports gain a warnings list. When interface stations run without design/DESIGN.md, a warning is recorded. When reviewer-design runs without a design system, it forces verdict `changes_requested` with an explicit finding.

All additional requirements met: factory dogfooding (design/ directory present), comprehensive tests (5 scenarios covered, all pass), documentation (docs/DESIGN-SYSTEM.md), CHANGELOG updated, full suite green (94 tests pass), all pipelines valid.
