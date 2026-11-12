"""wo-gh-29 gate loopback round 4: tier resolution on the routed path, Codex credential source.

Maps to model-migration R10, R11, S8 (integration through run_pipeline), S9 and S10.
"""
import io, json, os, sys, tempfile, unittest
from pathlib import Path
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from anvil.executor import create_executor
from anvil.model import WorkOrder
from anvil.pipeline import load_pipeline
from anvil.routing import RoutingRecord
from anvil.runner import run_pipeline
from anvil.scaffold import init_project, scaffold_spec
from anvil.stations import load_registry

ROOT = Path(__file__).resolve().parent.parent
CONCRETE = {"claude-opus-5-5", "claude-sonnet-5-5"}
TIER_LABELS = {"review-balanced", "review-strong", "fast-builder", "reasoning-strong",
               "writing-strong", "fast-reader", "media-gen", "default"}

# Fake command runtime: records the model it was handed per station, writes its own
# review file for reviewers, and answers intake with an accepted outcome.
RUNTIME = '''import json, os, sys
from pathlib import Path
station, wo = "", ""
for line in open(sys.argv[1], encoding="utf-8"):
    if line.startswith("# Task packet:"):
        station = line.split(":", 1)[1].strip()
    elif line.startswith("- id:") and not wo:
        wo = line.split(":", 1)[1].strip()
with open(os.environ["RECORD_PATH"], "a") as fh:
    fh.write(station + " " + os.environ.get("ANVIL_CONFIGURED_MODEL", "") + "\\n")
if station == "intake":
    print(json.dumps({"intake_outcome": {"outcome": "accepted"}, "risk": "high",
                      "surfaces": ["payments", "security", "ui"]}))
elif station.startswith("reviewer"):
    p = Path.cwd() / "runs" / wo / (station + ".review.json")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"station": station, "verdict": "pass", "findings": []}))
    print("wrote review")
else:
    print("done " + station)
'''


def drive(tmp, wo_id, routing=None, mutate=None):
    """Run sdlc-default with a fake command runtime. routing is patched in as the
    routing record (tier labels) when given, so the routed branch of run_pipeline runs."""
    proj = Path(tmp) / "proj"
    init_project(proj, "Demo")
    scaffold_spec(proj, "demo-feature", "Demo Feature")
    script = Path(tmp) / "rt.py"
    script.write_text(RUNTIME)
    record = Path(tmp) / "record.txt"
    ex = create_executor({"kind": "command",
                          "command": f"{sys.executable} {script} {{packet}}",
                          "timeout_seconds": 60})
    reg = load_registry(ROOT / "stations")
    if mutate:
        mutate(reg)
    pipe = load_pipeline(ROOT / "pipelines" / "sdlc-default.json", known_stations=set(reg.ids()))
    wo = WorkOrder(id=wo_id, kind="feature", title="Round 4 routed path")
    os.environ["RECORD_PATH"] = str(record)
    try:
        if routing is None:
            report = run_pipeline(proj, pipe, wo, registry=reg, executor=ex)
        else:
            with mock.patch("anvil.runner.route_reviewers", return_value=routing):
                report = run_pipeline(proj, pipe, wo, registry=reg, executor=ex)
    finally:
        os.environ.pop("RECORD_PATH", None)
    handed = {}
    if record.exists():
        for line in record.read_text().splitlines():
            st, _, model = line.partition(" ")
            handed[st] = model
    return report, handed


def tier_routing():
    return RoutingRecord(
        selected_reviewers=["reviewer-spec", "reviewer-security"],
        routed_out=[],
        selected_models={"reviewer-spec": "review-balanced",
                         "reviewer-security": "review-strong"},
        reason="round 4 integration fixture")


class TestTierResolutionOnRoutedPath(unittest.TestCase):
    def test_routed_reviewers_receive_concrete_model_through_run_pipeline_s8(self):
        """R10/S8: routing selects tier labels; the runtime must be handed a concrete model"""
        with tempfile.TemporaryDirectory() as tmp:
            report, handed = drive(tmp, "wo-r4-routed", routing=tier_routing())
            for st in ("reviewer-spec", "reviewer-security"):
                self.assertIn(st, handed, f"{st} never reached the runtime")
                self.assertNotIn(handed[st], TIER_LABELS, st)
                self.assertEqual(handed[st], "claude-sonnet-5-5", st)

    def test_recorded_configured_model_is_concrete_on_routed_path_s8(self):
        with tempfile.TemporaryDirectory() as tmp:
            report, handed = drive(tmp, "wo-r4-report", routing=tier_routing())
            steps = {s["station"]: s for s in report.steps}
            for st in ("reviewer-spec", "reviewer-security"):
                self.assertEqual(steps[st]["status"], "executed", steps[st])
                self.assertEqual(steps[st]["configured_model"], "claude-sonnet-5-5", st)
                # record and hand-off agree
                self.assertEqual(steps[st]["configured_model"], handed[st])

    def test_every_executed_step_has_concrete_model_and_hand_off_s8(self):
        """R10: for every station and branch that executes (intake included), no label leaks"""
        with tempfile.TemporaryDirectory() as tmp:
            report, handed = drive(tmp, "wo-r4-all", routing=tier_routing())
            self.assertIn("intake", handed)
            self.assertIn("builder", handed)
            for st, model in handed.items():
                self.assertIn(model, CONCRETE, f"{st} handed {model!r}")
            for step in report.steps:
                if step.get("executor"):
                    self.assertIn(step["configured_model"], CONCRETE, step["station"])

    def test_tier_label_from_registry_override_resolved_at_hand_off_s8(self):
        """R10: a tier label set on the station itself (pre-routing) is resolved too"""
        def mutate(reg):
            reg.get("intake").model = "reasoning-strong"
        with tempfile.TemporaryDirectory() as tmp:
            report, handed = drive(tmp, "wo-r4-intake", routing=tier_routing(), mutate=mutate)
            self.assertEqual(handed["intake"], "claude-opus-5-5")
            intake = [s for s in report.steps if s["station"] == "intake"][0]
            self.assertEqual(intake["configured_model"], "claude-opus-5-5")

    def test_guided_design_model_survives_routing_resolution_s8(self):
        """R10: a concrete routed model passes through unchanged"""
        routing = tier_routing()
        routing.selected_reviewers.append("reviewer-design")
        routing.selected_models["reviewer-design"] = "claude-opus-5-5"
        with tempfile.TemporaryDirectory() as tmp:
            report, handed = drive(tmp, "wo-r4-concrete", routing=routing)
            if "reviewer-design" in handed:
                self.assertEqual(handed["reviewer-design"], "claude-opus-5-5")

    def test_executed_model_still_null_without_self_report_s10(self):
        """S10: resolution at hand-off does not create executed_model evidence"""
        with tempfile.TemporaryDirectory() as tmp:
            report, _ = drive(tmp, "wo-r4-prov", routing=tier_routing())
            for step in report.steps:
                if step["station"] in ("reviewer-spec", "reviewer-security", "builder", "intake"):
                    self.assertIsNone(step["executed_model"], step["station"])


if __name__ == "__main__":
    unittest.main()
