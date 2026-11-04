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
}


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


def get_product_type(work_order):
    """Extract product type from work order description or default.

    Returns one of PRODUCT_TYPES. Defaults to 'physical_product' for
    visual UI work.
    """
    # Defensive: handle missing or invalid description attribute
    if not hasattr(work_order, "description"):
        return "physical_product"
    description = work_order.description
    if not isinstance(description, str):
        return "physical_product"
    description_lower = description.lower()
    if "game" in description_lower:
        return "game"
    elif "illustration" in description_lower:
        return "illustration"
    else:
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

    product_type = get_product_type(work_order)
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
