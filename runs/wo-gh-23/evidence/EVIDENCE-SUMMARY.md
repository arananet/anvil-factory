# Evidence Summary - wo-gh-23 Loopback Run

Build date: 2026-11-05 (loopback run)  
Work order: Showcase README implementation  
Context: Loopback after run 1 verdict no_reviews (checks gate failed, 3 test defects)

## Loopback Discipline

Per spec section "Loopback context":
- The README product from run 1 stands as the base (no changes to README.md)
- This loopback refreshes run evidence only
- Test fixes belong to the test-writer station (builder does not touch tests/)
- Playwright and Chromium now staged in execute workflow

## Evidence Files

All files in runs/wo-gh-23/evidence/:

### 1. quickstart-execution.txt
- **Purpose**: Verification that the quickstart completes under 5 minutes
- **Content**: Full execution record of cloning anvil-example-taskline and running tests
- **Result**: 0.322s total (clone: 0.212s, tests: 0.110s), 6/6 tests passing
- **Spec requirement**: S5, R1

### 2. social-preview.png
- **Purpose**: Social preview image for GitHub repository card
- **Dimensions**: 1280 x 640 pixels (verified)
- **Content**: ANVIL wordmark, station line visualization, one-line quote
- **Format**: PNG, 32KB
- **Spec requirement**: R4
- **Note**: Ready for upload via GitHub Settings > Social preview (operator step)

### 3. demo-note.md
- **Purpose**: Document why animated demo was not produced
- **Content**: Explanation of animated demo infeasibility and fallback to strongest truthful static evidence
- **Spec requirement**: R1 fallback clause documentation

### 4. link-and-claim-verification.md
- **Purpose**: Automated verification of all README links and claims
- **Content**: 
  - All relative links checked (20/20 pass)
  - All external showcase links verified live (3/3 live)
  - R3 claim hygiene checks (stations: 27, pipelines: 8, tests: 502)
  - Reviewer count correction verified
  - Capability items verification (wo-gh-6 through wo-gh-10 in git history)
  - Guardrails check (no em/en dashes, exact CTA wording twice)
- **Result**: All checks passed
- **Spec requirement**: Tests and verification section

### 5. readme-rendered-desktop.png (NEW in loopback)
- **Purpose**: Capture of rendered README from real GitHub view
- **Source**: https://github.com/arananet/anvil-factory/tree/anvil/run-readme-showcase
- **Viewport**: Desktop width (1280px)
- **Size**: 1.3MB
- **Format**: PNG
- **Spec requirement**: Tests and verification section (rendered README verified)
- **Note**: This capture was not available in run 1 due to missing Playwright; successfully produced in loopback with Playwright/Chromium staged

### 6. EVIDENCE-SUMMARY.md (this file)
- **Purpose**: Index of all evidence files with descriptions and loopback context

## Verification Results

### Links
- ✓ All 20 relative links resolve in tree
- ✓ All 3 showcase external links answer live (Sentia, Platform25, Status Board)

### Claims (R3)
- ✓ Station count: 27 (matches tree)
- ✓ Pipeline count: 8 (matches tree)
- ✓ Test suite: 502 functions (claimed as "over 500")
- ✓ Reviewer counts: All corrected to five
- ✓ Capability items: All verified in git history

### Guardrails
- ✓ No em dash or en dash characters
- ✓ Star CTA appears exactly twice with exact wording

### Spec Scenarios
- ✓ S1: First screen shows what ANVIL is, what it built, how to try it
- ✓ S2: Trust section claims link to evidence
- ✓ S3: All claims verifiable against tree in under 1 minute each
- ✓ S4: Social preview image ready (1280x640, production quality)
- ✓ S5: Quickstart executed under 5 minutes (0.322s actual)

## Test Defects from Run 1

Three test defects identified in tests/test_readme_showcase.py (test-writer output):

1. **test_showcase_external_links_valid**: Needs to skip unless ANVIL_LIVE_TESTS=1 and use browser user agent (Cloudflare bot filtering)
2. **test_station_count_accurate_r3**: Counter must use StationRegistry from anvil/stations.py (returned 0 in run 1)
3. **test_factory_suite_can_run**: Nested pytest invocation must be removed or made collection-only (pytest not a project dependency)

Per loopback discipline: builder does not touch tests/ (protected paths). These fixes belong to test-writer station.

## Files Modified in Loopback

None. Per spec: "this loopback changes the three tests and refreshes run evidence only" - README.md from run 1 stands as the base.

## Files Refreshed in Loopback

- runs/wo-gh-23/evidence/EVIDENCE-SUMMARY.md (updated with loopback context)
- runs/wo-gh-23/evidence/readme-rendered-desktop.png (NEW - now successfully captured)

## Next Steps

- Test-writer station: Fix the three test defects
- Checks gate: Re-run with fixed tests
- Review stations: Execute after checks gate passes
- Operator (post-merge): Upload social-preview.png, set metadata per R4
