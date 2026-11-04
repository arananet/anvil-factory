Perfect. My work as test-writer is complete:

## Summary

Fixed the single failing test `test_exception_sanitization_prevents_credential_leakage` in `tests/test_post_deploy_health.py`:

**The Problem**: Test patched `requests.get` but anvil/health.py is standard library only - when requests isn't installed, `anvil.health.requests` is `None`, causing the code to raise an exception before reaching the patched call.

**The Fix**: 
- Patched `anvil.health.requests` (the module reference) instead of `requests.get` (global)
- Created a proper mock with exceptions submodule to satisfy the runtime checks
- Used a realistic exception format with Bearer token and internal hostname that matches the sanitization patterns

**Result**: All 387 tests pass. The test now correctly verifies that credential and topology data gets sanitized from exception messages.
