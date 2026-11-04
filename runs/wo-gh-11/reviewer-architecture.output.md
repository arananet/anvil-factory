## Architecture Review Complete

**Verdict: PASS**

The S10 guided designation wiring is complete and architecturally sound.

### What Was Implemented

1. **Station dataclass enhanced** (`anvil/stations.py`):
   - Added `guided: bool = False` field to Station dataclass
   - Preserved in `load_registry` to read from station.json files

2. **Runtime model selection** (`anvil/runner.py`):
   - Import `get_design_model_from_routing` from knowledge module
   - Apply design model when `station.guided` is True
   - Special case for builder: only applies design model when working on UI surface (`"ui" in work_order.surfaces`)

3. **Station declarations** (`stations/*/station.json`):
   - Builder, reviewer-design, and writer properly declare `"guided": true`
   - Each has `"designation": "guided design station"` for catalog metadata

4. **Policy integration** (`anvil/knowledge.py`, `anvil/routing.py`):
   - `get_design_model_from_routing()` reads `MODEL_POLICY["designer"]`
   - Design model is "openai/gpt-6-astra" as specified in routing policy

### Architecture Fit

- Follows existing patterns for model selection and routing overrides
- Integrates cleanly with station registry, work order surfaces, and routing record  
- Design model is read from policy at runtime, not hardcoded in station files
- Proper precedence: guided designation takes final precedence over other model selections
- Defensive programming with appropriate null checks and default values

**No architectural issues found.** The implementation satisfies loopback 2 requirement #1 completely.
