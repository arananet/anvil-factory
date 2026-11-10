"""Quality standard for visual deliverables.

Implements the quality charter system: a factory-level document defining
production quality per product type, reference anchors carrying owner's
quality bar, and station duties to compare outputs against anchors and
charter criteria.
"""

import json
import re
from pathlib import Path


def _sanitize_control_chars(text):
    """Sanitize control characters from text to prevent injection.

    Removes or replaces control characters that could be used for
    injection attacks (F3).
    """
    if not isinstance(text, str):
        return str(text)
    # Remove control characters (except tab and newline which are safe in markdown)
    # Keep \t (tab) and \n (newline), remove other control chars
    sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    return sanitized


# Product types with different quality criteria
PRODUCT_TYPES = {
    "physical_product",  # Consumer products with photorealism criteria
    "game",             # Games with stated standard per project
    "illustration",     # Illustrations with stated standard per project
    "interface",        # Web pages, apps and dashboards: interface craft criteria
}

# Project declared product types (brain/project.md, design system) that are
# interfaces. The design knowledge base names its slices this way.
INTERFACE_PROJECT_TYPES = {
    "interface", "dashboard", "mobile-app", "marketing-site", "landing-page",
    "website", "web-app", "webapp", "web", "saas", "docs-site", "portfolio",
}

# Phrases in a work order title or description that mark interface work.
INTERFACE_KEYWORDS = (
    "landing page", "web page", "webpage", "website", "web site", "web app",
    "dashboard", "frontend", "front end", "user interface", "html", "css",
    "status page", "homepage", "home page", "single page",
)

# Phrases that mark imagery of a physical product.
PHYSICAL_KEYWORDS = (
    "product render", "product shot", "packshot", "photoreal", "product photo",
)


def load_quality_charter():
    """Load the factory-level quality charter document.

    Returns dict with version and criteria per product type, or None if
    charter doesn't exist yet.
    """
    # Charter is defined inline to match the docs/QUALITY_CHARTER.md structure
    # This is the source of truth loaded into every visual run packet
    return {
        "version": "1.0.0",
        "criteria": {
            "physical_product": {
                "materials": "Surfaces read as the materials the product is actually made of",
                "light": "One coherent light story, with shadows and reflections that agree with it",
                "contact": "Objects meet skin, surfaces and each other the way physical things do",
                "scale": "The object's size reads true against its context and human anatomy",
            },
            "game": {
                "stated_standard": "Project must state observable criteria in design system",
            },
            "illustration": {
                "stated_standard": "Project must state observable criteria in design system",
            },
            "interface": {
                "hierarchy": "One clear focal point per view; size, weight and space rank everything else beneath it",
                "typography": "A deliberate type scale and measure; body text reads comfortably and headings carry the voice",
                "layout": "A consistent spacing scale and alignment grid; nothing overflows or collides from 360 px to wide desktop",
                "color": "A restrained palette used with intent; text contrast of at least 4.5:1 and one accent that means something",
                "states": "Interactive elements show hover, focus, active and disabled states; empty, loading and error views are designed",
                "character": "The page has a point of view that fits its subject; it does not read as an unstyled template",
            },
        },
    }


def is_visual_run(work_order):
    """Determine if a work order produces visual deliverables.

    Visual work has 'ui' or 'content' in surfaces. API-only, data-only,
    security-only work is not visual.
    """
    # Defensive: handle missing or invalid surfaces attribute
    if not hasattr(work_order, "surfaces"):
        return False
    surfaces = work_order.surfaces
    if not isinstance(surfaces, (list, set, tuple)):
        return False
    visual_surfaces = {"ui", "content"}
    return bool(set(surfaces) & visual_surfaces)


def _declared_in_text(text):
    """An explicit "Product type: X" declaration, when X is a charter type."""
    match = re.search(r"product type:\s*([a-z_\-]+)", text)
    if match:
        declared = match.group(1).replace("-", "_")
        if declared in PRODUCT_TYPES:
            return declared
    return None


