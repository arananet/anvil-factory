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

For visual runs (when Quality Charter is present in your packet), return a JSON object with dual-section structure:

{
  "station": "reviewer-design",
  "verdict": "pass | fail | changes_requested",
  "compliance": {
    "verdict": "pass | fail | changes_requested",
    "findings": [
      "Design system compliance findings (tokens, rules, component patterns)"
    ]
  },
  "quality": {
    "verdict": "pass | fail | changes_requested",
    "findings": [
      "Quality findings comparing output against reference anchors and charter criteria"
    ],
    "anchor": "path/to/anchor/file or 'charter floor only' when no anchors"
  }
}

For non-visual runs (no Quality Charter in packet), return the simple structure:

{
  "station": "reviewer-design",
  "verdict": "pass | fail | changes_requested",
  "findings": [
    "Specific finding with reference to design system rule or quality bar"
  ]
}

### Dual-Section Review (Visual Runs)

For visual runs:

1. **Compliance section**: Judge design system adherence - tokens, component patterns, layout rules, motion guidelines.

2. **Quality section**: Judge visual quality by comparing the output against reference anchors and charter criteria. This is a separate judgment from compliance.
   - When reference anchors are present: Compare the output against the anchors. Name gap categories from the charter criteria (materials, light, scale, contact for physical products; stated criteria for games/illustrations).
   - When no anchors: Judge against charter floor alone.
   - Cite the anchor used in comparison or state "charter floor only" when no anchors available.

The overall verdict is the stricter of the two section verdicts. An output can pass compliance but fail quality, and such a case must be reported as changes_requested or fail at the overall level.

**Same-Subject Identity Consistency (S7)**: When the work order declares an `identity_reference` for runs producing multiple related visual outputs, the quality section may extend beyond individual anchor evaluation to include same-subject identity consistency verification across deliverable outputs. Your packet will specify this requirement when applicable. You must verify that all outputs maintain identical subject identity traits enumerated in the work order (examples for physical products: finish, detail colors, mounting or attachment, proportions and markings; stated equivalents apply for other product types). Divergence in these traits constitutes a quality failure even when each output individually meets anchor criteria. Such failures must name the specific output and trait in your findings, with ruling and evidence recorded in the quality section. This verification is part of quality section judgment, not a separate verdict.

### Quality Criteria by Product Type

When judging quality section findings, name specific criteria gaps:

**Physical products**: materials, light, contact, scale
**Games/Illustrations**: Apply the project's stated standard from the design system

The station field must equal "reviewer-design", and both the overall verdict and section verdicts must be one of pass, fail, or changes_requested.

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


<!-- source: design/DESIGN.md -->
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


## Spec

<!-- source: .openspec/specs/operator-requirements/spec.md -->
# Operator credential and permission requirements

## Problem

Operating this factory depends on two stored credentials: a fine-grained
GitHub personal access token and a Cloudflare credential, both held in the
Secure Vault and reached through connector entries. Which permission each
factory operation needs has so far been learned by trial and error and
recorded only in operator memory and chat. The failure modes are expensive:
a missing permission surfaces as a 403 deep inside a run (a report comment
that cannot post, a runs list that cannot be read), one wrong probe shape
produced a false diagnosis that a working credential was invalid, and one
settings detour confused a GitHub App client secret with a personal access
token. The owner ordered on 2026-11-04 that these requirements be
documented in the factory itself, so they are never forgotten or
re-derived.

## Requirements

R1. A new document at docs/OPERATOR-REQUIREMENTS.md records the operator
credential and permission requirements for GitHub, Cloudflare, and the
Secure Vault. Every fact in it is one verified in operation, and each
permission entry names the operation that proves it (the call that works
with the permission and the observed failure without it).

R2. The GitHub section covers the fine-grained PAT held in the Secure
Vault via the custom.github connector, permission by permission:
Contents read and write (file reads, pushes via the Git Database tooling,
branch and tree operations); Actions read and write (list workflow runs
and jobs, read run outcomes, dispatch and re-fire workflows; without it,
403 on the runs list and logs, and operators fall back to empty trigger
commits); Issues read and write (create issues and comment run reports;
without it, 403 on issue creation and on the workflow's report comment
step); Administration read and write (PATCH repository for the homepage
and PUT topics; without it, 403 on both, verified repeatedly); Secrets
write (PUT Actions secrets, used to load CF_AIG_TOKEN and provider keys
per repo), with the standing fact that Actions secrets are write-only: a
secret's value can never be read back or copied between repos, so each
repo needs its own load. The section also records that branch merges go
through the merges API, that the PAT cannot manage webhooks, labels, or
Pages enablement (403s on record), and the one hard limit with no API at
all: the repository social preview image can only be uploaded through the
web Settings UI, and no permission changes that.

R3. The GitHub section records the credential kind distinctions: a GitHub
App client secret is not a personal access token and authenticates
nothing by itself against the REST API (verified 401 against GitHub,
Cloudflare, and the gateway); the settings areas must not be confused
(Developer settings, GitHub Apps, Credentials is a different mechanism
from Personal access tokens, Fine-grained tokens). Permissions are
granted per repository in the token's Repository access list, under
Repository permissions; editing any other credential changes nothing for
the vault token.

