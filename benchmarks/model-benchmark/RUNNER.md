# Model Benchmark Runner Guide

This guide documents how to run the model benchmark arms for comparing design station models. The benchmark measures three candidate models: openai/gpt-6-astra, anthropic/claude-opus-5.5, and openai/gpt-6.1-sol.

## Overview

The benchmark has two arms:

1. **Reviewer arm**: Receives design system documentation and a fixture page, identifies violations
2. **Builder arm**: Receives design system documentation and a build brief, produces a page

## Fixture and Tooling

### Design System
- `fixture/design/DESIGN.md` - Complete design system rules and quality bars
- `fixture/design/tokens.json` - Machine-readable design tokens

### Fixture Page
- `fixture/src/page.html` - Self-contained HTML page with planted violations
- `fixture/evidence/contact-sheet.png` - Full page screenshot of the fixture

### Ground Truth
- `fixture/ground-truth.json` - Sealed record of 10 planted violations (V1-V10)
- **Never provided to benchmark arms**

### Tools
- `tools/scorer.py` - Deterministic scorer evaluating 12 checks (K1-K12)
- `tools/capture.py` - Playwright-based screenshot capture

## Running the Reviewer Arm

### Packet Contents

The reviewer arm receives:
- `fixture/design/DESIGN.md`
- `fixture/design/tokens.json`
- `fixture/src/page.html` (source code)
- Reference to `fixture/evidence/contact-sheet.png`

The reviewer arm responds in the reviewer-design station output shape:
```json
{
  "station": "reviewer-design",
  "verdict": "approved" | "rejected",
  "findings": [
    {
      "element": "contract element id or description",
      "property": "CSS property",
      "issue": "description of violation",
      "found_value": "measured value (optional)",
      "expected_value": "documented expectation (optional)"
    }
  ]
}
```

### Sealing Rule

The ground truth (`fixture/ground-truth.json`), the planted violation list (V1-V10), and the scorer check ids (K1-K12) are **never provided to any arm**. Arms receive only:
- Design system documentation
- Fixture page source or build brief
- Visual evidence (screenshot)

### Scoring Rubric for Reviewer Arm

Reviewer findings are scored against the ground truth as follows:

**Recall**: A planted violation counts as caught when at least one finding identifies:
- The same contract element (by id or unmistakable description)
- The same violated property

Recall is reported as: caught violations / 10 total violations

**Precision per caught finding**:
- **Measured**: Finding states both the found value and the documented expectation (both numbers, or both hex codes)
- **Partial**: Finding identifies element, property, and rule but states at most one of the two values
- **Vague**: Finding names neither a checkable value nor the specific element

**False positive**: A finding asserting a violation that is:
- Not in the ground truth, AND
- Not verifiable in the fixture source on inspection

**Unplanted true finding**: A finding asserting a violation that is:
- Not in the ground truth, BUT
- Verifiably real in the fixture source on inspection
- Reported separately (neither a catch nor a false positive)

## Running the Builder Arm

### Packet Contents

The builder arm receives:
- `fixture/design/DESIGN.md`
- A build brief describing the product page to create

The builder arm produces:
- One self-contained HTML file implementing the design system

### Scoring

Builder output is scored by `tools/scorer.py` only. No human judgment adjusts the score.

Run the scorer:
```bash
python3 tools/scorer.py path/to/output.html
```

The scorer evaluates 12 checks:
- K1-K10: Map to the 10 planted violations in the fixture
- K11-K12: Control checks (should always pass on compliant output)

Output format:
```json
{
  "passed": 12,
  "total": 12,
  "checks": [
    {
      "check_id": "K1",
      "passed": true,
      "measured": "measured value",
      "expectation": "documented expectation"
    }
  ]
}
```

## Evidence Capture

To generate screenshot evidence, use `tools/capture.py`:

```bash
python3 tools/capture.py fixture/src/page.html fixture/evidence/contact-sheet.png
```

### Fixed Capture Settings

For reproducibility, captures use these fixed settings:
- Browser: Chromium (Playwright)
- Viewport width: 1280px
- Device scale factor: 1
- Reduced motion: emulated (`prefers-reduced-motion: reduce`)
- Capture type: Full page

These settings are hard-coded in `tools/capture.py` and produce byte-identical output up to renderer version differences.

## Ground Truth Violations

The fixture contains exactly 10 planted violations (sealed, not provided to arms):

1. V1: hero-title font-size below minimum and off type scale
2. V2: body-text font-size below minimum and off type scale
3. V3: section padding-top violates spacing rhythm
4. V4: hero-sub color not from palette
5. V5: link-inline uses coral (reserved for price-badge)
6. V6: missing :focus-visible rule
7. V7: card border-radius not from radius tokens
8. V8: body-text line-height incorrect
9. V9: caption color has insufficient contrast
10. V10: heading-2 font-family does not start with Space Grotesk

Each violation maps to a scorer check K1-K10. The scorer also includes control checks K11 (page background) and K12 (cta-primary background).

## Reproducibility

This benchmark can be reproduced from the repository alone:
1. Clone the repository
2. Install Playwright: `pip install playwright && playwright install chromium`
3. Run scorer against fixture: `python3 tools/scorer.py fixture/src/page.html`
4. Expected result: 2 passed (K11, K12), 10 failed (K1-K10)
5. Run captures as needed: `python3 tools/capture.py <input.html> <output.png>`
6. Execute arms with packets documented above
7. Score reviewer findings against ground truth using the rubric
8. Score builder output using scorer.py

## Test Suite

The benchmark includes automated tests in `tests/test_model_benchmark.py`:
- S1: Fixture carries exactly the planted violations
- S2: Scorer convicts fixture and acquits compliant page
- S3: Tokens agree across design files

Run tests:
```bash
python3 -m unittest tests.test_model_benchmark
```
