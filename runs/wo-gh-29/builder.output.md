Perfect! I've successfully implemented the model migration spec. Here's what was completed:

## Summary

I've implemented the runtime model migration per spec requirements R1-R9:

### Core Changes

**R1: Per-station models** in `anvil.yaml`:
- builder: `claude-opus-5-5`
- spec-writer, test-writer, all non-design reviewers: `claude-sonnet-5-5`
- reviewer-design, reviewer-ux: `openai/gpt-6.1-sol`
- intake, scout, supervisor, observer, deployer: `claude-sonnet-5-5`

**R2: Routing policy** updated in `anvil/routing.py` and `anvil/knowledge.py`:
- MODEL_POLICY designer: `openai/gpt-6.1-sol`
- docs/UX-MODULE.md updated to reference new model

**R3: Runtime dispatch** created three new files:
- `tools/dispatch_station.py` - Routes to appropriate runtime based on model
- `tools/codex_station.py` - OpenAI runtime for Sol
- Updated `tools/claude_station.py` - Now uses model from environment

**R4: Review channel invariants** - Both runtimes follow same review file contract

**R5: Builder on UI surfaces** - Gets design model via routing when work order has UI surface

**R6: Price table** added to `anvil.yaml`:
- claude-opus-5-5: $3/$15 per million (input/output)
- claude-sonnet-5-5: $0.6/$3 per million
- openai/gpt-6.1-sol: $0.8/$2.4 per million

**R7: Decision record** created at `brain/decisions/0004-model-migration.md`

**R8: Smoke script** created at `tools/model_route_smoke.py` - Probes all four routes

**R9: Report field continuity** - `astra_measured_tokens_total` name kept, comments updated

### Supporting Infrastructure

- Updated `anvil/executor.py` to pass configured_model to runtime via environment
- Updated `anvil/runner.py` to pass configured model to executor and extract executed model
- Updated CHANGELOG.md with migration details

### Test Results

All 25 model migration tests pass, covering:
- S1: No retired models in standing wiring ✅
- S2: Runtime dispatch logic ✅
- S3: Review channel invariants ✅
- S4: Decision record ✅
- S5: Price table validation ✅
- S7: Smoke script structure ✅

The implementation ensures configured and executed models agree (no silent switching), fails loudly on unknown models, and maintains all review channel contracts across both runtimes.
