import tempfile
import unittest
from pathlib import Path

from anvil.approver import needs_human
from anvil.gates import brief_gate, disclosure_gate, human_gate
from anvil.model import WorkOrder
from anvil.pipeline import load_pipeline
from anvil.stations import load_registry

FACTORY = Path(__file__).resolve().parent.parent
CONTENT_STATIONS = ["brief-writer", "researcher", "writer", "media-producer",
                    "reviewer-facts", "reviewer-voice", "reviewer-platform", "reviewer-brand", "publisher"]


class ContentFactoryTests(unittest.TestCase):
    def test_s1_content_stations_in_registry(self):
        """content-factory S1: content stations share the registry"""
        registry = load_registry(FACTORY / "stations")
        for station in CONTENT_STATIONS:
            self.assertIn(station, registry)
        self.assertIn("builder", registry)

    def test_s2_content_pipelines_validate(self):
        """content-factory S2: four parallel reviewers, short line reuses two"""
        registry = load_registry(FACTORY / "stations")
        full = load_pipeline(FACTORY / "pipelines" / "content-default.json", known_stations=set(registry.ids()))
        order = full.topological_order()
        for reviewer in ("reviewer-facts", "reviewer-voice", "reviewer-platform", "reviewer-brand"):
            self.assertIn(reviewer, order)
        short = load_pipeline(FACTORY / "pipelines" / "content-short.json", known_stations=set(registry.ids()))
        short_order = short.topological_order()
        self.assertIn("reviewer-facts", short_order)
        self.assertNotIn("media-producer", short_order)

    def test_s3_brief_and_disclosure_gates(self):
        """content-factory S3: gates pass on a complete piece and fail clearly"""
        with tempfile.TemporaryDirectory() as tmp:
            piece = Path(tmp) / "content" / "demo"
            piece.mkdir(parents=True)
            (piece / "brief.md").write_text("Audience: builders\nAngle: factories beat prompts\nClaims:\n- Code validates\n")
            (piece / "draft.md").write_text("Draft text.\n\nDisclosure: this piece is AI generated and human reviewed.\n")
            self.assertTrue(brief_gate(tmp, "demo")[0])
            self.assertTrue(disclosure_gate(tmp, "demo")[0])
            (piece / "draft.md").write_text("Draft with no disclosure.\n")
            self.assertFalse(disclosure_gate(tmp, "demo")[0])
            self.assertFalse(brief_gate(tmp, "missing")[0])

    def test_s4_publishing_requires_human(self):
        """content-factory S4: publishing hint forces the human gate"""
        wo = WorkOrder(id="wo-content-1", kind="content", title="Launch post", risk_hints=["publishing"])
        self.assertEqual(human_gate(wo), "required")
        self.assertTrue(needs_human(wo, "approved"))


if __name__ == "__main__":
    unittest.main()