R4. The Cloudflare section covers the credential held in the Secure Vault
via the custom.cloudflare connector: it is a user token carrying API
Tokens Edit; it can list and mint account tokens and read account
permission groups (415 visible), and it cannot list user tokens (403,
code 9109). AI Gateway (arananet-ai-gateway) authorization: the gateway
accepts account tokens; the verified working shape for the Anthropic
route sends the token as x-api-key AND as cf-aig-authorization Bearer,
which is what the factory workflows set via ANTHROPIC_API_KEY and
ANTHROPIC_CUSTOM_HEADERS; the placeholder shape (x-api-key set to a
literal placeholder) returns 401, AiGatewayError code 2009. Per-repo
gateway access is delivered as the GitHub Actions secret CF_AIG_TOKEN in
each repo that runs stations; a dedicated minted token per repo is the
standing pattern, revocable in the Cloudflare panel. Gateway settings on
record: authentication on, BYOK-only off, log collection on; inference
billed through Unified Billing with credit top-ups by the owner. Wrangler
and deploys authenticate with the vault credential fetched in process and
passed as an environment token.

R5. The document closes with placement and care: where each credential
lives (the Secure Vault connector entries), what breaks without each
permission, and the two never-again lessons. One: a credential is only
declared invalid after a probe in the exact shape its consumer uses; the
placeholder-shape probe already produced one false diagnosis. Two: check
for an existing reservation, ticket, or secret before asking the owner
for a value; the values the factory needs are already held or mintable
through the vault connectors.

R6. No credential value, token id, or secret appears in the document or
in any other file this order produces. Credentials are referenced by
name and purpose only. This is verified by a scan of the produced files
for credential-shaped strings, which must find nothing.

R7. The README Documentation table gains a row for the new document, and
CHANGELOG gains an Unreleased entry. Nothing else changes: no code, no
tests created or modified, no other docs edited. The full factory suite
stays green.

## Acceptance scenarios

S1. A reader who has never operated the factory can answer, from the
document alone, which GitHub permission a given API operation needs and
what failure to expect without it, for every operation listed in R2.

S2. A reader can state why a GitHub App client secret cannot be used as
the factory's GitHub credential, and where the PAT's permissions are
actually granted.

S3. A reader can state the exact gateway authorization shape the factory
workflows use, why the placeholder shape must not be used to judge a
credential, and how a new repo receives its gateway access.

S4. A scan of every file the run produces finds no credential value, no
token id, and no secret; the document refers to credentials by name and
purpose only.


## Diff summary

- CHANGELOG.md: +1, -0
- README.md: +1, -0

## File access allowlist

This packet may only embed content from:
- design/DESIGN.md
- design/tokens.json
- .openspec/specs/operator-requirements/spec.md
- CHANGELOG.md
- README.md

## Work order

- id: wo-gh-32
- kind: task
- title: Document the operator credential and permission requirements (GitHub, Cloudflare, vault)
- source: github-issue
- description: Implement the spec in .openspec/specs/operator-requirements/spec.md. Owner's order 2026-11-04: document in this repo the operator credential and permission requirements for running the factory (GitHub, Cloudflare, and the Secure Vault), so they are never forgotten or re-derived by trial and error. Documentation only.

Build, per the spec requirements:

1. Create docs/OPERATOR-REQUIREMENTS.md recording ONLY facts verified in operation, each permission entry stated with the operation that proves it (the call that works with the permission and the observed failure without it). Sections: GitHub, Cloudflare, and placement and care.

