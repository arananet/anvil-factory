---
name: interface-design
description: Design web pages and app interfaces with a clear point of view, strong hierarchy and deliberate type, color and spacing, so the result reads as designed and not as a default template. Use when building any page or screen a person will see.
---

The project's design system is the authority. This skill is how to use it well, and what to do where it is silent. If the design tokens are placeholders (TODO) and the work order gives a palette or direction, define the tokens from that direction first, record them in the design system, then build from the tokens.

**Decide the direction before any code**
- Write one sentence: who this is for, what it must make them feel, and the one thing they should do. Pick an aesthetic that fits that sentence and commit to it: editorial, technical, playful, luxurious, brutal, calm. A committed direction beats a safe average.
- Name the one memorable element (an oversized headline, a diagram, a strong color field, a distinctive type pairing) and let the rest support it.
- Avoid the default look: centered everything, a purple to blue gradient, a generic sans serif at one weight, three identical feature cards with icons, rounded rectangles with soft shadows on white. If the page could belong to any product, it is not designed yet.

**Hierarchy**
- One focal point per view. Rank everything else beneath it with size, weight, color and space, in that order of strength. If everything is emphasized, nothing is.
- De-emphasize instead of only emphasizing: secondary text gets a quieter color and smaller size so the primary can stay calm.
- Primary action is unmistakable and there is one per view. Secondary actions are visibly secondary.

**Typography**
- Choose type with character that suits the subject; pair a display face for headings with a readable text face, or use one family at clearly different weights. Use fonts the project allows; when no external assets are allowed, build a deliberate system font stack instead of leaving the default.
- Use a real scale (for example 1.25 or 1.333 ratio) with few sizes. Make the jump from body to headline big enough to see: timid scales look undesigned.
- Body text 16 to 20 px, line height about 1.5, measure 45 to 75 characters. Headlines get tighter line height (1.05 to 1.2) and slightly negative tracking at large sizes.
- Set numbers, code and labels on purpose (tabular figures, monospace only where it means something).

**Color**
- Build from a neutral ramp of 8 to 10 steps plus one accent, with semantic colors for success, warning and error. Tint the neutrals slightly toward the accent so they belong together.
- Use the accent sparingly so it keeps its meaning: actions and the one thing to notice.
- Text contrast at least 4.5:1 (3:1 for large text and for interface components). Check the real pairs, including text on tinted and accent surfaces. On dark themes, avoid pure white on pure black; lift the background and soften the text.
- Never rely on color alone to carry meaning.

**Space and layout**
- One spacing scale (4 or 8 px base) used everywhere. Space inside a group is smaller than space between groups; that difference is what shows structure.
- Be generous: more whitespace than feels necessary around sections and the hero. Dense is a decision for data tools, not a default.
- Align to a grid and keep edges consistent. Break the grid deliberately in one place for emphasis, not accidentally in many.
- Constrain reading width; let sections vary in rhythm (full bleed, contained, split) so a long page does not read as a stack of identical blocks.

**Depth, detail and motion**
- Pick one depth language (borders, or shadows, or tonal layers) and use it consistently. Shadows are soft, layered and tinted, never a hard grey blur.
- Finish the details: consistent radius, icon stroke and size, aligned baselines, real content instead of lorem ipsum, designed empty and error states.
- Motion has a purpose (orientation, feedback, delight at one key moment). 150 to 300 ms, ease out for entering, honor reduced motion.

**Before you hand off, check**
- Squint at the page: is the focal point obvious, and does the eye travel in the intended order?
- Look at it at 360 px, a tablet width and wide desktop. Nothing overflows, wraps awkwardly or loses hierarchy.
- Compare against the reference anchors or the stated direction and name any gap honestly.
