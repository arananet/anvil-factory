# Design System

## Brand Identity

### Palette
TODO: Define your color palette. What are your primary, secondary, accent colors?
Consider accessibility (minimum 4.5:1 contrast ratio for text).

### Typography
TODO: What typefaces express your brand?
- Headings:
- Body text:
- Monospace (if applicable):

What is your type scale? (e.g., base size, scale ratio)

### Voice
TODO: How does your brand speak?
- Tone:
- Formality level:
- Key characteristics:

## Art Direction

TODO: Name the reference class for this project. What product pages, applications,
or experiences does this aspire to sit next to? What is the visual quality bar
you are aiming for?

## Tokens

Machine-readable design tokens live in `design/tokens.json`. That file is the
single source of truth for token values. Web projects can generate CSS variables
from it; native projects can generate platform-specific formats.

## Component and Layout Rules

TODO: Document component patterns and layout principles.

### Component Guidelines
- Buttons:
- Forms:
- Cards:
- Navigation:

### Layout Principles
- Spacing system:
- Grid/column structure:
- Breakpoints:

## Motion Rules

TODO: How does motion work in this project?

- Duration range:
- Easing preferences:
- What moves, what doesn't:
- Reduced motion considerations:

## Quality Bars for Product Pages

These bars apply to every product page or interface this project ships.

### Visual Hierarchy
- [ ] Clear content hierarchy with size, weight, and spacing
- [ ] Important actions are visually prominent
- [ ] Related elements are grouped

### Scale Contrast
- [ ] Minimum 4.5:1 contrast ratio for normal text
- [ ] Minimum 3:1 contrast ratio for large text (18pt+)
- [ ] Interactive elements have sufficient contrast

### Spacing Rhythm
- [ ] Consistent spacing scale used throughout
- [ ] Whitespace creates clear content boundaries
- [ ] Spacing adapts appropriately to different screen sizes

### Responsive Behavior
- [ ] Layout works on mobile, tablet, and desktop
- [ ] Touch targets are at least 44x44px on mobile
- [ ] Text is readable without zooming on any device
- [ ] No horizontal scrolling on standard viewports
