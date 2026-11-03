Security review complete. I found five security issues, including one critical gap where the provenance-based allowlist check is implemented but never enforced.

**Review verdict: changes_requested**

**Key findings:**
1. **Critical** - Provenance allowlist verification function exists but is never called in the run path
2. **High** - Substring matching in allowlist check allows unintended path matches
3. **High** - PNG decompression bomb vulnerability (no validation of decompressed size)
4. **Medium** - Allowlist integration unclear (built but not enforced)
5. **Low** - No cap on accumulated IDAT data before decompression

**Security controls that work correctly:**
- File size caps (100MB before read)
- Dimension caps (50000x50000 from headers)
- PNG CRC verification for all chunks
- Chunk length bounds checking
- Path traversal protection for output paths and WorkOrder file paths

The review has been written to `runs/wo-gh-21/reviewer-security.review.json` as the authoritative verdict, with detailed findings in `reviewer-security.output.md`.
