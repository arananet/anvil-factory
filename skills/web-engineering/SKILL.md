---
name: web-engineering
description: Build web pages and front ends that are semantic, accessible, responsive, fast and complete in every state. Use when writing HTML, CSS or client side code.
---

**Semantic structure**
- Use the element that means the thing: `header`, `nav`, `main`, `section`, `article`, `footer`, `button` for actions, `a` for navigation, real lists and tables. One `h1`, heading levels in order with no skipped levels.
- Set `lang`, a descriptive `title`, a meta description and the viewport meta. Give every image real `alt` text, or empty `alt` when decorative. Inline SVG that carries meaning gets a `title` or `aria-label`; decorative SVG is `aria-hidden`.
- Label every form control with a `label`. Group related controls. Use the right input types and `autocomplete`.

**Accessibility (WCAG 2.2 AA is the floor)**
- Everything works with a keyboard alone, in a logical order, with a clearly visible focus indicator. Never remove an outline without replacing it.
- Text contrast at least 4.5:1, large text and interface components at least 3:1.
- Pointer targets at least 44 by 44 px with space between them.
- Prefer native elements over ARIA. Add ARIA only for what HTML cannot express, and then wire the full pattern: role, state and keyboard behaviour.
- Announce changes that happen without navigation (status and error messages) through a live region. Errors say what went wrong and how to fix it, next to the field.
- Honor `prefers-reduced-motion`; nothing flashes; no information carried by color alone.

**Responsive layout**
- Design mobile first from 360 px and enhance upward. Use fluid layout (flex, grid, `minmax`, `clamp`) instead of fixed widths, and let content decide breakpoints.
- No horizontal scroll at any width from 360 px up. Long words, code blocks, tables and wide SVG are the usual offenders: give them `overflow-wrap`, `overflow-x: auto` or `max-width: 100%`.
- Media scales with its container and declares `width` and `height` (or `aspect-ratio`) so the layout does not shift.
- Type and spacing scale with the viewport within sensible bounds. Test at 360, 768, 1024 and 1440 px and in landscape on a phone.

**CSS that lasts**
- Put the design tokens in custom properties on `:root` and use them everywhere; no stray hex values or one off pixel sizes.
- Low specificity, class based selectors, no `!important`. Use logical properties and `rem` for type.
- Support light and dark where the design calls for it through `prefers-color-scheme`, driven by the same tokens.

**Performance**
- Ship the least that works: no framework or library the page does not need. Inline critical CSS for a single page; defer or drop non essential scripts.
- Size and compress images, use modern formats, lazy load below the fold, and never load a font or asset the design does not use.
- Target good Core Web Vitals: largest content paints quickly, no layout shift, input responds immediately. Avoid long main thread work and animation of layout properties; animate `transform` and `opacity`.

**Every state exists**
- Interactive elements have hover, focus visible, active and disabled styles.
- Views that load data have loading, empty, error and success states. Long text, missing images and very short content do not break the layout.
- The page works without JavaScript where the content does not require it, and fails gracefully where it does.

**Verify in a browser before handoff**
- Open the real page. Tab through it. Resize from 360 px upward. Check the console for errors.
- Validate the HTML, check every link target resolves, and confirm every spelled label and number on the page against its source.
- Produce the rendered captures the order asks for at the stated viewports, from the final tree.
