Perfect! All tests pass. Let me create a final summary of the implementation.

## Summary

I've successfully implemented the spec in `.openspec/specs/astra-consumption/spec.md` to reduce Astra route consumption. All 17 new tests pass, and all 144 existing factory tests continue to pass.

### Changes Made

**Sequencing Gate Verification**: Confirmed that the run branch has the wo-gh-16 merge (verified `review_suffix` function in `tools/claude_station.py` and "Output Format" sections in station prompts).

**S1: Packet Budget System**
- Added `estimate_tokens()` function in `anvil/runner.py` (deterministic, using `CHARS_PER_TOKEN` constant)
- Added `prepare_packet()` with trim order: compact tokens → reduced quality bars → limited learnings
- Added budget tracking to all station steps: `measured_tokens`, `budget`, `budget_action`
- Factory defaults in `anvil/config.py`: 50,000 tokens for budgeted stations
- Budgeted stations: builder, writer, media-producer, brief-writer, reviewer-design

**S2: Evidence Image Policy**
- Added `assemble_contact_sheet()` in `anvil/runner.py` (PNG only, scales down to max width, never up)
- Extended `WorkOrder` model with `spec_path` and `evidence_images` fields
- Factory default: 1600px max width for contact sheets

**S3: Fresh Session Design Review**
- Added `build_reviewer_design_packet()` with scoped content (design, spec, diff summary, contact sheet)
- Added `verify_packet_allowlist()` for deterministic allowlist checking
- Packet contains no builder transcript or full file contents

**S4: Stable Prefix Layout**
- Modified `_packet_text()` to assemble stable sections first (prompt, design, learnings), then variable sections (work order, upstream steps)
- Enables provider prefix caching

**S5: Per Station Cost Visibility**
- Each step records: `configured_model`, `executed_model`, `measured_tokens`, `budget`, `budget_action`, `usage` (when runtime reports it)
- Cost stays null unless runtime reports numeric cost

**Supporting Functions**
- Added `packet_design_section_compact()` and `packet_design_section_reduced()` in `anvil/design.py`
- Added `packet_learnings_section_limited()` in `anvil/brain.py`
- Added config helpers: `get_station_budget()`, `get_contact_sheet_max_width()`
- Added exceptions: `PacketBudgetError`, `ContactSheetError`, `AllowlistViolation`

All code uses Python standard library only (no external dependencies). No em/en dashes in the produced files.
