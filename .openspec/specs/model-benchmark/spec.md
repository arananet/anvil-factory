# Model Benchmark: Design Station Models

Status: approved
Slug: model-benchmark

## Roles
- implementer: builds the benchmark harness described here
- reviewer: checks the harness against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
The factory routing that sends UI and design stations to gpt-6-astra was a judgment call made on 2026-10-28 and was never tested against the alternatives. In the audited gateway window of 2026-10-28 to 2026-11-03 the Astra route cost 70.14 USD of 119.80 USD total, while claude-opus-5-5 never ran a full design order and gpt-6.1-sol never ran at all. This spec defines a benchmark harness that produces scored, comparable evidence for the three candidate design station models: openai/gpt-6-astra, anthropic/claude-opus-5.5 and openai/gpt-6.1-sol. The harness measures; it does not change the routing policy. The policy decision stays with the product owner after he sees the results.

## Requirements

### Layout
- Everything the harness owns lives under benchmarks/model-benchmark/ in this repository: fixture/design/DESIGN.md, fixture/design/tokens.json, fixture/src/page.html, fixture/ground-truth.json, fixture/evidence/ (generated captures), tools/capture.py, tools/scorer.py and RUNNER.md.
- Tests live in the factory suite as tests/test_model_benchmark.py, written in the existing suite style (unittest, tempfile fixtures where needed, scenario tagged docstrings).

### The fixture design system
- fixture/design/DESIGN.md documents a concrete design system for a fictional product, the Meridian Patch, with exactly these tokens, and fixture/design/tokens.json carries the same values in machine readable form:
  - Colors: paper #FAFAF6 (page background), ink #14201B (headings and primary text), pine #53685C (secondary text and captions), teal #0E7C66 (primary action background), coral #FF6B4A (reserved: the price badge only), line #E3E6DF (borders and dividers).
  - Type scale in px: 12, 14, 16, 20, 24, 32, 40, 56, 64. The hero title is at least 56. Body text is at least 16.
  - Spacing: every margin and padding value is a multiple of 8; 0 is allowed.
  - Radius tokens in px: 4, 8, 12, 16, 999.
  - Line heights: headings 1.2, body text 1.5, unitless and exact.
  - Fonts: the first family of every heading stack is "Space Grotesk"; the first family of the body stack is "Inter".
  - Focus: links and buttons show a :focus-visible outline of 2px solid teal with a 2px offset.
  - Contrast: text on paper is at least 4.5 to 1 by the WCAG relative luminance formula.
  - Motion: transitions are permitted only with a prefers-reduced-motion block that disables them.
- DESIGN.md states these as rules a reviewer can cite, in the same shape as the project design systems the factory already writes (rules and quality bars, not only value lists).

### The fixture page and the planted violations
- fixture/src/page.html is one self contained HTML file (one style block in the head, no external resources) implementing a small product page for the Meridian Patch with exactly these contract elements, each carrying the given id: page (the body wrapper), hero-title, hero-sub, cta-primary, price-badge, section, heading-2, body-text, caption, link-inline, card.
- The page violates DESIGN.md in exactly 10 planted violations and is otherwise fully compliant with every documented rule, including the motion rule (it carries a compliant prefers-reduced-motion block disabling its one transition) and every token it uses outside the planted values:
  - V1: hero-title font-size is 48px (below the documented hero minimum of 56 and off the type scale).
  - V2: body-text font-size is 15px (below the documented body minimum of 16 and off the type scale).
  - V3: section padding-top is 30px (off the 8px spacing rhythm; every other margin and padding on the contract elements is a multiple of 8).
  - V4: hero-sub color is #5C6F66 (not a palette hex; the compliant value is pine #53685C).
  - V5: link-inline color is coral #FF6B4A (coral is reserved for the price badge; price-badge itself uses coral correctly).
  - V6: the stylesheet contains no :focus-visible rule (the documented focus rule is absent entirely).
  - V7: card border-radius is 10px (not a radius token).
  - V8: body-text line-height is 1.33 (not the documented body line height of 1.5).
  - V9: caption color is line #E3E6DF on paper #FAFAF6 (contrast about 1.3 to 1, failing the documented 4.5 to 1 minimum; the compliant caption color is pine).
  - V10: heading-2 font-family first family is "Arial" (the documented heading stack starts with "Space Grotesk").
- fixture/ground-truth.json is the sealed record of the 10 violations: one entry per violation with its id (V1 to V10), the scorer check it maps to (K1 to K10), the contract element, the property, the planted value, the documented expectation, and a one line description a scorer can match a review finding against. Ground truth is benchmark data for the operator; no arm ever receives it (see the sealing scenario).