def detect_product_type(work_order, project=None, keywords=True):
    """The product type the evidence supports, or None when nothing says.

    Order: an explicit "Product type: X" in the work order, the type the
    project itself declares (brain/project.md or its design system), the
    game and illustration keywords, the physical imagery phrases, then
    interface phrases in the work order. No default is applied here.
    With keywords=False only the two declarations count, which is the
    strict signal skill resolution uses when the surfaces do not say the
    work is visual.
    """
    description = getattr(work_order, "description", "")
    title = getattr(work_order, "title", "")
    description_lower = description.lower() if isinstance(description, str) else ""
    text = description_lower + "\n" + (title.lower() if isinstance(title, str) else "")

    declared = _declared_in_text(description_lower)
    if declared:
        return declared
    if project is not None:
        from .knowledge import get_project_product_type
        try:
            project_type = get_project_product_type(Path(project))
        except OSError:
            project_type = None
        if project_type:
            normalized = project_type.strip().lower().strip(".,;")
            if normalized.replace("-", "_") in PRODUCT_TYPES:
                return normalized.replace("-", "_")
            if normalized in INTERFACE_PROJECT_TYPES:
                return "interface"

    if not keywords:
        return None
    if "game" in description_lower:
        return "game"
    if "illustration" in description_lower:
        return "illustration"
    if any(phrase in text for phrase in PHYSICAL_KEYWORDS):
        return "physical_product"
    if any(phrase in text for phrase in INTERFACE_KEYWORDS):
        return "interface"
    return None


def get_product_type(work_order, project=None):
    """Product type for the quality charter. Returns one of PRODUCT_TYPES.

    Uses detect_product_type. When nothing is detected and the project is
    known, a run on the ui surface alone is interface work; anything else
    keeps the historical default of 'physical_product'.
    """
    # Defensive: handle missing or invalid description attribute
    if not hasattr(work_order, "description"):
        return "physical_product"
    if not isinstance(work_order.description, str):
        return "physical_product"
    detected = detect_product_type(work_order, project)
    if detected:
        return detected
    if project is not None:
        surfaces = getattr(work_order, "surfaces", None) or []
        if "ui" in surfaces and "content" not in surfaces:
            return "interface"
    return "physical_product"


def packet_quality_charter_section(project, station_id, work_order):
    """Render the quality charter section for station packets.

    Injects charter criteria into packets for stations that generate or
    review imagery, but only on visual runs. Returns "" for non-visual
    runs or non-imagery stations.

    When the work order declares identity_reference or deliverable_set,
    also injects the same-subject test duty for reviewing stations.
    """
    # TODO: Implement charter injection logic
    # Only inject for visual runs
    if not is_visual_run(work_order):
        return ""

    # Only inject for imagery stations
    imagery_stations = {
        "builder",
        "media-producer",
        "reviewer-design",
        "reviewer-ux",
    }

    if station_id not in imagery_stations:
        return ""

    charter = load_quality_charter()
    if not charter:
        return ""

    product_type = get_product_type(work_order, project)
    criteria = charter["criteria"].get(product_type, {})

    lines = ["## Quality Charter", ""]
    lines.append(f"Product type: {product_type}")
    lines.append("")
    lines.append("Observable criteria:")
    lines.append("")

    for criterion, description in criteria.items():
        lines.append(f"- **{criterion.replace('_', ' ').title()}**: {description}")

    lines.append("")

    # Inject same-subject test duty when BOTH identity_reference AND deliverable_set present
    has_identity_ref = hasattr(work_order, "identity_reference") and work_order.identity_reference
    has_deliverable_set = hasattr(work_order, "deliverable_set") and work_order.deliverable_set

    if (has_identity_ref and has_deliverable_set) and station_id in {"reviewer-design", "reviewer-ux"}:
        lines.append("## Same-Subject Test Duty")
        lines.append("")
        lines.append("This run produces a set of related visual deliverables.")
        lines.append("")

        # Reference the canonical identity source
        safe_identity_ref = _sanitize_control_chars(work_order.identity_reference)
        lines.append(f"**Identity reference**: `{safe_identity_ref}`")
        lines.append("")

        # List identity traits to check
        if hasattr(work_order, "identity_traits") and work_order.identity_traits:
            lines.append("**Identity traits to verify** (must remain constant across all deliverables):")
            for trait in work_order.identity_traits:
                safe_trait = _sanitize_control_chars(trait)
                lines.append(f"- {safe_trait}")
            lines.append("")

        # State the duty
        lines.append("**Your duty**: Perform a same-subject comparison across the entire deliverable set.")
        lines.append("")
        lines.append("1. Compare every deliverable against the identity reference on each identity trait listed above")
        lines.append("2. Any divergence in identity traits is a quality failure, even when every asset individually passes the anchor comparison")
        lines.append("3. Record the same-subject test ruling and its evidence in the quality section of your review")
        lines.append("4. If divergence is found, name the specific divergent asset and trait in your findings")
        lines.append("")
        lines.append("This test is part of the quality section judgment, not a separate verdict.")
        lines.append("")

    return "\n".join(lines)


