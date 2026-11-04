# Task packet: reviewer-design

## Station prompt

# Reviewer Design

## Role
Judge interface output against the project's own design system: its design tokens, component and layout rules, motion rules, and quality bars.

## Inputs
- design system (tokens, rules, quality bars from design/DESIGN.md and design/tokens.json)
- interface output (HTML, React components, CSS, user-facing pages, or other interface artifacts)

## Outputs
- review (JSON format with verdict and findings)

## Rules
- Work only from the inputs listed above and the work order in the packet.
- If the project has no design system (no design/DESIGN.md), your verdict MUST be `changes_requested` with a finding stating that no design system exists for the project.
- If the project has a design system, review the interface output against:
  - Design tokens: Are the correct colors, typography, spacing values being used?
  - Component and layout rules: Do components follow the documented patterns?
  - Motion rules: Does any animation or transition follow the motion guidelines?
  - Quality bars: Does the interface meet the stated quality bars for visual hierarchy, scale contrast, spacing rhythm, and responsive behavior?
- **Authority**: The project's own design system (design/DESIGN.md, design/tokens.json) is the authority for this project. The Design knowledge section in your packet (when present) is reference material that the design system may draw from. On any conflict between the project's design system and the knowledge base, the project's design system wins. A deviation from the knowledge base alone is never a finding; a deviation from the project's design system is.
- Focus on the design system the project has defined. Do not impose external design opinions or preferences that are not documented in the project's design system.
- A design token marked as "TODO" or placeholder means the project hasn't defined that value yet. Flag missing values as findings only if the interface output actually uses undefined tokens.
- Findings should be specific and actionable: cite which quality bar was violated, which token was used incorrectly, or which rule was not followed. When referencing the Design knowledge base in a finding or suggestion, name the specific knowledge entry (e.g., "metrics-blue palette", "data-dense style", "accessibility guideline for contrast").
- Your verdict must be one of: `pass`, `fail`, or `changes_requested`.
- Produce the output as a JSON object, not as chat text.

## Output Format

Return a JSON object with this structure:

{
  "station": "reviewer-design",
  "verdict": "pass | fail | changes_requested",
  "findings": [
    "Specific finding with reference to design system rule or quality bar",
    "Another finding if applicable"
  ]
}

The station field must equal "reviewer-design", the verdict must be one of pass, fail, or changes_requested, and findings must be a list of strings.

## Examples

Example 1: No design system exists
- verdict: changes_requested
- finding: "No design system exists for this project. The project must define design/DESIGN.md and design/tokens.json before interface output can be reviewed against design standards."

Example 2: Interface violates quality bar
- verdict: changes_requested
- findings:
  * "Quality bar violation: Scale Contrast - The button text has only 2.8:1 contrast ratio against its background, failing the minimum 4.5:1 requirement stated in the quality bars."
  * "Token usage: The page uses hardcoded color '#FF5733' instead of the defined primary color token."

Example 3: Interface meets design system
- verdict: pass
- findings: (empty list)


## Work order

- id: wo-gh-11
- kind: feature
- title: Design knowledge base for the design stations
- source: github-issue
- description: Implement the spec in .openspec/specs/design-knowledge/spec.md in the factory. The spec defines the UX module's base layer and its guide designation.

Build, per the spec scenarios:

S1: the built in starter knowledge dataset, original content authored for ANVIL in the factory's voice, as data files under design-knowledge/ (styles.json, palettes.json organized by product type, fonts.json, guidelines.json, product-types.json), with a loader that validates required fields per entry and fails naming the file and entry on a malformed entry.

S2: deterministic slice matching: the project's declared product type selects the product type note plus the styles, palettes and pairings it references and the general guidelines; same inputs, same slice.

S3: packet injection of a Design knowledge section (slice plus authority statement) for reviewer-design, for the builder on a UI surface, and for the design authoring path (a station whose work order targets design/DESIGN.md); other stations' packets unchanged; the slice is computed once per run.

S4: authority stated in the injected section and in reviewer-design's contract: the project's design system wins on conflict, and a deviation from the knowledge base alone is never a finding.

S5: an undeclared or unknown product type selects the general guidelines only and the packet records that no product type slice matched.

S6: citation discipline in the station contracts: a Design knowledge sources note in DESIGN.md citing entries by data kind and entry name (pack supplied entries cited as operator supplied pack entries), and reviewer-design names the knowledge entry behind any suggestion.

S7 and S8: operator supplied knowledge packs at runtime. A work order may name a pack by a filesystem path (knowledge_pack field): a directory outside any repository tree holding manifest.json (pack name, format version, product types covered, data files) plus data files in the same five kinds. The runner loads and validates the pack at run start, prefers pack entries for the product types the pack covers, falls back to the built in dataset otherwise, and records the pack in the run report as an operator supplied input (name, manifest product types, file list). The runner never writes pack files into the project or factory tree, and a factory test proves a pack handed in with a work order reaches the design packets while the repository tree after the run contains no pack file and no committed file contains pack content.

S9: a pack path that does not resolve or a manifest that fails validation stops the run at intake with the failure recorded and no station spawned.

