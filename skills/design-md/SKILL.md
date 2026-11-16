---
name: design-md
description: Work with a project DESIGN.md as the design system of record: read and follow it when one exists, draft one in the Stitch DESIGN.md format when a visual project has none, and judge a built page against it section by section. Use on interface work where design consistency across pages matters.
---

A DESIGN.md is a plain text design system document at the project root: how the project looks and feels, written for agents to read. AGENTS.md says how to build; DESIGN.md says how it should look. In this factory's authority order a project DESIGN.md is part of the project design system, so it beats every skill, including this one. interface-design teaches how to design; this skill teaches how to work with the document that records the design.

**When the project has a DESIGN.md**
- Read it before designing or building, all of it, and build from its tokens: colors, type, spacing, shapes, components and their states. Where it is silent, interface-design fills the gap; where it speaks, it wins.
- Never improvise a token the document already defines, and never copy another brand's DESIGN.md over the project's own. A named brand file is a reference for format and depth only, unless the work order itself names that brand as the design anchor.
- When the built page and the document disagree, the document is the bug report: fix the page, or record the intended change by updating the document in the same change. Never drift silently.

**When a visual project has none, draft one**
- Draft DESIGN.md at the project root from the project's real decisions (the brief, the brain, the tokens already in code), in the Stitch format the awesome-design-md collection uses: Overview; Colors (brand and accent, surface, text, semantic); Typography (families, hierarchy, principles); Layout (spacing system, grid and container, responsive strategy, breakpoints, touch targets); Elevation and depth; Shapes (radius scale, image geometry); Components (buttons, cards, inputs, navigation, signature components, each with states); Do and Don't lists.
- Write values, not adjectives: hex colors, pixel sizes, ratios and named rules an agent can check. Mark anything not yet decided as a placeholder instead of inventing a decision.
- A drafted DESIGN.md is a proposal until the project adopts it; say so in the report. Do not draft one for a one-off page the project will not revisit.

**Reviewing against it**
- reviewer-design: check the captures against the document section by section (colors, typography, layout, components, the Don't list) and cite the section in each finding.
- A page that follows its DESIGN.md and still looks wrong is a document problem: report it as one. Do not fail the builder for obeying the system of record.

The format and the worked examples come from VoltAgent's awesome-design-md collection (MIT), which holds a DESIGN.md extracted from more than eighty production websites. The collection is referenced as the format reference, not vendored: its files are other brands' design systems, and copying one in as a factory default would fight every project's own system.
