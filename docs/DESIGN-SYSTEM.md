# Project design systems

A run can pass every gate ANVIL has and still ship a page that looks basic,
because no station owns design and no project artifact says what good looks
like for that project. The Sentia launch page proved it: correct, live, and
visually plain, because the factory had no design surface at all.

Every project now has a design system of its own: a scaffold the factory
creates, an identity the project supplies, tokens and quality bars that
travel into station packets, and a reviewer whose whole job is judging
interface output against that system.

## The layout

- `design/DESIGN.md` is the human-readable design system: brand identity
  inputs (palette, typography, voice), art direction anchors (the reference
  class the project names for itself), component and layout rules, motion
  rules, and quality bars for product pages.

- `design/tokens.json` holds machine-readable design token values. Tokens
  are JSON rather than CSS because ANVIL projects are not all web projects:
  JSON is target agnostic, a packet can carry the exact values, and a web
  project can generate its CSS variables from the same file.

Scaffolding (`anvil init`, `anvil new-project`, `anvil onboard`) creates
both files when absent and never overwrites existing files, matching the
onboarding discipline for brain files.

## The scaffold: structure, not style

The scaffold ships with sections and placeholder values. It asks questions
the project must answer but prescribes no colors, fonts, or factory house
style. Every project defines its own look.

`design/DESIGN.md` sections:
- Brand identity: palette, typography, voice
- Art direction: reference class and visual quality bar
- Tokens: pointer to tokens.json
- Component and layout rules
- Motion rules
- Quality bars: hierarchy, scale contrast, spacing rhythm, responsive behavior

`design/tokens.json` structure:
- colors (primary, secondary, accent, text, backgrounds, status colors)
- typography (families, sizes, scale, line heights)
- spacing (unit, scale)
- layout (max-width, breakpoints)
- motion (durations, easing)

## Packet injection

When a project has `design/DESIGN.md`, runs add a Project design section to
the packets of stations that produce or judge interface output:

- builder
- writer
- media-producer
- brief-writer
- reviewer-design

The section carries the token values from `tokens.json` and the quality bars
from `DESIGN.md`. It is computed once per run from the project on disk, the
same injection mechanism verified learnings use for the brain.

Stations outside that set receive packets unchanged.

## The reviewer

`reviewer-design` is a station (agent kind) whose contract is to judge
interface output against the project's own design system: its tokens,
component and layout rules, motion rules, and quality bars.

It joins the parallel reviewer group of:
- sdlc-default (software development pipeline)
- content-default (full content pipeline)
- content-short (short content pipeline)

These pipelines produce interface output, so design review applies.

## Missing design system: warnings, not silent passes

A run whose pipeline includes interface producing stations, in a project
with no `design/DESIGN.md`, records the gap as a warning in the run report.

When `reviewer-design` runs in a project with no design system, the review
carries verdict `changes_requested` and a finding stating that no design
system exists. The approver sees the missing precondition as a named finding
rather than an unearned pass.

## Why per-project, not factory-wide

A design system that belongs to the factory would make every project look
like the factory. Each project sets its own identity:

- The factory ships the structure (sections, token names, quality bar
  categories)
- The project supplies the values (its palette, its typography, its motion
  preferences)

The factory dogfoods its own scaffolding: the factory repo itself has
`design/DESIGN.md` and `design/tokens.json`, created the same way every
other project gets them.
