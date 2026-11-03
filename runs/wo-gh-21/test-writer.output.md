Tests written for loopback gate round 2. Updated `tests/test_astra_consumption.py` with 11 new tests covering:

**Integration (items 1-2):**
- Contact sheet assembly in run path
- Scoped packet builder in run path  
- Architectural layer validation

**Security hardening (items 3-4):**
- Provenance-based allowlist checking (2 tests)
- PNG size caps enforcement
- PNG CRC verification
- PNG chunk bounds checking
- Output path validation
- WorkOrder path validation

**Report visibility (item 5):**
- Real run report.json field verification

All tests map to spec scenarios. Suite now contains 26 tests total. Python syntax validated and all tests loadable.

Output: `runs/wo-gh-21/test-writer.output.md`
