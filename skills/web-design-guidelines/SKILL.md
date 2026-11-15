---
name: web-design-guidelines
description: Audit a built interface against the Web Interface Guidelines: accessibility, focus, forms, animation, typography, images, performance, navigation, touch, theming and locale, reported as terse file and line findings. Use when reviewing a page or app interface before it ships.
---

Audit only. Judge the built files against the rules below and report findings grouped by file, one per line, as `path:line - finding`. State the issue and the location; skip explanation unless the fix is not obvious. A file with no findings is marked pass. Do not rewrite the page; the builder fixes findings on the next round.

The rules are distilled from Vercel's Web Interface Guidelines (command.md, vendored pinned under third_party/web-interface-guidelines/, MIT), so a verdict is reproducible instead of fetched fresh at review time. They extend web-engineering, which the builder already holds; where a rule repeats it, treat the repetition as the audit form of the same bar. Framework wording is translated: a rule written for React components applies to whatever builds the same element.

**Accessibility and focus**
- Icon-only buttons carry an aria-label; decorative icons are aria-hidden. Form controls have a label or aria-label. Async updates (toasts, validation) use aria-live polite.
- Semantic elements before ARIA: button for actions, a for navigation, never a div with a click handler. Headings in order h1 to h6; a skip link reaches main content; anchored headings have scroll-margin-top.
- Every interactive element shows a visible focus, :focus-visible rather than :focus, never an outline removed without a replacement. Compound controls group focus with :focus-within. Sticky bars never cover the focused element.

**Forms**
- Inputs have autocomplete and a meaningful name, the correct type and inputmode. Paste is never blocked. Labels are clickable. Spellcheck is off on emails, codes and usernames.
- The submit button stays enabled until the request starts, then shows progress. Errors sit inline next to their field and the first error takes focus on submit. Placeholders end with the ellipsis character and show the expected pattern. Warn before navigation loses unsaved changes.

**Animation, typography, content**
- prefers-reduced-motion is honored with a reduced variant or none. Animate transform and opacity only; never transition: all; list the properties. Motion over 5 seconds next to other content has pause, stop or hide.
- Use the ellipsis character and curly quotes, not three dots or straight quotes. Number columns use tabular figures. Headings use text-wrap balance or pretty.
- Containers survive long content (truncate, line clamp or break words); flex children that must shrink carry min-width 0. Empty states render designed, not broken.

**Images, performance, navigation**
- Images declare width and height; below the fold they lazy load; the critical above-fold image is prioritized. Prefer muted looping video over an animated GIF, with a still alternative.
- Lists over about 50 items use content-visibility or virtualization before reaching for a library. No layout reads in render paths; DOM reads and writes are batched. CDN and asset domains are preconnected; critical fonts preload with font-display swap.
- The URL reflects state (filters, tabs, pagination, open panels) and stateful views deep-link. Links are real links that survive cmd-click and middle-click. Destructive actions ask for confirmation or offer undo, never fire immediately.

**Touch, layout, theming, locale**
- touch-action manipulation; the tap highlight set on purpose; modals and drawers contain overscroll. Full-bleed layouts respect safe-area insets. Layout comes from flex and grid, not JS measurement.
- Dark themes set color-scheme and a theme-color meta that matches the background; native selects get explicit colors. Dates, numbers and currency go through Intl formatters, never hardcoded formats; language is detected from Accept-Language, not IP. Brand names and identifiers are marked translate no.

**Copy in the interface**
- Active voice, second person, specific labels (Save API Key, not Continue), numerals for counts. Error messages name the fix or the next step, not only the problem. Title case on headings and buttons.

**Flag on sight**
- Zoom disabled (user-scalable no or maximum-scale 1), paste blocked, transition: all, an outline removed without replacement, click handlers on a div or span, images without dimensions, unlabelled inputs or icon buttons, hardcoded date or number formats, autofocus without a clear reason, an animated GIF where video fits.
