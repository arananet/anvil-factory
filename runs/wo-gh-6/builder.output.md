Implementation complete! All changes have been made and tested.

## Summary

Fixed the S4 base ref control to wire it through the CLI execution path (loopback round 3). The CLI now:

1. **Automatically derives the base ref** as the merge base of HEAD and the project's base branch when running in a git repository
2. **Accepts `--base-ref` option** for manual override
3. **Supports `base_branch` configuration** in `anvil.json` 
4. **Records the base ref** in the run report for auditable provenance

### Key Changes

- **`anvil/gates.py`**: Added `derive_base_ref()` function
- **`anvil/cli.py`**: Integrated automatic derivation and `--base-ref` option
- **`anvil/runner.py`**: Added `base_ref` field to RunReport
- **`docs/CHECKS-GATE.md`**: Documented base ref derivation and CLI option
- **`CHANGELOG.md`**: Added loopback round 3 entry
- **`tests/test_checks_gate.py`**: Fixed CLI regression test

### Test Results

✅ All 144 tests pass, including the critical CLI regression test that proves check commands are resolved from the base ref through the CLI path, not from working tree modifications.

The S4 security control is now properly enforced: a branch cannot modify the checks it will be judged by, whether running through the module API or the CLI.
