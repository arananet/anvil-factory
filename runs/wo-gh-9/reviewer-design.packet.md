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
- Focus on the design system the project has defined. Do not impose external design opinions or preferences that are not documented in the project's design system.
- A design token marked as "TODO" or placeholder means the project hasn't defined that value yet. Flag missing values as findings only if the interface output actually uses undefined tokens.
- Findings should be specific and actionable: cite which quality bar was violated, which token was used incorrectly, or which rule was not followed.
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

- id: wo-gh-9
- kind: feature
- title: Rendered design review: reviewer-design judges screenshots of the built page
- source: github-issue
- description: Implement the spec in .openspec/specs/rendered-design-review/spec.md in the factory.

Build, per the spec scenarios:

S1: a project can declare a servable web page in its configuration (serve command or static root, page path, breakpoints; defaults 390x844 and 1440x900). After the builder and before reviewer-design's packet is built, the runner serves the project locally, captures one PNG per breakpoint into the run's evidence directory named by dimensions, and the run report lists the captures as evidence.

S2: reviewer-design's packet gains a Rendered evidence section when captures exist, naming the screenshots and instructing that layout, scale and spacing findings cite the rendered evidence. With no captures configured, no section and the report records that no rendered evidence was configured.

S3: when serving or capture is attempted and fails, the run completes, reviewer-design's recorded review states that rendered evidence could not be captured, gives the reason, and says it judged source only; the report claims no screenshot evidence.

S4: demonstrate the capability on the factory's own status page (the servable static page this repo already ships): declare it servable in the factory project config, and hold a demonstration run whose evidence directory contains the breakpoint screenshots referenced from its report. The executed-run workflow wiring pattern gains the matching serve plus headless capture step so executed runs produce the same evidence.

Keep capture out of the unit suite's critical path: unit tests cover the packet section, the evidence listing and the failure record with the capture tool behind an injectable seam, in the factory suite style. Docs updated, CHANGELOG Unreleased updated. Keep the whole suite green and every pipeline valid.

GitHub issue: https://github.com/arananet/anvil-factory/issues/9

GATE LOOPBACK 1 (after run 41741068693's successor run 41747657375, verdict rejected, reviews counted 5 of 5). Round 1 state, read from the run artifact (the run's commit-back was rejected, so round 1's implementation tree was lost with the run workspace and this round rebuilds it): reviewer-security returned fail, reviewer-spec changes_requested, reviewer-tests, reviewer-architecture and reviewer-design pass. Rebuild the full item (capture module, configuration, design packet evidence section, runner integration, anvil.yaml servable configuration, docs, CHANGELOG, tests) with the findings below as design constraints from the start.

Why the commit-back failed, and the standing rule it creates: round 1's builder modified .github/workflows/anvil-execute-rendered-design-review.yml, and the Actions token cannot push workflow changes (remote rejected: refusing to allow a GitHub App to create or update workflow without workflows permission). The builder must not create or modify anything under .github/workflows/ in this or any later round. The operator has preinstalled Playwright and Chromium in the workflow before the line step; any status page generation the demonstration needs happens in factory code or the capture module, never in workflow steps.

Security findings from reviewer-security (fail), all in the new anvil/capture.py, verbatim in substance:
1. CRITICAL, command injection: the serve_command from anvil.yaml is executed with shell=True via subprocess.Popen without validation. Fix: shell=False, split the command with shlex.split, or use an allowlist of permitted serve commands.
2. CRITICAL, path traversal: the static_root configuration value is used directly in Path(project_dir) / static_root without validation, so a value like ../../../etc escapes the project. Fix: resolve the path and require it to stay within project_dir.
3. HIGH, URL path injection: page_path from configuration is concatenated to base_url without validation. Fix: require page_path to start with '/' and contain no '..' sequences.
4. MEDIUM, hardcoded port: the static server port 8765 is hardcoded and can collide. Fix: dynamic port allocation or configurable port with fallback.
5. MEDIUM, unvalidated breakpoint dimensions: width and height from configuration are used unchecked; extreme values can exhaust memory. Fix: validate bounds (width 1 to 7680, height 1 to 4320).
6. MEDIUM, subprocess cleanup: terminate then kill leaves spawned children behind. Fix: terminate the process group (os.killpg) so children are cleaned up.
7. LOW, evidence directory permissions: create the evidence directory with owner-only permissions (0o700).

Spec finding (reviewer-spec, echoed by reviewer-tests): S4's demonstration must exist from this run, not be deferred. The run's evidence directory runs/wo-gh-9/evidence/ must contain the breakpoint screenshots of the served factory status page, referenced from the run report, produced by the capture step inside the line using the preinstalled Playwright and Chromium.

Discipline: test changes are written by the test-writer station; the builder must not modify tests/, anvil.json, pipelines/ or .github/workflows/. Keep the whole suite green and every pipeline valid. Update CHANGELOG Unreleased.
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


## Output contract

Your complete answer is exactly one review JSON object written to runs/wo-gh-9/reviewer-design.review.json. The free output transcript stays as provenance and is never parsed for a review.
