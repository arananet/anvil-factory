## Implementation Complete

I've successfully implemented all three findings from gate round 3:

### 1. **CRITICAL: Wired S3 provenance check into preparation path**
- `verify_packet_allowlist_by_provenance` now called in `prepare_reviewer_design_step` (anvil/runner.py:425)
- `build_reviewer_design_packet` returns `(packet, allowlist)` tuple
- Provenance check executes before any model call, failing with `AllowlistViolation` on violations
- Allowlist is surfaced so both building and verification use the same list

### 2. **Resolved .stations layer violation**
- Removed function-scoped `from .stations import load_registry` from `build_reviewer_design_packet`
- Caller (`prepare_reviewer_design_step`) resolves prompt through station registry and passes it in
- No imports from .stations at any scope for this functionality

### 3. **Security residuals fixed**
- **(a) Path boundary matching**: Uses `os.path.normpath` to resolve `..` traversals, enforces exact matches or nested paths at separator boundaries
- **(b) IDAT decompression bounds**: Limited to expected raw size calculated from IHDR dimensions, verified after decompression
- **(c) IDAT accumulation cap**: Caps accumulated compressed bytes before decompression based on expected raw size

### Test Results
- **All 186 factory tests pass** ✓
- **35 astra consumption tests pass**, including:
  - Path boundary tests (sibling prefix, partial segment, traversal, exact, nested)
  - IDAT security tests (decompression bounds, accumulation cap)
  - Integration tests (provenance check in preparation path)

Implementation documented in `/runs/wo-gh-21/builder.output.md` and ready for review.
