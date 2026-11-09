"""Regression tests for the station artifact contract (spec: station-artifact-contract).

Scenario map:
  S1  test_prose_channel_with_artifact_is_counted_s1
      test_missing_review_artifact_fails_fast_with_reason_s1
      test_empty_review_artifact_fails_fast_with_reason_s1
  S2  test_abbreviated_literal_bounces_builder_before_reviewers_s2
      test_full_literals_let_reviewers_run_s2
      test_no_declared_literals_behave_as_before_s2
  S3  test_uncounted_reviewer_is_never_silently_approved_s3
      test_all_reviewers_counted_still_approves_s3
      test_aggregate_honesty_unit_s3
  S4  (a) test_empty_captured_output_with_valid_review_json_s4a
      (b) test_extra_output_md_beside_review_file_s4b
      (c) test_builder_chat_summary_bounced_s4c
  S5  covered by the untouched existing suite; the healthy path is asserted in
      test_all_reviewers_counted_still_approves_s3.
"""
import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from anvil.executor import create_executor
from anvil.pipeline import load_pipeline
from anvil.runner import run_pipeline
from anvil.scaffold import init_project, scaffold_spec
from anvil.stations import load_registry

ROOT = Path(__file__).resolve().parent.parent
SHA = "67217b9d5c1e0f3a8b2d4e6f7a9c0b1d2e3f4a5b6c7d8e9f0a1b2c3d4c83b86f"

# Fake channel. Behavior per station comes from a JSON plan file:
#   plan[station] = {"stdout": str, "files": {relative_name: text}}
# Files are written into runs/<wo>/ (the directory of the packet). A marker
# line is appended to calls.log so tests can prove which stations ran.
FAKE = '''
import json, sys
from pathlib import Path
packet = Path(sys.argv[1]); plan = json.load(open(sys.argv[2], encoding="utf-8"))
station = ""
for line in packet.read_text(encoding="utf-8").splitlines():
    if line.startswith("# Task packet:"):
        station = line.split(":", 1)[1].strip(); break
run_dir = packet.parent
with open(Path(sys.argv[2]).parent / "calls.log", "a", encoding="utf-8") as fh:
    fh.write(station + "\\n")
spec = plan.get(station, {})
for name, text in spec.get("files", {}).items():
    (run_dir / name).write_text(text, encoding="utf-8")
sys.stdout.write(spec.get("stdout", ""))
'''

def review_json(station, verdict="pass"):
    return json.dumps({"station": station, "verdict": verdict, "findings": ["Substantive finding for " + station]})

def healthy_plan(sha_text="Report with " + SHA):
    plan = {"builder": {"stdout": "", "files": {"builder.output.md": sha_text}}}
    for st in ("reviewer-spec", "reviewer-security", "reviewer-tests", "reviewer-architecture", "reviewer-design", "reviewer-ux"):
        plan[st] = {"stdout": "", "files": {st + ".review.json": review_json(st)}}
    return plan

class Harness:
    def __init__(self, tmp, plan):
        self.tmp = Path(tmp)
        self.proj = self.tmp / "proj"
        init_project(self.proj, "Demo")
        scaffold_spec(self.proj, "demo-feature", "Demo Feature")
        cfg = json.loads((self.proj / "anvil.json").read_text())
        cfg["checks"] = ["exit 0"]
        (self.proj / "anvil.json").write_text(json.dumps(cfg, indent=2))
        self.plan_dir = self.tmp / "plan"; self.plan_dir.mkdir()
        (self.plan_dir / "fake.py").write_text(FAKE)
        (self.plan_dir / "plan.json").write_text(json.dumps(plan))
        self.executor = create_executor({
            "kind": "command", "timeout_seconds": 60,
            "command": f"{sys.executable} {self.plan_dir / 'fake.py'} {{packet}} {self.plan_dir / 'plan.json'}"})

    def run(self, wo_id, **wo_extra):
        reg = load_registry(ROOT / "stations")
        pipe = load_pipeline(ROOT / "pipelines" / "sdlc-default.json", known_stations=set(reg.ids()))
        wo = {"id": wo_id, "kind": "feature", "title": "Contract test"}
        wo.update(wo_extra)
        report = run_pipeline(self.proj, pipe, wo, registry=reg, executor=self.executor)
        on_disk = json.loads((self.proj / "runs" / wo_id / "report.json").read_text())
        return report, on_disk

    def calls(self):
        p = self.plan_dir / "calls.log"
        return p.read_text().split() if p.exists() else []

def steps_of(report, station):
    return [s for s in report["steps"] if s.get("station") == station]

