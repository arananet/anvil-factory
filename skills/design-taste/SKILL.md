---
name: design-taste
description: Art direction for public pages (landing pages, marketing sites, company websites): read the brief as a kind of business, commit to one direction, lead with real visuals in one system, and check the result in a real browser before handoff. Adapted from the Taste Skill by Leonxlnx (MIT). Use when building a public page that must not read as a generic template.
---

The project's design system and interface-design govern the craft basics: hierarchy, type scale, color, spacing. This skill adds art direction: how a public page earns a point of view. It is written for landing pages, marketing sites and company websites. For dashboards, admin tools and data-dense product UI it does not apply: interface-design governs there, with no one-section-per-screen rule and no dealt moments.

**Read the brief as a kind of business**
- Name the kind first: software or a game, a physical product, a service people hire, or a place people visit. The kind decides what leads. Software shows its own real UI at work; a product shows the product itself, big and whole; a service shows the people and the work; a place leads with photographs of the place.
- Write down what is sold, who buys it, and the one main action (book, order, start, visit). The first screen says what is sold, for whom, with one hard fact.
- Nothing is invented: no invented reviews, quotes, customers, figures or prices. Where the brief is silent, say so in the report instead of filling the gap with plausible copy.

**One system, one direction**
- One button style pair, one card family, one radius scale, one link look, one heading scale. Two boxes deep at most; no cards inside cards.
- Equal left and right content edges on one wrap or grid. Nothing staggered, tilted or bleeding to one side by accident.
- The hero stands alone on the first screen with its main action inside it. Each section carries one idea and runs one or two screens tall, with no neighbour heading peeking in.
- Never violet or lavender as the page's own accent, ground or gradient. The upstream rule matches this factory's ban on the default purple to blue gradient look.

**Real visuals, honestly labelled**
- Real photographs and the client's own assets lead where they fit. A visual never renders as an empty ground at any width from 390 px up.
- A specific real product is shown by its own photographs or by renders built from the project's reference anchors, never by a stock look-alike passed off as the product. Generic stand-in photographs are allowed only for setting and trade detail, and each one is named as a stand-in in the builder report.
- No caption or description under an image; credits go in one footer line. No drawn look-alike of a real logo; use the real icon or none.

**Motion is a layer, not a garnish**
- Every button, link and linked card visibly answers the pointer: a small lift, a press, an underline that draws. The hero enters once on load. One or two deliberate moments on a long page; nothing fades in on scroll section after section, no parallax on text, no scroll-jacking.
- Anything moving longer than 5 seconds has a pause. Under reduced motion everything rests and nothing stays hidden.

**Check in a real browser, then report**
- Render the page and read screenshots at desktop and phone widths against this list: first screen complete, edges equal, no overflow at 320 px, every target at least 44 px, contrast on the real pairs, every link lands.
- Report what was checked, what could not be checked, and every assumed fact. A failed check is fixed or waived with its reason in the report, never hidden.

Adaptation note: upstream (design-taste-frontend 2.5.1) drives Node dealers, a component kit and a browser gate hook; none of that tooling is adopted here. This entry carries its house rules, kind system and checklist. The verbatim upstream text is vendored under third_party/taste-skill/.
