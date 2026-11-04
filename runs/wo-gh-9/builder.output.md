## Builder Station Complete

I've completed the Gate Loopback 2 builder work. Here's what was done:

### Implementation Fix

Fixed a **resource leak** in the capture module that was exposed by ResourceWarnings in the test output:
- Changed `_start_static_server()` and `_start_serve_command()` to use `subprocess.DEVNULL` instead of `subprocess.PIPE` for stdout/stderr
- Since we don't consume the server output, using DEVNULL prevents file descriptor leaks
- All security constraints remain intact (shell=False, process group cleanup, etc.)

### Test Results

✅ All 25 rendered design review tests: **PASS**  
✅ Full suite (267 tests): **PASS** (1 skipped)  
✅ No ResourceWarnings in rendered design review tests

### Complete Implementation Verified

All required components are in place:
- **Capture module** (`anvil/capture.py`): Security-hardened with all Round 1 fixes
- **Configuration** (`anvil.yaml`): Servable config for factory's status page  
- **Runner integration** (`anvil/runner.py`): Captures after builder, injects packet section
- **Documentation** (`docs/RENDERED-DESIGN-REVIEW.md`): Complete
- **CHANGELOG**: Updated
- **S4 demonstration**: Screenshots exist at `runs/wo-gh-9/evidence/` (158K + 79K)
- **Tests**: 24 real tests + 1 stub

### Note on Remaining Stub

Per packet rules, builder must not modify tests. One test remains a stub (`test_serve_command_validation_prevents_shell_injection` at line 32) - it only asserts a list exists without actually testing the security constraint. 

The **implementation is secure** (uses `shlex.split` and `shell=False` correctly), but the test doesn't verify it. This is test-writer's responsibility per the packet.

### Changes Made
- `anvil/capture.py`: 4 lines changed (PIPE → DEVNULL in 2 functions)
- `runs/wo-gh-9/builder.output.md`: Created with full summary
