Implementation complete! All requirements have been satisfied:

**Summary:**

✓ **R1 - Declared captures**: Contact sheet now assembles from declared PNG images (in order) + run directory captures  
✓ **R2 - Loud failure**: Missing/escaping declared evidence fails with `DeclaredEvidenceMissing` before reviewer-design executes  
✓ **R3 - Packet naming**: Evidence section lists contact sheet path AND each declared evidence path individually  
✓ **R4 - Reviewer packets**: All reviewer stations get "Declared evidence inputs" section when evidence_images declared  
✓ **R5 - Review only pipeline**: New `content-film-review.json` with intake → parallel [reviewer-design, reviewer-facts] → approver → triage-human → publisher → observer

**Test Results:**
- All 6 scenario tests pass (T1-T5)
- Full factory suite: 202/203 tests pass (1 pre-existing failure unrelated to this work)
- All 9 pipelines valid

**Files Changed:**
1. anvil/runner.py - Core implementation
2. pipelines/content-film-review.json - New pipeline
3. tests/test_review_parsing_integrity.py - Updated pipeline count
4. CHANGELOG.md - Added Unreleased entry

**Frozen Surfaces Honored:** parse_review semantics, canonical review contract, reviewer Output Format sections, review_suffix, wo-gh-24 producer channel, wo-gh-21 PNG hardening all unchanged. Python stdlib only, no em/en dashes, content/ untouched.

**Staging Provenance Verified:** Film evidence at content/youtube-anvil-v2/anvil-youtube-v2.mp4 hash a277ce32... size 21,401,761 bytes confirmed.
