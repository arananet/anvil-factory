"""wo-gh-30 verification round 2: per-step model evidence on the run report.

Maps to model-migration-verification R2, R3, R5, R6 and scenarios S1, S2, S4, S5.
Round 2 correction (R6): the builder policy is claude-opus-5-5 on non-UI work and
openai/gpt-6.1-sol on UI-surface work, with executed_model self-reported by the
runtime and equal to the assignment. Round 1 wrongly encoded opus for every case.
"""
import json, os, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from anvil.config import apply_overrides, load_anvil_config
from anvil.executor import create_executor
from anvil.model import WorkOrder
from anvil.pipeline import load_pipeline
from anvil.runner import run_pipeline
from anvil.scaffold import init_project, scaffold_spec
from anvil.stations import load_registry

ROOT = Path(__file__).resolve().parent.parent
UI_BUILDER = "openai/gpt-6.1-sol"
NON_UI_BUILDER = "claude-opus-5-5"
SONNET = "claude-sonnet-5-5"
TIER_LABELS = {"review-cheap", "review-balanced", "review-strong", "fast-builder",
               "reasoning-strong", "writing-strong", "fast-reader", "media-gen", "default"}

# Fake runtime: self-reports the model it was handed (ANVIL_CONFIGURED_MODEL) as a
# JSON "model" field, as a real runtime would; SILENT stations report nothing.
RUNTIME = '''import json, os, sys
from pathlib import Path
station, wo = "", ""
for line in open(sys.argv[1], encoding="utf-8"):
    if line.startswith("# Task packet:"):
        station = line.split(":", 1)[1].strip()
    elif line.startswith("- id:") and not wo:
        wo = line.split(":", 1)[1].strip()
model = os.environ.get("ANVIL_CONFIGURED_MODEL", "")
silent = station in os.environ.get("SILENT", "").split(",")
if station == "intake":
    print(json.dumps({"intake_outcome": {"outcome": "accepted"}, "risk": "low",
                      "surfaces": json.loads(os.environ["SURFACES"])}))
elif station.startswith("reviewer"):
    p = Path.cwd() / "runs" / wo / (station + ".review.json")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"station": station, "verdict": "pass", "findings": []}))
    print("wrote review")
else:
    print("done " + station)
if not silent and station != "intake":
    print(json.dumps({"model": model}))
'''


def drive(tmp, wo_id, surfaces, silent=""):
    proj = Path(tmp) / "proj"
    init_project(proj, "Demo")
    scaffold_spec(proj, "demo-feature", "Demo Feature")
    script = Path(tmp) / "rt.py"
    script.write_text(RUNTIME)
    ex = create_executor({"kind": "command",
                          "command": f"{sys.executable} {script} {{packet}}",
                          "timeout_seconds": 60})
    reg = load_registry(ROOT / "stations")
    # Same as the CLI: the standing anvil.yaml station models override the registry.
    apply_overrides(reg, load_anvil_config(ROOT / "anvil.yaml"))
    pipe = load_pipeline(ROOT / "pipelines" / "sdlc-default.json", known_stations=set(reg.ids()))
    wo = WorkOrder(id=wo_id, kind="feature", title="Verification evidence")
    os.environ["SURFACES"] = json.dumps(surfaces)
    os.environ["SILENT"] = silent
    try:
        report = run_pipeline(proj, pipe, wo, registry=reg, executor=ex)
    finally:
        os.environ.pop("SURFACES", None)
        os.environ.pop("SILENT", None)
    return report


def expected(station, surfaces):
    if station == "builder":
        return UI_BUILDER if "ui" in surfaces else NON_UI_BUILDER
    if station in ("reviewer-design", "reviewer-ux"):
        return UI_BUILDER
    return SONNET


def executed(report):
    return [s for s in report.steps if s.get("executor")]


class TestBuilderPolicyBySurface(unittest.TestCase):
    def _builder(self, surfaces, wo_id):
        with tempfile.TemporaryDirectory() as tmp:
            report = drive(tmp, wo_id, surfaces)
            b = [s for s in report.steps if s["station"] == "builder"]
            self.assertTrue(b, "builder step missing")
            return b[0]

    def test_ui_surface_builder_is_design_model_s2(self):
        b = self._builder(["ui"], "wo-v2-ui")
        self.assertEqual(b["configured_model"], UI_BUILDER)
        self.assertEqual(b["executed_model"], UI_BUILDER)

    def test_non_ui_builder_is_opus_s2(self):
        b = self._builder([], "wo-v2-nonui")
        self.assertEqual(b["configured_model"], NON_UI_BUILDER)
        self.assertEqual(b["executed_model"], NON_UI_BUILDER)

    def test_wrong_builder_value_is_rejected_s2(self):
        """The encoded policy fails on opus for UI work and on sol for non-UI work."""
        self.assertNotEqual(expected("builder", ["ui"]), NON_UI_BUILDER)
        self.assertNotEqual(expected("builder", ["backend"]), UI_BUILDER)


class TestPerStepAgreement(unittest.TestCase):
    def _check(self, surfaces, wo_id):
        with tempfile.TemporaryDirectory() as tmp:
            report = drive(tmp, wo_id, surfaces)
            steps = executed(report)
            self.assertTrue(steps, "no executed steps")
            for s in steps:
                st = s["station"]
                if st == "intake":
                    continue  # deterministic here: intake is not a model-assigned run
                want = expected(st, surfaces)
                self.assertEqual(s["configured_model"], want, f"{st} configured")
                self.assertIsNotNone(s["executed_model"], f"{st}: missing self-report")
                self.assertEqual(s["executed_model"], s["configured_model"], f"{st} disagreement")
                self.assertNotIn(s["configured_model"], TIER_LABELS, f"{st} tier label leaked")

    def test_every_step_agrees_on_ui_work_s1_s4(self):
        self._check(["ui"], "wo-v2-all-ui")

    def test_every_step_agrees_on_non_ui_work_s1_s4(self):
        self._check([], "wo-v2-all-nonui")


class TestMissingSelfReport(unittest.TestCase):
    def test_silent_runtime_leaves_executed_model_null_s5(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = drive(tmp, "wo-v2-silent", ["ui"], silent="builder")
            b = [s for s in report.steps if s["station"] == "builder"][0]
            self.assertIsNone(b["executed_model"])


if __name__ == "__main__":
    unittest.main()
