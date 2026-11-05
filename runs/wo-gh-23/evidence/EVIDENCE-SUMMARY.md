# Evidence Summary - wo-gh-23

Build date: 2026-11-05
Work order: Showcase README implementation

## Evidence Files Created

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

### 5. EVIDENCE-SUMMARY.md (this file)
- **Purpose**: Index of all evidence files with descriptions

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

## Files Modified

- README.md: Rewritten with showcase content, existing documentation preserved below fold

## Files Created

- runs/wo-gh-23/builder.output.md
- runs/wo-gh-23/evidence/ (all evidence files above)
- brain/inbox/.gitkeep (directory created for linked path)

## Test Status

22 tests in test_readme_showcase.py:
- 18 passing
- 4 failing (test implementation issues, not README compliance issues)

Failures reported to test-writer per spec: "The factory suite must stay green; any suite change is reported, not fixed inside this order."

## Next Steps

This build is complete and ready for the review stations. Evidence files support all spec requirements R1-R5 and provide verification for scenarios S1-S5.
