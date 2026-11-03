Security review complete. The review has been written to `runs/wo-gh-21/reviewer-security.review.json`.

**Verdict**: changes_requested

**Summary**: Found 6 security issues requiring attention:

1. **PNG decompression bomb vulnerability** - No size limits before decompressing PNG data could allow memory exhaustion attacks
2. **Missing CRC validation** - PNG chunks are parsed without verifying integrity checksums
3. **Path traversal risk** - File paths in WorkOrder fields lack validation to ensure they're within project boundaries
4. **Weak allowlist enforcement** - Simple regex patterns could miss various file reference formats
5. **PNG chunk bounds checking** - Malformed chunks with excessive lengths could cause out-of-bounds reads
6. **Output path validation** - Contact sheet output path not validated to be within expected directory

All findings reference specific locations in anvil/runner.py and anvil/model.py with concrete remediation steps.
