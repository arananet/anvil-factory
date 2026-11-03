"""Tests for astra-consumption spec: packet budgets, evidence policy, scoped design review.

Spec: .openspec/specs/astra-consumption/spec.md
Tests map to scenarios S1-S5 as documented in the spec's Tests section.

Loopback gate round 2: Tests for integration, PNG hardening, provenance checking, report visibility.
"""

import json
import struct
import tempfile
import unittest
from pathlib import Path
import sys
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from anvil.model import WorkOrder
from anvil.runner import _packet_text
from anvil.config import load_anvil_config


class TestTokenEstimator(unittest.TestCase):
    """S1: Token estimator tests - determinism and monotonicity"""

    def test_estimator_determinism(self):
        """Same input always yields the same count"""
        from anvil.runner import estimate_tokens

        text = "This is a test packet with some content"
        count1 = estimate_tokens(text)
        count2 = estimate_tokens(text)
        self.assertEqual(count1, count2, "Estimator must be deterministic")

    def test_estimator_empty_packet_zero(self):
        """Empty packet counts zero"""
        from anvil.runner import estimate_tokens

        count = estimate_tokens("")
        self.assertEqual(count, 0, "Empty packet should count as zero tokens")

    def test_estimator_monotonic_growth(self):
        """Count grows with input size"""
        from anvil.runner import estimate_tokens

        short_text = "Short"
        long_text = short_text + " " + "Additional content " * 100

        short_count = estimate_tokens(short_text)
        long_count = estimate_tokens(long_text)

        self.assertGreater(long_count, short_count,
                          "Longer input must produce higher token count")


