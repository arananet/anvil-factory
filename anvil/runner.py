import json, os, shlex, struct, subprocess, time, zlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from .model import WorkOrder, Review
from .config import default_model, load_anvil_config, CHARS_PER_TOKEN
from .brain import packet_learnings_section
from .design import packet_design_section, load_design_system
from .gates import human_gate
from .approver import aggregate, needs_human, aggregate_explained, needs_human_explained, matched_risk_hints, RISK_SCAN_ORDER
from .executor import ExecutorError

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

class DeclaredEvidenceMissing(Exception):
    """Raised when a declared evidence image is missing or escapes the project tree"""
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
                                 prompt=None, declared_evidence_paths=None):
    """S3: Build a fresh, scoped packet for reviewer-design.

    Loopback item 2: Located in anvil/runner.py (runner module), not anvil/stations.
    The runner orchestrates packet assembly; stations consume packets.

    Loopback gate round 3, finding 2: The caller resolves the station prompt through
    the station registry and passes it in. This function never imports from .stations
    at any scope.

    Contains: station prompt, design section, spec, diff summary, contact sheet.
    Does NOT contain: builder transcript, other station outputs, whole file contents.

    Loopback item 3: Tags content with provenance for allowlist verification.

    R3: Evidence section lists contact sheet path and each declared evidence image path.

    Returns: (packet_text, allowlist) tuple where allowlist is the list of allowed
    source paths for verification.
    """
    project = Path(project)
    declared_evidence_paths = declared_evidence_paths or []

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

    # R3: Evidence section lists contact sheet and each declared evidence image path
    contact_sheet_ref = ""
    if contact_sheet_path or declared_evidence_paths:
        contact_sheet_ref = "\n## Evidence\n\n"
        if contact_sheet_path:
            contact_sheet_ref += f"Contact sheet: {contact_sheet_path}\n"
        if declared_evidence_paths:
            contact_sheet_ref += "\nDeclared evidence images:\n"
            for img_path in declared_evidence_paths:
                contact_sheet_ref += f"- {img_path}\n"

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

    R2: Before execution, validates every declared evidence image exists and resolves inside
    project tree. Missing or escaping images fail with DeclaredEvidenceMissing.

    R1: Assembles contact sheet from declared PNG images plus run directory captures.

    Returns (packet_text, contact_sheet_path) tuple.
    """
    from .config import load_anvil_config, get_contact_sheet_max_width

    project = Path(project)
    run_dir = project / "runs" / work_order.id
    project_resolved = project.resolve()

    # R2: Validate declared evidence images before execution
    declared_evidence_paths = []
    if work_order.evidence_images:
        for img_path in work_order.evidence_images:
            full_path = (project / img_path).resolve()
            # Check path resolves inside project tree
            try:
                full_path.relative_to(project_resolved)
            except ValueError:
                raise DeclaredEvidenceMissing(
                    f"Declared evidence image escapes project tree: {img_path} "
                    f"resolves to {full_path}, outside {project_resolved}"
                )
            # Check file exists
            if not full_path.exists():
                raise DeclaredEvidenceMissing(
                    f"Declared evidence image does not exist: {img_path}"
                )
            declared_evidence_paths.append(full_path)

    # R1: Assemble contact sheet from declared PNG images plus run directory captures
    # Declared images join in declaration order, only .png files
    capture_set = []
    for declared_path in declared_evidence_paths:
        if declared_path.suffix.lower() == '.png':
            capture_set.append(declared_path)

    # Add run directory captures
    capture_set.extend(captures)

    # S2: Assemble contact sheet if capture set exists
    contact_sheet_path = None
    if capture_set:
        max_width = get_contact_sheet_max_width(load_anvil_config(project / "anvil.yaml"))
        contact_sheet_path = run_dir / "contact-sheet.png"
        assemble_contact_sheet(capture_set, contact_sheet_path, max_width, evidence_dir=run_dir)

    # Loopback gate round 3, finding 2: Resolve prompt through station registry
    prompt = None
    if registry is not None:
        station = registry.get("reviewer-design")
        if station and station.prompt:
            prompt = station.prompt

    # S3: Build scoped packet through scoped packet builder
    # R3: Pass declared evidence paths for packet listing
    packet, allowlist = build_reviewer_design_packet(
        project, work_order, files_changed, contact_sheet_path, prompt=prompt,
        declared_evidence_paths=[str(p.relative_to(project)) for p in declared_evidence_paths]
    )

    # Loopback gate round 3, finding 1: Verify packet allowlist by provenance
    # This check executes in the preparation path on the built packet against
    # exactly the allowlist the packet declares
    verify_packet_allowlist_by_provenance(packet, allowlist)

    return packet, contact_sheet_path

def prepare_packet(project, station_id, prompt, work_order, steps,
                   learnings_section="", design_section=""):
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

    # Build initial packet
    packet = _packet_text(station_id, prompt, work_order, steps,
                         learnings_section, design_section)

    measured = estimate_tokens(packet)

    # Check if under budget
    if measured <= budget:
        return packet, "sent", measured, budget

    # Over budget - try trimming
    # Trim order: compact tokens, reduce quality bars, limit learnings

    # Try compact tokens (no pretty print)
    from .design import packet_design_section_compact
    design_compact = packet_design_section_compact(project, station_id)
    packet_trimmed = _packet_text(station_id, prompt, work_order, steps,
                                   learnings_section, design_compact)
    measured = estimate_tokens(packet_trimmed)

    if measured <= budget:
        return packet_trimmed, "trimmed", measured, budget

    # Try reduced quality bars
    from .design import packet_design_section_reduced
    design_reduced = packet_design_section_reduced(project, station_id)
    packet_trimmed = _packet_text(station_id, prompt, work_order, steps,
                                   learnings_section, design_reduced)
    measured = estimate_tokens(packet_trimmed)

    if measured <= budget:
        return packet_trimmed, "trimmed", measured, budget

    # Try limited learnings
    from .brain import packet_learnings_section_limited
    learnings_limited = packet_learnings_section_limited(project, budget // 10)
    packet_trimmed = _packet_text(station_id, prompt, work_order, steps,
                                   learnings_limited, design_reduced)
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
    def to_dict(self):
        return {"work_order_id": self.work_order_id, "pipeline": self.pipeline,
                "title": self.title, "kind": self.kind,
                "steps": self.steps, "verdict": self.verdict, "human_required": self.human_required,
                "max_loopbacks": self.max_loopbacks, "loopbacks": self.loopbacks,
                "deployment_status": self.deployment_status, "verify_results": self.verify_results,
                "risk_hints": self.risk_hints, "decision": self.decision, "warnings": self.warnings,
                "astra_measured_tokens_total": self.astra_measured_tokens_total}

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

def _run_shell(command, cwd, work_order_id, timeout):
    env = dict(os.environ)
    env["ANVIL_WORK_ORDER_ID"] = work_order_id
    try:
        proc = subprocess.run(command, shell=True, cwd=str(cwd), env=env,
                              capture_output=True, text=True, timeout=timeout)
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except subprocess.TimeoutExpired:
        return None, f"Timed out after {timeout}s"

def _packet_text(station_id, prompt, work_order, steps, learnings_section="", design_section=""):
    """S4: Assemble packet with stable prefix layout.

    Stable material first (prompt, design, learnings), variable material last
    (work order, upstream steps). This enables provider prefix caching.

    Loopback item 1: Builder packets reference evidence images only when the work order declares them.

    R4: Reviewer packets carry Declared evidence inputs section when work order declares evidence_images.
    """
    # Stable prefix: station prompt
    text = f"# Task packet: {station_id}\n\n## Station prompt\n\n{prompt}\n"

    # Stable: design section (when present)
    if design_section:
        text += f"\n{design_section}\n"

    # Stable: learnings section (when present)
    if learnings_section:
        text += f"\n{learnings_section}\n"

    # Variable: work order block
    upstream = "\n".join(f"- {s['station']}: {s['status']}" for s in steps) or "- (none)"
    text += (f"\n## Work order\n\n"
            f"- id: {work_order.id}\n- kind: {work_order.kind}\n- title: {work_order.title}\n"
            f"- source: {work_order.source}\n- description: {work_order.description}\n"
            f"- risk_hints: {', '.join(work_order.risk_hints)}\n- status: {work_order.status}\n\n")

    # Loopback item 1: Include evidence images for builder when work order declares them
    if station_id == "builder" and work_order.evidence_images:
        text += f"## Evidence images\n\n"
        for img_path in work_order.evidence_images:
            text += f"- {img_path}\n"
        text += "\n"

    # R4: Declared evidence inputs section for reviewer stations when work order declares evidence_images
    if station_id.startswith("reviewer") and work_order.evidence_images:
        text += f"## Declared evidence inputs\n\n"
        for img_path in work_order.evidence_images:
            text += f"- {img_path}\n"
        text += "\n"

    text += f"## Upstream steps\n\n{upstream}\n"

    # Reviewer stations have a specific output contract
    if station_id.startswith("reviewer"):
        text += (f"\n## Output contract\n\n"
                f"Your complete answer is exactly one review JSON object written to "
                f"runs/{work_order.id}/{station_id}.review.json. The free output transcript "
                f"stays as provenance and is never parsed for a review.\n")
    return text

def run_pipeline(project_dir, pipeline, work_order, registry=None, max_loopbacks=2,
                 executor=None, deploy_cfg=None):
    project = Path(project_dir)
    if isinstance(work_order, dict):
        work_order = WorkOrder.from_dict(work_order)

    # Loopback item 4: Validate WorkOrder file paths before run
    validate_work_order_paths(work_order, project)

    run_dir = project / "runs" / work_order.id
    envelopes_dir = run_dir / "envelopes"
    run_dir.mkdir(parents=True, exist_ok=True)
    envelopes_dir.mkdir(parents=True, exist_ok=True)
    steps = []
    verdict = ""
    loopbacks = 0
    order = pipeline.topological_order()
    execute_mode = executor is not None
    # Run scoped reviews: only reviews produced during this run feed the
    # approver. Standing project reviews under reviews/<slug>/ are the project
    # record read by `anvil check`, never inputs to a run.
    run_reviews = []
    run_findings = []
    deployment_status = None
    verify_results = []
    human_blocked = None  # decided at the triage step
    # Decision record: the approver entry is filled at the approver step from
    # the reviews counted there; the human gate entry is filled at the end
    # from the final verdict. Both rule sentences are generated from the
    # same values the code acted on.
    reviews_expected = [sid for sid in order if sid.startswith("reviewer")]
    decision_approver = None
    # Verified learnings are computed once per run: only non demoted entries
    # from brain/learnings.md, never inbox proposals (see anvil/brain.py).
    learnings_section = packet_learnings_section(project)

    # Check for design system and prepare warnings
    warnings = []
    has_design_system = load_design_system(project) is not None
    interface_stations = {"builder", "writer", "media-producer", "brief-writer", "reviewer-design"}
    pipeline_has_interface_stations = any(sid in interface_stations for sid in order)

    if pipeline_has_interface_stations and not has_design_system:
        warnings.append("Missing design system: This pipeline includes interface-producing stations, "
                       "but the project has no design/DESIGN.md. Define the design system to enable "
                       "design review.")

    # S5: Track Astra-bound stations' measured tokens for report total
    # Astra route: openai/gpt-6-astra through Codex (UI and design stations)
    astra_bound_stations = interface_stations  # Interface stations use Astra route
    astra_measured_tokens_total = 0

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
        packet = run_dir / f"{station_id}.packet.md"
        design_section = packet_design_section(project, station_id)

        # S1: Apply budget for interface stations
        if station_id in budgeted_stations:
            try:
                packet_text, action, measured, budget = prepare_packet(
                    project, station_id, prompt, work_order, steps,
                    learnings_section, design_section
                )
                packet.write_text(packet_text, encoding="utf-8")
                return packet, measured, budget, action
            except PacketBudgetError as exc:
                # Budget exceeded - record the failure
                raise exc
        else:
            # Non-budgeted stations - standard packet generation
            packet_text = _packet_text(station_id, prompt, work_order, steps,
                                      learnings_section, design_section)
            packet.write_text(packet_text, encoding="utf-8")
            measured = estimate_tokens(packet_text)
            return packet, measured, 0, "none"

    for idx, station_id in enumerate(order):
        started = time.perf_counter()
        station = None
        if registry is not None and station_id in registry:
            station = registry.get(station_id)
        kind = station.kind if station else ("deterministic" if station_id in {"intake", "approver", "triage-human"} else "agent")
        # Model provenance: the configured label is a fact of configuration,
        # recorded in every mode. Executed fields stay null until a runtime
        # actually runs the station (agent-execution S8).
        configured_model = station.model if station is not None and station.model else default_model(station_id)
        step_executor = None
        step_executed_model = None
        status = "completed"
        detail = ""
        artifact = ""
        extra_envelope = {}
        step_usage = None
        deferred_verifier = None
        next_station = order[idx + 1] if idx + 1 < len(order) else None
        # S1 & S5: Budget tracking fields
        measured_tokens = 0
        budget = 0
        budget_action = "none"
        if station_id == "intake":
            detail = "Work order normalized"
            artifact = str(run_dir / "report.json")
        elif station_id == "approver":
            if run_reviews:
                verdict, verdict_rule, counted = aggregate_explained(run_reviews)
            else:
                verdict = "no_reviews"
                verdict_rule = ("No reviews were produced in this run, so the verdict is no_reviews; "
                                "standing project reviews are never counted.")
                counted = []
            # When execution was attempted and counted reviews are fewer than expected,
            # state both numbers to flag the shrinkage
            counted_len = len(counted)
            expected_len = len(reviews_expected)
            if execute_mode and counted_len < expected_len:
                verdict_rule += f" (Counted {counted_len} reviews, expected {expected_len}.)"
            decision_approver = {"reviews_counted": counted,
                                 "reviews_expected": list(reviews_expected),
                                 "rule": verdict_rule}
            detail = f"Approver verdict: {verdict}"
            artifact = str(run_dir / "report.json")
        elif station_id == "triage-human":
            hr = needs_human(work_order, verdict) if verdict else (human_gate(work_order) == "required")
            human_blocked = hr
            detail = f"Human review: {'required' if hr else 'not_required'}"
        elif station_id == "deployer" and execute_mode and deploy_cfg and deploy_cfg.get("command"):
            blocked = human_blocked if human_blocked is not None else needs_human(work_order, verdict)
            if verdict == "approved" and not blocked:
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
                else:
                    status = "failed"
                    detail = f"Deploy command failed with exit code {code}"
                    deployment_status = "deploy_failed"
            else:
                packet, measured_tokens, budget, budget_action = packet_step(station, station_id)
                status = "packet_ready"
                detail = f"Deploy skipped (verdict: {verdict or 'pending'}, human gate {'blocks' if blocked else 'open'}); packet written to {packet}"
                artifact = str(packet)
        elif kind in {"deterministic", "gate"}:
            detail = "Deterministic step executed"
        elif station_id == "deployer":
            # The deployer never runs through a generic executor: without a
            # deploy config and an approved, unblocked run it stays a packet.
            packet, measured_tokens, budget, budget_action = packet_step(station, station_id)
            status = "packet_ready"
            detail = f"Packet written to {packet}"
            artifact = str(packet)
        elif station_id == "reviewer-design":
            # Loopback item 1: S3 integration - reviewer-design uses scoped packet builder
            # Collect captures from run directory
            captures = []
            if run_dir.exists():
                captures = list(run_dir.glob("capture-*.png"))

            # Get files changed from git or use empty list
            files_changed = []
            try:
                # Try to get diff from git (simple implementation for now)
                import subprocess
                result = subprocess.run(
                    ["git", "diff", "--numstat", "HEAD"],
                    cwd=project, capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            parts = line.split('\t')
                            if len(parts) >= 3:
                                added = int(parts[0]) if parts[0] != '-' else 0
                                removed = int(parts[1]) if parts[1] != '-' else 0
                                files_changed.append({
                                    "file": parts[2],
                                    "added": added,
                                    "removed": removed
                                })
            except Exception:
                pass  # Use empty files_changed if git fails

            # Use scoped packet builder
            # Loopback gate round 3, finding 2: Pass registry so prompt can be resolved
            packet_text, contact_sheet_path = prepare_reviewer_design_step(
                project, work_order, files_changed, captures, registry=registry
            )
            packet = run_dir / f"{station_id}.packet.md"
            packet.write_text(packet_text, encoding="utf-8")

            # Measure tokens for budget tracking
            from .config import get_station_budget, load_anvil_config
            config = load_anvil_config(project / "anvil.yaml")
            budget = get_station_budget(config, station_id)
            measured_tokens = estimate_tokens(packet_text)
            budget_action = "sent" if measured_tokens <= budget else "trimmed"

            if execute_mode:
                # Execute reviewer-design
                output_file = run_dir / f"{station_id}.output.md"
                try:
                    result = executor.execute(packet_text, station_id, packet_path=packet,
                                              output_path=output_file, cwd=project)
                    output_text = result.get("output", "") if isinstance(result, dict) else str(result)
                    usage = result.get("usage") if isinstance(result, dict) else None
                    output_file.write_text(output_text, encoding="utf-8")
                    status = "executed"
                    detail = f"Executed by {executor.name}; output written to {output_file}"
                    artifact = str(output_file)
                    step_executor, step_executed_model = _executor_provenance(executor, output_text)
                    extra_envelope = {}
                    if isinstance(usage, dict):
                        step_usage = usage
                        extra_envelope["usage"] = usage
                        tokens = {k: usage[k] for k in usage if "token" in k}
                        if tokens:
                            extra_envelope["tokens"] = tokens

                    # Write the executor output to the authoritative review channel
                    review_file = run_dir / f"{station_id}.review.json"
                    review_file.write_text(output_text, encoding="utf-8")

                    # Parse review only from the authoritative channel
                    review = parse_review(output_text, station_id)
                    # Special handling for reviewer-design when no design system exists
                    if not has_design_system:
                        # Force a changes_requested verdict with a finding about missing design system
                        review = Review(
                            station="reviewer-design",
                            verdict="changes_requested",
                            findings=["No design system exists for this project. The project must define "
                                     "design/DESIGN.md and design/tokens.json before interface output can be "
                                     "reviewed against design standards."]
                        )
                    if review is not None:
                        run_reviews.append(review)
                        run_findings.extend(review.findings)
                        extra_envelope["review"] = review.to_dict()
                    else:
                        extra_envelope["review_parse_failed"] = True
                        detail += "; review output did not parse as a review JSON"
                except ExecutorError as exc:
                    status = "failed"
                    detail = f"Executor failed: {exc}"
                    artifact = str(packet)
                    step_executor, step_executed_model = _executor_provenance(executor)
                    extra_envelope = {"error": str(exc)}
            else:
                status = "packet_ready"
                detail = f"Packet written to {packet}"
                artifact = str(packet)
        elif execute_mode:
            packet, measured_tokens, budget, budget_action = packet_step(station, station_id)
            packet_text = packet.read_text(encoding="utf-8")
            output_file = run_dir / f"{station_id}.output.md"

            # For reviewer stations, remove any pre-existing review file before execution (S3)
            if station_id.startswith("reviewer"):
                review_file = run_dir / f"{station_id}.review.json"
                try:
                    review_file.unlink()
                except FileNotFoundError:
                    pass

            try:
                result = executor.execute(packet_text, station_id, packet_path=packet,
                                          output_path=output_file, cwd=project)
                output_text = result.get("output", "") if isinstance(result, dict) else str(result)
                usage = result.get("usage") if isinstance(result, dict) else None
                output_file.write_text(output_text, encoding="utf-8")
                status = "executed"
                detail = f"Executed by {executor.name}; output written to {output_file}"
                artifact = str(output_file)
                step_executor, step_executed_model = _executor_provenance(executor, output_text)
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

                    if review_file.exists():
                        try:
                            review_file_text = review_file.read_text(encoding="utf-8")
                            review = parse_review(review_file_text, station_id)
                        except Exception as e:
                            # File exists but couldn't be read or parsed
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

                    if review is not None:
                        run_reviews.append(review)
                        run_findings.extend(review.findings)
                        extra_envelope["review"] = review.to_dict()

            except ExecutorError as exc:
                status = "failed"
                detail = f"Executor failed: {exc}"
                artifact = str(packet)
                step_executor, step_executed_model = _executor_provenance(executor)
                extra_envelope = {"error": str(exc)}
        else:
            packet, measured_tokens, budget, budget_action = packet_step(station, station_id)
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
            if isinstance(step_usage.get("cost"), (int, float)):
                step["cost"] = step_usage["cost"]
        steps.append(step)

        # S5: Track Astra-bound stations' measured tokens for report total
        if station_id in astra_bound_stations and measured_tokens > 0:
            astra_measured_tokens_total += measured_tokens

        env_extra = dict(extra_envelope)
        env_extra["configured_model"] = configured_model
        if step_executor is not None:
            env_extra["executor"] = step_executor
            env_extra["executed_model"] = step_executed_model
        write_envelope(station_id, next_station, artifact or str(run_dir / "report.json"), status, env_extra)
        if deferred_verifier is not None:
            steps.append(deferred_verifier)
            write_envelope("verifier", next_station,
                           deferred_verifier["artifacts"][0] if deferred_verifier["artifacts"] else str(run_dir / "report.json"),
                           deferred_verifier["status"], {"configured_model": None})
        # Loopback right after approver when aggregation fails
        if station_id == "approver" and verdict in {"rejected", "changes_requested"} and loopbacks < max_loopbacks:
            loopbacks += 1
            # Spec failures return to spec-writer, implementation failures to builder.
            return_to = "spec-writer" if any("spec" in str(f).lower() and "missing" in str(f).lower() for f in run_findings) else "builder"
            reason = "; ".join(run_findings) if run_findings else f"Approver verdict: {verdict}"
            steps.append({"station": station_id, "status": "loopback", "return_to": return_to,
                          "detail": f"Loopback to {return_to}: {reason}", "reason": reason,
                          "duration_ms": 0.0, "cost": None, "artifacts": [],
                          "configured_model": None, "executed_model": None, "executor": None})
    if not verdict:
        verdict = "packet_ready"
    if decision_approver is None:
        # A pipeline without an approver step aggregates nothing; say so
        # instead of inventing a verdict explanation.
        decision_approver = {"reviews_counted": [{"station": r.station, "verdict": r.verdict} for r in run_reviews],
                             "reviews_expected": list(reviews_expected),
                             "rule": "The pipeline has no approver step, so no reviews were aggregated into a verdict."}
    if verdict in {"approved", "rejected", "changes_requested", "no_reviews"}:
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
    decision = {"approver": decision_approver,
                "human_gate": {"required": human_required, "rule": human_rule, "hints_matched": hints_matched}}
    report = RunReport(work_order_id=work_order.id, pipeline=pipeline.name, steps=steps, verdict=verdict,
                       title=work_order.title, kind=work_order.kind,
                       human_required=human_required, max_loopbacks=max_loopbacks, loopbacks=loopbacks,
                       deployment_status=deployment_status, verify_results=verify_results,
                       risk_hints=list(work_order.risk_hints or []), decision=decision, warnings=warnings,
                       astra_measured_tokens_total=astra_measured_tokens_total)
    (run_dir / "report.json").write_text(json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8")
    # Swimlane
    lines = ["# Swimlane", "", "Cost is reported as null here. Model runtimes report cost when they run a station; ANVIL never invents a number.", "",
             "| Station | Status | Duration ms | Artifacts | Cost |", "|---|---|---|---|---|"]
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
    (run_dir / "swimlane.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report

run = run_pipeline
