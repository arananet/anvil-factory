import json, tempfile, unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from anvil.model import slugify, WorkOrder, Review
from anvil.pipeline import Pipeline, load_pipeline
from anvil.stations import load_registry
from anvil.gates import spec_gate, tdd_gate, review_gate, human_gate
from anvil.approver import aggregate, needs_human
from anvil.scaffold import init_project, scaffold_spec
from anvil.runner import run_pipeline
from anvil.config import load_anvil_config, apply_overrides

ROOT = Path(__file__).resolve().parent.parent

def make_project(tmp):
    proj = Path(tmp) / "proj"
    init_project(proj, "Demo")
    scaffold_spec(proj, "demo-feature", "Demo Feature")
    # Make the spec pass: it already has Status, Scenario and S1
    return proj

class TestSlugify(unittest.TestCase):
    def test_slugify_s4(self):
        """project-scaffolding S4 and factory-gates coverage"""
        self.assertEqual(slugify("Hello, World! Test"), "hello-world-test")
        self.assertEqual(slugify("  Taskline API  "), "taskline-api")

class TestPipeline(unittest.TestCase):
    KNOWN = {"intake","builder","approver","spec-writer"}
    def write_pipe(self, tmp, data):
        p = Path(tmp) / "p.json"; p.write_text(json.dumps(data)); return p
    def test_valid_s1(self):
        """factory-pipeline-engine S1"""
        with tempfile.TemporaryDirectory() as tmp:
            f = self.write_pipe(tmp, {"name":"x","stages":[{"station":"intake"},{"parallel":["builder","spec-writer"]},{"station":"approver"}]})
            pipe = load_pipeline(f, known_stations=self.KNOWN)
            self.assertEqual(pipe.topological_order(), ["intake","builder","spec-writer","approver"])
    def test_unknown_s2(self):
        """factory-pipeline-engine S2"""
        with tempfile.TemporaryDirectory() as tmp:
            f = self.write_pipe(tmp, {"name":"x","stages":[{"station":"nope"}]})
            with self.assertRaises(ValueError) as cm: load_pipeline(f, known_stations=self.KNOWN)
            self.assertIn("Unknown station", str(cm.exception))
    def test_duplicate_s3(self):
        """factory-pipeline-engine S3"""
        with tempfile.TemporaryDirectory() as tmp:
            f = self.write_pipe(tmp, {"name":"x","stages":[{"station":"intake"},{"station":"intake"}]})
            with self.assertRaises(ValueError) as cm: load_pipeline(f, known_stations=self.KNOWN)
            self.assertIn("Duplicate station", str(cm.exception))
    def test_empty_s4(self):
        """factory-pipeline-engine S4"""
        with tempfile.TemporaryDirectory() as tmp:
            f = self.write_pipe(tmp, {"name":"x","stages":[]})
            with self.assertRaises(ValueError) as cm: load_pipeline(f, known_stations=self.KNOWN)
            self.assertIn("empty", str(cm.exception).lower())
    def test_parallel_s5(self):
        """factory-pipeline-engine S5"""
        with tempfile.TemporaryDirectory() as tmp:
            f = self.write_pipe(tmp, {"name":"x","stages":[{"parallel":["builder"]}]})
            with self.assertRaises(ValueError) as cm: load_pipeline(f, known_stations=self.KNOWN)
            self.assertIn("at least 2", str(cm.exception))

class TestRegistry(unittest.TestCase):
    def test_registry_s6(self):
        """factory-pipeline-engine S6: 23 stations including scout, blueprint and content"""
        reg = load_registry(ROOT / "stations")
        self.assertEqual(len(reg), 23)
        self.assertIn("scout", reg)
        self.assertIn("blueprint", reg)
        self.assertIn("writer", reg)
        self.assertIn("publisher", reg)
        for pipe_file in (ROOT / "pipelines").glob("*.json"):
            load_pipeline(pipe_file, known_stations=set(reg.ids()))

class TestConfigOverride(unittest.TestCase):
    def test_override_s8(self):
        """factory-pipeline-engine S8: Core Four override"""
        reg = load_registry(ROOT / "stations")
        self.assertEqual(reg.get("builder").model, "fast-builder")
        cfg = {"stations": {"builder": {"model": "custom-model-x", "context": ["docs/"], "tools": ["git"], "prompt": "custom/PROMPT.md"}}}
        apply_overrides(reg, cfg)
        self.assertEqual(reg.get("builder").model, "custom-model-x")
        self.assertEqual(reg.get("builder").context, ["docs/"])
        self.assertEqual(reg.get("builder").tools, ["git"])

