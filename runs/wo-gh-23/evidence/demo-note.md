# Demo Evidence Note

## Animated Demo Feasibility

Per spec R1, the README should include "an animated demo of one real run cycle...produced from a real run's own evidence...never a mockup."

**Assessment**: A truthful animated demo (GIF or MP4) cannot be produced within the line constraints at this build session. Creating such a demo would require:

1. Screen captures of multiple stages (work order, spec, tests, build, reviews, human gate, merge)
2. Video editing and composition tools
3. Timing and transition work
4. Verification of text accuracy in each frame

**Resolution**: Per the spec's fallback clause, "if a truthful animated demo cannot be produced inside the line, say so plainly in the run output and ship the README with the strongest truthful static evidence instead."

## Strongest Truthful Static Evidence

The README will instead link to:

1. **Complete run evidence from wo-gh-9** (rendered design review capability):
   - Work order: work_orders/wo-gh-9.json
   - Spec: .openspec/specs/design-review-rendered/spec.md
   - Tests: tests/test_design_review_rendered.py
   - Build artifacts: runs/wo-gh-9/ with all station outputs
   - Reviews: 5 review files (spec, security, tests, architecture, design)
   - Run report: runs/wo-gh-9/report.json showing execution through to merge

2. **Taskline example repository** (arananet/anvil-example-taskline):
   - Complete greenfield build trail
   - Evidence files showing red-green TDD cycle
   - All station artifacts preserved

3. **Status board** (https://anvil-status.pages.dev):
   - Live run status from real factory operations

This static evidence is truthful and verifiable, referencing only runs that actually happened and are recorded in the repository.
