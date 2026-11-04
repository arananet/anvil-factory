"""Tests for declared-evidence-review spec: declared evidence wiring to reviewer-design and review-only pipeline.

Spec: .openspec/specs/declared-evidence-review/spec.md
Tests map to scenarios S1-S5 as documented in the spec's Tests section.

Work order: wo-gh-26
GitHub issue: https://github.com/arananet/anvil-factory/issues/26
"""

import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from anvil.model import WorkOrder
from anvil.runner import prepare_reviewer_design_step


class TestDeclaredEvidenceContactSheet(unittest.TestCase):
    """T1/S1: Declared images reach reviewer-design as a contact sheet"""

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

        # Create evidence directory
        self.evidence_dir = self.project / "evidence"
        self.evidence_dir.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def _create_test_png(self, path, width, height, color=(255, 0, 0)):
        """Helper to create a minimal test PNG image using standard library"""
        signature = b'\x89PNG\r\n\x1a\n'

        # IHDR chunk
        ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
        ihdr_chunk = self._make_png_chunk(b'IHDR', ihdr_data)

        # IDAT chunk with compressed pixel data
        scanline = b'\x00' + (bytes(color) * width)
        raw_data = scanline * height
        compressed = zlib.compress(raw_data)
        idat_chunk = self._make_png_chunk(b'IDAT', compressed)

        # IEND chunk
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

    def test_declared_pngs_assemble_contact_sheet_no_run_captures(self):
        """T1: Declared PNG fixtures with no run captures produce contact sheet and packet references it"""
        # Create declared evidence images
        evidence1 = self._create_test_png(self.evidence_dir / "evidence1.png", 800, 600)
        evidence2 = self._create_test_png(self.evidence_dir / "evidence2.png", 1000, 800)

        # Work order declaring evidence images
        wo = WorkOrder(
            id="wo-declared-001",
            kind="feature",
            title="Declared evidence test",
            source="test",
            description="Test declared evidence images reach reviewer-design",
            spec_path=".openspec/specs/test-feature/spec.md",
            evidence_images=["evidence/evidence1.png", "evidence/evidence2.png"]
        )

        # Empty run directory (no capture-*.png files)
        run_dir = self.project / "runs" / wo.id
        run_dir.mkdir(parents=True)

        files_changed = [{"file": "src/app.py", "added": 10, "removed": 5}]

        # Prepare reviewer-design step
        packet, contact_sheet_path = prepare_reviewer_design_step(
            self.project, wo, files_changed, captures=[]
        )

        # Verify contact sheet was assembled from declared evidence
        self.assertTrue(
            contact_sheet_path.exists(),
            "Contact sheet must be assembled from declared evidence images"
        )
        self.assertEqual(
            contact_sheet_path.name,
            "contact-sheet.png",
            "Contact sheet must be named contact-sheet.png"
        )

        # Verify packet references the contact sheet
        self.assertIn(
            "contact-sheet.png", packet,
            "Packet must reference the assembled contact sheet"
        )


