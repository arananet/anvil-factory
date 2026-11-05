# Link and Claim Verification Evidence

Executed: 2026-11-05
README: /home/runner/work/anvil-factory/anvil-factory/README.md

## Relative Links Verification

Checking all relative links resolve in the tree:

- [x] runs/wo-gh-9/ - EXISTS (directory with complete run evidence)
- [x] runs/wo-gh-9/reviewer-spec.review.json - EXISTS
- [x] runs/wo-gh-9/reviewer-security.review.json - EXISTS
- [x] runs/wo-gh-9/reviewer-tests.review.json - EXISTS
- [x] runs/wo-gh-9/reviewer-architecture.review.json - EXISTS
- [x] runs/wo-gh-9/reviewer-design.review.json - EXISTS
- [x] brain/inbox/ - EXISTS
- [x] brain/learnings.md - EXISTS
- [x] docs/MEMORY-GATE.md - EXISTS
- [x] stations/triage-human/station.json - EXISTS
- [x] stations/approver/station.json - EXISTS
- [x] runs/wo-gh-9/report.json - EXISTS
- [x] docs/ARCHITECTURE.md - EXISTS
- [x] docs/SDLC.md - EXISTS
- [x] docs/EXECUTION.md - EXISTS
- [x] docs/STATUS-PAGE.md - EXISTS
- [x] docs/SUPERVISOR.md - EXISTS
- [x] brain/project.md - EXISTS
- [x] templates/spec.md - EXISTS
- [x] LICENSE - EXISTS

All relative links resolve: PASS

## External Showcase Links Verification

Checking the three Built by ANVIL links answer live:

Testing https://sentia.info-693.workers.dev... LIVE (HTTP success)
Testing https://platform25.pages.dev... LIVE (HTTP success)
Testing https://anvil-status.pages.dev... LIVE (HTTP success)

## R3 Claim Hygiene Verification

Verifying every number against the tree:

### Station count
- Actual stations in tree: 27
- Claimed in README: 27
- Status: MATCH

### Pipeline count
- Actual pipelines in tree: 8
- Claimed in README: 8
- Status: MATCH

### Test suite count
- Actual test functions in tree: 502
- Claimed in README: over 500
- Status: MATCH (actual: 502, claim: over 500)

### Reviewer count correction
- Spec requirement: Correct from four to five reviewers
- README check: "five software reviewers" ✓
- README check: "five different reviewers" (content) ✓
- README check: "five parallel reviewers" (pipelines) ✓
- README check: "Aggregate the five reviews" (approver) ✓
- README check: Station table shows 5 distinct reviewer-* stations for software ✓
- README check: Station table shows 5 distinct reviewer-* stations for content ✓
- Status: CORRECTED (no instances of "four reviewers" remain)

### Capability items verification
- S4 fix in checks-gate: Referenced as merged (wo-gh-6 in git history)
- Intake outcomes: Referenced as merged (wo-gh-7 in git history)
- Risk and surface routing: Referenced as merged (wo-gh-8 in git history)
- Rendered design review: Referenced as merged (wo-gh-9 in git history, reviewer-design in station table)
- Per job cost: Referenced as merged (wo-gh-10 in git history)
- Status: VERIFIED (all capability items in main, cited as fact not roadmap)

## Guardrails Check

### Em dash and en dash prohibition
- Status: PASS (no em dash or en dash characters)

## Star Call to Action Check

Exact wording required: "If ANVIL is useful to you, a star helps other builders find it."
- Occurrences found: 2
- Status: PASS (appears exactly twice as required)

## Summary

All verification checks completed. Review the status of each item above for pass/mismatch indicators.