def reviewers_run(h):
    return [c for c in h.calls() if c.startswith("reviewer")]

class TestArtifactIsResult(unittest.TestCase):
    def test_prose_channel_with_artifact_is_counted_s1(self):
        """S1: channel returns prose, artifact written: the artifact is the result"""
        plan = healthy_plan()
        plan["reviewer-tests"]["stdout"] = "I reviewed everything and it looks great, ship it."
        with tempfile.TemporaryDirectory() as tmp:
            h = Harness(tmp, plan)
            _, rep = h.run("wo-s1-prose")
            counted = {c["station"]: c["verdict"] for c in rep["decision"]["approver"]["reviews_counted"]}
            self.assertEqual(counted.get("reviewer-tests"), "pass")
            step = steps_of(rep, "reviewer-tests")[0]
            self.assertEqual(step["status"], "executed")
            review = json.loads((h.proj / "runs" / "wo-s1-prose" / "reviewer-tests.review.json").read_text())
            self.assertEqual(review["verdict"], "pass")

    def test_missing_review_artifact_fails_fast_with_reason_s1(self):
        """S1: artifact missing: station recorded failed with the expected artifact named"""
        plan = healthy_plan()
        plan["reviewer-tests"] = {"stdout": "Here is my review in chat: all good.", "files": {}}
        with tempfile.TemporaryDirectory() as tmp:
            h = Harness(tmp, plan)
            _, rep = h.run("wo-s1-missing")
            step = steps_of(rep, "reviewer-tests")[0]
            self.assertEqual(step["status"], "failed")
            self.assertIn("reviewer-tests.review.json", step["detail"])
            self.assertIn("missing", step["detail"].lower())
            self.assertNotIn("reviewer-tests", [c["station"] for c in rep["decision"]["approver"]["reviews_counted"]])

    def test_empty_review_artifact_fails_fast_with_reason_s1(self):
        """S1: artifact empty: station recorded failed with the observed state"""
        plan = healthy_plan()
        plan["reviewer-tests"] = {"stdout": "", "files": {"reviewer-tests.review.json": ""}}
        with tempfile.TemporaryDirectory() as tmp:
            h = Harness(tmp, plan)
            _, rep = h.run("wo-s1-empty")
            step = steps_of(rep, "reviewer-tests")[0]
            self.assertEqual(step["status"], "failed")
            self.assertIn("empty", step["detail"].lower())

class TestBuilderReportValidation(unittest.TestCase):
    def test_abbreviated_literal_bounces_builder_before_reviewers_s2(self):
        """S2: abbreviated sha256 in the builder report: gate fails, loopback to builder, no reviewer runs"""
        abbreviated = "All 159 tests pass. sha256 67217b9d...c83b86f confirmed."
        with tempfile.TemporaryDirectory() as tmp:
            h = Harness(tmp, healthy_plan(abbreviated))
            _, rep = h.run("wo-s2-abbrev", required_literals=[SHA])
            gate = steps_of(rep, "checks-gate")[0]
            self.assertEqual(gate["status"], "failed")
            self.assertIn(SHA, gate["detail"] + (gate.get("feedback") or "") +
                          (h.proj / "runs" / "wo-s2-abbrev" / "checks-gate.pre-review.output.md").read_text())
            loops = steps_of(rep, "loopback")
            self.assertTrue(loops)
            self.assertEqual(loops[0]["return_to"], "builder")
            self.assertEqual(reviewers_run(h), [])

    def test_full_literals_let_reviewers_run_s2(self):
        """S2: every required literal present in full: validation passes, reviewers run"""
        with tempfile.TemporaryDirectory() as tmp:
            h = Harness(tmp, healthy_plan())
            _, rep = h.run("wo-s2-full", required_literals=[SHA])
            self.assertEqual(steps_of(rep, "checks-gate")[0]["status"], "passed")
            self.assertTrue(reviewers_run(h))

    def test_no_declared_literals_behave_as_before_s2(self):
        """S2: field absent: only existence and non-empty are checked"""
        with tempfile.TemporaryDirectory() as tmp:
            h = Harness(tmp, healthy_plan("any non-empty report"))
            _, rep = h.run("wo-s2-none")
            self.assertEqual(steps_of(rep, "checks-gate")[0]["status"], "passed")
            self.assertTrue(reviewers_run(h))

    def test_empty_builder_report_bounces_s2(self):
        """S2: builder report empty (stub of nothing): validation fails before reviewers"""
        plan = healthy_plan("")
        plan["builder"] = {"stdout": "", "files": {"builder.output.md": ""}}
        with tempfile.TemporaryDirectory() as tmp:
            h = Harness(tmp, plan)
            h.run("wo-s2-empty")
            self.assertEqual(reviewers_run(h), [])