### The deterministic scorer
- tools/scorer.py is Python standard library only. It reads one candidate HTML file in the fixture contract shape (contract ids present, styles authored in the style block via id selectors or inline on the element) and evaluates exactly 12 checks, printing a JSON object with the number of checks passed, the total, and per check detail (check id, pass or fail, the measured value found, the expectation).
  - K1: hero-title font-size is on the type scale and at least 56 (maps V1).
  - K2: body-text font-size is on the type scale and at least 16 (maps V2).
  - K3: every margin and padding authored for section, card, hero-title, body-text and cta-primary is a multiple of 8 (maps V3).
  - K4: every color authored for the contract elements (color, background-color, border-color) is one of the six palette hexes, compared case insensitively (maps V4).
  - K5: coral #FF6B4A appears only on price-badge among the contract elements (maps V5).
  - K6: the stylesheet contains a :focus-visible rule that sets an outline (maps V6).
  - K7: every border-radius authored for the contract elements is one of the radius tokens (maps V7).
  - K8: hero-title line-height is 1.2 and body-text line-height is 1.5 (maps V8).
  - K9: the contrast ratio between caption color and the page background is at least 4.5 to 1 (maps V9).
  - K10: the first font family of heading-2 is "Space Grotesk" and the first font family of body-text is "Inter" (maps V10).
  - K11 (control): the page background is paper #FAFAF6.
  - K12 (control): the cta-primary background is teal #0E7C66.
- A missing contract element or a missing property is a failed check whose detail says missing. The scorer never guesses a value it cannot read.
- The scorer run against fixture/src/page.html fails exactly K1 to K10 and passes K11 and K12. Run against a fully compliant page in the same contract shape it passes all 12.

### The capture tool
- tools/capture.py renders one HTML file with Playwright Chromium at a viewport width of 1280, device scale factor 1, reduced motion emulated, and writes exactly one evidence image: a full page capture. For the fixture page the committed output is fixture/evidence/contact-sheet.png. The same files are used for every benchmark arm; the reviewer arm never receives captures produced per model.
- Capture settings are fixed in the script and restated in RUNNER.md so the evidence is reproducible byte for byte up to renderer version noise.

### The runner notes and the scoring rubric
- RUNNER.md documents how the operator runs the arms: the exact packet contents per arm, the sealing rule, and the scoring rubric below, so a second operator could reproduce the benchmark from the repository alone.
- Reviewer arm scoring rubric, fixed here before any arm runs. The reviewer arm receives DESIGN.md, tokens.json, the fixture page source and the one contact sheet, and answers in the reviewer-design station output shape (a JSON object with station, verdict and findings). Scoring against the ground truth:
  - Recall: a planted violation counts as caught when at least one finding identifies the same contract element (by id or unmistakable description) and the same violated property. Recall is reported as caught out of 10.
  - Precision per caught finding: "measured" when the finding states both the found value and the documented expectation (both numbers, or the offending hex and the documented hex); "partial" when it identifies the element, the property and the rule but states at most one of the two values; "vague" when it names neither a checkable value nor the specific element.
  - False positive: a finding asserting a violation that is neither in the ground truth nor verifiable in the fixture source on inspection.
  - Unplanted true finding: a finding asserting a violation that is not in the ground truth but is verifiably real in the fixture source on inspection. Reported separately; it is neither a catch nor a false positive.
- Builder arm scoring: the produced page is scored by tools/scorer.py only. No human adjusts the number.

### Boundaries
- This order changes no routing configuration, no station prompt, no pipeline and no policy file. It adds the benchmark directory, its tests, this spec and its work order.
- Runtime code for the scorer stays on the Python standard library. capture.py may depend on Playwright, which the run workflow installs; no test may require Playwright or a browser.
- No produced or modified file contains an em dash or an en dash.
- The factory suite stays green.

## Scenarios

### Scenario: The fixture carries exactly the planted violations
- S1: Given fixture/ground-truth.json, when it is read, then it contains exactly 10 entries, V1 to V10, each naming a scorer check K1 to K10, a contract element, a property, the planted value and the documented expectation; and given fixture/src/page.html, when its authored styles are inspected, then each planted value is present exactly as the ground truth states.

### Scenario: The scorer convicts the fixture and acquits a compliant page
- S2: Given tools/scorer.py, when it runs against fixture/src/page.html, then it reports exactly K1 to K10 failed and K11 and K12 passed; and when it runs against a compliant page in the same contract shape (carried in the tests), then it reports 12 of 12 passed.

### Scenario: Tokens agree across the design system files
- S3: Given fixture/design/DESIGN.md and fixture/design/tokens.json, when the tests compare them, then every color hex, type scale value, radius token and line height in tokens.json matches the value DESIGN.md documents, with no extra or missing token.

### Scenario: The evidence is one deterministic capture set
- S4: Given tools/capture.py, when it renders fixture/src/page.html with the settings fixed in the script, then fixture/evidence/contact-sheet.png exists, is a PNG, and is the single evidence image the reviewer arm receives; the capture settings are restated in RUNNER.md.

### Scenario: The ground truth stays sealed from the arms
- S5: Given the arm packets described in RUNNER.md, when they are inspected, then neither packet contains the ground truth, the planted violation list, or the scorer check ids; the reviewer packet contains DESIGN.md, tokens.json, the fixture page source and the contact sheet reference only, and the builder packet contains the build brief and DESIGN.md only.

### Scenario: The rubric predates the arms
- S6: Given this spec, when the benchmark results are later read against it, then the recall, precision and false positive definitions used are the ones written in the Requirements section above, unchanged after any arm has run.

### Scenario: The factory suite stays green and the boundary holds
- S7: Given the change is complete, when the full factory test suite runs, then it passes; and when the diff is inspected, then it touches only benchmarks/model-benchmark/, tests/test_model_benchmark.py, this spec and the work order, with no change to routing, station prompts, pipelines or policy files.
