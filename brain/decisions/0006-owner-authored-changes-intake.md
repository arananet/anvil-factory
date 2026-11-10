# 0006: Owner-authored changes intake

Status: recorded 2026-11-10 by the operator at the owner's request.

## Context

On 2026-11-10 the owner reworked the Dreamrun game end to end (three
commits on arananet/dreamrun, which he also renamed from
arananet/giana-3d) and landed a large factory improvement commit
directly on this repository's main (66aad5e986, "Improve station
guidance and add project token dashboards"). Both bodies of work were
produced with Claude Code, outside the line. The owner's stated reason:
the factory "no iba bien".

## Decision

Owner-authored work outside the line is a legitimate input to the
factory memory when three conditions hold:

1. It is documented from verifiable artifacts (diffs, commit messages,
   specs the owner wrote), never from reconstructed session history.
2. Practices derived from it enter only through the quarantine door
   (brain/inbox) with this record as their source, and promotion stays
   the owner's word.
3. The record states plainly that the line neither produced nor
   reviewed the work.

## Consequences

Six practice proposals derived from the 2026-11-10 owner work were
filed in brain/inbox on 2026-11-10 and wait there for promotion. The
learning document (operator copy: anvil-learnings-owner-work-2026-11-10)
records the changes and the extracted lessons, including the open
governance question this commit raises: the curated skills catalog
(skills/, producer guidance) and the practices base (brain/practices.md,
review rules) now coexist, and their split of duties is documented but
not yet governed by a single rule.

## Addendum (2026-11-10, later the same day)

The game now carries its final name end to end: the repository was
renamed arananet/giana-3d to arananet/dreamrun to arananet/mochi-smash,
and the game is deployed at its own URL, https://mochi-smash.pages.dev
(Cloudflare Pages project mochi-smash). The project is referenced in
project-reports/catalog.json. The earlier URL dreamrun-3d.pages.dev
still serves the same build as a historical alias of the factory era.