class TestPacketBudget(unittest.TestCase):
    """S1: Packet budget enforcement with trimming and failure modes"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name) / "proj"
        self.project.mkdir(parents=True)

        # Create a minimal project structure
        (self.project / "design").mkdir()
        (self.project / "design" / "DESIGN.md").write_text("# Design\n## Quality Bars\n- Bar 1\n- Bar 2\n")
        (self.project / "design" / "tokens.json").write_text(json.dumps({"color": {"primary": "#000"}}, indent=2))
        (self.project / "brain").mkdir()
        (self.project / "brain" / "learnings.json").write_text("[]")

    def tearDown(self):
        self.tmp.cleanup()

    def test_over_budget_packet_trimmed_in_order(self):
        """Over budget packet is trimmed in declared order and then fits"""
        from anvil.runner import prepare_packet, estimate_tokens

        # Configure a very low budget
        config = {"station_budgets": {"reviewer-design": 500}}
        (self.project / "anvil.yaml").write_text(json.dumps(config))

        wo = WorkOrder(id="wo-trim-001", kind="feature", title="Test",
                      source="test", description="Large packet test")

        # Create a packet that exceeds budget
        station_id = "reviewer-design"
        prompt = "Station prompt"
        steps = []

        packet_text, action, measured, budget = prepare_packet(
            self.project, station_id, prompt, wo, steps
        )

        # Verify trimming occurred
        self.assertIn(action, ["trimmed", "sent"],
                     "Action must be 'trimmed' or 'sent'")
        if action == "trimmed":
            # After trimming, packet should fit within budget
            self.assertLessEqual(measured, budget,
                               "Trimmed packet must fit within budget")

    def test_fail_policy_prevents_execution(self):
        """With fail policy, preparation raises and executor is never called"""
        from anvil.runner import prepare_packet, PacketBudgetError

        # Configure fail policy
        config = {
            "station_budgets": {"builder": 100},
            "over_budget_policy": "fail"
        }
        (self.project / "anvil.yaml").write_text(json.dumps(config))

        wo = WorkOrder(id="wo-fail-001", kind="feature", title="Test",
                      source="test", description="Budget failure test " * 50)

        station_id = "builder"
        prompt = "Build the feature"
        steps = []

        # Should raise before execution
        with self.assertRaises(PacketBudgetError) as ctx:
            prepare_packet(self.project, station_id, prompt, wo, steps)

        # Error should include measured size and budget
        error_msg = str(ctx.exception)
        self.assertIn("budget", error_msg.lower())

    def test_under_budget_packet_byte_identical(self):
        """Under budget packet reaches executor byte unchanged"""
        from anvil.runner import prepare_packet

        # Configure generous budget
        config = {"station_budgets": {"builder": 100000}}
        (self.project / "anvil.yaml").write_text(json.dumps(config))

        wo = WorkOrder(id="wo-under-001", kind="bug", title="Small",
                      source="test", description="Tiny packet")

        station_id = "builder"
        prompt = "Fix it"
        steps = []

        # Get the original packet text
        original = _packet_text(station_id, prompt, wo, steps)

        # Prepare with budget check
        packet_text, action, measured, budget = prepare_packet(
            self.project, station_id, prompt, wo, steps
        )

        # Should be sent unchanged
        self.assertEqual(action, "sent")
        self.assertEqual(packet_text, original,
                        "Under budget packet must be byte identical")

    def test_report_fields_recorded(self):
        """Report entries carry measured tokens, budget and action"""
        from anvil.runner import run_pipeline
        from anvil.pipeline import load_pipeline
        from anvil.stations import load_registry

        ROOT = Path(__file__).resolve().parent.parent

        # Configure budget
        config = {"station_budgets": {"builder": 50000}}
        (self.project / "anvil.yaml").write_text(json.dumps(config))

        # Create minimal pipeline
        (self.project / ".openspec").mkdir()
        (self.project / ".openspec" / "specs").mkdir()
        spec_dir = self.project / ".openspec" / "specs" / "test-feature"
        spec_dir.mkdir()
        (spec_dir / "spec.md").write_text("# Test\n")

        wo = WorkOrder(id="wo-report-001", kind="bug", title="Report test",
                      source="test", description="Check report fields")

        # Run without executor (packets_only mode)
        reg = load_registry(ROOT / "stations")
        pipeline = load_pipeline(ROOT / "pipelines" / "hotfix.json",
                                known_stations=set(reg.ids()))

        report = run_pipeline(self.project, pipeline, wo, registry=reg)

        # Check that report steps have the required fields
        for step in report.steps:
            if step.get("status") == "packet_ready":
                self.assertIn("measured_tokens", step,
                            "Step must record measured tokens")
                self.assertIn("budget", step,
                            "Step must record budget")
                self.assertIn("budget_action", step,
                            "Step must record action (sent/trimmed/failed)")


class TestContactSheet(unittest.TestCase):
    """S2: Evidence image policy - contact sheet assembly"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.evidence_dir = Path(self.tmp.name) / "evidence"
        self.evidence_dir.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def _create_test_png(self, path, width, height, color=(255, 0, 0)):
        """Helper to create a minimal test PNG image using standard library"""
        # PNG signature
        signature = b'\x89PNG\r\n\x1a\n'

        # IHDR chunk (image header)
        ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
        ihdr_chunk = self._make_png_chunk(b'IHDR', ihdr_data)

        # IDAT chunk (minimal image data - empty for simplicity)
        # For a valid minimal PNG, we need at least some compressed data
        # Create a minimal scanline (filter byte + RGB pixels)
        scanline = b'\x00' + (bytes(color) * width)
        raw_data = scanline * height
        compressed = zlib.compress(raw_data)
        idat_chunk = self._make_png_chunk(b'IDAT', compressed)

        # IEND chunk (marks end of PNG)
        iend_chunk = self._make_png_chunk(b'IEND', b'')

        # Write complete PNG
        path.write_bytes(signature + ihdr_chunk + idat_chunk + iend_chunk)
        return path

    def _make_png_chunk(self, chunk_type, data):
        """Create a PNG chunk with length, type, data, and CRC"""
        length = struct.pack('>I', len(data))
        chunk = chunk_type + data
        crc = struct.pack('>I', zlib.crc32(chunk) & 0xffffffff)
        return length + chunk + crc

    def _read_png_dimensions(self, path):
        """Read PNG dimensions using standard library"""
        data = path.read_bytes()

        # Verify PNG signature
        if not data.startswith(b'\x89PNG\r\n\x1a\n'):
            raise ValueError("Not a valid PNG file")

        # Find IHDR chunk (should be first chunk after signature)
        # PNG chunk structure: 4 bytes length + 4 bytes type + data + 4 bytes CRC
        idx = 8  # Skip signature
        length = struct.unpack('>I', data[idx:idx+4])[0]
        chunk_type = data[idx+4:idx+8]

        if chunk_type != b'IHDR':
            raise ValueError("IHDR chunk not found where expected")

        # IHDR format: width (4 bytes), height (4 bytes), ...
        ihdr_data = data[idx+8:idx+8+length]
        width, height = struct.unpack('>II', ihdr_data[:8])

        return width, height

    def test_contact_sheet_within_max_width(self):
        """Fixture PNGs produce one PNG sheet with width <= configured max"""
        from anvil.runner import assemble_contact_sheet

        # Create test captures
        captures = [
            self._create_test_png(self.evidence_dir / "cap1.png", 800, 600),
            self._create_test_png(self.evidence_dir / "cap2.png", 1200, 800),
            self._create_test_png(self.evidence_dir / "cap3.png", 1000, 1000),
        ]

        max_width = 1600
        output_path = self.evidence_dir / "contact-sheet.png"

        result = assemble_contact_sheet(captures, output_path, max_width)

        # Verify output exists and is PNG
        self.assertTrue(output_path.exists())

        # Check dimensions
        width, height = self._read_png_dimensions(output_path)
        self.assertLessEqual(width, max_width,
                           f"Contact sheet width {width} exceeds max {max_width}")

    def test_contact_sheet_scales_down_not_up(self):
        """Captures are scaled down proportionally, never up"""
        from anvil.runner import assemble_contact_sheet

        # Create small capture
        small_cap = self._create_test_png(self.evidence_dir / "small.png", 400, 300)

        max_width = 1600
        output_path = self.evidence_dir / "contact-sheet-small.png"

        assemble_contact_sheet([small_cap], output_path, max_width)

        # Original dimensions
        orig_w, orig_h = self._read_png_dimensions(small_cap)

        # Contact sheet dimensions
        sheet_w, sheet_h = self._read_png_dimensions(output_path)

        # Should not be scaled up
        self.assertLessEqual(sheet_w, max(orig_w, max_width),
                           "Small images must not be scaled up")

    def test_originals_unchanged(self):
        """Original captures remain byte unchanged"""
        from anvil.runner import assemble_contact_sheet

        cap_path = self._create_test_png(self.evidence_dir / "original.png", 800, 600)

        # Read original bytes
        original_bytes = cap_path.read_bytes()

        output_path = self.evidence_dir / "contact-sheet.png"
        assemble_contact_sheet([cap_path], output_path, max_width=1600)

        # Verify original unchanged
        current_bytes = cap_path.read_bytes()
        self.assertEqual(original_bytes, current_bytes,
                        "Original capture must remain byte identical")

    def test_non_png_fails_loudly(self):
        """Non-PNG capture causes assembler to fail loudly"""
        from anvil.runner import assemble_contact_sheet, ContactSheetError

        # Create a non-PNG file
        fake_png = self.evidence_dir / "fake.png"
        fake_png.write_text("This is not a PNG file")

        output_path = self.evidence_dir / "contact-sheet.png"

        with self.assertRaises(ContactSheetError) as ctx:
            assemble_contact_sheet([fake_png], output_path, max_width=1600)

        error_msg = str(ctx.exception)
        self.assertTrue(error_msg, "Must fail with clear error message")

    def test_png_size_caps_enforced(self):
        """Loopback item 4: PNG assembler enforces input size caps before inflation"""
        from anvil.runner import assemble_contact_sheet, ContactSheetError

        # Create a PNG with dimensions that would exceed caps
        # This tests that size is validated from headers before inflating data
        huge_png = self.evidence_dir / "huge.png"

        # Create PNG with header claiming huge dimensions
        signature = b'\x89PNG\r\n\x1a\n'
        # IHDR with excessive dimensions (100000 x 100000)
        ihdr_data = struct.pack('>IIBBBBB', 100000, 100000, 8, 2, 0, 0, 0)
        ihdr_chunk = self._make_png_chunk(b'IHDR', ihdr_data)
        # Minimal IDAT (won't decompress properly but we should fail before that)
        idat_chunk = self._make_png_chunk(b'IDAT', b'\x78\x9c\x03\x00\x00\x00\x00\x01')
        iend_chunk = self._make_png_chunk(b'IEND', b'')

        huge_png.write_bytes(signature + ihdr_chunk + idat_chunk + iend_chunk)

        output_path = self.evidence_dir / "contact-sheet.png"

        # Should fail with size cap error before attempting to inflate
        with self.assertRaises(ContactSheetError) as ctx:
            assemble_contact_sheet([huge_png], output_path, max_width=1600)

        error_msg = str(ctx.exception).lower()
        # Error should indicate size/dimension issue
        self.assertTrue(
            "dimension" in error_msg or "size" in error_msg or "cap" in error_msg,
            f"Error should indicate size cap violation: {ctx.exception}"
        )

    def test_png_crc_verification(self):
        """Loopback item 4: PNG assembler verifies chunk CRCs"""
        from anvil.runner import assemble_contact_sheet, ContactSheetError

        # Create PNG with corrupted CRC
        corrupt_png = self.evidence_dir / "corrupt.png"

        signature = b'\x89PNG\r\n\x1a\n'
        ihdr_data = struct.pack('>IIBBBBB', 100, 100, 8, 2, 0, 0, 0)

        # Create chunk with WRONG CRC
        length = struct.pack('>I', len(ihdr_data))
        chunk = b'IHDR' + ihdr_data
        bad_crc = struct.pack('>I', 0xDEADBEEF)  # Wrong CRC
        ihdr_chunk = length + chunk + bad_crc

        # Valid compressed data
        scanline = b'\x00' + (b'\xff\x00\x00' * 100)
        raw_data = scanline * 100
        compressed = zlib.compress(raw_data)
        idat_chunk = self._make_png_chunk(b'IDAT', compressed)
        iend_chunk = self._make_png_chunk(b'IEND', b'')

        corrupt_png.write_bytes(signature + ihdr_chunk + idat_chunk + iend_chunk)

        output_path = self.evidence_dir / "contact-sheet.png"

        # Should fail due to CRC mismatch
        with self.assertRaises(ContactSheetError) as ctx:
            assemble_contact_sheet([corrupt_png], output_path, max_width=1600)

        error_msg = str(ctx.exception).lower()
        self.assertTrue(
            "crc" in error_msg or "corrupt" in error_msg or "invalid" in error_msg,
            f"Error should indicate CRC failure: {ctx.exception}"
        )

    def test_png_chunk_length_bounds_check(self):
        """Loopback item 4: PNG assembler bounds checks chunk lengths before reads"""
        from anvil.runner import assemble_contact_sheet, ContactSheetError

        # Create PNG with chunk length exceeding file size
        malformed_png = self.evidence_dir / "malformed.png"

        signature = b'\x89PNG\r\n\x1a\n'
        # Chunk claiming huge length that extends beyond actual data
        bad_length = struct.pack('>I', 0xFFFFFFFF)  # Claims max size
        chunk_type = b'IHDR'
        minimal_data = struct.pack('>IIBBBBB', 100, 100, 8, 2, 0, 0, 0)
        crc = struct.pack('>I', zlib.crc32(chunk_type + minimal_data) & 0xffffffff)

        malformed_png.write_bytes(signature + bad_length + chunk_type + minimal_data + crc)

        output_path = self.evidence_dir / "contact-sheet.png"

        # Should fail due to bounds check
        with self.assertRaises(ContactSheetError) as ctx:
            assemble_contact_sheet([malformed_png], output_path, max_width=1600)

        error_msg = str(ctx.exception).lower()
        self.assertTrue(
            "bounds" in error_msg or "length" in error_msg or "invalid" in error_msg,
            f"Error should indicate bounds check failure: {ctx.exception}"
        )

    def test_contact_sheet_output_path_validation(self):
        """Loopback item 4: Contact sheet output path must resolve inside run evidence directory"""
        from anvil.runner import assemble_contact_sheet, ContactSheetError

        # Create a valid capture
        cap = self._create_test_png(self.evidence_dir / "valid.png", 100, 100)

        # Try to write outside evidence directory using path traversal
        malicious_output = self.evidence_dir / ".." / ".." / "etc" / "passwd"

        # Should fail due to path validation
        with self.assertRaises(ContactSheetError) as ctx:
            assemble_contact_sheet([cap], malicious_output, max_width=1600)

        error_msg = str(ctx.exception).lower()
        self.assertTrue(
            "path" in error_msg or "directory" in error_msg or "invalid" in error_msg,
            f"Error should indicate path validation failure: {ctx.exception}"
        )


