"""
Design knowledge base for the UX module.

Provides:
- Built-in starter dataset (styles, palettes, fonts, guidelines, product types)
- Operator-supplied knowledge pack loading
- Deterministic slice matching by product type
- Packet injection for design stations
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any


# Required fields for each data kind
REQUIRED_FIELDS = {
    "styles": ["name", "description"],
    "palettes": ["name"],  # Palettes can have "colors" array or direct "hex" field
    "fonts": ["name", "display", "text", "character"],
    "guidelines": ["guideline", "concern"],
    "product-types": ["product_type", "styles", "palettes", "fonts", "why"],
}


class KnowledgeValidationError(ValueError):
    """Raised when knowledge data validation fails."""
    pass


def validate_knowledge_entry(filepath: Path, entry: Dict, data_kind: str):
    """Validate that a knowledge entry has all required fields.

    Args:
        filepath: Path to the data file (for error messages)
        entry: The entry dict to validate
        data_kind: The kind of data (styles, palettes, fonts, guidelines, product-types)

    Raises:
        KnowledgeValidationError: If entry is missing required fields
    """
    required = REQUIRED_FIELDS.get(data_kind, [])
    missing = [field for field in required if field not in entry]

    if missing:
        entry_name = entry.get("name") or entry.get("product_type") or entry.get("guideline", "")[:30]
        raise KnowledgeValidationError(
            f"Malformed entry in {filepath.name}: '{entry_name}' missing required fields: {missing}"
        )


def load_builtin_knowledge() -> Dict[str, Any]:
    """Load the built-in knowledge dataset from design-knowledge/.

    Returns:
        Dict with keys: styles, palettes, fonts, guidelines, product_types

    Raises:
        KnowledgeValidationError: If data files are missing or malformed
    """
    knowledge_dir = Path(__file__).parent.parent / "design-knowledge"

    if not knowledge_dir.exists():
        raise KnowledgeValidationError(f"Built-in knowledge directory not found: {knowledge_dir}")

    knowledge = {}
    file_map = {
        "styles": "styles.json",
        "palettes": "palettes.json",
        "fonts": "fonts.json",
        "guidelines": "guidelines.json",
        "product_types": "product-types.json",
    }

    for kind, filename in file_map.items():
        filepath = knowledge_dir / filename

        if not filepath.exists():
            raise KnowledgeValidationError(f"Required knowledge file not found: {filepath}")

        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise KnowledgeValidationError(f"Invalid JSON in {filepath}: {e}")

        # Validate each entry
        data_kind = "product-types" if kind == "product_types" else kind
        if isinstance(data, list):
            for entry in data:
                validate_knowledge_entry(filepath, entry, data_kind)
        elif isinstance(data, dict):
            for key, entries in data.items():
                if isinstance(entries, list):
                    for entry in entries:
                        validate_knowledge_entry(filepath, entry, data_kind)

        knowledge[kind] = data

    return knowledge


def load_knowledge_pack(pack_path: Path) -> Dict[str, Any]:
    """Load an operator-supplied knowledge pack.

    Args:
        pack_path: Path to the pack directory containing manifest.json

    Returns:
        Dict with: name, format_version, product_types, data (loaded data files),
                   manifest (original manifest), files (list of data files)

    Raises:
        FileNotFoundError: If pack path does not exist
        KnowledgeValidationError: If manifest or data is invalid
    """
    pack_path = Path(pack_path)

    # Defense in depth: reject paths that resolve into sensitive system locations
    try:
        resolved_path = pack_path.resolve()
    except (OSError, RuntimeError) as e:
        raise KnowledgeValidationError(f"Cannot resolve pack path: {e}")

    sensitive_prefixes = ["/etc", "/sys", "/proc", "/dev", "/boot"]
    for prefix in sensitive_prefixes:
        prefix_path = Path(prefix).resolve()
        try:
            resolved_path.relative_to(prefix_path)
            # If relative_to succeeds, the path is under the sensitive prefix
            raise KnowledgeValidationError(
                f"Knowledge pack path rejected: {resolved_path} resolves into sensitive "
                f"system location {prefix}. Pack paths must be outside system directories."
            )
        except ValueError:
            # relative_to raises ValueError if not a subpath - this is what we want
            pass

    if not pack_path.exists():
        raise FileNotFoundError(f"Knowledge pack path does not exist: {pack_path}")

    if not pack_path.is_dir():
        raise KnowledgeValidationError(f"Knowledge pack path is not a directory: {pack_path}")

    manifest_path = pack_path / "manifest.json"
    if not manifest_path.exists():
        raise KnowledgeValidationError(f"Pack manifest not found: {manifest_path}")

    try:
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        raise KnowledgeValidationError(f"Invalid JSON in pack manifest: {e}")

    # Validate manifest structure
    required_manifest_fields = ["name", "format_version", "product_types", "data_files"]
    missing = [field for field in required_manifest_fields if field not in manifest]
    if missing:
        raise KnowledgeValidationError(f"Pack manifest missing required fields: {missing}")

    if not isinstance(manifest["product_types"], list):
        raise KnowledgeValidationError("Pack manifest 'product_types' must be a list")

    if not isinstance(manifest["data_files"], list):
        raise KnowledgeValidationError("Pack manifest 'data_files' must be a list")

    # Load data files
    pack_data = {}
    kind_map = {
        "styles.json": "styles",
        "palettes.json": "palettes",
        "fonts.json": "fonts",
        "guidelines.json": "guidelines",
        "product-types.json": "product_types",
    }

    for filename in manifest["data_files"]:
        if filename not in kind_map:
            raise KnowledgeValidationError(f"Unknown data file in pack manifest: {filename}")

        data_path = pack_path / filename
        if not data_path.exists():
            raise KnowledgeValidationError(f"Pack data file not found: {data_path}")

        try:
            with open(data_path, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise KnowledgeValidationError(f"Invalid JSON in pack data file {filename}: {e}")

        # Validate entries
        kind = kind_map[filename]
        data_kind = "product-types" if kind == "product_types" else kind
        if isinstance(data, list):
            for entry in data:
                validate_knowledge_entry(data_path, entry, data_kind)
        elif isinstance(data, dict):
            for key, entries in data.items():
                if isinstance(entries, list):
                    for entry in entries:
                        validate_knowledge_entry(data_path, entry, data_kind)

        pack_data[kind] = data

    return {
        "name": manifest["name"],
        "format_version": manifest["format_version"],
        "product_types": manifest["product_types"],
        "data": pack_data,
        "manifest": manifest,
        "files": manifest["data_files"],
    }


def get_project_product_type(project_dir: Path) -> Optional[str]:
    """Extract product type from project brain or design system.

    Args:
        project_dir: Path to project directory

    Returns:
        Product type string, or None if not declared
    """
    # Check brain/project.md
    brain_file = project_dir / "brain" / "project.md"
    if brain_file.exists():
        content = brain_file.read_text(encoding="utf-8")
        # Look for "Product type: X" pattern
        import re
        match = re.search(r"Product type:\s*(\S+)", content, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    # Check design/tokens.json
    tokens_file = project_dir / "design" / "tokens.json"
    if tokens_file.exists():
        try:
            with open(tokens_file, encoding="utf-8") as f:
                tokens = json.load(f)
                if "product_type" in tokens:
                    return tokens["product_type"]
        except (json.JSONDecodeError, OSError):
            pass

    # Check design/DESIGN.md
    design_file = project_dir / "design" / "DESIGN.md"
    if design_file.exists():
        content = design_file.read_text(encoding="utf-8")
        import re
        match = re.search(r"Product type:\s*(\S+)", content, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None


def compute_knowledge_slice(
    product_type: Optional[str],
    knowledge_pack: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Compute knowledge slice for a product type.

    Deterministic: same inputs always return same slice.

    Args:
        product_type: Product type to match, or None for undeclared
        knowledge_pack: Optional operator-supplied pack (from load_knowledge_pack)

    Returns:
        Dict with: product_type_note, styles, palettes, fonts, guidelines,
                   matched (bool), pack_used (bool)
    """
    # Load built-in knowledge
    builtin = load_builtin_knowledge()

    # Determine active knowledge (pack overrides for covered product types)
    if knowledge_pack and product_type in knowledge_pack["product_types"]:
        # Use pack data for kinds it covers, built-in for the rest
        active = {}
        pack_data = knowledge_pack["data"]
        for kind in ["styles", "palettes", "fonts", "guidelines", "product_types"]:
            active[kind] = pack_data.get(kind, builtin.get(kind, [] if kind != "palettes" else {}))
        pack_used = True
    else:
        active = builtin
        pack_used = False

    # If no product type, return general guidelines only
    if not product_type:
        return {
            "product_type_note": None,
            "styles": [],
            "palettes": [],
            "fonts": [],
            "guidelines": active.get("guidelines", []),
            "matched": False,
            "pack_used": False,
        }

    # Find product type note
    product_types = active.get("product_types", [])
    product_note = None

    for pt in product_types:
        if pt.get("product_type") == product_type:
            product_note = pt
            break

    if not product_note:
        # Unknown product type - return general guidelines only
        return {
            "product_type_note": None,
            "styles": [],
            "palettes": [],
            "fonts": [],
            "guidelines": active.get("guidelines", []),
            "matched": False,
            "pack_used": pack_used,
        }

    # Extract referenced items
    referenced_styles = product_note.get("styles", [])
    referenced_palettes = product_note.get("palettes", [])
    referenced_fonts = product_note.get("fonts", [])

    # Gather matching styles
    all_styles = active.get("styles", [])
    matched_styles = [s for s in all_styles if s.get("name") in referenced_styles]

    # Gather matching palettes
    all_palettes = active.get("palettes", {})
    matched_palettes = []
    if isinstance(all_palettes, dict):
        # Palettes organized by product type
        product_palettes = all_palettes.get(product_type, [])
        for palette in product_palettes:
            if palette.get("name") in referenced_palettes:
                matched_palettes.append(palette)
    elif isinstance(all_palettes, list):
        # Flat list of palettes
        matched_palettes = [p for p in all_palettes if p.get("name") in referenced_palettes]

    # Gather matching fonts
    all_fonts = active.get("fonts", [])
    matched_fonts = [f for f in all_fonts if f.get("name") in referenced_fonts]

    # Always include general guidelines
    guidelines = active.get("guidelines", [])

    return {
        "product_type_note": product_note,
        "styles": matched_styles,
        "palettes": matched_palettes,
        "fonts": matched_fonts,
        "guidelines": guidelines,
        "matched": True,
        "pack_used": pack_used,
    }


