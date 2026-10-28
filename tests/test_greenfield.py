import json
import tempfile
import unittest
from pathlib import Path

from anvil.blueprints import load_blueprints, get_blueprint
from anvil.model import WorkOrder
from anvil.pipeline import load_pipeline
from anvil.scaffold import new_project
from anvil.stations import load_registry

FACTORY = Path(__file__).resolve().parent.parent


class GreenfieldTests(unittest.TestCase):
    def test_s1_idea_work_order_accepted(self):
        """greenfield-projects S1: idea kind validates"""
        wo = WorkOrder(id="wo-idea-1", kind="idea", title="A habit tracker for divers")
        self.assertEqual(wo.kind, "idea")
        with self.assertRaises(ValueError):
            WorkOrder(id="wo-x", kind="nonsense", title="Nope")

    def test_s2_blueprint_catalog_loads(self):
        """greenfield-projects S2: catalog loads, unknown id errors"""
        blueprints = load_blueprints(FACTORY / "blueprints")
        self.assertGreaterEqual(len(blueprints), 3)
        self.assertIn("cloudflare-worker", blueprints)
        with self.assertRaises(ValueError):
            get_blueprint(FACTORY / "blueprints", "does-not-exist")

    def test_s3_new_project_scaffolds_from_blueprint(self):
        """greenfield-projects S3: BLUEPRINT.md, brain seed, pipeline, first spec"""
        bp = get_blueprint(FACTORY / "blueprints", "python-service")
        with tempfile.TemporaryDirectory() as tmp:
            root = new_project(Path(tmp) / "demo", "Demo", bp, idea="Track habits")
            self.assertTrue((root / "BLUEPRINT.md").exists())
            self.assertIn("Track habits", (root / "brain" / "project.md").read_text())
            config = json.loads((root / "anvil.json").read_text())
            self.assertEqual(config["pipeline"], "greenfield")
            self.assertTrue((root / ".openspec" / "specs" / "core-service" / "spec.md").exists())

    def test_s4_greenfield_pipeline_validates(self):
        """greenfield-projects S4: order starts intake, blueprint, spec-writer"""
        registry = load_registry(FACTORY / "stations")
        pipe = load_pipeline(FACTORY / "pipelines" / "greenfield.json", known_stations=set(registry.ids()))
        order = pipe.topological_order()
        self.assertEqual(order[:3], ["intake", "blueprint", "spec-writer"])
        for reviewer in ("reviewer-spec", "reviewer-security", "reviewer-tests", "reviewer-architecture"):
            self.assertIn(reviewer, order)


if __name__ == "__main__":
    unittest.main()
