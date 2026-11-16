# 0012: Every shipped web project credits ANVIL by default

Status: accepted 2026-11-16, work order wo-gh-43, spec attribution-default.

## Context

The owner rule, stated 2026-11-15: every project the factory ships carries an
ANVIL attribution by default. An operator audit of the shipped projects on
2026-11-15 found the rule was not true. Sentia carried a bespoke credit ("Sentia
is a concept product, designed and built end to end by ANVIL, an open source
software factory. Developed by Eduardo Arana."), while Doom Fire, Mochi Smash,
Platform25 and the live C64 page carried none. Nothing in the factory produced
the attribution: the scaffold did not seed it, the builder and publisher
guidance did not state it, and the checks gate could not see its absence.

## Decision

- The default attribution text is, exactly:
  "Made with ANVIL, an open source software factory."
  linked to https://anvil-landing-7x1.pages.dev (the factory repository link
  is an accepted alternative target). A bespoke
  credit that names ANVIL as the builder is compliant and is kept; Sentia is
  the standing example. Placement is the page footer or an equivalent visible
  spot; on a game surface, a credits or footer element outside the canvas and
  the input handling region.
- The wording, the compliance test and the deliverable check live in one
  module, anvil/attribution.py, read by scaffold, onboard and the checks gate.
- anvil/scaffold.py seeds the requirement into the first spec and
  brain/project.md of every blueprint with "ships_pages": true (static-site).
  anvil/onboard.py records it in ONBOARDING.md for a project with an HTML
  deliverable and never writes into the project's pages or existing files.
- stations/builder/PROMPT.md and stations/publisher/PROMPT.md state the rule;
  the publisher treats a missing attribution as a defect.
- The checks gate (anvil/gates.py, checks_gate) checks the index page of the
  web deliverable (public/, then dist/, then the project root). It passes on
  visible text carrying the default line or a sentence stating ANVIL built or
  made the project, and fails otherwise. Comments, attributes, script and
  style content do not count. A project without an HTML deliverable is not
  checked and gets no attribution output.
- The only exception is an owner approved exception recorded in a project
  spec as a line "Attribution exception: approved by <owner> on <YYYY-MM-DD>:
  <reason>", or the same form in anvil.json attribution_exception. The gate
  passes and quotes the line.

## Consequences

- Future web projects ship compliant from the first build; the gate catches a
  regression before review.
- Already shipped projects are not changed by this decision; each is
  retrofitted by its own order in its own repo.
- The bespoke credit test is a deterministic pattern (a build verb near "by",
  "with" or "using" ANVIL, or ANVIL followed by a build verb). An unusual
  bespoke wording can false fail; the fix is to reword the credit or record an
  owner exception, not to loosen the gate silently.
- cloudflare-worker is marked "ships_pages": false because its first spec is
  a worker entry, not a page. A worker project that later ships an HTML
  deliverable is still checked by the gate.
- Only the index page is checked when one exists; an attribution missing from
  secondary pages is not detected.