def render_knowledge_slice(slice_data: Dict[str, Any]) -> str:
    """Render a knowledge slice as markdown text for packet injection.

    Args:
        slice_data: Slice dict from compute_knowledge_slice

    Returns:
        Markdown text
    """
    lines = []

    if slice_data.get("matched") and slice_data.get("product_type_note"):
        note = slice_data["product_type_note"]
        lines.append(f"### Product Type: {note['product_type']}")
        lines.append(f"\n{note.get('why', '')}\n")

        # Styles
        if slice_data.get("styles"):
            lines.append("### Interface Styles")
            for style in slice_data["styles"]:
                lines.append(f"- **{style['name']}**: {style['description']}")
            lines.append("")

        # Palettes
        if slice_data.get("palettes"):
            lines.append("### Color Palettes")
            for palette in slice_data["palettes"]:
                lines.append(f"- **{palette['name']}**")
                if "colors" in palette:
                    for color in palette["colors"]:
                        lines.append(f"  - {color['name']}: {color['hex']}")
            lines.append("")

        # Fonts
        if slice_data.get("fonts"):
            lines.append("### Font Pairings")
            for font in slice_data["fonts"]:
                lines.append(f"- **{font['name']}**: {font['character']}")
                lines.append(f"  - Display: {font['display']}")
                lines.append(f"  - Text: {font['text']}")
            lines.append("")
    else:
        lines.append("### Product Type: Undeclared")
        lines.append("\nNo specific product type declared. Using general guidelines only.\n")

    # Guidelines
    if slice_data.get("guidelines"):
        lines.append("### UX Guidelines")
        concerns = {}
        for guideline in slice_data["guidelines"]:
            concern = guideline.get("concern", "general")
            if concern not in concerns:
                concerns[concern] = []
            concerns[concern].append(guideline["guideline"])

        for concern, items in sorted(concerns.items()):
            lines.append(f"\n**{concern.title()}:**")
            for item in items:
                lines.append(f"- {item}")
        lines.append("")

    return "\n".join(lines)


