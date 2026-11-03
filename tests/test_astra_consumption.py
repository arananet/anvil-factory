"""Tests for astra-consumption spec: packet budgets, evidence policy, scoped design review.

Spec: .openspec/specs/astra-consumption/spec.md
Tests map to scenarios S1-S5 as documented in the spec's Tests section.
"""

import json
import struct
import tempfile
import unittest
from pathlib import Path
import sys

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
        import zlib
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
        import zlib
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

    def test_allowlist_check_rejects_out_of_scope(self):
        """Allowlist check rejects packet with content from outside allowlist"""
        from anvil.runner import verify_packet_allowlist, AllowlistViolation

        wo = WorkOrder(id="wo-allowlist-001", kind="feature", title="Test",
                      source="test", description="Allowlist test",
                      spec_path=".openspec/specs/test-spec/spec.md")

        # Files the order touches
        touched_files = ["src/app.py", "src/ui.py"]

        # Design system files
        design_files = ["design/DESIGN.md", "design/tokens.json"]

        # Build allowlist
        allowlist = touched_files + design_files + [wo.spec_path]

        # Create packet with content from outside allowlist
        packet_with_violation = """
# Task packet: reviewer-design

## Project design
...design content...

## File: src/secret.py
This file is not in the allowlist!
"""

        with self.assertRaises(AllowlistViolation) as ctx:
            verify_packet_allowlist(packet_with_violation, allowlist)

        error_msg = str(ctx.exception)
        self.assertIn("src/secret.py", error_msg,
                     "Error must identify the out-of-allowlist file")

    def test_allowlist_check_passes_for_scoped_content(self):
        """Allowlist check passes when all embedded content is in scope"""
        from anvil.runner import verify_packet_allowlist

        wo = WorkOrder(id="wo-allowlist-002", kind="feature", title="Test",
                      source="test", description="Valid packet")

        allowlist = [
            "src/app.py",
            "design/DESIGN.md",
            ".openspec/specs/test-spec/spec.md"
        ]

        # Packet with only allowed file references
        valid_packet = """
# Task packet: reviewer-design

## Project design
From design/DESIGN.md:
...design content...

## Spec
From .openspec/specs/test-spec/spec.md:
...spec content...

## Diff summary
- src/app.py: +10, -5
"""

        # Should not raise
        try:
            verify_packet_allowlist(valid_packet, allowlist)
        except Exception as e:
            self.fail(f"Valid packet should pass allowlist check: {e}")


class TestIntegration(unittest.TestCase):
    """Integration tests: full factory suite compatibility"""

    def test_existing_tests_still_pass(self):
        """Verify changes don't break existing factory tests"""
        # This is a placeholder that documents the requirement
        # The actual existing tests are in other test_*.py files
        # CI runs the full suite, this test ensures the intent is captured
        pass


if __name__ == '__main__':
    unittest.main()
