import inspect
import uuid
import hashlib
import json, os, shlex, struct, subprocess, time, zlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from .model import WorkOrder, Review
from .config import default_model, resolve_model, load_anvil_config, health_config, CHARS_PER_TOKEN, get_station_budget
from .brain import (packet_learnings_section, resolve_practices, practices_by_id,
                    packet_practices_section, gate_practices_section)
from .design import packet_design_section, load_design_system
from .capture import capture_breakpoints, packet_rendered_evidence_section
from .gates import human_gate, checks_gate, resolve_base_ref_config, _run_shell, validate_builder_report, review_artifact_state
from .approver import aggregate, needs_human, aggregate_explained, needs_human_explained, matched_risk_hints, RISK_SCAN_ORDER
from .executor import ExecutorError
from .routing import route_reviewers, write_routing_record, render_routing_section, routing_swimlane_summary
from .cost import load_price_table, calculate_cost, build_cost_section
from .knowledge import (
    load_knowledge_pack,
    packet_knowledge_section,
    get_project_product_type,
    get_design_model_from_routing,
    KnowledgeValidationError,
)
from .quality import (
    packet_quality_charter_section,
    packet_anchor_section,
    is_visual_run,
)
from .skills import resolve_skills, skills_by_id, packet_skills_section, public_resolution
from .telemetry import summarize_steps, efficiency_config, budget_reason, EFFICIENCY_NOTE

def _sanitize_control_chars(text):
    """Sanitize control characters from text to prevent injection.

    Removes or replaces control characters that could be used for
    injection attacks (F3).
    """
    if not isinstance(text, str):
        return str(text)
    # Remove control characters (except tab and newline which are safe in markdown)
    import re
    # Keep \t (tab) and \n (newline), remove other control chars
    sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    return sanitized
from .health import verify_health
from .observe import RunRecorder, mark_crashed
from . import line as _line

def _escape_markdown(text):
    """Escape markdown special characters to prevent content injection.

    Escapes characters that could be used to inject markdown formatting,
    links, or other content into generated reports.
    """
    if not isinstance(text, str):
        return str(text)
    # Escape markdown special characters
    special_chars = ['\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '#', '+', '-', '.', '!', '|', '<', '>']
    result = text
    for char in special_chars:
        result = result.replace(char, '\\' + char)
    return result

class PacketBudgetError(Exception):
    """Raised when a packet exceeds budget and policy is fail"""
    pass

class ContactSheetError(Exception):
    """Raised when contact sheet assembly fails"""
    pass

class AllowlistViolation(Exception):
    """Raised when packet contains content from outside allowlist"""
    pass

class PathValidationError(Exception):
    """Raised when a path fails validation"""
    pass

def estimate_tokens(text):
    """S1: Deterministic token estimator for packet budgeting.

    Returns an estimated token count based on character count. This is a
    heuristic for budgeting, never presented as the provider's tokenizer count.
    The constant CHARS_PER_TOKEN is visible in config for transparency.
    """
    if not text:
        return 0
    return int(len(text) / CHARS_PER_TOKEN)

def assemble_contact_sheet(capture_paths, output_path, max_width, evidence_dir=None):
    """S2: Combine PNG captures into one contact sheet, scaled down if needed.

    Loopback item 4: Security hardening - validates output path, enforces size caps,
    verifies CRCs, and bounds checks chunk lengths.

    Captures are scaled down proportionally to fit max_width, never scaled up.
    Returns the output path. Fails loudly on non-PNG inputs.
    """
    if not capture_paths:
        raise ContactSheetError("No captures provided")

    # Loopback item 4: Validate output path resolves inside evidence directory
    # If evidence_dir is not provided, infer it from the first capture path
    if evidence_dir is None and capture_paths:
        evidence_dir = Path(capture_paths[0]).parent

    if evidence_dir is not None:
        output_resolved = Path(output_path).resolve()
        evidence_resolved = Path(evidence_dir).resolve()
        try:
            output_resolved.relative_to(evidence_resolved)
        except ValueError:
            raise ContactSheetError(
                f"Contact sheet output path must resolve inside evidence directory. "
                f"Output: {output_resolved}, Evidence dir: {evidence_resolved}"
            )

    images = []
    for path in capture_paths:
        try:
            width, height, pixels = _read_png(path)
            images.append((width, height, pixels, path))
        except Exception as e:
            raise ContactSheetError(f"Failed to process {path}: {e}")

    # Calculate contact sheet layout (vertical stack)
    # Scale down images that exceed max_width
    scaled_images = []
    total_height = 0
    sheet_width = 0

    for width, height, pixels, path in images:
        if width > max_width:
            # Scale down proportionally
            scale = max_width / width
            new_width = max_width
            new_height = int(height * scale)
            scaled_pixels = _scale_png_pixels(pixels, width, height, new_width, new_height)
            scaled_images.append((new_width, new_height, scaled_pixels))
            total_height += new_height
            sheet_width = max(sheet_width, new_width)
        else:
            # Keep original size (never scale up)
            scaled_images.append((width, height, pixels))
            total_height += height
            sheet_width = max(sheet_width, width)

    # Create contact sheet by stacking images vertically
    contact_sheet_pixels = []
    for img_width, img_height, img_pixels in scaled_images:
        for row in img_pixels:
            # Pad row to sheet width if needed
            if img_width < sheet_width:
                padding = b'\x00\x00\x00' * (sheet_width - img_width)
                contact_sheet_pixels.append(row + padding)
            else:
                contact_sheet_pixels.append(row)

    # Write contact sheet PNG
    _write_png(output_path, sheet_width, total_height, contact_sheet_pixels)
    return output_path

def _read_png(path):
    """Read PNG dimensions and pixel data. Raises on non-PNG or invalid files.

    Loopback item 4: Security hardening with size caps, CRC verification, and bounds checking.
    """
    # Loopback item 4: Enforce byte size cap before reading
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
    file_size = Path(path).stat().st_size
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"PNG file size {file_size} exceeds cap of {MAX_FILE_SIZE} bytes")

    data = Path(path).read_bytes()

    # Verify PNG signature
    if not data.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError(f"Not a valid PNG file: {path}")

    # Parse IHDR chunk for dimensions
    idx = 8

    # Loopback item 4: Bounds check chunk length before read
    if idx + 4 > len(data):
        raise ValueError(f"Malformed PNG: unexpected end of file reading IHDR length")

    ihdr_length = struct.unpack('>I', data[idx:idx+4])[0]

    # Loopback item 4: Bounds check chunk data availability
    if idx + 8 + ihdr_length + 4 > len(data):
        raise ValueError(f"Malformed PNG: IHDR chunk length {ihdr_length} exceeds available data")

    ihdr_type = data[idx+4:idx+8]

    if ihdr_type != b'IHDR':
        raise ValueError(f"IHDR chunk not found: {path}")

    ihdr_data = data[idx+8:idx+8+ihdr_length]

    # Loopback item 4: Verify IHDR CRC
    ihdr_crc_expected = struct.unpack('>I', data[idx+8+ihdr_length:idx+8+ihdr_length+4])[0]
    ihdr_crc_computed = zlib.crc32(ihdr_type + ihdr_data) & 0xffffffff
    if ihdr_crc_computed != ihdr_crc_expected:
        raise ValueError(f"PNG CRC mismatch in IHDR chunk: expected {ihdr_crc_expected:08x}, got {ihdr_crc_computed:08x}")

    width, height = struct.unpack('>II', ihdr_data[:8])

    # Loopback item 4: Enforce dimension caps before inflating image data
    MAX_DIMENSION = 50000
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise ValueError(f"PNG dimensions {width}x{height} exceed cap of {MAX_DIMENSION}x{MAX_DIMENSION}")

    # Extract IDAT chunks and decompress pixel data
    # Loopback gate round 3, finding 3b & 3c: Calculate expected raw size and cap IDAT bytes
    # Expected raw size: height rows of (1 filter byte + width * 3 bytes RGB)
    expected_raw_size = height * (1 + width * 3)

    # Loopback gate round 3, finding 3c: Cap accumulated IDAT bytes
    # Use a bound tied to expected raw size (allow reasonable compression ratio)
    # PNG typically compresses well, but set a reasonable upper limit
    max_idat_compressed = max(expected_raw_size * 2, 10 * 1024 * 1024)  # 2x expected or 10MB, whichever is smaller

    idx = 8
    idat_data = b''
    while idx < len(data):
        # Loopback item 4: Bounds check before reading chunk length
        if idx + 4 > len(data):
            break

        chunk_length = struct.unpack('>I', data[idx:idx+4])[0]

        # Loopback item 4: Bounds check chunk length against available data
        if idx + 8 + chunk_length + 4 > len(data):
            raise ValueError(f"Malformed PNG: chunk length {chunk_length} at offset {idx} exceeds available data")

        chunk_type = data[idx+4:idx+8]
        chunk_data = data[idx+8:idx+8+chunk_length]
        chunk_crc_expected = struct.unpack('>I', data[idx+8+chunk_length:idx+8+chunk_length+4])[0]

        # Loopback item 4: Verify chunk CRC
        chunk_crc_computed = zlib.crc32(chunk_type + chunk_data) & 0xffffffff
        if chunk_crc_computed != chunk_crc_expected:
            raise ValueError(f"PNG CRC mismatch in {chunk_type.decode('ascii', errors='replace')} chunk: expected {chunk_crc_expected:08x}, got {chunk_crc_computed:08x}")

        if chunk_type == b'IDAT':
            # Loopback gate round 3, finding 3c: Check accumulated size before adding
            if len(idat_data) + len(chunk_data) > max_idat_compressed:
                raise ValueError(
                    f"PNG accumulated IDAT size {len(idat_data) + len(chunk_data)} exceeds cap of {max_idat_compressed} bytes "
                    f"(expected raw size: {expected_raw_size} bytes)"
                )
            idat_data += chunk_data
        elif chunk_type == b'IEND':
            break

        idx += 12 + chunk_length  # length + type + data + CRC

    # Loopback gate round 4, item 2: Decompress with hard cap to prevent memory exhaustion
    # CRITICAL: zlib.decompress bufsize parameter is NOT a hard limit - it is only a buffer hint
    # A crafted PNG can decompress far beyond bufsize before any size check executes
    # Use decompressobj with max_length = expected_raw_size to ensure we never materialize
    # more than expected_raw_size bytes before detecting a violation
    try:
        decompressor = zlib.decompressobj()

        # Decompress with hard cap set to expected_raw_size
        # This ensures we never materialize more than expected bytes before failing
        raw_pixels = decompressor.decompress(idat_data, expected_raw_size)

        # Check if there's more data in the stream beyond expected_raw_size
        # If unconsumed_tail exists, the decompressor stopped at max_length
        if decompressor.unconsumed_tail:
            # Try to decompress one more byte to verify there's excess data
            excess = decompressor.decompress(decompressor.unconsumed_tail, 1)
            if excess:
                # Stream contains more data than expected - fail immediately
                raise ValueError(
                    f"PNG IDAT decompression exceeds expected size during inflation: "
                    f"stream yields more than expected {expected_raw_size} bytes. "
                    f"Possible compression bomb (dimensions {width}x{height} imply {expected_raw_size} bytes)."
                )

        # Flush any remaining buffered data
        final_chunk = decompressor.flush()
        if final_chunk:
            # Check if flush would exceed expected size
            if len(raw_pixels) + len(final_chunk) > expected_raw_size:
                raise ValueError(
                    f"PNG IDAT decompression exceeds expected size during flush: "
                    f"total {len(raw_pixels) + len(final_chunk)} bytes, expected {expected_raw_size} bytes "
                    f"(dimensions {width}x{height} imply {expected_raw_size} bytes). "
                    f"Possible compression bomb attack."
                )
            raw_pixels += final_chunk
    except zlib.error as e:
        raise ValueError(f"PNG IDAT decompression failed: {e}")

    # Loopback gate round 3, finding 3b: Verify decompressed size matches expected (second line of defense)
    if len(raw_pixels) != expected_raw_size:
        raise ValueError(
            f"PNG decompressed IDAT size {len(raw_pixels)} does not match expected size {expected_raw_size} "
            f"(dimensions {width}x{height} imply {height} rows of {1 + width * 3} bytes)"
        )

    # Parse scanlines (each row has a filter byte + RGB pixels)
    pixels = []
    bytes_per_row = width * 3 + 1  # filter byte + RGB for each pixel
    for row_idx in range(height):
        start = row_idx * bytes_per_row
        row_data = raw_pixels[start:start + bytes_per_row]
        pixels.append(row_data[1:])  # Skip filter byte

    return width, height, pixels

def _scale_png_pixels(pixels, orig_width, orig_height, new_width, new_height):
    """Scale PNG pixels using nearest neighbor. Returns scaled pixel rows."""
    scaled = []
    for y in range(new_height):
        orig_y = int(y * orig_height / new_height)
        row = []
        for x in range(new_width):
            orig_x = int(x * orig_width / new_width)
            pixel_start = orig_x * 3
            pixel = pixels[orig_y][pixel_start:pixel_start + 3]
            row.append(pixel)
        scaled.append(b''.join(row))
    return scaled