class TestApproverHonesty(unittest.TestCase):
    def test_uncounted_reviewer_is_never_silently_approved_s3(self):
        """S3: an expected reviewer failed: verdict is not approved and the decision names it"""
        plan = healthy_plan()
        plan["reviewer-architecture"] = {"stdout": "", "files": {}}
        with tempfile.TemporaryDirectory() as tmp:
            h = Harness(tmp, plan)
            report, rep = h.run("wo-s3-drop")
            self.assertNotEqual(rep["verdict"], "approved")
            self.assertTrue(rep["human_required"])
            text = rep["decision"]["approver"]["rule"]
            self.assertIn("reviewer-architecture", text)
            self.assertNotIn("reviewer-tests", text.split("reviewer-architecture")[0].replace("counted", ""))

    def test_all_reviewers_counted_still_approves_s3(self):
        """S3/S5: every expected reviewer counted: approver behaves as before"""
        with tempfile.TemporaryDirectory() as tmp:
            h = Harness(tmp, healthy_plan())
            _, rep = h.run("wo-s3-healthy")
            self.assertEqual(rep["verdict"], "approved")
            self.assertTrue(rep["decision"]["approver"]["rule"].startswith("All counted reviews passed."))

    def test_aggregate_honesty_unit_s3(self):
        """S3: approver aggregation with an expected station missing from the counted set"""
        from anvil import approver
        verdict, rule, counted = approver.aggregate_explained(
            [{"station": "reviewer-tests", "verdict": "pass"}],
            expected=["reviewer-tests", "reviewer-ux"],
            uncounted={"reviewer-ux": "failed: review artifact missing"})
        self.assertIn(verdict, {"human_required", "changes_requested"})
        self.assertIn("reviewer-ux", rule)
        self.assertIn("review artifact missing", rule)
        verdict, rule, _ = approver.aggregate_explained(
            [{"station": "reviewer-tests", "verdict": "pass"}],
            expected=["reviewer-tests"], uncounted={})
        self.assertEqual((verdict, rule), ("approved", "All counted reviews passed."))

class TestObservedModes(unittest.TestCase):
    def test_empty_captured_output_with_valid_review_json_s4a(self):
        """S4a: channel output empty while a valid review.json was written: counted, never dropped"""
        plan = healthy_plan()
        plan["reviewer-design"] = {"stdout": "", "files": {
            "reviewer-design.review.json": review_json("reviewer-design", "changes_requested")}}
        with tempfile.TemporaryDirectory() as tmp:
            h = Harness(tmp, plan)
            _, rep = h.run("wo-s4a")
            counted = {c["station"]: c["verdict"] for c in rep["decision"]["approver"]["reviews_counted"]}
            self.assertEqual(counted.get("reviewer-design"), "changes_requested")
            self.assertNotEqual(rep["verdict"], "approved")

    def test_extra_output_md_beside_review_file_s4b(self):
        """S4b: reviewer writes an extra .output.md next to its review: review still collected"""
        plan = healthy_plan()
        plan["reviewer-architecture"] = {"stdout": "", "files": {
            "reviewer-architecture.review.json": review_json("reviewer-architecture"),
            "reviewer-architecture.scratch.output.md": "scratch working notes"}}
        with tempfile.TemporaryDirectory() as tmp:
            h = Harness(tmp, plan)
            _, rep = h.run("wo-s4b")
            counted = [c["station"] for c in rep["decision"]["approver"]["reviews_counted"]]
            step = steps_of(rep, "reviewer-architecture")[0]
            self.assertTrue("reviewer-architecture" in counted or
                            (step["status"] == "failed" and "outside" in step["detail"].lower()),
                            "architecture review must be counted or fail with the scope reason")
            self.assertIn("reviewer-architecture", counted)

    def test_builder_chat_summary_bounced_s4c(self):
        """S4c: builder returns a first-person chat summary lacking the required literal"""
        chat = {"builder": {"stdout": "I implemented the change and all 159 tests pass. The sha256 is 67217b9d...c83b86f.",
                            "files": {}}}
        plan = healthy_plan(); plan.update(chat)
        with tempfile.TemporaryDirectory() as tmp:
            h = Harness(tmp, plan)
            _, rep = h.run("wo-s4c", required_literals=[SHA])
            self.assertEqual(steps_of(rep, "checks-gate")[0]["status"], "failed")
            self.assertEqual(reviewers_run(h), [])
            self.assertTrue(steps_of(rep, "loopback"))

if __name__ == "__main__":
    unittest.main()
