"""Quality standard for visual deliverables.

Implements the quality charter system: a factory-level document defining
production quality per product type, reference anchors carrying owner's
quality bar, and station duties to compare outputs against anchors and
charter criteria.
"""

import json
from pathlib import Path


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
    # TODO: Implement proper visual run detection
    visual_surfaces = {"ui", "content"}
    return bool(set(work_order.surfaces) & visual_surfaces)


def get_product_type(work_order):
    """Extract product type from work order description or default.

    Returns one of PRODUCT_TYPES. Defaults to 'physical_product' for
    visual UI work.
    """
    # TODO: Implement product type extraction from work order
    description = work_order.description.lower()
    if "game" in description:
        return "game"
    elif "illustration" in description:
        return "illustration"
    else:
        return "physical_product"


def packet_quality_charter_section(project, station_id, work_order):
    """Render the quality charter section for station packets.

    Injects charter criteria into packets for stations that generate or
    review imagery, but only on visual runs. Returns "" for non-visual
    runs or non-imagery stations.
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

    return "\n".join(lines)


def packet_anchor_section(project, work_order):
    """Render the reference anchors section for station packets.

    Returns anchor paths and a warning if no anchors are available.
    """
    # TODO: Implement anchor section with proper anchor loading
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
            lines.append(f"- {anchor}")
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