GitHub section (fine-grained PAT held in the Secure Vault via the custom.github connector): Contents read and write (file reads, pushes via the Git Database tooling, branch and tree operations). Actions read and write (list workflow runs and jobs, read run outcomes, dispatch and re-fire workflows; without it, 403 on the runs list and logs and operators fall back to empty trigger commits). Issues read and write (create issues and comment run reports; without it, 403 on issue creation and on the workflow's report comment step). Administration read and write (PATCH repository for the homepage and PUT topics; without it, 403 on both, verified repeatedly). Secrets write (PUT Actions secrets, used to load CF_AIG_TOKEN and provider keys per repo), with the standing fact that Actions secrets are write-only: a secret's value can never be read back or copied between repos, so each repo needs its own load. Branch merges go through the merges API. The PAT cannot manage webhooks, labels, or Pages enablement (403s on record). One hard limit with no API at all: the repository social preview image can only be uploaded through the web Settings UI, and no permission changes that.

Credential kind distinctions (same section): a GitHub App client secret is NOT a personal access token and authenticates nothing by itself against the REST API (verified 401 against GitHub, Cloudflare, and the gateway). Do not confuse Developer settings, GitHub Apps, Credentials with Personal access tokens, Fine-grained tokens; reference the distinction only, naming no app and no value. Permissions are granted per repository in the token's Repository access list, under Repository permissions; editing any other credential changes nothing for the vault token.

Cloudflare section (credential in the Secure Vault via the custom.cloudflare connector): the vault credential is a user token carrying API Tokens Edit; it can list and mint account tokens and read account permission groups (415 visible), and cannot list user tokens (403, code 9109). AI Gateway (arananet-ai-gateway) authorization: the gateway accepts account tokens; the verified working shape for the Anthropic route sends the token as x-api-key AND as cf-aig-authorization Bearer, which is what the factory workflows set via ANTHROPIC_API_KEY and ANTHROPIC_CUSTOM_HEADERS; the placeholder shape (x-api-key set to a literal placeholder) returns 401, AiGatewayError code 2009, and already produced one false diagnosis. Per-repo gateway access is delivered as the GitHub Actions secret CF_AIG_TOKEN in each repo that runs stations; a dedicated minted token per repo is the standing pattern, revocable in the Cloudflare panel. Gateway settings on record: authentication on, BYOK-only off, log collection on; inference billed through Unified Billing with credit top-ups by the owner. Wrangler and deploys authenticate with the vault credential fetched in process and passed as an environment token; values are never printed or committed.

Placement and care (closing section): where each credential lives (the Secure Vault connector entries), what breaks without each permission, and the two never-again lessons: probe a credential in the exact shape its consumer uses before declaring it invalid, and check for an existing reservation, ticket or secret before asking the owner for a value.

2. Add a row for docs/OPERATOR-REQUIREMENTS.md to the README Documentation table, in the table's existing style.

3. Add a CHANGELOG Unreleased entry.

HARD CONSTRAINT: no credential value, token id, or secret appears in the document or in any other file this order produces; credentials are referenced by name and purpose only (spec R6, scenario S4).

Guardrails: the builder may only create docs/OPERATOR-REQUIREMENTS.md and edit README.md (Documentation table row only) and CHANGELOG.md (Unreleased entry only). No code changes. Do not create, modify, or delete any file under tests/ (the checks gate protects base ref test files). The review parsing contract, the producer mechanism and the checks gate base ref behavior are frozen. Full suite green. No em dash or en dash characters in any produced file.

GitHub issue: https://github.com/arananet/anvil-factory/issues/32

OPERATOR CORRECTION (round 2). Round 1 never reached a station: intake validation rejected the staged work order with "Invalid surface values: ['docs']. Must be from ['api', 'content', 'data', 'deploy', 'payments', 'security', 'ui']", so the run produced no report. The surface is corrected to 'content' (this is documentation work). Nothing else in this order changes; the guardrails stand.
- risk_hints: 
- status: new

## Rendered evidence

This run captured screenshots of the served project at the following breakpoints:

- `screenshot-1440x900.png` at `runs/wo-gh-32/evidence/screenshot-1440x900.png`
- `screenshot-390x844.png` at `runs/wo-gh-32/evidence/screenshot-390x844.png`

**Design review instruction:** When judging layout, scale, spacing, or visual hierarchy findings, cite the rendered evidence screenshots where applicable. The screenshots show what the page actually looks like at each breakpoint, not just what the source implies.


## Design knowledge

**Authority**: The project's own design system (design/DESIGN.md, design/tokens.json) is the authority for this project. The knowledge base below is reference material that the design system may draw from. On any conflict, the project's design system wins. A deviation from the knowledge base alone is not a finding; a deviation from the project's design system is.

**Note**: No product type slice matched. General guidelines only.

### Product Type: Undeclared

No specific product type declared. Using general guidelines only.

### UX Guidelines

**Accessibility:**
- Maintain minimum 4.5:1 contrast ratio for normal text, 3:1 for large text (18pt+)
- Touch targets must be at least 44x44px on mobile devices

**Feedback:**
- Loading states should appear after 300ms delay to avoid flashing
- Provide immediate visual feedback for user actions

**Forms:**
- Form fields should have clear labels and validation feedback
- Error messages should explain what went wrong and how to fix it

**Hierarchy:**
- Establish clear visual hierarchy using size, weight, and color
- Important actions should be visually prominent and easy to locate

**Motion:**
- Keep animation durations between 200-400ms for most transitions
- Provide reduced motion alternatives for users with vestibular sensitivity

**Responsive:**
- Test layouts at mobile (320-768px), tablet (768-1024px), and desktop (1024px+) breakpoints
- Avoid horizontal scrolling on standard viewports

**Spacing:**
- Use consistent spacing scale throughout (e.g., 4px, 8px, 16px, 24px, 32px)
- Group related elements together with whitespace separating distinct sections


## Quality Charter

Product type: physical_product

Observable criteria:

- **Materials**: Surfaces read as the materials the product is actually made of
- **Light**: One coherent light story, with shadows and reflections that agree with it
- **Contact**: Objects meet skin, surfaces and each other the way physical things do
- **Scale**: The object's size reads true against its context and human anatomy


## Reference Anchors

⚠️ **WARNING**: This run has no reference anchors.

The review will proceed under the charter floor alone.