def _write_png(path, width, height, pixels):
    """Write PNG file with given dimensions and pixel rows."""
    # PNG signature
    signature = b'\x89PNG\r\n\x1a\n'

    # IHDR chunk
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr_chunk = _make_png_chunk(b'IHDR', ihdr_data)

    # IDAT chunk (compress pixel data with filter bytes)
    raw_data = b''
    for row in pixels:
        raw_data += b'\x00' + row  # Add filter byte
    compressed = zlib.compress(raw_data)
    idat_chunk = _make_png_chunk(b'IDAT', compressed)

    # IEND chunk
    iend_chunk = _make_png_chunk(b'IEND', b'')

    Path(path).write_bytes(signature + ihdr_chunk + idat_chunk + iend_chunk)

def _make_png_chunk(chunk_type, data):
    """Create PNG chunk with length, type, data, and CRC."""
    length = struct.pack('>I', len(data))
    chunk = chunk_type + data
    crc = struct.pack('>I', zlib.crc32(chunk) & 0xffffffff)
    return length + chunk + crc

def validate_work_order_paths(work_order, project):
    """Loopback item 4: Validate WorkOrder file path fields resolve inside project tree."""
    project_resolved = Path(project).resolve()

    # Validate evidence_images paths
    for img_path in work_order.evidence_images:
        full_path = (project_resolved / img_path).resolve()
        try:
            full_path.relative_to(project_resolved)
        except ValueError:
            raise PathValidationError(
                f"Evidence image path escapes project tree: {img_path} "
                f"resolves to {full_path}, outside {project_resolved}"
            )

    # Validate spec_path if present
    if work_order.spec_path:
        full_path = (project_resolved / work_order.spec_path).resolve()
        try:
            full_path.relative_to(project_resolved)
        except ValueError:
            raise PathValidationError(
                f"Spec path escapes project tree: {work_order.spec_path} "
                f"resolves to {full_path}, outside {project_resolved}"
            )

def verify_packet_allowlist_by_provenance(packet, allowlist):
    """Loopback item 3: Verify packet allowlist compliance by checking provenance tags.

    Content blocks must be tagged with their source file path using HTML comments:
    <!-- source: path/to/file.md -->

    This function verifies that every tagged source is in the allowlist. Pattern
    scanning of packet text cannot verify provenance and is insufficient.

    Loopback gate round 3, finding 3a: Path boundaries enforced - a source is allowed
    only when it equals an allowlist entry or lies beneath an allowlisted path at a
    path separator boundary. Path traversals (..) are resolved before matching.
    """
    import re
    import os

    # Extract all provenance tags
    tag_pattern = r'<!-- source: (.+?) -->'
    sources = re.findall(tag_pattern, packet)

    # Normalize allowlist paths for comparison - preserve trailing slashes
    normalized_allowlist = []
    for p in allowlist:
        # Use os.path.normpath to resolve .. and . but it removes trailing slashes,
        # so we need to track and restore them
        has_trailing_slash = p.endswith('/')
        normalized = os.path.normpath(p).replace('\\', '/')
        if has_trailing_slash and not normalized.endswith('/'):
            normalized += '/'
        normalized_allowlist.append(normalized)

    for source in sources:
        # Normalize source path - resolve .. and . using os.path.normpath
        source_normalized = os.path.normpath(source).replace('\\', '/')

        # Check if source is in allowlist using path boundaries
        allowed = False
        for allowed_path in normalized_allowlist:
            # Exact match
            if source_normalized == allowed_path or source_normalized == allowed_path.rstrip('/'):
                allowed = True
                break
            # Nested beneath at path separator boundary
            # Check if source starts with allowed_path followed by a separator
            if allowed_path.endswith('/'):
                # allowed_path is a directory - check if source is under it
                if source_normalized.startswith(allowed_path):
                    allowed = True
                    break
            else:
                # allowed_path is a file or directory without trailing slash
                # Check if source is nested beneath it (allowed_path + '/')
                if source_normalized.startswith(allowed_path + '/'):
                    allowed = True
                    break

        if not allowed:
            raise AllowlistViolation(
                f"Packet contains content from file outside allowlist: {source}. "
                f"Allowlist: {', '.join(normalized_allowlist)}"
            )

def build_reviewer_design_packet(project, work_order, files_changed, contact_sheet_path,
                                 prompt=None):
    """S3: Build a fresh, scoped packet for reviewer-design.

    Loopback item 2: Located in anvil/runner.py (runner module), not anvil/stations.
    The runner orchestrates packet assembly; stations consume packets.

    Loopback gate round 3, finding 2: The caller resolves the station prompt through
    the station registry and passes it in. This function never imports from .stations
    at any scope.

    Contains: station prompt, design section, spec, diff summary, contact sheet.
    Does NOT contain: builder transcript, other station outputs, whole file contents.

    Loopback item 3: Tags content with provenance for allowlist verification.

    Returns: (packet_text, allowlist) tuple where allowlist is the list of allowed
    source paths for verification.
    """
    project = Path(project)

    # Loopback gate round 3, finding 2: Default prompt if none provided (no import)
    if prompt is None:
        prompt = "Review the design against the design system."

    # Design section with provenance tag
    design_section = packet_design_section(project, "reviewer-design")
    design_section = f"<!-- source: design/DESIGN.md -->\n{design_section}"

    # Spec content with provenance tag
    spec_content = ""
    if work_order.spec_path:
        spec_path = project / work_order.spec_path
        if spec_path.exists():
            spec_content = spec_path.read_text(encoding="utf-8")
            spec_content = f"<!-- source: {work_order.spec_path} -->\n{spec_content}"

    # Diff summary (deterministic from files_changed)
    diff_lines = ["## Diff summary", ""]
    for file_info in files_changed:
        file_name = file_info["file"]
        added = file_info.get("added", 0)
        removed = file_info.get("removed", 0)
        diff_lines.append(f"- {file_name}: +{added}, -{removed}")
    diff_summary = "\n".join(diff_lines)

    # Contact sheet reference
    contact_sheet_ref = ""
    if contact_sheet_path:
        contact_sheet_ref = f"\n## Evidence\n\nContact sheet: {contact_sheet_path}\n"

    # Build allowlist from files changed, design files, and spec
    allowlist = []
    allowlist.append("design/DESIGN.md")
    allowlist.append("design/tokens.json")
    if work_order.spec_path:
        allowlist.append(work_order.spec_path)
    for file_info in files_changed:
        allowlist.append(file_info["file"])

    # Build packet
    packet = (
        f"# Task packet: reviewer-design\n\n"
        f"## Station prompt\n\n{prompt}\n\n"
        f"{design_section}\n\n"
        f"## Spec\n\n{spec_content}\n\n"
        f"{diff_summary}\n"
        f"{contact_sheet_ref}\n"
        f"## File access allowlist\n\n"
        f"This packet may only embed content from:\n"
    )

    for allowed_file in allowlist:
        packet += f"- {allowed_file}\n"

    # Loopback gate round 3, finding 1: Return allowlist so caller can verify
    return packet, allowlist

def prepare_reviewer_design_step(project, work_order, files_changed, captures, registry=None):
    """Loopback item 1: Prepare reviewer-design step by assembling contact sheet and scoped packet.

    This integrates S2 (contact sheet assembly) and S3 (scoped packet builder) into the run path.

    Loopback gate round 3, finding 1: Calls verify_packet_allowlist_by_provenance on the
    built packet against the declared allowlist before returning. A packet with out-of-allowlist
    content fails here with AllowlistViolation.

    Loopback gate round 3, finding 2: Resolves the reviewer-design prompt through the station
    registry and passes it to the builder.

    Returns (packet_text, contact_sheet_path) tuple.
    """
    from .config import load_anvil_config, get_contact_sheet_max_width

    project = Path(project)
    run_dir = project / "runs" / work_order.id

    # S2: Assemble contact sheet if captures exist
    contact_sheet_path = None
    if captures:
        max_width = get_contact_sheet_max_width(load_anvil_config(project / "anvil.yaml"))
        contact_sheet_path = run_dir / "contact-sheet.png"
        assemble_contact_sheet(captures, contact_sheet_path, max_width, evidence_dir=run_dir)

    # Loopback gate round 3, finding 2: Resolve prompt through station registry
    prompt = None
    if registry is not None:
        station = registry.get("reviewer-design")
        if station and station.prompt:
            prompt = station.prompt

    # S3: Build scoped packet through scoped packet builder
    packet, allowlist = build_reviewer_design_packet(
        project, work_order, files_changed, contact_sheet_path, prompt=prompt
    )

    # Loopback gate round 3, finding 1: Verify packet allowlist by provenance
    # This check executes in the preparation path on the built packet against
    # exactly the allowlist the packet declares
    verify_packet_allowlist_by_provenance(packet, allowlist)

    return packet, contact_sheet_path

