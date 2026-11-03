# Task packet: builder

## Station prompt

# Builder

## Role
Implement the spec so the scenario tests pass.

## Inputs
- spec
- tests

## Outputs
- code change

## Rules
- Work only from the inputs listed above and the work order in the packet.
- Produce the output as a file in the repo, not as chat text.
- If the inputs are not enough, say what is missing instead of guessing.
- Never approve your own work. Approval belongs to a different station.
- Keep the change small and mapped to a spec scenario where one applies.


## Work order

- id: wo-gh-7
- kind: feature
- title: Intake outcomes: reject, rescope, needs-info parking, risk and surfaces
- source: github-issue
- description: Implement the spec in .openspec/specs/intake-outcomes/spec.md in the factory.

Build, per the spec scenarios:

S1: intake can REJECT a work order whose purpose is harmful, deceptive or unlawful, with reasons recorded on the work order; rejection is terminal, the runner spawns no further station, the work order status becomes rejected, and the report and swimlane show the rejection and its reasons.

S2: intake can RESCOPE an oversized or vague work order: the description becomes the buildable scope, the outcome record states what was cut and why, and downstream packets carry the rescoped description.

S3: intake can answer NEEDS-INFO: outcome waiting_info, questions recorded, work order status waiting_info, nothing further spawns, and the report records a waiting state rather than a pass or a failure. When answers are recorded and the work order returns to a runnable status, a later run proceeds from intake again.

S4: accepted and rescoped work orders carry intake's risk rating (low, medium, high) and surfaces list from the spec's vocabulary; both appear in the run report.

S5: rejected and waiting runs render honestly: no station beyond intake listed as executed, reasons and questions shown, neither rendered as approved.

The work order model gains the intake outcome record (outcome, reasons, questions, rescoped description, risk, surfaces). Intake's station prompt and contract describe all four outcomes, the refusal class, the rescope discipline and the risk and surface vocabulary. Tests covering S1 to S5 in the factory suite style, docs updated, CHANGELOG Unreleased updated. Keep the whole suite green and every pipeline valid.

GitHub issue: https://github.com/arananet/anvil-factory/issues/7
- risk_hints: 
- status: new

## Upstream steps

- intake: completed
- spec-writer: executed
- test-writer: executed

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

