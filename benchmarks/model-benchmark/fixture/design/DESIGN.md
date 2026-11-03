# Meridian Patch Design System

## Color Palette

The Meridian Patch uses a refined, nature-inspired palette:

- **paper** `#FAFAF6` - Page background
- **ink** `#14201B` - Headings and primary text
- **pine** `#53685C` - Secondary text and captions
- **teal** `#0E7C66` - Primary action background
- **coral** `#FF6B4A` - Reserved exclusively for the price badge
- **line** `#E3E6DF` - Borders and dividers

## Typography

### Type Scale

All text sizes are drawn from this scale (in px): 12, 14, 16, 20, 24, 32, 40, 56, 64.

- Hero titles must use at least 56px
- Body text must use at least 16px

### Font Stacks

- **Headings**: The first family in every heading stack is "Space Grotesk"
- **Body**: The first family in the body stack is "Inter"

### Line Heights

- **Headings**: 1.2 (unitless)
- **Body text**: 1.5 (unitless)

## Spacing

All margin and padding values are multiples of 8. Zero is permitted.

## Border Radius

Radius tokens (in px): 4, 8, 12, 16, 999.

All border-radius values must use one of these tokens.

## Focus States

Links and buttons show a `:focus-visible` outline with these properties:
- 2px solid teal (`#0E7C66`)
- 2px offset

## Accessibility

### Contrast

Text on the paper background must meet at least 4.5:1 contrast ratio by the WCAG relative luminance formula.

### Motion

Transitions are permitted only when accompanied by a `prefers-reduced-motion` media query block that disables them for users who prefer reduced motion.

## Quality Bars

### Color Usage
- [ ] All colors are from the documented palette
- [ ] Coral is used only on the price badge
- [ ] Text contrast on paper meets 4.5:1 minimum

### Typography
- [ ] Hero titles are at least 56px from the type scale
- [ ] Body text is at least 16px from the type scale
- [ ] All font sizes are from the type scale
- [ ] Headings use Space Grotesk as first family
- [ ] Body text uses Inter as first family
- [ ] Heading line height is 1.2
- [ ] Body line height is 1.5

### Spacing
- [ ] All margins and paddings are multiples of 8

### Border Radius
- [ ] All border-radius values use documented radius tokens

### Focus and Accessibility
- [ ] Focus-visible outline is 2px solid teal with 2px offset
- [ ] Transitions have prefers-reduced-motion block