class TestDeclaredEvidenceMissingFailure(unittest.TestCase):
    """T2/S2: Missing declared image fails preparation with declared_evidence_missing"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name) / "proj"
        self.project.mkdir(parents=True)

        # Setup minimal project structure
        (self.project / "design").mkdir()
        (self.project / "design" / "DESIGN.md").write_text("# Design\n")
        (self.project / "design" / "tokens.json").write_text("{}")
        (self.project / "brain").mkdir()
        (self.project / "brain" / "learnings.json").write_text("[]")
        (self.project / ".openspec" / "specs" / "test-feature").mkdir(parents=True)
        (self.project / ".openspec" / "specs" / "test-feature" / "spec.md").write_text("# Test\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_declared_image_fails_with_named_error(self):
        """T2: Missing declared image fails preparation with declared_evidence_missing and path in detail"""
        from anvil.runner import DeclaredEvidenceMissing

        # Work order declaring evidence that does not exist
        wo = WorkOrder(
            id="wo-missing-001",
            kind="feature",
            title="Missing evidence test",
            source="test",
            description="Test missing declared evidence fails",
            spec_path=".openspec/specs/test-feature/spec.md",
            evidence_images=["evidence/does-not-exist.png"]
        )

        run_dir = self.project / "runs" / wo.id
        run_dir.mkdir(parents=True)

        files_changed = [{"file": "src/app.py", "added": 5, "removed": 2}]

        # Should fail with declared_evidence_missing
        with self.assertRaises(DeclaredEvidenceMissing) as ctx:
            prepare_reviewer_design_step(
                self.project, wo, files_changed, captures=[]
            )

        # Verify error contains the missing path
        error_msg = str(ctx.exception)
        self.assertIn(
            "does-not-exist.png", error_msg,
            "Error must identify the missing declared evidence path"
        )


class TestPacketListsDeclaredPaths(unittest.TestCase):
    """T3/S3: Packet lists contact sheet and each declared path individually"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name) / "proj"
        self.project.mkdir(parents=True)

        # Setup project structure
        (self.project / "design").mkdir()
        (self.project / "design" / "DESIGN.md").write_text("# Design\n")
        (self.project / "design" / "tokens.json").write_text("{}")
        (self.project / "brain").mkdir()
        (self.project / "brain" / "learnings.json").write_text("[]")
        (self.project / ".openspec" / "specs" / "test-feature").mkdir(parents=True)
        (self.project / ".openspec" / "specs" / "test-feature" / "spec.md").write_text("# Test\n")

        # Create evidence directory with test PNGs
        self.evidence_dir = self.project / "evidence"
        self.evidence_dir.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def _create_test_png(self, path, width, height):
        """Helper to create a minimal test PNG"""
        signature = b'\x89PNG\r\n\x1a\n'
        ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
        ihdr_chunk = self._make_png_chunk(b'IHDR', ihdr_data)
        scanline = b'\x00' + (b'\xff\x00\x00' * width)
        compressed = zlib.compress(scanline * height)
        idat_chunk = self._make_png_chunk(b'IDAT', compressed)
        iend_chunk = self._make_png_chunk(b'IEND', b'')
        path.write_bytes(signature + ihdr_chunk + idat_chunk + iend_chunk)
        return path

    def _make_png_chunk(self, chunk_type, data):
        """Create a PNG chunk with CRC"""
        length = struct.pack('>I', len(data))
        chunk = chunk_type + data
        crc = struct.pack('>I', zlib.crc32(chunk) & 0xffffffff)
        return length + chunk + crc

    def test_packet_lists_contact_sheet_and_declared_paths(self):
        """T3: Packet Evidence section lists contact sheet and all declared paths individually"""
        # Create three declared evidence images
        evidence1 = self._create_test_png(self.evidence_dir / "evidence1.png", 100, 100)
        evidence2 = self._create_test_png(self.evidence_dir / "evidence2.png", 100, 100)
        evidence3 = self._create_test_png(self.evidence_dir / "evidence3.png", 100, 100)

        wo = WorkOrder(
            id="wo-packet-paths-001",
            kind="feature",
            title="Packet paths test",
            source="test",
            description="Test packet lists all declared paths",
            spec_path=".openspec/specs/test-feature/spec.md",
            evidence_images=[
                "evidence/evidence1.png",
                "evidence/evidence2.png",
                "evidence/evidence3.png"
            ]
        )

        run_dir = self.project / "runs" / wo.id
        run_dir.mkdir(parents=True)

        files_changed = [{"file": "src/app.py", "added": 5, "removed": 2}]

        # Prepare reviewer-design step
        packet, contact_sheet_path = prepare_reviewer_design_step(
            self.project, wo, files_changed, captures=[]
        )

        # Verify packet contains Evidence section
        self.assertIn("## Evidence", packet, "Packet must contain Evidence section")

        # Verify contact sheet is listed
        self.assertIn("contact-sheet.png", packet, "Packet must list contact sheet")

        # Verify each declared path is listed individually
        self.assertIn("evidence1.png", packet, "Packet must list evidence1.png")
        self.assertIn("evidence2.png", packet, "Packet must list evidence2.png")
        self.assertIn("evidence3.png", packet, "Packet must list evidence3.png")