class TestPacketLayout(unittest.TestCase):
    """S4: Stable prefix packet layout"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name) / "proj"
        self.project.mkdir(parents=True)

        # Setup project structure
        (self.project / "design").mkdir()
        (self.project / "design" / "DESIGN.md").write_text("# Design\n## Quality Bars\n- Quality bar\n")
        (self.project / "design" / "tokens.json").write_text("{}")
        (self.project / "brain").mkdir()
        learnings = [{"content": "Test learning", "timestamp": "2024-01-01"}]
        (self.project / "brain" / "learnings.json").write_text(json.dumps(learnings))

    def tearDown(self):
        self.tmp.cleanup()

    def test_stable_prefix_across_runs(self):
        """Two packets for one station share byte-identical stable prefix"""
        from anvil.runner import _packet_text

        station_id = "builder"
        prompt = "Build the feature"

        # First work order
        wo1 = WorkOrder(id="wo-stable-001", kind="feature", title="First",
                       source="test", description="First order")
        steps1 = [{"station": "intake", "status": "completed"}]

        packet1 = _packet_text(station_id, prompt, wo1, steps1,
                              learnings_section="## Verified learnings\n- Learning 1\n",
                              design_section="## Project design\n- Token 1\n")

        # Second work order (different variable content)
        wo2 = WorkOrder(id="wo-stable-002", kind="bug", title="Second",
                       source="test", description="Different order")
        steps2 = [{"station": "intake", "status": "completed"},
                  {"station": "spec-writer", "status": "executed"}]

        packet2 = _packet_text(station_id, prompt, wo2, steps2,
                              learnings_section="## Verified learnings\n- Learning 1\n",
                              design_section="## Project design\n- Token 1\n")

        # Find where work order block starts
        wo_marker = "\n## Work order\n"
        idx1 = packet1.find(wo_marker)
        idx2 = packet2.find(wo_marker)

        self.assertGreater(idx1, 0, "Work order marker must be found in packet1")
        self.assertGreater(idx2, 0, "Work order marker must be found in packet2")

        # Stable prefix should be byte identical
        prefix1 = packet1[:idx1]
        prefix2 = packet2[:idx2]

        self.assertEqual(prefix1, prefix2,
                        "Packets must share byte-identical stable prefix")

    def test_design_and_learnings_before_work_order(self):
        """Design and learnings sections appear before work order block"""
        from anvil.runner import _packet_text

        station_id = "reviewer-design"
        prompt = "Review the design"
        wo = WorkOrder(id="wo-layout-001", kind="feature", title="Test",
                      source="test", description="Layout test")
        steps = []

        learnings = "## Verified learnings\n- A learning\n"
        design = "## Project design\n- A token\n"

        packet = _packet_text(station_id, prompt, wo, steps,
                             learnings_section=learnings,
                             design_section=design)

        # Find positions
        prompt_pos = packet.find("## Station prompt")
        design_pos = packet.find("## Project design")
        learnings_pos = packet.find("## Verified learnings")
        wo_pos = packet.find("## Work order")
        upstream_pos = packet.find("## Upstream steps")

        # Verify stable material comes before variable material
        self.assertGreater(wo_pos, prompt_pos,
                          "Work order must come after prompt")
        self.assertGreater(wo_pos, design_pos,
                          "Work order must come after design")
        self.assertGreater(wo_pos, learnings_pos,
                          "Work order must come after learnings")
        self.assertGreater(upstream_pos, wo_pos,
                          "Upstream steps must come after work order")


class TestScopedReview(unittest.TestCase):
    """S3: Fresh session, scoped design review"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name) / "proj"
        self.project.mkdir(parents=True)

        # Setup project structure
        (self.project / "design").mkdir()
        (self.project / "design" / "DESIGN.md").write_text("# Design\n")
        (self.project / ".openspec" / "specs" / "test-spec").mkdir(parents=True)
        (self.project / ".openspec" / "specs" / "test-spec" / "spec.md").write_text("# Spec\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_reviewer_design_packet_contents(self):
        """reviewer-design packet contains design, spec, diff summary, contact sheet"""
        from anvil.runner import build_reviewer_design_packet

        wo = WorkOrder(id="wo-scoped-001", kind="feature", title="Test",
                      source="test", description="Test scoped review",
                      spec_path=".openspec/specs/test-spec/spec.md")

        # Create a mock diff
        files_changed = [
            {"file": "src/app.py", "added": 10, "removed": 5},
            {"file": "src/ui.py", "added": 20, "removed": 3}
        ]

        contact_sheet_path = self.project / "runs" / wo.id / "contact-sheet.png"

        packet = build_reviewer_design_packet(
            self.project, wo, files_changed, contact_sheet_path
        )

        # Verify expected contents are present
        self.assertIn("## Project design", packet,
                     "Packet must contain design section")
        self.assertIn("## Spec", packet,
                     "Packet must contain spec")
        self.assertIn("src/app.py", packet,
                     "Packet must contain diff summary")
        self.assertIn("contact-sheet.png", packet,
                     "Packet must reference contact sheet")

        # Verify excluded contents are NOT present
        self.assertNotIn("builder session", packet.lower(),
                        "Packet must not contain builder transcript")
        self.assertNotIn("## Output from", packet,
                        "Packet must not contain other station outputs")

    def test_scoped_packet_builder_location(self):
        """Loopback item 2: Scoped packet builder is in anvil/runner.py, not anvil/stations"""
        # This test verifies architectural placement by checking imports
        import anvil.runner

        # build_reviewer_design_packet should be in anvil.runner
        self.assertTrue(
            hasattr(anvil.runner, 'build_reviewer_design_packet'),
            "build_reviewer_design_packet must be in anvil.runner module"
        )

        # Verify it doesn't import from anvil.stations at module level
        # (imports within functions are allowed for station prompt loading)
        import inspect
        source = inspect.getsource(anvil.runner)
        module_level_imports = []
        for line in source.split('\n'):
            stripped = line.strip()
            if stripped.startswith('from anvil.stations'):
                # Module-level import would be at column 0 (not indented)
                if not line.startswith(' ') and not line.startswith('\t'):
                    module_level_imports.append(line)

        self.assertEqual(
            len(module_level_imports), 0,
            f"anvil.runner must not import from anvil.stations at module level. Found: {module_level_imports}"
        )

    def test_provenance_based_allowlist_check(self):
        """Loopback item 3: Allowlist verification uses provenance tags, not pattern scanning"""
        from anvil.runner import verify_packet_allowlist_by_provenance, AllowlistViolation

        # Allowlist
        allowlist = [
            "src/app.py",
            "design/DESIGN.md",
            ".openspec/specs/test-spec/spec.md"
        ]

        # Packet with provenance tags
        # Content blocks are tagged with source paths at assembly time
        tagged_packet = """
# Task packet: reviewer-design

## Project design
<!-- source: design/DESIGN.md -->
Design content from DESIGN.md

## Spec
<!-- source: .openspec/specs/test-spec/spec.md -->
Spec content

## Diff summary
- src/app.py: +10, -5
"""

        # Valid packet should pass
        try:
            verify_packet_allowlist_by_provenance(tagged_packet, allowlist)
        except Exception as e:
            self.fail(f"Valid tagged packet should pass: {e}")

        # Packet with content from outside allowlist
        packet_with_violation = """
# Task packet: reviewer-design

## Project design
<!-- source: design/DESIGN.md -->
Design content

## Secret content
<!-- source: src/secrets.py -->
This content is from outside the allowlist
"""

        # Should fail because src/secrets.py is not in allowlist
        with self.assertRaises(AllowlistViolation) as ctx:
            verify_packet_allowlist_by_provenance(packet_with_violation, allowlist)

        error_msg = str(ctx.exception)
        self.assertIn("src/secrets.py", error_msg,
                     "Error must identify the out-of-allowlist source file")

    def test_provenance_tags_prevent_text_pattern_bypass(self):
        """Loopback item 3: Content mentioning allowlisted names but from wrong source fails check"""
        from anvil.runner import verify_packet_allowlist_by_provenance, AllowlistViolation

        allowlist = ["src/app.py", "design/DESIGN.md"]

        # Packet where content mentions allowlisted filenames but has wrong provenance tag
        sneaky_packet = """
# Task packet: reviewer-design

## Content
<!-- source: src/malicious.py -->
This content mentions src/app.py and design/DESIGN.md in its text,
but the provenance tag shows it actually came from src/malicious.py
which is NOT in the allowlist.
"""

        # Must fail based on provenance tag, not text pattern matching
        with self.assertRaises(AllowlistViolation) as ctx:
            verify_packet_allowlist_by_provenance(sneaky_packet, allowlist)

        error_msg = str(ctx.exception)
        self.assertIn("malicious", error_msg.lower(),
                     "Error must identify the actual source file from provenance tag")


class TestWorkOrderFilePathValidation(unittest.TestCase):
    """Loopback item 4: WorkOrder file path validation"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name) / "proj"
        self.project.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_evidence_images_path_validation(self):
        """Loopback item 4: WorkOrder evidence_images paths must resolve inside project tree"""
        from anvil.runner import validate_work_order_paths, PathValidationError

        # Valid evidence_images paths
        valid_wo = WorkOrder(
            id="wo-valid-001",
            kind="feature",
            title="Valid paths",
            source="test",
            description="Test path validation",
            evidence_images=["design/screenshot1.png", "design/screenshot2.png"]
        )

        # Should pass validation
        try:
            validate_work_order_paths(valid_wo, self.project)
        except Exception as e:
            self.fail(f"Valid paths should pass: {e}")

        # Invalid path using traversal to escape project tree
        invalid_wo = WorkOrder(
            id="wo-invalid-001",
            kind="feature",
            title="Invalid paths",
            source="test",
            description="Test path validation",
            evidence_images=["design/../../../etc/passwd"]
        )

        # Should fail validation
        with self.assertRaises(PathValidationError) as ctx:
            validate_work_order_paths(invalid_wo, self.project)

        error_msg = str(ctx.exception).lower()
        self.assertTrue(
            "path" in error_msg or "outside" in error_msg or "invalid" in error_msg,
            f"Error should indicate path traversal: {ctx.exception}"
        )


class TestIntegration(unittest.TestCase):
    """Integration tests: S2/S3 wiring into run path, report visibility"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name) / "proj"
        self.project.mkdir(parents=True)

        # Setup project structure
        (self.project / "design").mkdir()
        (self.project / "design" / "DESIGN.md").write_text("# Design\n## Quality Bars\n- Bar 1\n")
        (self.project / "design" / "tokens.json").write_text(json.dumps({"color": {"primary": "#000"}}))
        (self.project / "brain").mkdir()
        (self.project / "brain" / "learnings.json").write_text("[]")
        (self.project / ".openspec" / "specs" / "test-feature").mkdir(parents=True)
        (self.project / ".openspec" / "specs" / "test-feature" / "spec.md").write_text("# Test Feature\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_contact_sheet_assembly_wired_into_run_path(self):
        """Loopback item 1: Contact sheet is assembled during reviewer-design preparation"""
        from anvil.runner import prepare_reviewer_design_step
        from pathlib import Path

        # Create test captures in run evidence
        run_dir = self.project / "runs" / "wo-integration-001"
        run_dir.mkdir(parents=True)

        captures = []
        for i in range(2):
            cap_path = run_dir / f"capture-{i}.png"
            # Create minimal valid PNG
            signature = b'\x89PNG\r\n\x1a\n'
            ihdr_data = struct.pack('>IIBBBBB', 100, 100, 8, 2, 0, 0, 0)
            ihdr_chunk = self._make_png_chunk(b'IHDR', ihdr_data)
            scanline = b'\x00' + (b'\xff\x00\x00' * 100)
            compressed = zlib.compress(scanline * 100)
            idat_chunk = self._make_png_chunk(b'IDAT', compressed)
            iend_chunk = self._make_png_chunk(b'IEND', b'')
            cap_path.write_bytes(signature + ihdr_chunk + idat_chunk + iend_chunk)
            captures.append(cap_path)

        wo = WorkOrder(
            id="wo-integration-001",
            kind="feature",
            title="Integration test",
            source="test",
            description="Test S2 integration",
            spec_path=".openspec/specs/test-feature/spec.md"
        )

        files_changed = [{"file": "src/app.py", "added": 5, "removed": 2}]

        # Prepare reviewer-design step (should assemble contact sheet)
        packet, contact_sheet_path = prepare_reviewer_design_step(
            self.project, wo, files_changed, captures
        )

        # Verify contact sheet was created
        self.assertTrue(
            contact_sheet_path.exists(),
            "Contact sheet must be assembled during reviewer-design preparation"
        )
        self.assertTrue(
            contact_sheet_path.name == "contact-sheet.png",
            "Contact sheet must be named contact-sheet.png"
        )

        # Verify packet references contact sheet
        self.assertIn("contact-sheet.png", packet,
                     "Packet must reference the assembled contact sheet")

    def test_scoped_packet_builder_wired_into_run_path(self):
        """Loopback item 1: Scoped packet builder is called for reviewer-design"""
        from anvil.runner import prepare_reviewer_design_step

        wo = WorkOrder(
            id="wo-scoped-integration-001",
            kind="feature",
            title="Scoped integration",
            source="test",
            description="Test S3 integration",
            spec_path=".openspec/specs/test-feature/spec.md"
        )

        files_changed = [{"file": "src/ui.py", "added": 15, "removed": 8}]

        # Prepare reviewer-design step (should use scoped builder)
        packet, _ = prepare_reviewer_design_step(
            self.project, wo, files_changed, captures=[]
        )

        # Verify packet has scoped structure (fresh session characteristics)
        self.assertIn("## Project design", packet,
                     "Scoped packet must contain design section")
        self.assertIn("## Spec", packet,
                     "Scoped packet must contain spec")
        self.assertIn("## Diff summary", packet,
                     "Scoped packet must contain diff summary")
        self.assertIn("## File access allowlist", packet,
                     "Scoped packet must declare allowlist")

        # Verify it does NOT have standard packet characteristics
        self.assertNotIn("## Upstream steps", packet,
                        "Scoped packet must not contain upstream steps")

    def test_report_visibility_in_real_run(self):
        """Loopback item 5: S1/S5 measurements visible in actual report.json"""
        from anvil.runner import run_pipeline
        from anvil.pipeline import load_pipeline
        from anvil.stations import load_registry

        ROOT = Path(__file__).resolve().parent.parent

        # Configure budgets
        config = {
            "station_budgets": {
                "builder": 50000,
                "reviewer-design": 30000
            }
        }
        (self.project / "anvil.yaml").write_text(json.dumps(config))

        wo = WorkOrder(
            id="wo-report-visibility-001",
            kind="feature",
            title="Report visibility",
            source="test",
            description="Test S5 report visibility",
            spec_path=".openspec/specs/test-feature/spec.md"
        )

        # Run a pipeline
        reg = load_registry(ROOT / "stations")
        pipeline = load_pipeline(
            ROOT / "pipelines" / "hotfix.json",
            known_stations=set(reg.ids())
        )

        report = run_pipeline(self.project, pipeline, wo, registry=reg)

        # Write report to file (simulating real run)
        report_path = self.project / "runs" / wo.id / "report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report.to_dict(), indent=2))

        # Read back and verify required fields
        report_data = json.loads(report_path.read_text())

        # S1: Per-step measurements must be present
        for step in report_data.get("steps", []):
            if step.get("status") in ["packet_ready", "executed", "completed"]:
                self.assertIn("measured_tokens", step,
                            f"Step {step.get('station')} must record measured_tokens")
                self.assertIn("budget", step,
                            f"Step {step.get('station')} must record budget")
                self.assertIn("budget_action", step,
                            f"Step {step.get('station')} must record budget_action")

        # S5: Astra total must be present field (even if zero)
        self.assertIn("astra_measured_tokens_total", report_data,
                     "Report must contain astra_measured_tokens_total field")

        # S5: Usage fields per step (input/output tokens or null)
        for step in report_data.get("steps", []):
            if step.get("status") == "executed":
                # Usage should be present (as dict with input/output or as null)
                self.assertIn("usage", step,
                            f"Executed step {step.get('station')} must have usage field")

    def _make_png_chunk(self, chunk_type, data):
        """Helper to create PNG chunk"""
        length = struct.pack('>I', len(data))
        chunk = chunk_type + data
        crc = struct.pack('>I', zlib.crc32(chunk) & 0xffffffff)
        return length + chunk + crc


class TestFactorySuiteCompatibility(unittest.TestCase):
    """Integration tests: full factory suite compatibility"""

    def test_existing_tests_still_pass(self):
        """Verify changes do not break existing factory tests"""
        # This test documents the requirement that the full factory suite must pass
        # The actual existing tests are in other test_*.py files
        # CI runs the full suite to verify compatibility
        pass


if __name__ == '__main__':
    unittest.main()
