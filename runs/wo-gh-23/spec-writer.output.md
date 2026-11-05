Spec revision complete. I've updated `.openspec/specs/readme-showcase/spec.md` to incorporate the gate loopback brief from run 1.

**Key changes:**
- Added "Loopback context" section documenting run 1's no_reviews verdict and the three test defects
- Specified loopback discipline: README from run 1 stands as base, this run fixes tests only
- Detailed the three test defects with fixes for test-writer:
  1. test_showcase_external_links_valid: skip unless ANVIL_LIVE_TESTS=1, use browser user agent
  2. test_station_count_accurate_r3: count StationRegistry from anvil/stations.py (27 stations)
  3. test_factory_suite_can_run: remove nested pytest invocation
- Updated R3 claim hygiene: station count now 27 (up from 25 with checks-gate and reviewer-ux)
- Clarified scope: loopback changes tests and evidence only, not README or protected paths
- Added acceptance criteria: all three test defects fixed, suite green

Output: `.openspec/specs/readme-showcase/spec.md` (90 lines), `runs/wo-gh-23/spec-writer.output.md`