class TestGates(unittest.TestCase):
    def test_spec_pass_s1(self):
        """factory-gates S1"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            ok, _ = spec_gate(proj, "demo-feature"); self.assertTrue(ok)
    def test_spec_fail_s2(self):
        """factory-gates S2"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            spec = proj / ".openspec" / "specs" / "demo-feature" / "spec.md"
            spec.write_text("Status: draft\nNo scenarios here.\n")
            ok, _ = spec_gate(proj, "demo-feature"); self.assertFalse(ok)
    def test_tdd_pass_s3(self):
        """factory-gates S3: S1 referenced"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            (proj / "tests" / "test_demo.py").write_text("# S1\n")
            ok, detail = tdd_gate(proj, "demo-feature"); self.assertTrue(ok, detail)
    def test_tdd_fail_s4(self):
        """factory-gates S4"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            (proj / "tests" / "test_demo.py").write_text("# nothing\n")
            ok, detail = tdd_gate(proj, "demo-feature"); self.assertFalse(ok); self.assertIn("S1", detail)
    def test_review_and_approver_s5(self):
        """factory-gates S5"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            base = proj / "reviews" / "demo-feature"; base.mkdir(parents=True)
            for s in ["reviewer-spec","reviewer-security","reviewer-tests","reviewer-architecture"]:
                (base / f"{s}.json").write_text(json.dumps({"station":s,"verdict":"pass","findings":["ok"]}))
            ok, _ = review_gate(proj, "demo-feature"); self.assertTrue(ok)
            self.assertEqual(aggregate([Review("a","pass",[]), Review("b","pass",[])]), "approved")
            self.assertEqual(aggregate([Review("a","fail",[])]), "rejected")
            self.assertEqual(aggregate([Review("a","changes_requested",[])]), "changes_requested")
    def test_human_s6(self):
        """factory-gates S6"""
        wo = WorkOrder(id="wo-1", kind="feature", title="Pay", risk_hints=["payments"])
        self.assertEqual(human_gate(wo), "required")
        self.assertTrue(needs_human(wo, "approved"))
        wo2 = WorkOrder(id="wo-2", kind="task", title="Docs", risk_hints=[])
        self.assertEqual(human_gate(wo2), "not_required")
        self.assertFalse(needs_human(wo2, "approved"))
        self.assertTrue(needs_human(wo2, "rejected"))

class TestScaffold(unittest.TestCase):
    def test_init_s1_s2(self):
        """project-scaffolding S1 S2"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "p"; init_project(proj, "Demo")
            for rel in [".openspec/specs","brain/project.md","brain/glossary.md","brain/worklog.md","tests","reviews","anvil.json","anvil.yaml"]:
                self.assertTrue((proj / rel).exists(), rel)
            cfg = load_anvil_config(proj / "anvil.yaml")
            builder = cfg["stations"]["builder"]
            for key in ["context","model","prompt","tools"]:
                self.assertIn(key, builder)
    def test_new_spec_s3(self):
        """project-scaffolding S3"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            text = (proj / ".openspec" / "specs" / "demo-feature" / "spec.md").read_text()
            self.assertIn("Status:", text); self.assertIn("Demo Feature", text); self.assertIn("S1", text)

class TestRunner(unittest.TestCase):
    def test_dry_run_s7(self):
        """factory-pipeline-engine S7: packets, envelopes, swimlane, durations"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            pipe = load_pipeline(ROOT / "pipelines" / "sdlc-default.json", known_stations=set(reg.ids()))
            wo = WorkOrder(id="wo-test-001", kind="feature", title="Demo Feature")
            report = run_pipeline(proj, pipe, wo, registry=reg)
            run_dir = proj / "runs" / "wo-test-001"
            self.assertTrue((run_dir / "report.json").exists())
            self.assertTrue((run_dir / "swimlane.md").exists())
            self.assertTrue((run_dir / "spec-writer.packet.md").exists())
            self.assertTrue((run_dir / "builder.packet.md").exists())
            data = json.loads((run_dir / "report.json").read_text())
            self.assertTrue(all("duration_ms" in s for s in data["steps"]))
            self.assertEqual(data["max_loopbacks"], 2)
            # Envelopes
            env_dir = run_dir / "envelopes"
            envs = sorted(env_dir.glob("*.envelope.json"))
            self.assertTrue(envs)
            env = json.loads(envs[0].read_text())
            self.assertEqual(env["schema"], "anvil/envelope@1")
            for key in ["from_station","to_station","work_order_id","artifact_path","created_at"]:
                self.assertIn(key, env)
            statuses = {s["station"]: s["status"] for s in data["steps"]}
            self.assertEqual(statuses["spec-writer"], "packet_ready")
            swim = (run_dir / "swimlane.md").read_text()
            self.assertIn("null", swim); self.assertIn("spec-writer", swim)
    def test_loopback_s9(self):
        """factory-pipeline-engine S9: a fail review produced during the run loops back to builder"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            reg = load_registry(ROOT / "stations")
            pipe = load_pipeline(ROOT / "pipelines" / "sdlc-default.json", known_stations=set(reg.ids()))
            wo = WorkOrder(id="wo-loop-001", kind="bug", title="Broken Thing")
            report = run_pipeline(proj, pipe, wo, registry=reg, executor=FailReviewExecutor())
            self.assertNotEqual(report.verdict, "approved")
            self.assertEqual(report.verdict, "rejected")
            loopbacks = [s for s in report.steps if s["status"] == "loopback"]
            self.assertEqual(len(loopbacks), 1)
            self.assertEqual(loopbacks[0]["return_to"], "builder")
            self.assertIn("misses", loopbacks[0]["detail"])

class FailReviewExecutor:
    """Test double: reviewers return a fail review JSON, others plain text."""
    name = "command"
    def execute(self, packet_text, station_id, packet_path=None, output_path=None, cwd=None):
        if station_id.startswith("reviewer"):
            return {"output": json.dumps({"station": station_id, "verdict": "fail",
                    "findings": ["Implementation misses the required behaviour."]}), "usage": None}
        return {"output": "done", "usage": None}

if __name__ == "__main__":
    unittest.main()
