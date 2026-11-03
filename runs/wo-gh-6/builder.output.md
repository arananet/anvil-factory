Implementation complete. I've successfully implemented all the loopback round fixes for the checks gate:

## Critical S4 Base Ref Enforcement Fix

**Security issue resolved**: Configuration is now read from the git base ref, not the working tree. This prevents branches from modifying the checks they'll be judged by.

- Added `resolve_base_ref_config()` in `anvil/gates.py` using `git show <base-ref>:anvil.json`
- Updated `run_pipeline()` to accept and propagate `base_ref` parameter
- Modified `_get_changed_files()` to compare against base ref with `git diff <base-ref>...HEAD`
- Both S4 regression tests pass (uncommitted and committed mutations to config don't affect gate commands)

## Hygiene Fixes

1. **Documentation**: Created `docs/CHECKS-GATE.md` covering purpose, configuration, base ref rule, protected paths, two gate phases, shell command safety
2. **CHANGELOG**: Added comprehensive entry in Unreleased section
3. **Refactored gate logic**: Moved gate evaluation from `runner.py` to pure function `checks_gate()` in `anvil/gates.py` with signature `checks_gate(phase, base_ref_config, changed_files, project_dir, work_order_id, timeout)`
4. **Protected paths default**: Now references config file path dynamically instead of hardcoded `"anvil.json"`
5. **Station kind**: Changed from `"gate"` to `"deterministic"` in `stations/checks-gate/station.json`

## Test Results

- All 137 tests pass including 18 checks gate tests and 8 gate pure function tests
- All 8 pipelines validate successfully
- S4 regression tests prove base ref enforcement works for both uncommitted and committed config mutations

The implementation closes all round 1 findings while maintaining the full S1-S6 scenario coverage.
