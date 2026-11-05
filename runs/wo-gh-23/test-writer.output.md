Tests written. Created `tests/test_readme_showcase.py` with 22 test methods mapping to spec scenarios S1-S5 and verification requirements:

**Spec scenario coverage:**
- **S1** (First screen): 5 tests verify header, Built by ANVIL block, quickstart, star CTA, and style rules
- **S2** (Trust section): 4 tests verify all three trust mechanisms link to evidence
- **S3** (Claim hygiene): 4 tests verify station count, pipeline count, reviewer count correction (four→five), and test suite count against tree
- **S4** (Social preview): 1 test verifies 1280x640 dimensions when image exists
- **S5** (Quickstart execution): 1 test verifies quickstart evidence under 5 minutes

**Additional verification tests:**
- Link validation: 2 tests for relative links and external showcase links
- Closing content: 4 tests for Contributing, License, Developer, ko-fi sections per house template
- Factory suite stability: 1 test ensures suite can run

All tests check against the actual tree state (station/pipeline/test counts), verify link resolution, and enforce the no em/en dash style rule. Tests are designed to run before implementation, failing initially, then passing once the builder produces the README per spec.