class TestReviewerPacketsDeclaredInputsSection(unittest.TestCase):
    """T4/S4: Reviewer packets carry Declared evidence inputs section"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name) / "proj"
        self.project.mkdir(parents=True)

        # Setup project structure
        (self.project / "design").mkdir()
        (self.project / "design" / "DESIGN.md").write_text("# Design\n")
        (self.project / "brain").mkdir()
        (self.project / "brain" / "learnings.json").write_text("[]")

        # Create evidence directory with test PNGs
        self.evidence_dir = self.project / "evidence"
        self.evidence_dir.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def _create_test_png(self, path, width, height):
        """Helper to create a minimal test PNG"""
        signature = b'\x89PNG\r\n\x1a\n'
        ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
        ihdr_chunk = self._make_png_chunk(b'IHDR', ihdr_data)
        scanline = b'\x00' + (b'\xff\x00\x00' * width)
        compressed = zlib.compress(scanline * height)
        idat_chunk = self._make_png_chunk(b'IDAT', compressed)
        iend_chunk = self._make_png_chunk(b'IEND', b'')
        path.write_bytes(signature + ihdr_chunk + idat_chunk + iend_chunk)
        return path

    def _make_png_chunk(self, chunk_type, data):
        """Create a PNG chunk with CRC"""
        length = struct.pack('>I', len(data))
        chunk = chunk_type + data
        crc = struct.pack('>I', zlib.crc32(chunk) & 0xffffffff)
        return length + chunk + crc

    def test_reviewer_facts_packet_has_declared_inputs_section(self):
        """T4: Another reviewer station packet contains Declared evidence inputs section"""
        from anvil.runner import _packet_text

        # Create declared evidence images
        evidence1 = self._create_test_png(self.evidence_dir / "evidence1.png", 100, 100)
        evidence2 = self._create_test_png(self.evidence_dir / "evidence2.png", 100, 100)

        wo = WorkOrder(
            id="wo-reviewer-facts-001",
            kind="feature",
            title="Reviewer facts packet test",
            source="test",
            description="Test reviewer-facts packet has declared inputs section",
            evidence_images=[
                "evidence/evidence1.png",
                "evidence/evidence2.png"
            ]
        )

        station_id = "reviewer-facts"
        prompt = "Review the facts"
        steps = []

        # Build packet for reviewer-facts
        packet = _packet_text(station_id, prompt, wo, steps)

        # Verify packet contains Declared evidence inputs section
        self.assertIn(
            "## Declared evidence inputs", packet,
            "Packet must contain Declared evidence inputs section"
        )

        # Verify declared paths are listed
        self.assertIn("evidence1.png", packet, "Packet must list evidence1.png")
        self.assertIn("evidence2.png", packet, "Packet must list evidence2.png")


class TestReviewOnlyPipeline(unittest.TestCase):
    """T5/S5: Review only content pipeline loads and has correct topological order"""

    def test_content_film_review_pipeline_loads_and_validates(self):
        """T5: New pipeline loads, validates, and topological order matches spec"""
        from anvil.pipeline import load_pipeline
        from pathlib import Path

        ROOT = Path(__file__).resolve().parent.parent

        # Pipeline file path
        pipeline_path = ROOT / "pipelines" / "content-film-review.json"

        # Known stations (subset relevant for this pipeline)
        known_stations = {
            "intake", "reviewer-design", "reviewer-facts",
            "approver", "triage-human", "publisher", "observer"
        }

        # Load pipeline
        pipeline = load_pipeline(pipeline_path, known_stations=known_stations)

        # Verify pipeline loaded
        self.assertIsNotNone(pipeline, "Pipeline must load successfully")

        # Verify topological order matches spec exactly:
        # intake; parallel [reviewer-design, reviewer-facts]; approver; triage-human; publisher; observer
        order = pipeline.topological_order()

        # Expected order:
        # 1. intake (first)
        # 2. reviewer-design and reviewer-facts (parallel, both depend on intake)
        # 3. approver (depends on reviewers)
        # 4. triage-human (depends on approver)
        # 5. publisher (depends on triage-human)
        # 6. observer (last, depends on publisher)

        self.assertEqual(order[0], "intake", "First stage must be intake")

        # reviewer-design and reviewer-facts should be at positions 1 and 2 (parallel)
        reviewers = {order[1], order[2]}
        self.assertEqual(
            reviewers, {"reviewer-design", "reviewer-facts"},
            "Positions 1 and 2 must be reviewer-design and reviewer-facts in parallel"
        )

        self.assertEqual(order[3], "approver", "Position 3 must be approver")
        self.assertEqual(order[4], "triage-human", "Position 4 must be triage-human")
        self.assertEqual(order[5], "publisher", "Position 5 must be publisher")
        self.assertEqual(order[6], "observer", "Position 6 must be observer")

        # Verify no authoring stations in the pipeline
        authoring_stations = {
            "brief-writer", "researcher", "writer", "media-producer", "builder"
        }
        pipeline_stations = set(order)
        authoring_in_pipeline = authoring_stations.intersection(pipeline_stations)

        self.assertEqual(
            len(authoring_in_pipeline), 0,
            f"No authoring stations must appear in pipeline. Found: {authoring_in_pipeline}"
        )

    def test_all_pipelines_valid_count_increased(self):
        """T5: All pipelines still validate and count increased by one"""
        from anvil.pipeline import load_pipeline
        from pathlib import Path

        ROOT = Path(__file__).resolve().parent.parent
        pipelines_dir = ROOT / "pipelines"

        # Load all pipeline files
        pipeline_files = list(pipelines_dir.glob("*.json"))

        # Count must be at least 9 (8 existing + 1 new)
        self.assertGreaterEqual(
            len(pipeline_files), 9,
            "Pipeline count must be at least 9 (8 existing + 1 new content-film-review)"
        )

        # Verify content-film-review.json exists
        content_film_review_path = pipelines_dir / "content-film-review.json"
        self.assertTrue(
            content_film_review_path.exists(),
            "content-film-review.json must exist"
        )

        # Verify all pipelines are valid JSON
        for pipeline_file in pipeline_files:
            try:
                with open(pipeline_file) as f:
                    pipeline_data = json.load(f)
                self.assertIn("stages", pipeline_data, f"{pipeline_file.name} must have stages")
            except Exception as e:
                self.fail(f"Pipeline {pipeline_file.name} failed to load: {e}")


if __name__ == '__main__':
    unittest.main()