def packet_anchor_section(project, station_id, work_order):
    """Render the reference anchors section for station packets.

    Returns anchor paths and a warning if no anchors are available.
    Only for visual runs and imagery stations.
    """
    # Only inject for visual runs
    if not is_visual_run(work_order):
        return ""

    # Only inject for imagery stations
    imagery_stations = {
        "builder",
        "media-producer",
        "reviewer-design",
        "reviewer-ux",
    }

    if station_id not in imagery_stations:
        return ""

    project_path = Path(project)
    ref_dir = project_path / "design" / "reference"

    lines = ["## Reference Anchors", ""]

    # Check for anchors in work order or project
    anchors = getattr(work_order, "anchors", [])

    if not anchors and not ref_dir.exists():
        lines.append("⚠️ **WARNING**: This run has no reference anchors.")
        lines.append("")
        lines.append("The review will proceed under the charter floor alone.")
        lines.append("")
        return "\n".join(lines)

    if anchors:
        for anchor in anchors:
            safe_anchor = _sanitize_control_chars(anchor)
            lines.append(f"- {safe_anchor}")
        lines.append("")

    return "\n".join(lines)


def validate_generating_station_comparison(comparison):
    """Validate that a generating station's self-comparison has required fields.

    Required fields:
    - output: path to generated image
    - anchor_cited: anchor path
    - criteria_checked: list of criteria
    - gaps: list of gaps (or empty)
    - statement: explicit statement about gaps
    """
    required = ["output", "anchor_cited", "criteria_checked", "gaps", "statement"]

    for field in required:
        if field not in comparison:
            return False

    # Statement must not be empty
    if not comparison["statement"]:
        return False

    # Gaps must be a list
    if not isinstance(comparison["gaps"], list):
        return False

    # Each gap must have criterion and description
    for gap in comparison["gaps"]:
        if "criterion" not in gap or "description" not in gap:
            return False

    return True


def validate_reviewer_quality_section(review):
    """Validate that a reviewer's quality section has proper structure.

    Quality section should be separate from compliance, cite anchors,
    and name specific criteria in findings.
    """
    if "quality" not in review:
        return False

    quality = review["quality"]

    # Must have verdict
    if "verdict" not in quality:
        return False

    # Must have findings (can be empty list)
    if "findings" not in quality:
        return False

    # If there are findings, at least one should reference an anchor or be explicit about floor
    if quality["findings"] and "anchor" not in quality:
        # Check if it's a floor gap explicitly named
        has_floor_gap = any("floor gap" in f.lower() for f in quality["findings"])
        if not has_floor_gap:
            return False

    return True
