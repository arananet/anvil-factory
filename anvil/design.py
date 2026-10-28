"""Project design system: scaffold, load, and inject into station packets.

Every project can have a design system at design/DESIGN.md (identity, anchors,
rules, quality bars) and design/tokens.json (machine readable token values).
The scaffold is a structure with questions, never a factory imposed style.
When present, the design system flows into packets for interface producing
stations: builder, writer, media-producer, brief-writer and reviewer-design.
"""

import json
from pathlib import Path


DESIGN_MD_TEMPLATE = """# Design System

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
"""


TOKENS_JSON_TEMPLATE = {
    "colors": {
        "primary": "TODO",
        "secondary": "TODO",
        "accent": "TODO",
        "background": "TODO",
        "surface": "TODO",
        "text": "TODO",
        "text-secondary": "TODO",
        "error": "TODO",
        "warning": "TODO",
        "success": "TODO",
        "info": "TODO"
    },
    "typography": {
        "font-family-base": "TODO",
        "font-family-heading": "TODO",
        "font-family-mono": "TODO",
        "font-size-base": "TODO",
        "font-size-scale": "TODO",
        "line-height-base": "TODO",
        "line-height-heading": "TODO"
    },
    "spacing": {
        "unit": "TODO",
        "scale": ["TODO"]
    },
    "layout": {
        "max-width": "TODO",
        "breakpoint-mobile": "TODO",
        "breakpoint-tablet": "TODO",
        "breakpoint-desktop": "TODO"
    },
    "motion": {
        "duration-fast": "TODO",
        "duration-base": "TODO",
        "duration-slow": "TODO",
        "easing-standard": "TODO",
        "easing-enter": "TODO",
        "easing-exit": "TODO"
    }
}


def scaffold_design_system(project):
    """Create design/DESIGN.md and design/tokens.json when absent.

    Never overwrites existing files, matching the onboarding discipline for
    brain files. Returns a list of created file paths relative to project root.
    """
    project = Path(project)
    created = []

    design_dir = project / "design"
    design_md = design_dir / "DESIGN.md"
    tokens_json = design_dir / "tokens.json"

    # Create design directory if it doesn't exist
    if not design_dir.exists():
        design_dir.mkdir(parents=True, exist_ok=True)

    # Create DESIGN.md only if it doesn't exist
    if not design_md.exists():
        design_md.write_text(DESIGN_MD_TEMPLATE.strip() + "\n", encoding="utf-8")
        created.append("design/DESIGN.md")

    # Create tokens.json only if it doesn't exist
    if not tokens_json.exists():
        tokens_json.write_text(
            json.dumps(TOKENS_JSON_TEMPLATE, indent=2) + "\n",
            encoding="utf-8"
        )
        created.append("design/tokens.json")

    return created


def load_design_system(project):
    """Load the project's design system if it exists.

    Returns a dict with 'tokens' (parsed JSON) and 'quality_bars' (extracted
    from DESIGN.md), or None if the design system doesn't exist.
    """
    project = Path(project)
    design_md = project / "design" / "DESIGN.md"
    tokens_json = project / "design" / "tokens.json"

    if not design_md.exists():
        return None

    tokens = {}
    if tokens_json.exists():
        try:
            tokens = json.loads(tokens_json.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            tokens = {}

    # Extract quality bars section from DESIGN.md
    quality_bars = ""
    try:
        content = design_md.read_text(encoding="utf-8")
        # Look for the Quality Bars section
        if "## Quality Bars" in content:
            start = content.index("## Quality Bars")
            # Find the next ## heading or end of file
            rest = content[start + len("## Quality Bars"):]
            next_section = rest.find("\n## ")
            if next_section != -1:
                quality_bars = rest[:next_section].strip()
            else:
                quality_bars = rest.strip()
    except OSError:
        pass

    return {
        "tokens": tokens,
        "quality_bars": quality_bars
    }


def packet_design_section(project, station_id):
    """Render the packet's Project design section for interface stations.

    Returns a markdown section with design tokens and quality bars for stations
    that produce or judge interface output (builder, writer, media-producer,
    brief-writer, reviewer-design), or "" for all other stations and when no
    design system exists.
    """
    interface_stations = {
        "builder",
        "writer",
        "media-producer",
        "brief-writer",
        "reviewer-design"
    }

    if station_id not in interface_stations:
        return ""

    design_system = load_design_system(project)
    if design_system is None:
        return ""

    lines = ["## Project design", ""]

    # Add tokens
    if design_system["tokens"]:
        lines.append("### Design tokens")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(design_system["tokens"], indent=2))
        lines.append("```")
        lines.append("")

    # Add quality bars
    if design_system["quality_bars"]:
        lines.append("### Quality bars")
        lines.append("")
        lines.append(design_system["quality_bars"])
        lines.append("")

    return "\n".join(lines)