def prepare_packet(project, station_id, prompt, work_order, steps,
                   learnings_section="", design_section="",
                   rendered_evidence_section="", knowledge_section="",
                   quality_charter_section="", anchor_section="", practices_section="",
                   skills_section="", run_context_section=""):
    """S1: Prepare packet with budget measurement and trimming.

    Returns (packet_text, action, measured_tokens, budget) where:
    - action is 'sent', 'trimmed', or raises PacketBudgetError if policy is fail
    - measured_tokens is the final packet size
    - budget is the configured budget for this station
    """
    from .config import get_station_budget

    project = Path(project)
    config = load_anvil_config(project / "anvil.yaml")

    # Get budget (factory defaults from config module)
    budget = get_station_budget(config, station_id)
    packet_cap = efficiency_config(config).get("max_packet_tokens")
    if packet_cap:
        budget = min(budget, packet_cap)

    # Build initial packet
    packet = _packet_text(station_id, prompt, work_order, steps,
                         learnings_section, design_section,
                         rendered_evidence_section, knowledge_section,
                         quality_charter_section, anchor_section, practices_section,
                         skills_section, run_context_section)

    measured = estimate_tokens(packet)

    # Check if under budget
    if measured <= budget:
        return packet, "sent", measured, budget

    # Over budget - try trimming
    # Trim order: compact tokens, reduce quality bars, limit learnings

    # Try compact tokens (no pretty print)
    from .design import packet_design_section_compact
    design_compact = packet_design_section_compact(project, station_id) if design_section else ""
    packet_trimmed = _packet_text(station_id, prompt, work_order, steps,
                                   learnings_section, design_compact,
                         rendered_evidence_section, knowledge_section,
                         quality_charter_section, anchor_section, practices_section,
                         skills_section, run_context_section)
    measured = estimate_tokens(packet_trimmed)

    if measured <= budget:
        return packet_trimmed, "trimmed", measured, budget

    # Try reduced quality bars
    from .design import packet_design_section_reduced
    design_reduced = packet_design_section_reduced(project, station_id) if design_section else ""
    packet_trimmed = _packet_text(station_id, prompt, work_order, steps,
                                   learnings_section, design_reduced,
                         rendered_evidence_section, knowledge_section,
                         quality_charter_section, anchor_section, practices_section,
                         skills_section, run_context_section)
    measured = estimate_tokens(packet_trimmed)

    if measured <= budget:
        return packet_trimmed, "trimmed", measured, budget

    # Try limited learnings
    from .brain import packet_learnings_section_limited
    learnings_limited = packet_learnings_section_limited(project, budget // 10)
    packet_trimmed = _packet_text(station_id, prompt, work_order, steps,
                                   learnings_limited, design_reduced,
                         rendered_evidence_section, knowledge_section,
                         quality_charter_section, anchor_section, practices_section,
                         skills_section, run_context_section)
    measured = estimate_tokens(packet_trimmed)

    if measured <= budget:
        return packet_trimmed, "trimmed", measured, budget

    # Still over budget - check policy
    policy = config.get("over_budget_policy", "trim")
    if policy == "fail":
        raise PacketBudgetError(
            f"Packet for {station_id} exceeds budget: {measured} tokens > {budget} budget"
        )

    # Policy is trim but we still exceed - fail anyway
    raise PacketBudgetError(
        f"Packet for {station_id} exceeds budget after all trim rules: "
        f"{measured} tokens > {budget} budget"
    )

@dataclass
class RunReport:
    work_order_id: str
    pipeline: str
    title: str = ""
    kind: str = ""
    steps: list = field(default_factory=list)
    verdict: str = ""
    human_required: bool = False
    max_loopbacks: int = 2
    loopbacks: int = 0
    deployment_status: str = None
    verify_results: list = field(default_factory=list)
    risk_hints: list = field(default_factory=list)
    decision: dict = field(default_factory=dict)
    warnings: list = field(default_factory=list)
    astra_measured_tokens_total: int = 0
    base_ref: str = None
    evidence: list = field(default_factory=list)
    health: dict = field(default_factory=dict)
    # Practice skills R4: resolved practice ids per station, topics excluded
    # by project override, and the active base count at run start.
    practices: dict = field(default_factory=lambda: {"resolved": {}, "excluded_topics": [], "active_count": 0})
    skills: dict = field(default_factory=lambda: {"resolved": {}, "disabled": [], "catalog_count": 0, "signals": {}})
    efficiency: dict = field(default_factory=dict)
    run_id: str = ""
    def to_dict(self):
        # Build cost section from steps
        measured_steps = [s for s in self.steps if s.get("cost") is not None]
        executed_steps = [s for s in self.steps if s.get("status") == "executed"]
        unmeasured_steps = [s for s in executed_steps if s.get("cost") is None]
        cost_total = sum(s["cost"] for s in measured_steps)
        cost_section = {
            "total": cost_total,
            "measured_steps": len(measured_steps),
            "unmeasured_steps": len(unmeasured_steps)
        }

        result = {"work_order_id": self.work_order_id, "pipeline": self.pipeline,
                "title": self.title, "kind": self.kind,
                "steps": self.steps, "verdict": self.verdict, "human_required": self.human_required,
                "max_loopbacks": self.max_loopbacks, "loopbacks": self.loopbacks,
                "deployment_status": self.deployment_status, "verify_results": self.verify_results,
                "risk_hints": self.risk_hints, "decision": self.decision, "warnings": self.warnings,
                "astra_measured_tokens_total": self.astra_measured_tokens_total,
                "base_ref": self.base_ref, "evidence": self.evidence, "cost": cost_section,
                "practices": self.practices,
                "skills": self.skills,
                "token_usage": summarize_steps(self.steps), "efficiency": self.efficiency,
                "run_id": self.run_id}

        # Add health section if present
        if self.health:
            result["health"] = self.health

        return result

def parse_review(text, station_id):
    """Parse exactly one review JSON object from the authoritative channel.

    The review file must parse as exactly one JSON object (surrounding
    whitespace and one surrounding markdown code fence allowed) with station
    equal to the step station id, verdict one of pass, fail, changes_requested,
    and findings a list of strings. Anything else returns None; the caller
    records that as review_parse_failed and the station contributes no review.
    """
    if not text:
        return None

    # Strip whitespace and optional markdown code fence
    content = text.strip()
    if content.startswith("```json") or content.startswith("```"):
        lines = content.splitlines()
        # Remove first line (opening fence)
        lines = lines[1:]
        # Remove last line if it's a closing fence
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        content = "\n".join(lines).strip()

    # Parse as exactly one JSON object
    try:
        obj = json.loads(content)
    except json.JSONDecodeError:
        return None

    if not isinstance(obj, dict):
        return None
    if "verdict" not in obj or "station" not in obj:
        return None
    if obj["station"] != station_id:
        return None
    if obj["verdict"] not in {"pass", "fail", "changes_requested"}:
        return None

    try:
        return Review(station=str(obj["station"]),
                      verdict=str(obj["verdict"]),
                      findings=[str(f) for f in obj.get("findings", [])])
    except ValueError:
        return None

def _reported_model(text):
    """A model name counts only when the runtime output itself reports one.

    Scans the output for a JSON object with a string "model" field. Anything
    else returns None: ANVIL never guesses which model a runtime used.
    """
    if not text:
        return None
    decoder = json.JSONDecoder()
    for idx, ch in enumerate(text):
        if ch != "{":
            continue
        try:
            obj, _ = decoder.raw_decode(text[idx:])
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and isinstance(obj.get("model"), str) and obj["model"]:
            return obj["model"]
    return None

def _consumes_model_handoff(executor):
    """True when the executor hands the assigned model to its runtime.

    The command executor exports it as ANVIL_CONFIGURED_MODEL and the
    dispatcher selects the runtime by it; the http executor always runs the
    model named in its own config.
    """
    return getattr(executor, "kind", None) == "command"


def _call_executor(executor, packet_text, station_id, configured_model=None, **kwargs):
    """Call executor.execute, handing it the assigned model when it accepts one.

    Executors written before the model hand-off (for example test doubles)
    have no configured_model parameter; they are called without it.
    """
    try:
        params = inspect.signature(executor.execute).parameters
    except (TypeError, ValueError):
        params = {}
    accepts = "configured_model" in params or any(
        p.kind is inspect.Parameter.VAR_KEYWORD for p in params.values())
    if accepts:
        kwargs["configured_model"] = configured_model
    return executor.execute(packet_text, station_id, **kwargs)


def _executor_provenance(executor, output_text=""):
    """Return (executor_object, executed_model) for an attempted execution.

    The http executor runs the model named in its config, so that model is
    the executed model and the detail is the endpoint host. A command
    executor is an opaque local process: the detail is the template's first
    token and the executed model is known only when the runtime output
    reports one itself.
    """
    kind = getattr(executor, "kind", "unknown")
    if kind == "http":
        endpoint = getattr(executor, "endpoint", "")
        detail = urlparse(endpoint).hostname or endpoint
        return {"kind": "http", "detail": detail}, (getattr(executor, "model", "") or None)
    if kind == "command":
        template = getattr(executor, "template", "")
        try:
            tokens = shlex.split(template)
        except ValueError:
            tokens = template.split()
        detail = tokens[0] if tokens else ""
        return {"kind": "command", "detail": detail}, _reported_model(output_text)
    return {"kind": str(kind), "detail": getattr(executor, "name", str(kind))}, None


def _snapshot_working_tree(project_dir):
    """Capture current state of working tree files.

    Args:
        project_dir: Path to project directory

    Returns:
        Dict mapping relative file paths to their content hash (or None for deleted/new).
    """
    project_path = Path(project_dir)
    snapshot = {}

    for p in project_path.rglob("*"):
        if p.is_file() and ".git" not in p.parts and "runs" not in p.parts:
            try:
                rel_path = str(p.relative_to(project_path))
                # Use file modification time as a simple hash
                snapshot[rel_path] = p.stat().st_mtime
            except (ValueError, OSError):
                pass

    return snapshot


def _compute_delta(before_snapshot, after_snapshot):
    """Compute the delta between two working tree snapshots.

    Args:
        before_snapshot: Dict from _snapshot_working_tree (before state)
        after_snapshot: Dict from _snapshot_working_tree (after state)

    Returns:
        Set of file paths that were added, modified, or deleted.
    """
    delta = set()

    # Files added or modified
    for file_path, mtime in after_snapshot.items():
        if file_path not in before_snapshot or before_snapshot[file_path] != mtime:
            delta.add(file_path)

    # Files deleted
    for file_path in before_snapshot:
        if file_path not in after_snapshot:
            delta.add(file_path)

    return delta


def _get_changed_files(project_dir, initial_files=None, work_output_dirs=None, base_ref=None):
    """Get list of changed files relative to base ref.

    Uses git to detect changes. If git is not available and initial_files
    snapshot is provided, compares current state against the snapshot to find
    new or deleted files.

    Args:
        project_dir: Path to project directory
        initial_files: Set of initial files for fallback comparison
        work_output_dirs: Set of directories where new files are always considered changed
        base_ref: Git ref to compare against (if None, compares against HEAD for uncommitted)

    Returns a set of file paths relative to project root.
    """
    project_path = Path(project_dir)

    # Try git first
    try:
        # Check if this is a git repo
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            # Get changed files from git
            if base_ref:
                # Compare current HEAD against base ref to get all changes on the work branch
                result = subprocess.run(
                    ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
                    cwd=str(project_dir),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            else:
                # No base ref, just get uncommitted changes
                result = subprocess.run(
                    ["git", "diff", "--name-only", "HEAD"],
                    cwd=str(project_dir),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            files = {line.strip() for line in result.stdout.split('\n') if line.strip()}

            # Also get untracked files
            result2 = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"],
                cwd=str(project_dir),
                capture_output=True,
                text=True,
                timeout=10
            )
            if result2.returncode == 0:
                files.update({line.strip() for line in result2.stdout.split('\n') if line.strip()})

            # If we have a base_ref, also include uncommitted changes
            if base_ref:
                result3 = subprocess.run(
                    ["git", "diff", "--name-only"],
                    cwd=str(project_dir),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result3.returncode == 0:
                    files.update({line.strip() for line in result3.stdout.split('\n') if line.strip()})

            return files
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass

    # Fallback: compare against initial snapshot
    if initial_files is not None:
        current_files = set()
        for p in project_path.rglob("*"):
            if p.is_file() and ".git" not in p.parts and "runs" not in p.parts:
                try:
                    rel_path = p.relative_to(project_path)
                    current_files.add(str(rel_path))
                except ValueError:
                    pass

        # Files that are NEW or were DELETED
        new_files = current_files - initial_files
        deleted_files = initial_files - current_files
        changed = new_files | deleted_files

        # Also treat files in work output directories as changed
        # (e.g., tests/ is for test files created during work)
        if work_output_dirs:
            for file_path in current_files:
                # Check if file is in a work output directory
                for work_dir in work_output_dirs:
                    if file_path.startswith(work_dir + "/") or file_path.startswith(work_dir + "\\"):
                        changed.add(file_path)
                        break

        return changed

    # No git and no snapshot: can't determine changes
    return set()


CHECK_AWARE_STATIONS = {"test-writer", "builder", "reviewer-tests"}


def packet_run_context_section(project, work_order, steps, station_id, checks=None):
    """Point a station at the work that already exists for this run.

    Lists only what is on disk: the spec the work order names, the output
    file of each upstream step, and for the stations that write or judge
    code, the project's own check commands. Returns "" when there is
    nothing to point at.
    """
    project = Path(project)
    lines = []
    spec_path = str(getattr(work_order, "spec_path", "") or "")
    if spec_path and ".." not in spec_path and not spec_path.startswith("/") and (project / spec_path).is_file():
        lines.append(f"- Spec for this order: {_sanitize_control_chars(spec_path)}")
    for step in steps:
        upstream_id = str(step.get("station", ""))
        if upstream_id and (project / "runs" / work_order.id / f"{upstream_id}.output.md").is_file():
            lines.append(f"- Output of {upstream_id}: runs/{work_order.id}/{upstream_id}.output.md")
    if station_id in CHECK_AWARE_STATIONS:
        for command in checks or []:
            lines.append(f"- Project check: `{_sanitize_control_chars(str(command))}`")
    if not lines:
        return ""
    header = ["## Run context", "",
              "Read the upstream work before you start; it is the input your station builds on."]
    if station_id in CHECK_AWARE_STATIONS and checks:
        header.append("The checks gate runs the project checks listed here; run them yourself before you hand off.")
    return "\n".join(header + [""] + lines)


def packet_loopback_section(note, station_id):
    """Feedback for the stations of a loopback attempt (autonomous line S1).

    note is the record the runner keeps when a loopback sends the work back:
    which station sent it, why, and the findings. Returns "" on a first
    attempt. Findings are reviewer or gate text, so they are sanitized and
    bounded before they reach a packet.
    """
    if not note:
        return ""
    lines = [f"## Loopback feedback (attempt {note['attempt']} of {note['max_attempts']})", ""]
    if station_id.startswith("reviewer"):
        lines.append(f"This is a re-review. The previous attempt was sent back by {note['from_station']} "
                     f"to {note['return_to']}. Judge the work as it is now, and check that each finding "
                     f"below is resolved; do not pass a finding that is still open.")
    else:
        lines.append(f"The previous attempt was sent back by {note['from_station']} to {note['return_to']}. "
                     f"Resolve every finding below. Keep what already passed; do not start over.")
    lines += ["", f"Reason: {_sanitize_control_chars(str(note.get('reason', '')))[:1000]}", ""]
    for finding in list(note.get("findings") or [])[:20]:
        text = _sanitize_control_chars(str(finding)).strip()[:1500]
        if text:
            lines.append("- " + text.replace("\n", "\n  "))
    return "\n".join(lines).rstrip()


def _packet_text(station_id, prompt, work_order, steps, learnings_section="", design_section="", rendered_evidence_section="", knowledge_section="", quality_charter_section="", anchor_section="", practices_section="",
                 skills_section="", run_context_section=""):
    """Assemble a station packet.

    S4 stable prefix layout (design route consumption work): stable material
    first (station prompt, design, learnings, knowledge, quality charter,
    anchors, rendered evidence), variable material last (work order,
    upstream steps), so providers can cache the shared prefix.

    Work order controlled strings are sanitized (F3 control character
    sanitization) and a rescoped intake outcome substitutes its rescoped
    description for downstream stations. Builder packets reference evidence
    images only when the work order declares them.
    """
    # Stable prefix: station prompt
    text = f"# Task packet: {station_id}\n\n## Station prompt\n\n{prompt}\n"

    # Stable sections, in composition order
    if design_section:
        text += f"\n{design_section}\n"
    if learnings_section:
        text += f"\n{learnings_section}\n"
    # Practice skills R6: prompt enforced practices resolved for this station
    if practices_section:
        text += f"\n{practices_section}\n"
    # Curated craft skills resolved for this station (anvil/skills.py)
    if skills_section:
        text += f"\n{skills_section}\n"
    if knowledge_section:
        text += f"\n{knowledge_section}\n"
    if quality_charter_section:
        text += f"\n{quality_charter_section}\n"
    if anchor_section:
        text += f"\n{anchor_section}\n"
    if rendered_evidence_section:
        text += f"\n{rendered_evidence_section}\n"

    # Variable: work order block (sanitized, rescope aware)
    description = work_order.description
    if work_order.intake_outcome.get("outcome") == "rescoped" and work_order.intake_outcome.get("rescoped_description"):
        description = work_order.intake_outcome["rescoped_description"]
    safe_title = _sanitize_control_chars(work_order.title)
    safe_description = _sanitize_control_chars(description)
    safe_source = _sanitize_control_chars(work_order.source)
    safe_risk_hints = ', '.join(_sanitize_control_chars(hint) for hint in work_order.risk_hints)
    upstream = "\n".join(f"- {s['station']}: {s['status']}" for s in steps) or "- (none)"
    text += (f"\n## Work order\n\n"
            f"- id: {work_order.id}\n- kind: {work_order.kind}\n- title: {safe_title}\n"
            f"- source: {safe_source}\n- description: {safe_description}\n"
            f"- risk_hints: {safe_risk_hints}\n- status: {work_order.status}\n\n")

    # Builder packets reference evidence images only when the work order declares them
    if station_id == "builder" and work_order.evidence_images:
        text += f"## Evidence images\n\n"
        for img_path in work_order.evidence_images:
            text += f"- {img_path}\n"
        text += "\n"

    text += f"## Upstream steps\n\n{upstream}\n"

    # Where the upstream work lives and which checks the project runs
    if run_context_section:
        text += f"\n{run_context_section}\n"

    # Reviewer stations have a specific output contract
    if station_id.startswith("reviewer"):
        text += (f"\n## Output contract\n\n"
                f"Your complete answer is exactly one review JSON object written to "
                f"runs/{work_order.id}/{station_id}.review.json. The free output transcript "
                f"stays as provenance and is never parsed for a review.\n")
    # Builder output contract (station artifact contract): the report is a
    # file the station writes; the checks gate validates it before reviewers.
    if station_id == "builder":
        text += (f"\n## Output contract\n\n"
                 f"Write your builder report as a file to runs/{work_order.id}/builder.output.md. "
                 f"The checks gate reads that file back from the run tree before any reviewer runs; "
                 f"your chat reply is never accepted as the report.\n")
        literals = list(getattr(work_order, "required_literals", []) or [])
        if literals:
            text += ("\nThe report must contain each of these literals in full, exactly as written "
                     "(no abbreviation, no ellipsis):\n\n")
            for lit in literals:
                text += f"- {_sanitize_control_chars(lit)}\n"
    return text

    # Reviewer stations have a specific output contract
    if station_id.startswith("reviewer"):
        text += (f"\n## Output contract\n\n"
                f"Your complete answer is exactly one review JSON object written to "
                f"runs/{work_order.id}/{station_id}.review.json. The free output transcript "
                f"stays as provenance and is never parsed for a review.\n")
    return text

def run_pipeline(project_dir, pipeline, work_order, registry=None, max_loopbacks=2,
                 executor=None, deploy_cfg=None, health_cfg=None, base_ref=None, resume=None):
    """Run the line. A run that raises leaves its state marked crashed
    (governed-delivery S1) instead of looking like it is still running."""
    try:
        return _run_pipeline(project_dir, pipeline, work_order, registry=registry, max_loopbacks=max_loopbacks,
                             executor=executor, deploy_cfg=deploy_cfg, health_cfg=health_cfg,
                             base_ref=base_ref, resume=resume)
    except BaseException as exc:
        wo_id = work_order.get("id") if isinstance(work_order, dict) else getattr(work_order, "id", None)
        if wo_id:
            try:
                mark_crashed(Path(project_dir) / "runs" / str(wo_id), exc)
            except Exception:
                pass
        raise


def _run_pipeline(project_dir, pipeline, work_order, registry=None, max_loopbacks=2,
                  executor=None, deploy_cfg=None, health_cfg=None, base_ref=None, resume=None):
    project = Path(project_dir)
    if isinstance(work_order, dict):
        work_order = WorkOrder.from_dict(work_order)

    # Loopback item 4: Validate WorkOrder file paths before run
    validate_work_order_paths(work_order, project)

    run_dir = project / "runs" / work_order.id
    envelopes_dir = run_dir / "envelopes"
    run_dir.mkdir(parents=True, exist_ok=True)
    envelopes_dir.mkdir(parents=True, exist_ok=True)
    previous_report = run_dir / "report.json"
    if previous_report.is_file():
        raw = previous_report.read_bytes()
        history = run_dir / "history"
        history.mkdir(exist_ok=True)
        (history / (hashlib.sha256(raw).hexdigest() + ".json")).write_bytes(raw)
    run_id = uuid.uuid4().hex
    steps = []
    verdict = ""
    loopbacks = 0
    order = pipeline.topological_order()
    execute_mode = executor is not None

    # Load price table for cost measurement
    config = load_anvil_config(project / "anvil.yaml")
    limits = efficiency_config(config)
    if getattr(executor, "kind", None) == "command":
        executor.limits = {}
        for key, name in (("max_runtime_turns", "ANVIL_MAX_RUNTIME_TURNS"),
                          ("tool_output_tokens", "ANVIL_TOOL_OUTPUT_TOKENS")):
            if key in limits:
                executor.limits[name] = limits[key]
    try:
        price_table = load_price_table(config)
    except ValueError as e:
        # Price table validation failed - log warning but continue
        price_table = {}
        print(f"Warning: {e}")
    # Run scoped reviews: only reviews produced during this run feed the
    # approver. Standing project reviews under reviews/<slug>/ are the project
    # record read by `anvil check`, never inputs to a run.
    run_reviews = []
    run_findings = []
    deployment_status = None
    verify_results = []
    health_result = {}  # Health verification result
    human_blocked = None  # decided at the triage step
    # Decision record: the approver entry is filled at the approver step from
    # the reviews counted there; the human gate entry is filled at the end
    # from the final verdict. Both rule sentences are generated from the
    # same values the code acted on.
    reviews_expected = [sid for sid in order if sid.startswith("reviewer")]
    decision_approver = None
    # Station artifact contract: why each reviewer was not counted, and the
    # artifact failure recorded on the failed step.
    uncounted_reasons = {}
    artifact_failures = {}
    # Who wrote the builder report: "station" (the artifact), "transcript"
    # (captured channel output saved by the runner) or None (builder not run).
    builder_report_source = None
    # Verified learnings are computed once per run: only non demoted entries
    # from brain/learnings.md, never inbox proposals (see anvil/brain.py).
    learnings_section = packet_learnings_section(project)
    # Practice skills R3: resolve the applicable practices deterministically
    # before any packet is built, from the work order surfaces, the pipeline
    # station list and the config language signal. Absent base: empty record.
    practice_entries = practices_by_id(project)
    practices_resolution = resolve_practices(project, work_order, order, config)
    # Curated craft skills: resolved the same way, from the catalog, by
    # station, surfaces, product type and work order kind.
    skill_entries = skills_by_id(project)
    skills_resolution = resolve_skills(project, work_order, order, config)

    # Load knowledge pack if provided in work order (S7, S8, S9)
    knowledge_pack = None
    pack_load_error = None
    if hasattr(work_order, 'knowledge_pack') and work_order.knowledge_pack:
        try:
            knowledge_pack = load_knowledge_pack(Path(work_order.knowledge_pack))
        except (FileNotFoundError, KnowledgeValidationError) as e:
            pack_load_error = str(e)
            # Pack loading failure stops the run at intake (S9)

    # Routing record: will be populated after intake
    routing_record = None

    # Evidence list: will be populated with screenshots from capture
    evidence_list = []

    # Snapshot base ref configuration for checks gate (S4)
    # Configuration is resolved from the base ref through git where a repo is
    # present, never from the working tree file (which may have been modified by
    # the builder). The working tree fallback is only for projects with no git repo.
    base_ref_config = resolve_base_ref_config(project, base_ref)

    # Snapshot initial files at run start for non-git changed file tracking
    # Directories where new files are always considered "changed" (spec S3)
    # These are work output directories that start empty in a fresh project
    work_output_dirs = {"tests", "reviews"}

    initial_files = set()
    for p in project.rglob("*"):
        if p.is_file() and ".git" not in p.parts and "runs" not in p.parts:
            try:
                rel_path = p.relative_to(project)
                initial_files.add(str(rel_path))
            except ValueError:
                pass

    # Track gate state
    gate_failed = False

    # Track builder delta for protected path checking (Loopback round 2)
    # Each builder attempt is judged on its own delta
    builder_attempt = 0
    builder_delta = set()
    builder_snapshot_before = None

    # Check for design system and prepare warnings
    warnings = []
    has_design_system = load_design_system(project) is not None
    interface_stations = {"builder", "writer", "media-producer", "brief-writer", "reviewer-design"}
    pipeline_has_interface_stations = any(sid in interface_stations for sid in order)

    if pipeline_has_interface_stations and not has_design_system:
        warnings.append("Missing design system: This pipeline includes interface-producing stations, "
                       "but the project has no design/DESIGN.md. Define the design system to enable "
                       "design review.")

    # S5: Track interface stations' measured tokens for report total
    # Interface stations (builder, writer, media-producer, brief-writer, reviewer-design)
    # use the design model from routing policy (currently claude-opus-5-5)
    astra_bound_stations = interface_stations  # Field name kept for continuity
    astra_measured_tokens_total = 0  # Field name kept for continuity
    # S2: Add warning for visual runs with no reference anchors
    if is_visual_run(work_order):
        ref_dir = project / "design" / "reference"
        anchors = getattr(work_order, "anchors", [])
        if not anchors and not ref_dir.exists():
            warnings.append("No reference anchors: This visual run has no reference anchors. "
                          "The review will proceed under the charter floor alone.")

    def write_envelope(station_id, next_station, artifact, status, extra=None):
        envelope = {"schema": "anvil/envelope@1", "from_station": station_id, "to_station": next_station,
                    "work_order_id": work_order.id, "artifact_path": artifact,
                    "status": status, "created_at": datetime.now(timezone.utc).isoformat()}
        if extra:
            envelope.update(extra)
        (envelopes_dir / f"{station_id}.envelope.json").write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")

    # S1: Identify stations subject to packet budgeting
    budgeted_stations = {"builder", "writer", "media-producer", "brief-writer", "reviewer-design"}

    def packet_step(station, station_id):
        """Generate packet, with budget measurement and trimming for budgeted stations.

        Returns (packet_path, measured_tokens, budget, action) tuple.
        For non-budgeted stations, measured/budget/action are 0/0/'none'.
        """
        prompt = station.prompt if station and station.prompt else f"Station {station_id}: carry out your role for this work order."
        if limits:
            prompt += EFFICIENCY_NOTE
        packet = run_dir / f"{station_id}.packet.md"
        design_section = packet_design_section(project, station_id) if not limits or is_visual_run(work_order) else ""

        # Sections every station packet can carry (each builder self-gates
        # to an empty string when the section does not apply)
        rendered_evidence_section = packet_rendered_evidence_section(project, work_order.id, station_id)
        # S3: Design knowledge section for design stations (computed once per run)
        knowledge_section = packet_knowledge_section(project, station_id, knowledge_pack)
        # Quality charter and anchor sections for visual runs
        quality_charter_section = packet_quality_charter_section(project, station_id, work_order)
        anchor_section = packet_anchor_section(project, station_id, work_order)
        practices_section = packet_practices_section(project, practices_resolution, station_id, practice_entries)
        skills_section = packet_skills_section(skills_resolution, station_id, skill_entries)
        run_context_section = packet_run_context_section(
            project, work_order, steps, station_id, (base_ref_config or {}).get("checks"))
        feedback_section = packet_loopback_section(loopback_note, station_id)
        if preview_url and station_id.startswith("reviewer"):
            feedback_section = (f"## Preview deployment\n\nThis attempt is deployed for review at "
                                f"{_sanitize_control_chars(preview_url)}\n\n" + feedback_section).strip()
        if station_id == "reviewer-tests" and tdd_red is False:
            feedback_section = ("## TDD red check\n\nThe project checks passed before the builder ran: the new "
                                "tests did not fail first. Verify that the tests exercise the new behavior and "
                                "would fail without the change.\n\n" + feedback_section).strip()
        if feedback_section:
            run_context_section = (run_context_section + "\n\n" + feedback_section).strip()

        # S1: Apply budget for interface stations
        if station_id in budgeted_stations or limits.get("max_packet_tokens"):
            packet_text, action, measured, budget = prepare_packet(
                project, station_id, prompt, work_order, steps,
                learnings_section, design_section,
                rendered_evidence_section, knowledge_section,
                quality_charter_section, anchor_section, practices_section,
                skills_section, run_context_section
            )
            packet.write_text(packet_text, encoding="utf-8")
            return packet, measured, budget, action

        # Non-budgeted stations: full packet with every applicable section
        packet_text = _packet_text(station_id, prompt, work_order, steps, learnings_section, design_section, rendered_evidence_section, knowledge_section, quality_charter_section, anchor_section, practices_section,
                                   skills_section, run_context_section)
        packet.write_text(packet_text, encoding="utf-8")
        measured = estimate_tokens(packet_text)
        return packet, measured, 0, "none"

    # Autonomous line: the line is walked with a position pointer so a
    # loopback can really send the work back (S1), and a resumed run can
    # re-enter after the human gate (S4).
    pos = 0
    tdd_red = None         # True/False once the red check ran, None when it did not
    loopback_note = None   # feedback handed to the stations of the next attempt
    approval = None        # human approval applied to this (resumed) run
    approval_original_verdict = None
    if resume:
        prev = resume.get("report") or {}
        gate_station = next((s for s in ("triage-human", "approver") if s in order), None)
        prev_steps = list(prev.get("steps") or [])
        cut = max((i for i, s in enumerate(prev_steps) if s.get("station") == gate_station), default=-1)
        if gate_station is None or cut < 0:
            raise ValueError("Cannot resume: the previous run never reached its approval gate")
        steps = prev_steps[:cut + 1]
        pos = order.index(gate_station) + 1
        run_id = prev.get("run_id") or run_id
        verdict = prev.get("verdict") or ""
        loopbacks = int(prev.get("loopbacks") or 0)
        decision_approver = (prev.get("decision") or {}).get("approver")
        human_blocked = bool(prev.get("human_required"))
        approval = resume.get("approval")
        if approval:
            approval_original_verdict = verdict
            verdict = "approved"
            human_blocked = False

    # Governed delivery S1/S2: state and events exist while the run is going.
    try:
        project_name = json.loads((project / "anvil.json").read_text(encoding="utf-8")).get("project")
    except (OSError, ValueError, AttributeError):
        project_name = None
    recorder = RunRecorder(run_dir, run_id, work_order.id, str(project_name or project.resolve().name),
                           pipeline.name, config)
    recorder.emitted = len(steps)  # a resumed run does not re-emit kept steps
    recorder.event("run.resumed" if resume else "run.started", work_order_kind=work_order.kind,
                   risk_hints=list(work_order.risk_hints or []), executed=execute_mode)
    # Governed delivery S6: one preview deployment per attempt, before review.
    preview_cfg = (deploy_cfg or {}).get("preview") if execute_mode and isinstance(deploy_cfg, dict) else None
    preview_at = None
    if isinstance(preview_cfg, dict) and preview_cfg.get("command") and "builder" in order:
        preview_at = next((sid for sid in order[order.index("builder") + 1:]
                           if sid.startswith("reviewer") or sid == "approver"), None)
    preview_done = False
    preview_url = None

    while pos < len(order):
        idx = pos
        station_id = order[idx]
        pos += 1
        recorder.flush(steps, current_station=station_id, verdict=verdict, loopbacks=loopbacks)
        if station_id == preview_at and not preview_done and not gate_failed and builder_attempt > 0:
            preview_done = True
            p_started = time.perf_counter()
            p_result = _line.run_preview(project, preview_cfg, work_order.id)
            p_out = run_dir / "preview.output.md"
            p_out.write_text(p_result["output"], encoding="utf-8")
            preview_url = p_result["url"] if p_result["ok"] else None
            p_step = {"station": "preview", "status": "completed" if p_result["ok"] else "failed",
                      "detail": p_result["detail"], "duration_ms": round((time.perf_counter() - p_started) * 1000, 3),
                      "cost": None, "artifacts": [str(p_out)], "configured_model": None, "executed_model": None,
                      "executor": None, "url": p_result["url"], "preview_name": p_result["name"]}
            if loopback_note:
                p_step["attempt"] = loopback_note["attempt"]
            steps.append(p_step)
            if not p_result["ok"]:
                warnings.append(f"Preview deployment failed: {p_result['detail']}. Review proceeds without a preview.")
        started = time.perf_counter()

        # S9: Pack loading failure stops the run at intake
        if station_id == "intake" and pack_load_error:
            steps.append({"station": station_id, "status": "failed", "elapsed": 0,
                        "model": "", "usage": {}, "cost": None,
                        "error": f"Knowledge pack loading failed: {pack_load_error}"})
            verdict = "failed"
            break

        station = None
        if registry is not None and station_id in registry:
            station = registry.get(station_id)
        kind = station.kind if station else ("deterministic" if station_id in {"intake", "approver", "triage-human"} else "agent")
        routed_out = (station_id.startswith("reviewer") and
                      (gate_failed or (routing_record and station_id not in routing_record.selected_reviewers)))
        calls_agent = (execute_mode and (station_id == "intake" or kind == "agent") and not routed_out
                       and not (station_id == "deployer" and deploy_cfg and deploy_cfg.get("command")))
        if calls_agent:
            reason = budget_reason(steps, limits)
            if reason:
                steps.append({"station": station_id, "status": "budget_exceeded", "detail": reason,
                              "duration_ms": 0, "cost": None, "artifacts": [], "executor": None})
                verdict = "budget_exceeded"
                break
            if getattr(executor, "kind", None) == "command":
                totals = summarize_steps(steps)
                if limits.get("max_run_tokens"):
                    executor.limits["ANVIL_MAX_STATION_TOKENS"] = max(1, limits["max_run_tokens"] - (totals["total_tokens"] or 0))
                if limits.get("max_agent_calls"):
                    executor.limits["ANVIL_MAX_ATTEMPTS"] = max(1, min(2, limits["max_agent_calls"] - totals["calls"]))
        # Model provenance: the configured label is a fact of configuration,
        # recorded in every mode. Executed fields stay null until a runtime
        # actually runs the station (agent-execution S8).
        configured_model = station.model if station is not None and station.model else default_model(station_id)
        # Apply routing model overrides if routing selected a specific model for this station
        if routing_record and station_id in routing_record.selected_models:
            # R10: routing speaks tier labels; resolve them at hand-off so the
            # report's configured_model for a routed station is concrete.
            configured_model = resolve_model(routing_record.selected_models[station_id])
        # Apply guided designation: guided design stations use the design model from routing policy
        # For the builder, only apply guided model when working on UI surface
        if station and station.guided:
            if station_id == "builder" and "ui" not in work_order.surfaces:
                pass  # Builder not on UI surface, keep configured model
            else:
                configured_model = get_design_model_from_routing()
        # R10: the model handed to the runtime is always concrete. The report
        # keeps the configured value (agent-execution S8 records the label for
        # unrouted stations); the hand-off never carries an unresolved label.
        handoff_model = resolve_model(configured_model)
        # R10 (round 4): resolution happens here, once, after every override
        # (registry, project config, routing, guided) has produced the final
        # label. When the step runs on a runtime that consumes the hand-off,
        # the recorded configured_model is that same concrete model, so the
        # record and the hand-off always agree. Packet mode and the http
        # executor (which runs its own endpoint model, ignoring the hand-off)
        # keep recording the configured label (agent-execution S8).
        if execute_mode and _consumes_model_handoff(executor):
            configured_model = handoff_model
        step_executor = None
        step_executed_model = None
        status = "completed"
        detail = ""
        artifact = ""
        extra_envelope = {}
        step_usage = None
        step_telemetry = {}
        deferred_verifier = None
        deferred_pre_deploy_gate = None
        deferred_health_step = None
        deferred_health_result = None
        next_station = order[idx + 1] if idx + 1 < len(order) else None
        # S1 & S5: Budget tracking fields
        measured_tokens = 0
        budget = 0
        budget_action = "none"
        terminal_outcome = False  # Track if intake outcome is terminal
        rewind = None  # (return_to, reason, from_station, findings) when this step loops back
        gate_result = {}
        # reviewer-design pre-step: build the scoped packet (wo-gh-21 S3,
        # contact sheet and provenance allowlist) plus the standard work
        # order block and the capability sections, then let the generic
        # paths below handle it. Execution follows the producer channel
        # rules (wo-gh-24) exactly like every other reviewer: the runner
        # never transcribes executor output into the review file.
        prebuilt_packet = None
        if calls_agent and station_id != "reviewer-design":
            try:
                prebuilt_packet = packet_step(station, station_id)
            except PacketBudgetError as exc:
                steps.append({"station": station_id, "status": "budget_exceeded", "detail": str(exc),
                              "duration_ms": 0, "cost": None, "artifacts": [], "executor": None})
                verdict = "budget_exceeded"
                break
        if station_id == "reviewer-design":
            rd_captures = []
            if run_dir.exists():
                rd_captures = list(run_dir.glob("capture-*.png"))
            rd_files_changed = []
            try:
                import subprocess
                rd_result = subprocess.run(
                    ["git", "diff", "--numstat", "HEAD"],
                    cwd=project, capture_output=True, text=True, timeout=5
                )
                if rd_result.returncode == 0:
                    for rd_line in rd_result.stdout.strip().split('\n'):
                        if rd_line:
                            rd_parts = rd_line.split('\t')
                            if len(rd_parts) >= 3:
                                rd_added = int(rd_parts[0]) if rd_parts[0] != '-' else 0
                                rd_removed = int(rd_parts[1]) if rd_parts[1] != '-' else 0
                                rd_files_changed.append({
                                    "file": rd_parts[2],
                                    "added": rd_added,
                                    "removed": rd_removed
                                })
            except Exception:
                pass  # Use empty files_changed if git fails
            scoped_text, contact_sheet_path = prepare_reviewer_design_step(
                project, work_order, rd_files_changed, rd_captures, registry=registry
            )
            wo_description = work_order.description
            if work_order.intake_outcome and work_order.intake_outcome.get("outcome") == "rescoped":
                wo_description = work_order.intake_outcome.get("rescoped_description", wo_description)
            scoped_text += (
                "\n## Work order\n\n"
                f"- id: {_sanitize_control_chars(work_order.id)}\n"
                f"- kind: {_sanitize_control_chars(work_order.kind)}\n"
                f"- title: {_sanitize_control_chars(work_order.title)}\n"
                f"- source: {_sanitize_control_chars(work_order.source)}\n"
                f"- description: {_sanitize_control_chars(wo_description)}\n"
                f"- risk_hints: {_sanitize_control_chars(', '.join(work_order.risk_hints))}\n"
                f"- status: {_sanitize_control_chars(work_order.status)}\n"
            )
            for extra_section in (
                packet_loopback_section(loopback_note, station_id),
                packet_practices_section(project, practices_resolution, station_id, practice_entries),
                packet_skills_section(skills_resolution, station_id, skill_entries),
                packet_rendered_evidence_section(project, work_order.id, station_id),
                packet_knowledge_section(project, station_id, knowledge_pack),
                packet_quality_charter_section(project, station_id, work_order),
                packet_anchor_section(project, station_id, work_order),
            ):
                if extra_section:
                    scoped_text += "\n" + extra_section + "\n"
            prebuilt_path = run_dir / f"{station_id}.packet.md"
            prebuilt_path.write_text(scoped_text, encoding="utf-8")
            prebuilt_measured = estimate_tokens(scoped_text)
            prebuilt_budget = get_station_budget(load_anvil_config(project / "anvil.yaml"), station_id)
            if limits.get("max_packet_tokens"):
                prebuilt_budget = min(prebuilt_budget, limits["max_packet_tokens"])
                if prebuilt_measured > prebuilt_budget and calls_agent:
                    steps.append({"station": station_id, "status": "budget_exceeded",
                                  "detail": f"Scoped design packet exceeds {prebuilt_budget} tokens",
                                  "duration_ms": 0, "cost": None, "artifacts": [str(prebuilt_path)], "executor": None})
                    verdict = "budget_exceeded"
                    break
            prebuilt_action = "sent" if prebuilt_measured <= prebuilt_budget else "trimmed"
            prebuilt_packet = (prebuilt_path, prebuilt_measured, prebuilt_budget, prebuilt_action)
        if station_id == "intake":
            # In execute mode, parse intake output for outcomes
            if execute_mode:
                packet, measured_tokens, budget, budget_action = prebuilt_packet if prebuilt_packet is not None else packet_step(station, station_id)
                packet_text = packet.read_text(encoding="utf-8")
                output_file = run_dir / f"{station_id}.output.md"
                try:
                    result = _call_executor(executor, packet_text, station_id, packet_path=packet,
                                              output_path=output_file, cwd=project,
                                              configured_model=handoff_model)
                    output_text = result.get("output", "") if isinstance(result, dict) else str(result)
                    usage = result.get("usage") if isinstance(result, dict) else None
                    step_telemetry = result.get("telemetry") or {} if isinstance(result, dict) else {}
                    executed_model_from_result = result.get("model") if isinstance(result, dict) else None
                    output_file.write_text(output_text, encoding="utf-8")
                    step_executor, step_executed_model = _executor_provenance(executor, output_text)
                    # Use model from result if available (runtime evidence)
                    if executed_model_from_result:
                        step_executed_model = executed_model_from_result
                    if isinstance(usage, dict):
                        step_usage = usage

                    # Parse intake output for intake_outcome, risk, surfaces
                    intake_data = {}
                    decoder = json.JSONDecoder()
                    for idx, ch in enumerate(output_text):
                        if ch != "{":
                            continue
                        try:
                            obj, _ = decoder.raw_decode(output_text[idx:])
                            if isinstance(obj, dict):
                                intake_data = obj
                                break
                        except json.JSONDecodeError:
                            continue

                    # Update work order with intake outcome
                    if "intake_outcome" in intake_data:
                        work_order.intake_outcome = intake_data["intake_outcome"]
                        outcome = work_order.intake_outcome.get("outcome")

                        # Update work order status based on outcome
                        if outcome == "rejected":
                            work_order.status = "rejected"
                            terminal_outcome = True
                        elif outcome == "waiting_info":
                            work_order.status = "waiting_info"
                            terminal_outcome = True

                    # Update risk and surfaces
                    if "risk" in intake_data:
                        work_order.risk = intake_data["risk"]
                    if "surfaces" in intake_data:
                        work_order.surfaces = intake_data["surfaces"]
                        # Practice skills R3: intake may set the surfaces;
                        # re-resolve before any downstream packet is built.
                        practices_resolution = resolve_practices(project, work_order, order, config)
                        skills_resolution = resolve_skills(project, work_order, order, config)

                    # Save work order
                    wo_dir = project / "work_orders"
                    wo_dir.mkdir(parents=True, exist_ok=True)
                    wo_file = wo_dir / f"{work_order.id}.json"
                    wo_file.write_text(json.dumps(work_order.to_dict(), indent=2) + "\n", encoding="utf-8")

                    # Run routing after intake to determine reviewer selection
                    # Get all reviewer stations from the pipeline
                    pipeline_reviewers = [sid for sid in order if sid.startswith("reviewer")]
                    if pipeline_reviewers:
                        routing_record = route_reviewers(work_order, pipeline_reviewers, project)
                        write_routing_record(run_dir, routing_record)
                        # Practice skills R4: the routing record carries the
                        # same practice resolution as report.json.
                        routing_path = run_dir / "routing.json"
                        routing_data = json.loads(routing_path.read_text(encoding="utf-8"))
                        routing_data["practices"] = practices_resolution
                        routing_data["skills"] = public_resolution(skills_resolution)
                        routing_path.write_text(json.dumps(routing_data, indent=2) + "\n", encoding="utf-8")
                        # Update reviews_expected to only include selected reviewers
                        reviews_expected = routing_record.selected_reviewers

                    status = "executed"
                    detail = f"Executed by {executor.name}; outcome: {work_order.intake_outcome.get('outcome', 'unknown')}"
                    artifact = str(output_file)
                except ExecutorError as exc:
                    status = "failed"
                    detail = f"Executor failed: {exc}"
                    artifact = str(packet)
                    step_executor, step_executed_model = _executor_provenance(executor)
                    step_usage = exc.result.get("usage")
                    step_telemetry = exc.result.get("telemetry") or {}
            else:
                detail = "Work order normalized"
                artifact = str(run_dir / "report.json")
        elif station_id == "approver":
            if run_reviews:
                verdict, verdict_rule, counted = aggregate_explained(
                    run_reviews,
                    expected=list(reviews_expected) if execute_mode else None,
                    uncounted=uncounted_reasons)
            else:
                verdict = "no_reviews"
                verdict_rule = ("No reviews were produced in this run, so the verdict is no_reviews; "
                                "standing project reviews are never counted.")
                counted = []
            # When execution was attempted, state the review counts
            # This is especially important when routing reduced the panel (S5)
            counted_len = len(counted)
            expected_len = len(reviews_expected)
            if execute_mode:
                if counted_len < expected_len:
                    verdict_rule += f" (Counted {counted_len} reviews, expected {expected_len}.)"
                elif routing_record and routing_record.routed_out:
                    # When routing reduced the panel, mention the expected count after routing
                    verdict_rule += f" (Expected {expected_len} reviews after routing.)"
            decision_approver = {"reviews_counted": counted,
                                 "reviews_expected": list(reviews_expected),
                                 "rule": verdict_rule}
            if execute_mode:
                have = {c["station"] for c in counted}
                decision_approver["reviews_uncounted"] = [
                    {"station": sid, "reason": uncounted_reasons.get(sid) or "no countable review artifact was produced"}
                    for sid in reviews_expected if sid not in have]
            detail = f"Approver verdict: {verdict}"
            artifact = str(run_dir / "report.json")
        elif station_id == "checks-gate":
            # Determine phase: pre-review or pre-deploy
            # Pre-review: right after builder
            # Pre-deploy: after approver/triage and before deployer/publisher
            builder_idx = order.index("builder") if "builder" in order else -1
            approver_idx = order.index("approver") if "approver" in order else -1
            if builder_idx >= 0 and idx > builder_idx and (approver_idx < 0 or idx < approver_idx):
                phase = "pre-review"
            else:
                phase = "pre-deploy"

            # Loopback round 2: Use builder delta for protected path checking
            # The gate judges only the builder station's changes for the current attempt
            if phase == "pre-review" and builder_delta:
                gate_changed_files = builder_delta
                gate_basis = "builder_delta"
                gate_attempt = builder_attempt
            else:
                # For pre-deploy or when builder delta not available, use cumulative changes
                gate_changed_files = _get_changed_files(project, initial_files, work_output_dirs, base_ref)
                gate_basis = "cumulative_changes" if phase == "pre-deploy" else "builder_delta"
                gate_attempt = builder_attempt if phase == "pre-review" else None

            # Run the gate
            gate_result = checks_gate(phase, base_ref_config, gate_changed_files, project, work_order.id,
                                     base_ref=base_ref, basis=gate_basis, attempt=gate_attempt)
            # Practice skills R6: gate enforced practices are listed by id and
            # topic in the pre-review output, never injected as prompt text.
            if phase == "pre-review":
                gate_listing = gate_practices_section(project, practices_resolution, practice_entries)
                if gate_listing:
                    gate_result["output"] = gate_result["output"].rstrip("\n") + "\n\n" + gate_listing + "\n"
            status = gate_result["status"]
            detail = gate_result["detail"]

            # Write gate output
            gate_output_file = run_dir / f"{station_id}.{phase}.output.md"
            gate_output_file.write_text(gate_result["output"], encoding="utf-8")
            artifact = str(gate_output_file)

            # Record gate results in the step
            extra_envelope = {
                "phase": gate_result["phase"],
                "commands": gate_result["commands"],
                "exit_codes": gate_result["exit_codes"],
                "protected_paths": gate_result["protected_paths"],
                "protected_path_verdict": gate_result["protected_path_verdict"],
                "protected_path_findings": gate_result["protected_path_findings"],
                "observed_additions": gate_result.get("observed_additions", []),
                "basis": gate_result.get("basis", ""),
                "gate_verdict": gate_result["gate_verdict"]
            }

            # Station artifact contract S2: deterministic artifact validation
            # after the builder and before any reviewer is spawned.
            if phase == "pre-review" and execute_mode and builder_report_source is not None:
                validation = validate_builder_report(run_dir / "builder.output.md",
                                                     getattr(work_order, "required_literals", []),
                                                     source=builder_report_source)
                extra_envelope["artifact_validation"] = {
                    "passed": validation["passed"], "report": validation["report"],
                    "observed": validation["observed"], "report_source": builder_report_source,
                    "required_literals": validation["required_literals"],
                    "missing_literals": validation["missing_literals"],
                    "findings": validation["findings"]}
                gate_output_file.write_text(gate_result["output"].rstrip("\n") + "\n\n" + validation["log"],
                                            encoding="utf-8")
                if not validation["passed"]:
                    gate_result["gate_verdict"] = "fail"
                    extra_envelope["gate_verdict"] = "fail"
                    status = "failed"
                    detail = f"{detail}; artifact validation failed: {' '.join(validation['findings'])}"
                    extra_envelope["output"] = validation["log"]

            # If gate failed and we're in pre-review phase, trigger loopback (S2)
            if gate_result["gate_verdict"] == "fail" and phase == "pre-review":
                gate_failed = True
                # Skip reviewers by marking that we should loop back
            # If gate failed in pre-deploy phase, block deployment (S5)
            elif gate_result["gate_verdict"] == "fail" and phase == "pre-deploy":
                verdict = "gate_failed"
                detail += "; deployment blocked by gate failure"
        elif station_id == "triage-human":
            hr = needs_human(work_order, verdict) if verdict else (human_gate(work_order) == "required")
            human_blocked = hr
            detail = f"Human review: {'required' if hr else 'not_required'}"
        elif station_id == "deployer" and execute_mode and deploy_cfg and deploy_cfg.get("command"):
            blocked = human_blocked if human_blocked is not None else needs_human(work_order, verdict)
            # Run pre-deploy checks gate (S5) - only if pre-review gate didn't fail
            deferred_pre_deploy_gate = None
            if verdict == "approved" and not blocked and not gate_failed:
                gate_started = time.perf_counter()
                # Use builder delta for pre-deploy as well (same basis as pre-review)
                if builder_delta:
                    gate_changed_files = builder_delta
                else:
                    gate_changed_files = _get_changed_files(project, initial_files, work_output_dirs, base_ref)
                gate_result = checks_gate("pre-deploy", base_ref_config, gate_changed_files, project, work_order.id,
                                         base_ref=base_ref, basis="builder_delta", attempt=builder_attempt)

                gate_output_file = run_dir / "checks-gate.pre-deploy.output.md"
                gate_output_file.write_text(gate_result["output"], encoding="utf-8")

                gate_step = {
                    "station": "checks-gate",
                    "status": gate_result["status"],
                    "detail": gate_result["detail"],
                    "duration_ms": round((time.perf_counter() - gate_started) * 1000, 3),
                    "cost": None,
                    "artifacts": [str(gate_output_file)],
                    "configured_model": None,
                    "executed_model": None,
                    "executor": None,
                    "phase": gate_result["phase"],
                    "commands": gate_result["commands"],
                    "exit_codes": gate_result["exit_codes"],
                    "protected_paths": gate_result["protected_paths"],
                    "protected_path_verdict": gate_result["protected_path_verdict"],
                    "protected_path_findings": gate_result["protected_path_findings"],
                    "observed_additions": gate_result.get("observed_additions", []),
                    "basis": gate_result.get("basis", ""),
                    "gate_verdict": gate_result["gate_verdict"]
                }
                deferred_pre_deploy_gate = gate_step

                # If pre-deploy gate fails, block deployment (S5)
                if gate_result["gate_verdict"] == "fail":
                    verdict = "gate_failed"
                    blocked = True

            if verdict == "approved" and not blocked and verdict != "gate_failed":
                timeout = int(deploy_cfg.get("timeout_seconds", 600))
                code, out = _run_shell(str(deploy_cfg.get("command", "")), project, work_order.id, timeout)
                out_file = run_dir / "deployer.output.md"
                out_file.write_text(out, encoding="utf-8")
                artifact = str(out_file)
                if code == 0:
                    status = "executed"
                    detail = "Deploy command executed"
                    deployment_status = "deployed_unverified"
                    # Deterministic verification gate, run by the spine before
                    # any later station (for example observer) is emitted.
                    vstarted = time.perf_counter()
                    v_failed = []
                    for vcmd in deploy_cfg.get("verify", []) or []:
                        vcode, vout = _run_shell(str(vcmd), project, work_order.id, timeout)
                        ok = vcode == 0
                        verify_results.append({"command": str(vcmd), "status": "pass" if ok else "fail",
                                               "exit_code": vcode, "output": vout[-2000:]})
                        if not ok:
                            v_failed.append(str(vcmd))
                    if v_failed:
                        findings_file = run_dir / "verify-findings.md"
                        lines = ["# Verify findings", "",
                                 f"Work order: {work_order.id}",
                                 f"Deployment status: {deployment_status}", "",
                                 "The deploy command ran, but verification failed. The deploy is NOT verified.", ""]
                        for r in verify_results:
                            if r["status"] == "fail":
                                lines.append(f"## Failing command: {r['command']}")
                                lines.append("")
                                lines.append("```")
                                lines.append(r["output"])
                                lines.append("```")
                                lines.append("")
                        findings_file.write_text("\n".join(lines), encoding="utf-8")
                    else:
                        deployment_status = "deployed_verified"
                    vstep = {"station": "verifier",
                             "status": "executed" if not v_failed else "failed",
                             "detail": ("Verification passed for all commands" if not v_failed
                                        else f"Verification failed: {', '.join(v_failed)}"),
                             "duration_ms": round((time.perf_counter() - vstarted) * 1000, 3),
                             "cost": None,
                             "configured_model": None, "executed_model": None, "executor": None,
                             "artifacts": [str(run_dir / "verify-findings.md")] if v_failed else []}
                    deferred_verifier = vstep

                    # Health verification after deploy (post-deploy-health S1, S7)
                    health_started = time.perf_counter()
                    deploy_time = datetime.now(timezone.utc).isoformat()
                    health_verification_result = verify_health(health_cfg, deploy_time)

                    # Store in outer scope variable
                    health_result = health_verification_result

                    # Update deployment status based on health outcome
                    if health_verification_result["outcome"] == "healthy":
                        deployment_status = "deployed_and_healthy"
                    elif health_verification_result["outcome"] == "unhealthy":
                        deployment_status = "deployed_and_unhealthy"
                        # Force human gate on unhealthy (post-deploy-health S2)
                        if health_verification_result.get("requires_human_gate"):
                            human_blocked = True
                    elif health_verification_result["outcome"] == "unknown":
                        # Unknown doesn't change deployment_status from deployed_verified
                        # but adds a warning (post-deploy-health S3)
                        if health_verification_result.get("warning"):
                            warnings.append(health_verification_result["warning"])

                    # Create health verification step
                    health_step = {
                        "station": "health-check",
                        "status": "completed",
                        "detail": f"Health verification: {health_verification_result['outcome']}",
                        "duration_ms": round((time.perf_counter() - health_started) * 1000, 3),
                        "cost": None,
                        "configured_model": None,
                        "executed_model": None,
                        "executor": None,
                        "artifacts": [],
                        "outcome": health_verification_result["outcome"]
                    }
                    # Store health result for the report
                    deferred_health_step = health_step
                    deferred_health_result = health_verification_result
                else:
                    status = "failed"
                    detail = f"Deploy command failed with exit code {code}"
                    deployment_status = "deploy_failed"
            else:
                packet, measured_tokens, budget, budget_action = prebuilt_packet if prebuilt_packet is not None else packet_step(station, station_id)
                status = "packet_ready"
                detail = f"Deploy skipped (verdict: {verdict or 'pending'}, human gate {'blocks' if blocked else 'open'}); packet written to {packet}"
                artifact = str(packet)
        elif kind in {"deterministic", "gate"}:
            detail = "Deterministic step executed"
        elif station_id == "deployer":
            # The deployer never runs through a generic executor: without a
            # deploy config and an approved, unblocked run it stays a packet.
            packet, measured_tokens, budget, budget_action = prebuilt_packet if prebuilt_packet is not None else packet_step(station, station_id)
            status = "packet_ready"
            detail = f"Packet written to {packet}"
            artifact = str(packet)
        elif (station_id == "publisher" and execute_mode
              and (verdict != "approved"
                   or (human_blocked if human_blocked is not None else needs_human(work_order, verdict)))):
            # Autonomous line S5: publishing is held exactly like deploying.
            # The publisher never runs on an unapproved run or behind a
            # closed human gate; it runs on resume after a recorded approval.
            packet, measured_tokens, budget, budget_action = prebuilt_packet if prebuilt_packet is not None else packet_step(station, station_id)
            status = "packet_ready"
            detail = (f"Publish held (verdict: {verdict or 'pending'}, human gate "
                      f"{'blocks' if verdict == 'approved' else 'not reached with an approved verdict'}); "
                      f"packet written to {packet}")
            artifact = str(packet)
        elif execute_mode:
            # Skip reviewers if gate failed (S2)
            if gate_failed and station_id.startswith("reviewer"):
                status = "skipped"
                detail = "Skipped due to gate failure"
                packet = prebuilt_packet[0] if prebuilt_packet is not None else packet_step(station, station_id)[0]
                artifact = str(packet)
            # Skip reviewers that were routed out
            elif station_id.startswith("reviewer") and routing_record and station_id not in routing_record.selected_reviewers:
                status = "routed_out"
                routed_reason = next((r["reason"] for r in routing_record.routed_out if r["reviewer"] == station_id), "Not in selected panel")
                detail = f"Routed out: {routed_reason}"
                packet = prebuilt_packet[0] if prebuilt_packet is not None else packet_step(station, station_id)[0]
                artifact = str(packet)
            else:
                # Capture builder delta (Loopback round 2)
                if station_id == "builder":
                    builder_attempt += 1
                    builder_snapshot_before = _snapshot_working_tree(project)

                packet, measured_tokens, budget, budget_action = prebuilt_packet if prebuilt_packet is not None else packet_step(station, station_id)
                packet_text = packet.read_text(encoding="utf-8")
                output_file = run_dir / f"{station_id}.output.md"

                # Station artifact contract: the builder report is a file the
                # station writes; a stale one never stands in for this attempt.
                if station_id == "builder":
                    try:
                        output_file.unlink()
                    except FileNotFoundError:
                        pass

                # For reviewer stations, remove any pre-existing review file before execution (S3)
                if station_id.startswith("reviewer"):
                    review_file = run_dir / f"{station_id}.review.json"
                    try:
                        review_file.unlink()
                    except FileNotFoundError:
                        pass

                try:
                    result = _call_executor(executor, packet_text, station_id, packet_path=packet,
                                              output_path=output_file, cwd=project,
                                              configured_model=handoff_model)
                    output_text = result.get("output", "") if isinstance(result, dict) else str(result)
                    usage = result.get("usage") if isinstance(result, dict) else None
                    step_telemetry = result.get("telemetry") or {} if isinstance(result, dict) else {}
                    executed_model_from_result = result.get("model") if isinstance(result, dict) else None
                    if station_id == "builder" and output_file.is_file():
                        # The station wrote its report artifact: that file is
                        # the result. Captured channel output differing from it
                        # is kept beside it as a transcript, never written over it.
                        builder_report_source = "station"
                        try:
                            on_disk = output_file.read_text(encoding="utf-8")
                        except (OSError, UnicodeDecodeError):
                            on_disk = None
                        if output_text.strip() and output_text != on_disk:
                            (run_dir / f"{station_id}.transcript.md").write_text(output_text, encoding="utf-8")
                    else:
                        if station_id == "builder":
                            builder_report_source = "transcript"
                        output_file.write_text(output_text, encoding="utf-8")
                    status = "executed"
                    detail = f"Executed by {executor.name}; output written to {output_file}"
                    artifact = str(output_file)
                    step_executor, step_executed_model = _executor_provenance(executor, output_text)
                    # Use model from result if available (runtime evidence)
                    if executed_model_from_result:
                        step_executed_model = executed_model_from_result
                    extra_envelope = {}
                    if isinstance(usage, dict):
                        step_usage = usage
                        extra_envelope["usage"] = usage
                        tokens = {k: usage[k] for k in usage if "token" in k}
                        if tokens:
                            extra_envelope["tokens"] = tokens
                    if station_id.startswith("reviewer"):
                        # S2: Read review from the file the reviewer wrote, never from stdout
                        review_file = run_dir / f"{station_id}.review.json"
                        review = None
                        review_file_text = None

                        # Check if correction metadata exists
                        correction_meta_path = run_dir / f"{station_id}.correction.json"
                        if correction_meta_path.exists():
                            extra_envelope["correction_used"] = True

                        artifact_state, review_file_text = review_artifact_state(review_file)
                        if artifact_state == "present":
                            try:
                                review = parse_review(review_file_text, station_id)
                            except Exception:
                                review = None

                        # Special handling for reviewer-design when no design system exists
                        if station_id == "reviewer-design" and not has_design_system:
                            review = Review(
                                station="reviewer-design",
                                verdict="changes_requested",
                                findings=["No design system exists for this project. The project must define "
                                         "design/DESIGN.md and design/tokens.json before interface output can be "
                                         "reviewed against design standards."]
                            )
                        elif review is not None:
                            # Valid review parsed from file
                            pass
                        elif review_file.exists():
                            # File exists but failed to parse (S3)
                            extra_envelope["review_parse_failed"] = True
                            detail += "; review file exists but did not parse as valid review JSON"
                        else:
                            # File does not exist (S3)
                            extra_envelope["review_file_missing"] = True
                            detail += "; review file was not written by the station"

                        if review is None:
                            # Station artifact contract S1: no countable artifact
                            # fails the station fast, with the reason on record.
                            state_word = {"present": "did not parse as a valid review",
                                          "empty": "empty",
                                          "unreadable": "unreadable",
                                          "missing": "missing"}.get(artifact_state, artifact_state)
                            if artifact_state == "present":
                                artifact_state = "unparseable"
                            reason = f"review artifact {review_file.name} {state_word}"
                            if getattr(executor, "writes_artifacts", True):
                                status = "failed"
                                detail = (f"Station artifact check failed: expected review artifact "
                                          f"{review_file} is {state_word}; captured channel output is "
                                          f"diagnostic only and is never read as the review. {detail}")
                            else:
                                # A text-only channel cannot write the artifact;
                                # the step ran, but nothing is counted from it.
                                detail = (f"{detail}; expected review artifact {review_file} is "
                                          f"{state_word} and this channel cannot write artifacts, so no "
                                          f"review is counted")
                            artifact_failures[station_id] = {"expected_artifact": str(review_file),
                                                             "artifact_state": artifact_state,
                                                             "reason": reason}
                            uncounted_reasons[station_id] = f"failed: {reason}"

                        if review is not None:
                            run_reviews.append(review)
                            run_findings.extend(review.findings)
                            extra_envelope["review"] = review.to_dict()

                    # Track builder delta for protected path checking (Loopback round 2)
                    if station_id == "builder" and builder_snapshot_before is not None:
                        # Capture working tree state after builder execution
                        builder_snapshot_after = _snapshot_working_tree(project)
                        # Compute delta: files added, modified, or deleted by this builder attempt
                        builder_delta = _compute_delta(builder_snapshot_before, builder_snapshot_after)
                except ExecutorError as exc:
                    status = "failed"
                    detail = f"Executor failed: {exc}"
                    artifact = str(packet)
                    step_executor, step_executed_model = _executor_provenance(executor)
                    step_usage = exc.result.get("usage")
                    step_telemetry = exc.result.get("telemetry") or {}
                    extra_envelope = {"error": str(exc)}
                    if station_id.startswith("reviewer"):
                        # Station artifact contract S1/S3: a failed reviewer is
                        # recorded with its expected artifact and never counted
                        # silently; the approver names it.
                        review_file = run_dir / f"{station_id}.review.json"
                        artifact_state, _ = review_artifact_state(review_file)
                        reason = f"station failed ({exc})"
                        if artifact_state == "present":
                            reason += f"; {review_file.name} was written but is not counted from a failed station"
                        artifact_failures[station_id] = {"expected_artifact": str(review_file),
                                                         "artifact_state": artifact_state,
                                                         "reason": reason}
                        uncounted_reasons[station_id] = f"failed: {reason}"
                    elif station_id == "builder":
                        builder_report_source = "station" if output_file.is_file() else "none"
        else:
            packet, measured_tokens, budget, budget_action = prebuilt_packet if prebuilt_packet is not None else packet_step(station, station_id)
            status = "packet_ready"
            detail = f"Packet written to {packet}"
            artifact = str(packet)
        duration_ms = round((time.perf_counter() - started) * 1000, 3)
        # S1 & S5: Build step with budget fields
        step = {"station": station_id, "status": status, "detail": detail, "duration_ms": duration_ms,
                "cost": None, "artifacts": [artifact] if artifact else [],
                "configured_model": configured_model, "executed_model": step_executed_model,
                "executor": step_executor,
                "measured_tokens": measured_tokens, "budget": budget, "budget_action": budget_action}
        if step_usage is not None:
            step["usage"] = step_usage
            # Calculate cost from usage and price table
            # Use executed model if available, otherwise configured model
            cost_model = step_executed_model or configured_model
            cost_record = calculate_cost(step_usage, cost_model, price_table)
            step["cost"] = cost_record["cost"]
            # Optionally include detailed cost record
            if not cost_record["measured"]:
                step["cost_record"] = {
                    "measured": cost_record["measured"],
                    "reason": cost_record["reason"]
                }
        if step_telemetry:
            step["attempts"] = step_telemetry.get("attempts") or []
            step["usage_complete"] = bool(step_telemetry.get("complete"))
        if (station_id == "test-writer" and status == "executed" and "builder" in order[idx:]
                and (base_ref_config or {}).get("checks")):
            # Autonomous line S8: red before green is evidence, not a claim.
            # The project checks run once before the builder; they are
            # expected to fail because the new tests have nothing to pass on.
            red_codes = [_run_shell(str(cmd), project, work_order.id, 300, scrub=True)[0]
                         for cmd in base_ref_config["checks"]]
            red = any(code != 0 for code in red_codes)
            step["red_check"] = {"commands": [str(c) for c in base_ref_config["checks"]],
                                 "exit_codes": red_codes, "red": red}
            tdd_red = red
            if not red:
                warnings.append("TDD red check: the project checks passed before the builder ran, so the "
                                "new tests did not fail first. reviewer-tests is told to verify that the "
                                "tests exercise the new behavior.")
        if loopback_note:
            step["attempt"] = loopback_note["attempt"]
            if station_id == loopback_note["return_to"]:
                step["feedback"] = {"from_station": loopback_note["from_station"],
                                    "reason": loopback_note["reason"],
                                    "findings": list(loopback_note["findings"])[:20]}
        if station_id in artifact_failures:
            step["expected_artifact"] = artifact_failures[station_id]["expected_artifact"]
            step["artifact_state"] = artifact_failures[station_id]["artifact_state"]
        # Add extra fields from checks-gate to the step itself
        if station_id == "checks-gate" and extra_envelope:
            for key in ["phase", "commands", "exit_codes", "protected_paths",
                       "protected_path_verdict", "protected_path_findings", "gate_verdict",
                       "artifact_validation"]:
                if key in extra_envelope:
                    step[key] = extra_envelope[key]
        steps.append(step)

        # S5: Track interface stations' measured tokens for report total
        if station_id in astra_bound_stations and measured_tokens > 0:
            astra_measured_tokens_total += measured_tokens

        env_extra = dict(extra_envelope)
        env_extra["configured_model"] = configured_model
        if step_executor is not None:
            env_extra["executor"] = step_executor
            env_extra["executed_model"] = step_executed_model
        write_envelope(station_id, next_station, artifact or str(run_dir / "report.json"), status, env_extra)

        # Capture screenshots after builder completes successfully (S1)
        if station_id == "builder" and status == "executed" and execute_mode:
            evidence_dir = run_dir / "evidence"
            capture_result = capture_breakpoints(project, evidence_dir)

            # Record capture result in the report
            if capture_result["success"]:
                # Store capture metadata for later use in report
                for capture in capture_result["captures"]:
                    # Add to evidence list with relative path
                    rel_path = Path(capture["path"]).relative_to(project)
                    evidence_list.append({
                        "type": "screenshot",
                        "breakpoint": capture["breakpoint"],
                        "path": str(rel_path),
                        "width": capture["width"],
                        "height": capture["height"]
                    })
            else:
                # Record failure reason for reviewer-design
                # This will be picked up when building reviewer-design's packet
                capture_failure_file = run_dir / "capture_failure.txt"
                capture_failure_file.write_text(capture_result["error"], encoding="utf-8")

        # Stop pipeline if intake outcome is terminal (rejected or waiting_info)
        if station_id == "intake" and terminal_outcome:
            break

        # Insert pre-deploy gate before deployer (S5)
        if deferred_pre_deploy_gate is not None:
            steps.append(deferred_pre_deploy_gate)
            write_envelope("checks-gate", station_id,
                           deferred_pre_deploy_gate["artifacts"][0] if deferred_pre_deploy_gate["artifacts"] else str(run_dir / "report.json"),
                           deferred_pre_deploy_gate["status"],
                           {k: v for k, v in deferred_pre_deploy_gate.items()
                            if k in ["phase", "commands", "exit_codes", "protected_paths",
                                   "protected_path_verdict", "protected_path_findings", "gate_verdict"]})
        if deferred_verifier is not None:
            steps.append(deferred_verifier)
            write_envelope("verifier", next_station,
                           deferred_verifier["artifacts"][0] if deferred_verifier["artifacts"] else str(run_dir / "report.json"),
                           deferred_verifier["status"], {"configured_model": None})
        if deferred_health_step is not None:
            steps.append(deferred_health_step)
            write_envelope("health-check", next_station,
                           str(run_dir / "report.json"),
                           deferred_health_step["status"], {"configured_model": None})
        # Loopback after checks-gate failure (S2)
        if station_id == "checks-gate" and gate_failed and loopbacks < max_loopbacks:
            loopbacks += 1
            return_to = "builder"
            reason = f"Gate failure: {'; '.join(extra_envelope.get('protected_path_findings', [])[:3])}" if extra_envelope.get('protected_path_findings') else "Gate checks failed"
            av = extra_envelope.get("artifact_validation") or {}
            if av and not av.get("passed"):
                reason += f"; artifact validation: {' '.join(av.get('findings', [])[:3])}"
            steps.append({"station": "loopback", "status": "loopback", "return_to": return_to,
                          "detail": f"Loopback to {return_to}: {reason}", "reason": reason,
                          "duration_ms": 0.0, "cost": None, "artifacts": [],
                          "configured_model": None, "executed_model": None, "executor": None,
                          "feedback": extra_envelope.get("output", ""),
                          "from_station": "checks-gate"})
            rewind = (return_to, reason, "checks-gate",
                      [gate_result.get("output", "")[-3000:]] if gate_result.get("output") else [])
        # Loopback right after approver when aggregation fails
        elif station_id == "approver" and verdict in {"rejected", "changes_requested"} and loopbacks < max_loopbacks:
            loopbacks += 1
            # Spec failures return to spec-writer, implementation failures to builder.
            return_to = "spec-writer" if any("spec" in str(f).lower() and "missing" in str(f).lower() for f in run_findings) else "builder"
            reason = "; ".join(run_findings) if run_findings else f"Approver verdict: {verdict}"
            steps.append({"station": station_id, "status": "loopback", "return_to": return_to,
                          "detail": f"Loopback to {return_to}: {reason}", "reason": reason,
                          "duration_ms": 0.0, "cost": None, "artifacts": [],
                          "configured_model": None, "executed_model": None, "executor": None})
            rewind = (return_to, reason, "approver", list(run_findings))
        # Autonomous line S1: a loopback really sends the work back. The
        # line re-enters at the return station with the findings in the
        # packets of the next attempt; the attempt being replaced is archived.
        if rewind is not None and execute_mode:
            target = rewind[0] if rewind[0] in order[:idx] else ("builder" if "builder" in order[:idx] else None)
            # Another attempt is started only when the run thresholds leave
            # room for it; otherwise the verdict stands and the step says why.
            if target is not None:
                held = budget_reason(steps, limits)
                if not held and limits.get("max_agent_calls"):
                    needed = 0
                    for sid in order[order.index(target):idx]:
                        st = registry.get(sid) if registry is not None and sid in registry else None
                        is_agent = (st.kind == "agent") if st else sid not in {"intake", "approver", "triage-human"}
                        if is_agent and not (sid.startswith("reviewer") and routing_record
                                             and sid not in routing_record.selected_reviewers):
                            needed += 1
                    if summarize_steps(steps)["calls"] + needed > limits["max_agent_calls"]:
                        held = "Agent call limit leaves no room for another attempt"
                if held:
                    steps[-1]["detail"] += f"; not re-executed: {held}"
                    steps[-1]["not_reexecuted"] = held
                    target = None
            if target is not None:
                attempt_dir = run_dir / "attempts" / str(loopbacks)
                attempt_dir.mkdir(parents=True, exist_ok=True)
                for pattern in ("*.output.md", "*.review.json"):
                    for old in run_dir.glob(pattern):
                        (attempt_dir / old.name).write_bytes(old.read_bytes())
                steps[-1]["return_to"] = target
                steps[-1]["attempt_archive"] = str(attempt_dir)
                loopback_note = {"attempt": loopbacks + 1, "max_attempts": max_loopbacks + 1,
                                 "from_station": rewind[2], "return_to": target,
                                 "reason": rewind[1], "findings": rewind[3]}
                pos = order.index(target)
                gate_failed = False
                run_reviews, run_findings = [], []
                uncounted_reasons, artifact_failures = {}, {}
                verdict = ""
                decision_approver = None
                preview_done = False
    recorder.flush(steps, verdict=verdict, loopbacks=loopbacks)
    if not verdict:
        verdict = "packet_ready"
    if decision_approver is None:
        # A pipeline without an approver step aggregates nothing; say so
        # instead of inventing a verdict explanation.
        decision_approver = {"reviews_counted": [{"station": r.station, "verdict": r.verdict} for r in run_reviews],
                             "reviews_expected": list(reviews_expected),
                             "rule": "The pipeline has no approver step, so no reviews were aggregated into a verdict."}
    if verdict in {"approved", "rejected", "changes_requested", "no_reviews", "human_required"}:
        human_required, human_rule, hints_matched = needs_human_explained(work_order, verdict)
    else:
        # No approver verdict exists, so the gate looks at risk hints only,
        # exactly as human_gate does.
        hints_matched = matched_risk_hints(work_order)
        human_required = bool(hints_matched)
        if hints_matched:
            quoted = ", ".join(f"'{h}'" for h in hints_matched)
            noun = "risk hint" if len(hints_matched) == 1 else "risk hints"
            human_rule = (f"No approver verdict was produced by this pipeline, and the work order carries "
                          f"the {noun} {quoted}, so a human is required.")
        else:
            scanned = ", ".join(RISK_SCAN_ORDER)
            human_rule = (f"No approver verdict was produced by this pipeline and no risk hints matched "
                          f"(scanned: {scanned}), so no human is required.")

    # Override human gate if health is unhealthy (post-deploy-health S2)
    if health_result.get("outcome") == "unhealthy" and health_result.get("requires_human_gate"):
        human_required = True
        health_reason = health_result.get("health_reason", "Health verification failed")
        if human_rule and not human_required:
            # Was not required, now forced by health
            human_rule = f"{human_rule} However, health verification found the deployment unhealthy ({health_reason}), forcing human review."
        elif "unhealthy" not in human_rule:
            # Already required, add health reason
            human_rule = f"{human_rule} Additionally, health verification found the deployment unhealthy ({health_reason})."

    approval_record = None
    if approval:
        # Autonomous line S4: a recorded human approval opens the gate for
        # this run only, and the record says what the approver had decided.
        approval_record = {"approved_by": approval.get("approved_by"), "approved_at": approval.get("approved_at"),
                           "note": approval.get("note", ""), "override": bool(approval.get("override")),
                           "approver_verdict": approval_original_verdict,
                           "identity": approval.get("identity"),
                           "policy_checked": approval.get("policy_checked", [])}
        if not (health_result.get("outcome") == "unhealthy" and health_result.get("requires_human_gate")):
            human_required = False
        human_rule = (f"A human approved this run: {approval_record['approved_by']} at "
                      f"{approval_record['approved_at']} (approver verdict was {approval_original_verdict}"
                      f"{', recorded as an override' if approval_record['override'] else ''}). {human_rule}")

    decision = {"approver": decision_approver,
                "human_gate": {"required": human_required, "rule": human_rule, "hints_matched": hints_matched}}
    if approval_record:
        decision["human_gate"]["approval"] = approval_record
        if approval_record["override"] and verdict == "approved":
            # The human opened the gate; the line's own verdict stays on record.
            verdict = approval_original_verdict
    if resume:
        decision["resumed"] = {"from_station": order[order.index(gate_station) + 1] if order.index(gate_station) + 1 < len(order) else None,
                               "at": datetime.now(timezone.utc).isoformat()}
    report = RunReport(work_order_id=work_order.id, pipeline=pipeline.name, steps=steps, verdict=verdict,
                       title=work_order.title, kind=work_order.kind,
                       human_required=human_required, max_loopbacks=max_loopbacks, loopbacks=loopbacks,
                       deployment_status=deployment_status, verify_results=verify_results,
                       risk_hints=list(work_order.risk_hints or []), decision=decision, warnings=warnings,
                       astra_measured_tokens_total=astra_measured_tokens_total,
                       base_ref=base_ref, evidence=evidence_list, health=health_result,
                       practices=practices_resolution,
                       skills=public_resolution(skills_resolution),
                       efficiency={"limits": limits, "stopped": verdict == "budget_exceeded"},
                       run_id=run_id)
    (run_dir / "report.json").write_text(json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8")
    recorder.finish(steps, report.to_dict())
    # Swimlane
    lines = ["# Swimlane", ""]

    # Add intake outcome summary if present
    if work_order.intake_outcome:
        outcome = work_order.intake_outcome.get("outcome")
        if outcome == "rejected":
            lines.append("**Status**: rejected at intake")
            lines.append("")
        elif outcome == "waiting_info":
            lines.append("**Status**: waiting for information")
            lines.append("")

    # Add routing summary if present
    if routing_record:
        lines.append(routing_swimlane_summary(routing_record))
        lines.append("")

    # Add cost summary
    report_dict = report.to_dict()
    cost_section = report_dict["cost"]
    total_steps = cost_section["measured_steps"] + cost_section["unmeasured_steps"]
    if cost_section["measured_steps"] > 0:
        lines.append(f"**Cost**: ${cost_section['total']:.4f} ({cost_section['measured_steps']} of {total_steps} steps measured)")
    else:
        lines.append(f"**Cost**: No measured steps ({total_steps} executed steps)")
    lines.append("")
    lines.append("| Station | Status | Duration ms | Artifacts | Cost |")
    lines.append("|---|---|---|---|---|")
    for s in steps:
        arts = ", ".join(s.get("artifacts", [])) or "-"
        cost = s.get("cost")
        lines.append(f"| {s['station']} | {s['status']} | {s.get('duration_ms', 0)} | {arts} | {cost if cost is not None else 'null'} |")
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append(f"- Approver: {decision['approver']['rule']}")
    lines.append(f"- Human gate: {decision['human_gate']['rule']}")
    if deployment_status is not None:
        lines.append("")
        lines.append(f"Deployment: {deployment_status}")
    if verify_results:
        lines.append("")
        lines.append("Verification:")
        for r in verify_results:
            lines.append(f"- {r['status']}: {r['command']}")
    if health_result:
        lines.append("")
        lines.append(f"Health: {health_result.get('outcome', 'unknown')}")
        if health_result.get('health_reason'):
            lines.append(f"- Reason: {health_result['health_reason']}")
    (run_dir / "swimlane.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Render report.md
    report_lines = ["# Run Report", "", f"Work Order: {work_order.id}", f"Title: {work_order.title}",
                    f"Kind: {work_order.kind}", f"Status: {work_order.status}", ""]

    # Include intake outcome if present
    if work_order.intake_outcome:
        outcome = work_order.intake_outcome.get("outcome", "unknown")
        report_lines.append("## Intake Outcome")
        report_lines.append("")
        report_lines.append(f"Outcome: {outcome}")
        report_lines.append("")

        if outcome == "rejected":
            report_lines.append("This work order was rejected at intake.")
            report_lines.append("")
            if "reasons" in work_order.intake_outcome:
                report_lines.append("### Reasons")
                report_lines.append("")
                for reason in work_order.intake_outcome["reasons"]:
                    report_lines.append(f"- {_escape_markdown(reason)}")
                report_lines.append("")
        elif outcome == "waiting_info":
            report_lines.append("This work order is waiting for additional information.")
            report_lines.append("")
            if "questions" in work_order.intake_outcome:
                report_lines.append("### Questions")
                report_lines.append("")
                for question in work_order.intake_outcome["questions"]:
                    report_lines.append(f"- {_escape_markdown(question)}")
                report_lines.append("")
        elif outcome == "rescoped":
            report_lines.append("This work order was rescoped at intake.")
            report_lines.append("")
            if "rescoped_description" in work_order.intake_outcome:
                report_lines.append("### Rescoped Description")
                report_lines.append("")
                report_lines.append("```")
                report_lines.append(work_order.intake_outcome["rescoped_description"])
                report_lines.append("```")
                report_lines.append("")
            if "reasons" in work_order.intake_outcome:
                report_lines.append("### Rescope Reasons")
                report_lines.append("")
                for reason in work_order.intake_outcome["reasons"]:
                    report_lines.append(f"- {_escape_markdown(reason)}")
                report_lines.append("")

    # Include risk and surfaces
    if work_order.risk:
        report_lines.append(f"Risk: {work_order.risk}")
        report_lines.append("")
    if work_order.surfaces:
        report_lines.append(f"Surfaces: {', '.join(work_order.surfaces)}")
        report_lines.append("")

    # Include routing section if present
    if routing_record:
        report_lines.append(render_routing_section(routing_record))

    # S7: Record operator-supplied knowledge pack
    if knowledge_pack:
        report_lines.append("## Operator Supplied Inputs")
        report_lines.append("")
        report_lines.append("**Knowledge Pack**:")
        report_lines.append(f"- Name: {knowledge_pack['name']}")
        report_lines.append(f"- Product types covered: {', '.join(knowledge_pack['product_types'])}")
        report_lines.append(f"- Data files: {', '.join(knowledge_pack['files'])}")
        report_lines.append("")

    # Include verdict
    report_lines.append(f"## Verdict")
    report_lines.append("")
    report_lines.append(f"Verdict: {verdict}")
    report_lines.append("")

    # Include approver decision rule if present
    if decision and "approver" in decision and "rule" in decision["approver"]:
        report_lines.append(decision["approver"]["rule"])
        report_lines.append("")

    # Include steps
    report_lines.append("## Steps")
    report_lines.append("")
    for s in steps:
        report_lines.append(f"- {s['station']}: {s['status']}")
    report_lines.append("")

    (run_dir / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    if execute_mode:
        from .statuspage import generate_status_page
        try:
            generate_status_page(project)
        except OSError as exc:
            report.warnings.append(f"Status page refresh failed: {exc}")
            (run_dir / "report.json").write_text(json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8")
    return report

run = run_pipeline
