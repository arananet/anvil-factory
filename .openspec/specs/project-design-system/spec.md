# Project Design System

Status: approved
Slug: project-design-system

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
A run can pass every gate ANVIL has and still ship a page that looks basic, because no station owns design and no project artifact says what good looks like for that project. The Sentia launch page proved it: correct, live, and visually plain, because the factory had no design surface at all. This spec gives every project a design system of its own: a scaffold the factory creates, an identity the project supplies, tokens and quality bars that travel into station packets, and a reviewer whose whole job is judging interface output against that system. The factory ships the structure and the questions. It never imposes a house style, because a design system that belongs to the factory would make every project look like the factory.

## Requirements
- The design system lives in the project at design/DESIGN.md (identity, anchors, rules and quality bars in human language) and design/tokens.json (the machine readable token values). Tokens are JSON rather than CSS because ANVIL projects are not all web projects: JSON is target agnostic, a packet can carry the exact values, and a web project can generate its CSS variables from the same file. One source, no parsing of prose to recover a hex value.
- Scaffolding creates both files only when absent, through the same entry points that create the brain layout: `anvil init`, `anvil new-project` and `anvil onboard`. An existing design/DESIGN.md or design/tokens.json is never overwritten, truncated or merged into, matching the onboarding discipline the factory already keeps for project files.
- The scaffold is a structure, not a look. DESIGN.md ships with sections, each carrying the questions the project must answer and empty or placeholder values: brand identity inputs (palette, typography, voice), art direction anchors (the reference class the project names for itself, for example the product pages it aspires to sit next to), tokens (pointing at tokens.json), component and layout rules, motion rules, and quality bars for product pages stated as checkable bars (hierarchy, scale contrast, spacing rhythm, responsive behavior). tokens.json ships with the token names and empty or placeholder values. Nothing in the scaffold prescribes a color, a font or a style.
- When a project has design/DESIGN.md, runs add a Project design section to the packets of the stations that produce or judge interface output: builder, writer, media-producer, brief-writer and reviewer-design. The section carries the token values from tokens.json and the quality bars from DESIGN.md, and it is computed once per run from the project on disk, the same injection mechanism the verified learnings use for the brain. Stations outside that set receive packets unchanged.
- reviewer-design is a station in the catalog (stations/reviewer-design/, agent kind) whose contract is to judge interface output against the project's own design system: its tokens, its component and layout rules, its motion rules and its quality bars. It answers with a review in the standard review format (station, verdict, findings), like every other reviewer.
- reviewer-design joins the parallel reviewer group of sdlc-default, content-default and content-short. These are the shipped pipelines that produce interface output: product and application pages on the software line, pages and media on the content lines, including the short content line so a shorter pipeline is not a design bypass. The reviewer set of every pipeline only grows: no existing reviewer is removed or renamed by this change, which keeps the change consistent with the supervisor constitution, where a proposal may never drop a reviewer the base pipeline has.
- A run whose pipeline includes any of the interface producing stations above, in a project with no design/DESIGN.md, records the gap instead of passing silently: the run report gains a top level "warnings" list containing a warning that names the missing design system and the path design/DESIGN.md.
- reviewer-design never passes vacuously. When it runs in a project with no design/DESIGN.md, the review recorded for it in that run carries verdict changes_requested and a finding that states plainly that no design system exists for the project, so the approver sees the missing precondition as a named finding rather than an unearned pass.

## Scenarios

### Scenario: Scaffolding creates the design system once and never overwrites it
- S1: Given `anvil init`, `anvil new-project` or `anvil onboard` run against a project with no design/ directory, when scaffolding completes, then design/DESIGN.md and design/tokens.json exist with the scaffold structure; and given a design/DESIGN.md that a human has since edited, when any of the three runs again, then the edited file is byte for byte unchanged and tokens.json is likewise untouched.

### Scenario: The scaffold is a structure with questions, not a look
- S2: Given a freshly scaffolded project, when design/DESIGN.md is read, then it contains sections for brand identity inputs (palette, typography, voice), art direction anchors, tokens, component and layout rules, motion rules, and quality bars for product pages covering hierarchy, scale contrast and responsive behavior; and when the scaffold files are searched, then they contain no prescribed palette, font family or house style belonging to the factory, only placeholders and the questions the project must answer.

### Scenario: Packets carry the project design system to interface stations
- S3: Given a project whose design/DESIGN.md states its quality bars and whose design/tokens.json states token values, when a run writes station packets, then the packets for builder, writer, media-producer, brief-writer and reviewer-design contain a Project design section carrying those token values and quality bars, and the packet for a station outside that set (for example scout) contains no Project design section.

### Scenario: A design reviewer judges interface output against the project system
- S4: Given the shipped pipelines, when they are validated, then sdlc-default, content-default and content-short each include reviewer-design in their parallel reviewer group, every reviewer they had before this change is still present, and stations/reviewer-design/ exists in the catalog with a contract that names the project's design system (tokens, rules and quality bars) as what its verdict judges.

### Scenario: A missing design system is a named warning and a named finding, never a silent pass
- S5: Given a project with no design/DESIGN.md, when a run executes a pipeline that includes interface producing stations, then the run report's warnings list contains a warning naming the missing design system; and given a run that includes reviewer-design in such a project, when the reviews are recorded, then reviewer-design's review carries verdict changes_requested and a finding stating that no design system exists for the project.
