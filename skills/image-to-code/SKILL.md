---
name: image-to-code
description: Build from reference images without drift: extract the design system from the reference (text, typography, spacing, color, components), implement to match it, then compare rendered captures against the reference and close the gaps. Adapted from the image-to-code skill by Leonxlnx (MIT). Use when a work order supplies reference images, screenshots or an approved image pack as the visual target.
---

This skill applies when the work order supplies the visual target as images: owner reference photographs, screenshots, mockups, or an approved generated image pack (in this factory, art generated first and approved before the line integrates it). The reference is the visual contract. interface-design still governs where the reference is silent; the spec governs what is built.

**Analyze before coding**
- Treat each reference as a specification, not a mood. Extract, in writing, before any code: the readable text exactly as shown (headlines, labels, button text); the typography (families or their character, size and weight relationships, line counts, alignment); the spacing logic (gaps between headline, text and actions, card padding, gutters, section cadence); the colors (background, panels, accent, text hierarchy, borders, image treatment); the components (button shapes and hierarchy, cards, dividers, radius, shadows); the layout structure and section order.
- Work section by section from large, readable references. If a detail is too small or unclear to extract, say so and resolve it from a closer reference or a fresh generated detail image. Never guess a label, a number or a color the reference does not show.

**Implement without drift**
- Build the extracted system, not a reinterpretation: preserve layout logic, spacing rhythm, section order, typography mood and component family. Do not simplify distinctive sections into generic rows, compress generous spacing into dense layout, or replace strong type with a plain hierarchy.
- One extracted system across the whole page: no per-section palettes and no second design language halfway down.
- Resolve missing details in this order: the visible design language, the layout and spacing logic, the component family, the mood; only then the most implementation-friendly faithful choice. Record each resolution the reference forced you to invent.

**Verify against the reference**
- Render the build and place captures beside the reference at the same widths. Compare text, type scale, spacing, color and components section by section; name every gap plainly in the report and fix what the order's budget allows, largest gap first.
- The goal is faithful translation into real, working frontend: not a pixel-perfect trace, and never the reference image pasted in as the page. Do not lift the reference's photographs, logos or copy into the product unless the work order supplies them as the project's own material.

Adaptation note: upstream (image-to-code, in Leonxlnx/imagegen-skills) is written for an agent that generates the design images itself inside Codex. In this factory the images arrive with the work order or from the approved pack, so this entry carries its analysis, extraction and anti-drift discipline and drops the generation-side rules. The verbatim upstream text is vendored under third_party/image-to-code/.
