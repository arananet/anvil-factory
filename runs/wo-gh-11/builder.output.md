## Summary

I've successfully completed the gate loopback 2 requirements for wo-gh-11. The S10 guided designation is now fully wired into the runtime.

### Changes Implemented

1. **anvil/stations.py**:
   - Added `guided: bool = False` field to Station dataclass
   - Updated `load_registry()` to preserve the `guided` field from station.json files

2. **anvil/runner.py**:
   - Added `get_design_model_from_routing` import from knowledge module
   - Implemented guided designation logic that applies the design model from routing policy
   - Special handling for builder: only applies guided model for UI surface work

3. **CHANGELOG.md**:
   - Updated entry to document runtime wiring of guided designation

### Model Application Logic

- **reviewer-design**: Always uses design model when guided=true
- **writer**: Always uses design model when guided=true  
- **builder**: Only uses design model when guided=true AND "ui" in work_order.surfaces

The design model is read from `MODEL_POLICY["designer"]` in the routing policy, currently set to "openai/gpt-6-astra".

### Verification

✅ All 309 tests pass  
✅ All 27 design knowledge tests pass  
✅ All pipelines valid  
✅ No modifications to restricted paths (tests/, anvil.json, pipelines/, .github/workflows/)

The implementation fulfills S10: guided design stations now receive and apply the design model from the recorded routing policy at runtime.
