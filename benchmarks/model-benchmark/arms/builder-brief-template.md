# Task packet: builder (benchmark arm)

Work order: benchmark the design station models (GitHub issue 22 in arananet/anvil-factory). Build the page described below against the design system and return the finished file.

## Design system

### design/DESIGN.md

{{DESIGN_MD}}

## The page to build

A product page for the Meridian Patch with exactly this structure and copy. The element ids are contractual: style the contract elements through their id selectors in one style block (inline styles on a contract element are also read).

Structure and copy (verbatim):

- body
  - div id="page"
    - header
      - h1 id="hero-title": "Transform Your Health with Meridian Patch"
      - p id="hero-sub": "Advanced biosensor technology meets elegant design"
      - button id="cta-primary": "Start Your Journey"
      - span id="price-badge": "$199"
    - section id="section"
      - h2 id="heading-2": "Why Meridian Patch?"
      - p id="body-text": "The Meridian Patch combines cutting-edge health monitoring with seamless daily wear. Our proprietary biosensor array tracks your vital signs in real-time, providing actionable insights through our companion app. Designed for comfort and accuracy, the Meridian Patch represents the future of personal health technology."
      - p id="caption": "Clinical validation pending FDA review"
      - a id="link-inline" with href="#": "Learn more about our technology"
      - div id="card": an h3 "What's Included" and a list with three items: "30-day supply of Meridian Patches", "Premium companion app access", "24/7 health insights dashboard"

Rules for the deliverable:

- One self contained HTML file. All CSS in a single style block in the head. No external resources: no webfonts, no images, no scripts, no external stylesheets. Font stacks are CSS values only.
- The design system is the whole law: every color, size, spacing, radius, line height and font choice must follow it, including its minimums, its reserved color rule, its focus rule, its contrast rule and its motion rule.
- Use the copy verbatim. Do not add or remove contract elements.

## Output

Return only the complete HTML file content, beginning with <!DOCTYPE html>. No commentary, no explanation, no code fences.
