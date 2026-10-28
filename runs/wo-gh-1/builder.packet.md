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

- id: wo-gh-1
- kind: feature
- title: Add per project design systems to ANVIL (design scaffold, packet injection, reviewer-design)
- source: github-issue
- description: Spec: .openspec/specs/project-design-system/spec.md (slug project-design-system), approved and written before this implementation. Implement it in the factory.

The problem it solves: the Sentia launch page shipped correct, live and visually basic because nothing in the factory owned design. No project artifact stated what good looks like, no packet carried design intent, and no reviewer judged interface quality.

What to build, per the spec scenarios:

S1: anvil init, anvil new-project and anvil onboard scaffold design/DESIGN.md and design/tokens.json only when absent, and never overwrite an existing design system (same discipline as the brain layout in verified-memory S7). Tokens are JSON, not CSS: ANVIL projects are not all web projects, JSON is target agnostic and a packet can carry exact values.

S2: The scaffold is a structure, not a look. DESIGN.md sections: brand identity inputs (palette, typography, voice), art direction anchors the project names for itself, tokens (pointing at tokens.json), component and layout rules, motion rules, and quality bars for product pages covering hierarchy, scale contrast and responsive behavior. Placeholders and questions only; no factory palette, font or house style anywhere in the scaffold.

S3: When a project has design/DESIGN.md, station packets for builder, writer, media-producer, brief-writer and reviewer-design gain a Project design section carrying the token values from design/tokens.json and the quality bars from DESIGN.md, computed once per run like packet_learnings_section in the runner. Packets for other stations are unchanged.

S4: Add stations/reviewer-design/ to the catalog (agent kind, standard review format) with a contract that judges interface output against the project design system. Add reviewer-design to the parallel reviewer group of pipelines/sdlc-default.json, pipelines/content-default.json and pipelines/content-short.json. Remove no existing reviewer from any pipeline.

S5: When a run's pipeline includes interface producing stations and the project has no design/DESIGN.md, the run report gains a top level warnings list with a warning naming the missing design system. When reviewer-design runs in a project with no design/DESIGN.md, its recorded review carries verdict changes_requested and a finding stating that no design system exists for the project.

Also: the factory dogfoods its own scaffolding where the existing patterns call for it (the way verified-memory added the brain layout to the factory repo itself), tests covering S1 to S5 in the factory suite style, docs updated (a docs page or README section describing the design system, in the style of docs/MEMORY-GATE.md), and the CHANGELOG Unreleased section updated. Keep the whole suite green and every pipeline valid.

GitHub issue: https://github.com/arananet/anvil-factory/issues/1
- risk_hints: 
- status: new

## Upstream steps

- intake: completed
- spec-writer: executed
- test-writer: executed