S10: the guide designation recorded in the catalog: the design stations that apply the base (design authoring stations, the builder's UI surface role, reviewer-design) carry the guided design station designation in their catalog entries, naming the design model from the recorded routing policy (openai/gpt-6-astra) as their designated model.

Tests covering S1 to S10 in the factory suite style, docs updated (a docs page describing the UX module: the knowledge base layer, packs, the authority rule, and the guided stations), CHANGELOG Unreleased updated. Keep the whole suite green and every pipeline valid.

GitHub issue: https://github.com/arananet/anvil-factory/issues/11

Operator standing note for every round of this order: the builder must not create or modify anything under .github/workflows/ (the Actions token cannot push workflow changes; a run that touches them loses its commit-back). Tooling the run needs is staged by the operator in the workflow before the line step. Test changes are written by the test-writer station; the builder must not modify tests/, anvil.json or pipelines/. Tests must be real: every test calls the implementation it names and asserts behavior, never the mere existence of data structures.

GATE LOOPBACK 1 (after run 41768971456, verdict changes_requested, reviews counted 5 of 5; reviewer-architecture is the only requesting reviewer). The knowledge data layer and rendering exist; the runtime wiring does not. Fix exactly these counted findings:

1. Wire S3 into packet building: the runner's packet construction must include the Design knowledge section (slice plus authority statement) for reviewer-design, for the builder on a UI surface, and for the design authoring path, by calling the knowledge module (packet_knowledge_section or its successor) from the packet pipeline (anvil/runner.py packet_step and anvil/design.py as appropriate). Other stations' packets stay unchanged, and the slice is computed once per run (S2).

2. Wire the runtime pack flow (S7, S8, S9): at run start the runner reads the work order's knowledge_pack field when present, loads and validates the pack, prefers pack entries for the product types the pack covers, falls back to the built in dataset otherwise, and records the pack in the run report as an operator supplied input (name and manifest product types at minimum).

3. S10 guide designation: the station catalogs must stop hardcoding a design model string. The guide designation reads the design model from the recorded routing policy (anvil/routing.py) at the point of use, whatever model the policy currently records; no model name is duplicated across station.json files.

4. Defense in depth on pack loading (approver note): the pack loader rejects paths that resolve into sensitive system locations (for example /etc, /sys, /proc) with a named error at load, covered by a test. The existing whitelist based filename validation stays.

Real tests for the wiring, written by the test-writer station: a run level test proving a design station packet contains the knowledge section and a non design packet does not; a pack loading test proving preference, fallback and report recording; a sensitive path rejection test. The builder must not modify tests/, anvil.json, pipelines/ or .github/workflows/. Keep the whole suite green and every pipeline valid. Update CHANGELOG Unreleased.
- risk_hints: 
- status: new

## Upstream steps

- intake: executed
- spec-writer: executed
- test-writer: executed
- builder: executed
- checks-gate: passed
- reviewer-spec: executed
- reviewer-security: executed
- reviewer-tests: executed
- reviewer-architecture: executed

## Project design

### Design tokens

```json
{
  "colors": {
    "primary": "TODO",
    "secondary": "TODO",
    "accent": "TODO",
    "background": "TODO",
    "surface": "TODO",
    "text": "TODO",
    "text-secondary": "TODO",
    "error": "TODO",
    "warning": "TODO",
    "success": "TODO",
    "info": "TODO"
  },
  "typography": {
    "font-family-base": "TODO",
    "font-family-heading": "TODO",
    "font-family-mono": "TODO",
    "font-size-base": "TODO",
    "font-size-scale": "TODO",
    "line-height-base": "TODO",
    "line-height-heading": "TODO"
  },
  "spacing": {
    "unit": "TODO",
    "scale": [
      "TODO"
    ]
  },
  "layout": {
    "max-width": "TODO",
    "breakpoint-mobile": "TODO",
    "breakpoint-tablet": "TODO",
    "breakpoint-desktop": "TODO"
  },
  "motion": {
    "duration-fast": "TODO",
    "duration-base": "TODO",
    "duration-slow": "TODO",
    "easing-standard": "TODO",
    "easing-enter": "TODO",
    "easing-exit": "TODO"
  }
}
```

### Quality bars

for Product Pages

These bars apply to every product page or interface this project ships.

### Visual Hierarchy
- [ ] Clear content hierarchy with size, weight, and spacing
- [ ] Important actions are visually prominent
- [ ] Related elements are grouped

### Scale Contrast
- [ ] Minimum 4.5:1 contrast ratio for normal text
- [ ] Minimum 3:1 contrast ratio for large text (18pt+)
- [ ] Interactive elements have sufficient contrast

### Spacing Rhythm
- [ ] Consistent spacing scale used throughout
- [ ] Whitespace creates clear content boundaries
- [ ] Spacing adapts appropriately to different screen sizes

### Responsive Behavior
- [ ] Layout works on mobile, tablet, and desktop
- [ ] Touch targets are at least 44x44px on mobile
- [ ] Text is readable without zooming on any device
- [ ] No horizontal scrolling on standard viewports


## Rendered evidence

**Note:** Rendered evidence could not be captured for this run. Reason: capture failed for 390x844: Playwright not installed. Install with: pip install playwright && playwright install chromium. This review judged source only.


## Output contract

Your complete answer is exactly one review JSON object written to runs/wo-gh-11/reviewer-design.review.json. The free output transcript stays as provenance and is never parsed for a review.