def packet_knowledge_section(
    project_dir: Path,
    station_id: str,
    knowledge_pack: Optional[Dict[str, Any]] = None
) -> str:
    """Generate Design knowledge section for a station packet.

    Only design stations receive this section: reviewer-design, builder (for UI work),
    writer (for design authoring).

    Args:
        project_dir: Path to project directory
        station_id: Station ID
        knowledge_pack: Optional loaded pack from load_knowledge_pack()

    Returns:
        Markdown section text, or empty string if station should not receive it
    """
    # Design stations that receive knowledge
    design_stations = {"reviewer-design", "builder", "writer"}

    if station_id not in design_stations:
        return ""

    # Get product type
    product_type = get_project_product_type(project_dir)

    # Compute slice with pack if provided
    slice_data = compute_knowledge_slice(product_type, knowledge_pack)

    # Build section
    lines = ["## Design knowledge"]
    lines.append("")
    lines.append("**Authority**: The project's own design system (design/DESIGN.md, design/tokens.json) is the authority for this project. The knowledge base below is reference material that the design system may draw from. On any conflict, the project's design system wins. A deviation from the knowledge base alone is not a finding; a deviation from the project's design system is.")
    lines.append("")

    if not slice_data.get("matched"):
        lines.append("**Note**: No product type slice matched. General guidelines only.")
        lines.append("")

    lines.append(render_knowledge_slice(slice_data))

    return "\n".join(lines)


def record_pack_in_run_report(run_dir: Path, pack: Dict[str, Any]):
    """Record operator-supplied pack in run report.

    Args:
        run_dir: Path to run directory
        pack: Pack dict from load_knowledge_pack
    """
    report_file = run_dir / "report.md"

    if not report_file.exists():
        return

    # Add pack info to report
    pack_section = [
        "\n## Operator Supplied Inputs",
        "",
        "**Knowledge Pack**:",
        f"- Name: {pack['name']}",
        f"- Product types covered: {', '.join(pack['product_types'])}",
        f"- Data files: {', '.join(pack['files'])}",
        ""
    ]

    content = report_file.read_text(encoding="utf-8")
    # Append to end of file
    content += "\n".join(pack_section)
    report_file.write_text(content, encoding="utf-8")


def get_design_model_from_routing() -> str:
    """Get the design model from the factory's routing policy.

    Returns:
        Design model name from routing policy
    """
    from .routing import MODEL_POLICY
    return MODEL_POLICY.get("designer", "openai/gpt-6-astra")
