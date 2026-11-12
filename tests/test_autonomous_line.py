"""Tests for the autonomous line (spec: autonomous-line).

Scenario map:
  S1  test_loopback_reexecutes_with_findings_s1
  S2  test_loopbacks_exhausted_verdict_stands_s2
      test_no_budget_for_another_attempt_s2
  S3  test_exit_codes_s3, test_cli_exit_code_follows_verdict_s3
  S4  test_approve_and_resume_deploys_s4, test_approval_rules_s4
  S5  test_publisher_held_until_approved_s5
  S6  test_work_order_from_issue_s6, test_cli_work_order_from_issue_s6
  S7  test_worker_and_workflow_agree_on_dispatch_s7 (behavior: intake-worker/dispatch.test.js)
  S8  test_red_check_recorded_and_flagged_s8
  S9  test_one_generic_workflow_s9
  S10 test_isolated_run_commits_on_its_own_branch_s10
  S11 test_review_gate_counts_extra_reviews_s11
  S12 test_content_reviewers_are_not_routed_out_s12
"""
import contextlib, io, json, re, subprocess, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from anvil import line
from anvil.cli import main
from anvil.executor import create_executor
from anvil.gates import review_gate
from anvil.pipeline import load_pipeline
from anvil.runner import run_pipeline
from anvil.scaffold import init_project
from anvil.stations import load_registry

ROOT = Path(__file__).resolve().parent.parent

# Fake station runtime. It runs in the project tree like a real agent CLI:
# the builder edits a product file and writes its report, reviewers write
# their review file. behavior.json: {"fail_until_attempt": N} makes every
# reviewer fail while the builder has run fewer than N times.
FAKE = r'''
import json, sys
from pathlib import Path
packet = Path(sys.argv[1]); home = Path(sys.argv[2])
station = packet.name[:-len(".packet.md")]
run_dir = packet.parent
behavior = json.loads((home / "behavior.json").read_text())
with open(home / "calls.log", "a") as fh:
    fh.write(station + "\n")
builds = (home / "calls.log").read_text().split().count("builder")
(home / f"{station}.{(home / 'calls.log').read_text().split().count(station)}.packet").write_text(packet.read_text())
if station == "builder":
    Path("app.txt").write_text(f"build {builds}\n")
    (run_dir / "builder.output.md").write_text(f"Builder report, attempt {builds}\n")
elif station.startswith("reviewer"):
    ok = builds >= behavior.get("fail_until_attempt", 0)
    (run_dir / f"{station}.review.json").write_text(json.dumps(
        {"station": station, "verdict": "pass" if ok else "fail",
         "findings": ["all good"] if ok else ["misses the empty input edge case"]}))
print("done")
'''

SHORT = [{"station": "intake"}, {"station": "test-writer"}, {"station": "builder"},
         {"station": "reviewer-tests"}, {"station": "approver"}]
DEPLOY = SHORT + [{"station": "triage-human"}, {"station": "deployer"}, {"station": "observer"}]
CONTENT = [{"station": "intake"}, {"station": "writer"}, {"station": "reviewer-voice"},
           {"station": "approver"}, {"station": "triage-human"}, {"station": "publisher"}]


class Line:
    """A scaffolded git project wired to the fake runtime."""

    def __init__(self, tmp, stages, behavior=None, efficiency=None, deploy=None, checks=None):
        self.tmp = Path(tmp)
        self.proj = self.tmp / "proj"
        init_project(self.proj, "Demo")
        self.home = self.tmp / "home"; self.home.mkdir()
        (self.home / "fake.py").write_text(FAKE)
        (self.home / "behavior.json").write_text(json.dumps(behavior or {}))
        self.pipeline = self.home / "line.json"
        self.pipeline.write_text(json.dumps({"name": "line", "stages": stages}))
        cfg_path = self.proj / "anvil.yaml"
        cfg = json.loads(cfg_path.read_text()) if cfg_path.exists() else {"version": 1}
        cfg["runtime"] = {"kind": "command", "timeout_seconds": 60,
                          "command": f"{sys.executable} {self.home / 'fake.py'} {{packet}} {self.home}"}
        if efficiency is not None:
            cfg["efficiency"] = efficiency
        if deploy:
            cfg["deploy"] = deploy
        cfg_path.write_text(json.dumps(cfg, indent=2))
        if checks is not None:
            project_cfg = json.loads((self.proj / "anvil.json").read_text())
            project_cfg["checks"] = checks
            (self.proj / "anvil.json").write_text(json.dumps(project_cfg, indent=2))
        self.git("init", "-q", "-b", "main")
        self.git("add", "-A")
        self.git("-c", "user.name=t", "-c", "user.email=t@example.test", "commit", "-q", "-m", "base")

    def git(self, *args, cwd=None):
        return subprocess.run(["git", *args], cwd=cwd or self.proj, check=True, capture_output=True, text=True).stdout

    def work_order(self, wo_id, **extra):
        path = self.home / f"{wo_id}.json"
        path.write_text(json.dumps({"id": wo_id, "kind": "feature", "title": "Line test", **extra}))
        return path

    def run(self, wo_id, **extra):
        reg = load_registry(ROOT / "stations")
        pipe = load_pipeline(self.pipeline, known_stations=set(reg.ids()))
        cfg = json.loads((self.proj / "anvil.yaml").read_text())
        report = run_pipeline(self.proj, pipe, {"id": wo_id, "kind": "feature", "title": "Line test", **extra},
                              registry=reg, executor=create_executor(cfg["runtime"]))
        return report.to_dict()

    def cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main([str(a) for a in argv])
        return code, out.getvalue(), err.getvalue()

    def calls(self):
        log = self.home / "calls.log"
        return log.read_text().split() if log.exists() else []

    def packet(self, station, nth):
        return (self.home / f"{station}.{nth}.packet").read_text()

    def report(self, wo_id, root=None):
        return json.loads(((root or self.proj) / "runs" / wo_id / "report.json").read_text())


class TestRealLoopback(unittest.TestCase):
    def test_loopback_reexecutes_with_findings_s1(self):
        """S1: a failed review sends the work back, and the second attempt is approved"""
        with tempfile.TemporaryDirectory() as tmp:
            h = Line(tmp, SHORT, behavior={"fail_until_attempt": 2})
            rep = h.run("wo-s1")
            self.assertEqual(h.calls().count("builder"), 2)
            self.assertEqual(h.calls().count("reviewer-tests"), 2)
            self.assertEqual(h.calls().count("test-writer"), 1, "stations before the return station do not run again")
            self.assertEqual((rep["verdict"], rep["loopbacks"]), ("approved", 1))
            self.assertNotIn("Loopback feedback", h.packet("builder", 1))
            second = h.packet("builder", 2)
            self.assertIn("## Loopback feedback (attempt 2 of 3)", second)
            self.assertIn("misses the empty input edge case", second)
            self.assertIn("re-review", h.packet("reviewer-tests", 2))
            # Only the second attempt's review is counted
            self.assertEqual(rep["decision"]["approver"]["reviews_counted"],
                             [{"station": "reviewer-tests", "verdict": "pass"}])
            archived = json.loads((h.proj / "runs/wo-s1/attempts/1/reviewer-tests.review.json").read_text())
            self.assertEqual(archived["verdict"], "fail")
            builders = [s for s in rep["steps"] if s["station"] == "builder"]
            self.assertEqual(builders[1]["attempt"], 2)
            self.assertEqual(builders[1]["feedback"]["from_station"], "approver")
            self.assertIn("misses the empty input edge case", builders[1]["feedback"]["findings"])
            self.assertEqual((h.proj / "app.txt").read_text(), "build 2\n")

    def test_loopbacks_exhausted_verdict_stands_s2(self):
        """S2: a reviewer that never passes consumes the loopbacks and the verdict stands"""
        with tempfile.TemporaryDirectory() as tmp:
            h = Line(tmp, SHORT, behavior={"fail_until_attempt": 99})
            rep = h.run("wo-s2")
            self.assertEqual(h.calls().count("builder"), rep["max_loopbacks"] + 1)
            self.assertEqual((rep["verdict"], rep["loopbacks"]), ("rejected", rep["max_loopbacks"]))
            self.assertTrue(rep["human_required"])

    def test_no_budget_for_another_attempt_s2(self):
        """S2: with no room in the call limit, nothing is re-executed and the step says why"""
        with tempfile.TemporaryDirectory() as tmp:
            # first attempt: 4 calls; each further attempt needs 2 (builder, reviewer)
            h = Line(tmp, SHORT, behavior={"fail_until_attempt": 99}, efficiency={"max_agent_calls": 7})
            rep = h.run("wo-s2b")
            self.assertEqual(h.calls().count("builder"), 2)
            self.assertEqual(rep["verdict"], "rejected", "the verdict is the line's, not budget_exceeded")
            last = [s for s in rep["steps"] if s["status"] == "loopback"][-1]
            self.assertIn("no room for another attempt", last["not_reexecuted"])


class TestExitCodes(unittest.TestCase):
    def test_exit_codes_s3(self):
        """S3: the exit code names the outcome"""
        gate = {"decision": {"human_gate": {"approval": {"approved_by": "ana"}}}}
        cases = [
            ({"verdict": "approved", "human_required": False}, True, None, 0),
            ({"verdict": "approved", "human_required": True}, True, None, 3),
            ({"verdict": "human_required", "human_required": True}, True, None, 3),
            ({"verdict": "rejected", "human_required": True}, True, None, 1),
            ({"verdict": "changes_requested"}, True, None, 1),
            ({"verdict": "no_reviews"}, True, None, 1),
            ({"verdict": "budget_exceeded"}, True, None, 1),
            ({"verdict": "approved", "deployment_status": "deploy_failed"}, True, None, 1),
            ({"verdict": "approved", "deployment_status": "deployed_unverified"}, True, None, 1),
            ({"verdict": "rejected", "human_required": False, **gate}, True, None, 0),
            ({"verdict": "packet_ready", "steps": [{"status": "executed"}]}, True, None, 0),
            ({"verdict": "packet_ready", "steps": [{"status": "failed"}]}, True, None, 1),
            ({"verdict": "packet_ready"}, True, "waiting_info", 4),
            ({"verdict": "no_reviews"}, False, None, 0),
        ]
        for report, executed, status, expected in cases:
            self.assertEqual(line.exit_code(report, executed, status), expected, report)

    def test_cli_exit_code_follows_verdict_s3(self):
        """S3: anvil run returns the code; a packet-only run judges nothing"""
        with tempfile.TemporaryDirectory() as tmp:
            h = Line(tmp, SHORT, behavior={"fail_until_attempt": 99})
            wo = h.work_order("wo-s3")
            self.assertEqual(h.cli("run", h.proj, "--pipeline", h.pipeline, "--work-order", wo)[0], 0)
            self.assertEqual(h.calls(), [])
            self.assertEqual(h.cli("run", h.proj, "--pipeline", h.pipeline, "--work-order", wo, "--execute")[0], 1)
            (h.home / "behavior.json").write_text("{}")
            self.assertEqual(h.cli("run", h.proj, "--pipeline", h.pipeline, "--work-order", wo, "--execute")[0], 0)


class TestHumanGate(unittest.TestCase):
    def test_approve_and_resume_deploys_s4(self):
        """S4: the gate holds the deploy until a human approves, then resume finishes the line"""
        with tempfile.TemporaryDirectory() as tmp:
            h = Line(tmp, DEPLOY, deploy={"command": "echo shipped > deployed.txt", "verify": ["test -f deployed.txt"]})
            wo = h.work_order("wo-s4", risk_hints=["production-deploy"])
            code, _, err = h.cli("run", h.proj, "--pipeline", h.pipeline, "--work-order", wo, "--execute")
            self.assertEqual(code, 3)
            self.assertIn("anvil approve", err)
            self.assertFalse((h.proj / "deployed.txt").exists())
            first = h.report("wo-s4")
            self.assertEqual((first["verdict"], first["human_required"]), ("approved", True))
            # no approval on record: nothing to resume
            self.assertEqual(h.cli("resume", h.proj, "wo-s4", "--pipeline", h.pipeline, "--execute")[0], 2)
            calls_before = h.calls()
            self.assertEqual(h.cli("approve", h.proj, "wo-s4", "--by", "ana", "--note", "ok to ship")[0], 0)
            code, _, _ = h.cli("resume", h.proj, "wo-s4", "--pipeline", h.pipeline, "--execute")
            self.assertEqual(code, 0)
            self.assertTrue((h.proj / "deployed.txt").exists())
            self.assertEqual(h.calls()[len(calls_before):], ["observer"], "only stations after the gate run")
            rep = h.report("wo-s4")
            self.assertEqual(rep["run_id"], first["run_id"])
            self.assertTrue(str(rep["deployment_status"]).startswith("deployed"))
            self.assertFalse(rep["human_required"])
            approval = rep["decision"]["human_gate"]["approval"]
            self.assertEqual((approval["approved_by"], approval["note"], approval["override"]), ("ana", "ok to ship", False))
            self.assertIn("ana", rep["decision"]["human_gate"]["rule"])
            self.assertEqual([s["station"] for s in rep["steps"]][:5],
                             [s["station"] for s in first["steps"]][:5])
            # a finished run cannot be approved or resumed again
            self.assertEqual(h.cli("approve", h.proj, "wo-s4", "--by", "ana")[0], 1)
            self.assertEqual(h.cli("resume", h.proj, "wo-s4", "--pipeline", h.pipeline, "--execute")[0], 2)

    def test_approval_rules_s4(self):
        """S4: override is explicit and recorded; an approval binds to one run"""
        with tempfile.TemporaryDirectory() as tmp:
            h = Line(tmp, DEPLOY, behavior={"fail_until_attempt": 99}, deploy={"command": "echo shipped > deployed.txt"})
            wo = h.work_order("wo-s4b")
            run = ("run", h.proj, "--pipeline", h.pipeline, "--work-order", wo, "--execute")
            self.assertEqual(h.cli(*run)[0], 1)
            code, _, err = h.cli("approve", h.proj, "wo-s4b", "--by", "ana")
            self.assertEqual(code, 1)
            self.assertIn("--override", err)
            self.assertEqual(h.cli("approve", h.proj, "wo-s4b", "--by", "ana", "--override")[0], 0)
            # the line runs again: the approval was for the previous run
            self.assertEqual(h.cli(*run)[0], 1)
            code, _, err = h.cli("resume", h.proj, "wo-s4b", "--pipeline", h.pipeline, "--execute")
            self.assertEqual(code, 2)
            self.assertIn("different run", err)
            self.assertFalse((h.proj / "deployed.txt").exists())
            # approving the current run with the override deploys, and the line's verdict stays on record
            self.assertEqual(h.cli("approve", h.proj, "wo-s4b", "--by", "ana", "--override")[0], 0)
            self.assertEqual(h.cli("resume", h.proj, "wo-s4b", "--pipeline", h.pipeline, "--execute")[0], 0)
            rep = h.report("wo-s4b")
            self.assertTrue((h.proj / "deployed.txt").exists())
            self.assertEqual(rep["verdict"], "rejected")
            self.assertTrue(rep["decision"]["human_gate"]["approval"]["override"])
            self.assertEqual(rep["decision"]["human_gate"]["approval"]["approver_verdict"], "rejected")
            with self.assertRaises(ValueError):
                line.record_approval(h.proj, "wo-none", "ana")
            with self.assertRaises(ValueError):
                line.record_approval(h.proj, "wo-s4b", "  ")

    def test_publisher_held_until_approved_s5(self):
        """S5: publishing stops at the human gate in execute mode"""
        with tempfile.TemporaryDirectory() as tmp:
            h = Line(tmp, CONTENT)
            wo = h.work_order("wo-s5", kind="content", risk_hints=["publishing"])
            self.assertEqual(h.cli("run", h.proj, "--pipeline", h.pipeline, "--work-order", wo, "--execute")[0], 3)
            self.assertNotIn("publisher", h.calls())
            step = [s for s in h.report("wo-s5")["steps"] if s["station"] == "publisher"][0]
            self.assertEqual(step["status"], "packet_ready")
            self.assertIn("Publish held", step["detail"])
            self.assertEqual(h.cli("approve", h.proj, "wo-s5", "--by", "ana")[0], 0)
            self.assertEqual(h.cli("resume", h.proj, "wo-s5", "--pipeline", h.pipeline, "--execute")[0], 0)
            self.assertEqual(h.calls().count("publisher"), 1)
            self.assertEqual(h.calls().count("writer"), 1)

    def test_publisher_never_runs_on_a_rejected_run_s5(self):
        """S5: an unapproved content run does not publish, risk hint or not"""
        with tempfile.TemporaryDirectory() as tmp:
            h = Line(tmp, CONTENT, behavior={"fail_until_attempt": 99})
            h.run("wo-s5b", kind="content")
            self.assertNotIn("publisher", h.calls())


class TestIntake(unittest.TestCase):
    ISSUE = {"number": 42, "title": "Add CSV export", "body": "Please add it",
             "html_url": "https://github.com/acme/project/issues/42",
             "labels": [{"name": "anvil"}, {"name": "Bug"}, {"name": "risk:auth"}, {"name": "payments"},
                        {"name": "pipeline:hotfix"}, {"name": "good first issue"}]}

    def test_work_order_from_issue_s6(self):
        """S6: labels carry kind, risk hints and pipeline"""
        wo, pipeline = line.work_order_from_issue(self.ISSUE)
        self.assertEqual((wo["id"], wo["kind"], wo["source"], pipeline), ("wo-gh-42", "bug", "github-issue", "hotfix"))
        self.assertEqual(wo["risk_hints"], ["auth", "payments"])
        self.assertTrue(wo["description"].startswith("Please add it"))
        self.assertIn("issues/42", wo["description"])
        plain, pipeline = line.work_order_from_issue({"number": 7, "title": "T", "labels": ["anvil", "pipeline:../x"]})
        self.assertEqual((plain["kind"], plain["risk_hints"], pipeline), ("feature", [], None))
        with self.assertRaises(ValueError):
            line.work_order_from_issue({"number": "7; rm -rf", "title": "T"})

    def test_cli_work_order_from_issue_s6(self):
        """S6: the CLI accepts an issue or an event payload and writes the work order file"""
        with tempfile.TemporaryDirectory() as tmp:
            event = Path(tmp) / "event.json"
            event.write_text(json.dumps({"action": "labeled", "issue": self.ISSUE}))
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = main(["work-order-from-issue", str(event), "--out-dir", str(Path(tmp) / "wos")])
            self.assertEqual(code, 0)
            result = json.loads(out.getvalue())
            self.assertEqual((result["id"], result["pipeline"]), ("wo-gh-42", "hotfix"))
            self.assertEqual(json.loads(Path(result["work_order"]).read_text())["kind"], "bug")

    def test_worker_and_workflow_agree_on_dispatch_s7(self):
        """S7: the worker sends the event type the workflow listens for"""
        worker = (ROOT / "intake-worker" / "worker.js").read_text()
        workflow = (ROOT / ".github" / "workflows" / "anvil-line.yml").read_text()
        self.assertIn('event_type: "anvil-work-order"', worker)
        self.assertIn("/dispatches", worker)
        self.assertRegex(workflow, r"repository_dispatch:\s*\n\s*types: \[anvil-work-order\]")
        self.assertIn("client_payload", workflow)

    def test_one_generic_workflow_s9(self):
        """S9: one line workflow for every order, and it names none"""
        names = sorted(p.name for p in (ROOT / ".github" / "workflows").glob("anvil*"))
        self.assertEqual(names, ["anvil-line.yml"])
        text = (ROOT / ".github" / "workflows" / "anvil-line.yml").read_text()
        for trigger in ("issues:", "issue_comment:", "repository_dispatch:", "workflow_dispatch:"):
            self.assertIn(trigger, text)
        self.assertIsNone(re.search(r"issue-\d+\.json|wo-gh-\d+", text))
        self.assertIn("/anvil approve", text)
        self.assertIn('["OWNER","MEMBER","COLLABORATOR"]', text)
        # Event text reaches scripts through env or the event file, never by interpolation
        self.assertIsNone(re.search(r"\$\{\{\s*github\.event\.(issue|comment)\.(title|body)", text))


class TestEvidenceAndIsolation(unittest.TestCase):
    def test_red_check_recorded_and_flagged_s8(self):
        """S8: checks that pass before the build are recorded as not red and flagged"""
        with tempfile.TemporaryDirectory() as tmp:
            h = Line(tmp, SHORT, checks=["exit 0"])
            rep = h.run("wo-s8")
            step = [s for s in rep["steps"] if s["station"] == "test-writer"][0]
            self.assertEqual(step["red_check"], {"commands": ["exit 0"], "exit_codes": [0], "red": False})
            self.assertTrue(any("TDD red check" in w for w in rep["warnings"]))
            self.assertIn("## TDD red check", h.packet("reviewer-tests", 1))
        with tempfile.TemporaryDirectory() as tmp:
            # red before the build (app.txt does not exist yet), green after
            h = Line(tmp, SHORT, checks=["test -f app.txt"])
            rep = h.run("wo-s8b")
            step = [s for s in rep["steps"] if s["station"] == "test-writer"][0]
            self.assertTrue(step["red_check"]["red"])
            self.assertFalse(any("TDD red check" in w for w in rep["warnings"]))
            self.assertNotIn("TDD red check", h.packet("reviewer-tests", 1))
            self.assertEqual(rep["verdict"], "approved")

    def test_isolated_run_commits_on_its_own_branch_s10(self):
        """S10: --isolate leaves the checkout alone and commits on anvil/<id>"""
        with tempfile.TemporaryDirectory() as tmp:
            h = Line(tmp, SHORT)
            wo = h.work_order("wo-s10")
            code, out, _ = h.cli("run", h.proj, "--pipeline", h.pipeline, "--work-order", wo, "--execute", "--isolate")
            self.assertEqual(code, 0)
            self.assertIn("Branch: anvil/wo-s10", out)
            self.assertEqual(h.git("status", "--porcelain").strip(), "")
            self.assertFalse((h.proj / "app.txt").exists())
            self.assertEqual(h.git("rev-parse", "--abbrev-ref", "HEAD").strip(), "main")
            files = h.git("show", "--name-only", "--format=%s", "anvil/wo-s10").splitlines()
            self.assertEqual(files[0], "ANVIL run wo-s10: verdict approved")
            self.assertIn("app.txt", files)
            self.assertIn("runs/wo-s10/report.json", files)
            worktree = h.tmp / ".anvil-worktrees" / "proj" / "wo-s10"
            self.assertEqual(h.report("wo-s10", worktree)["verdict"], "approved")
            # a second isolated run of the same order continues on the same branch
            code, _, _ = h.cli("run", h.proj, "--pipeline", h.pipeline, "--work-order", wo, "--execute", "--isolate")
            self.assertEqual(code, 0)
            self.assertEqual(int(h.git("rev-list", "--count", "main..anvil/wo-s10").strip()), 2)

    def test_review_gate_counts_extra_reviews_s11(self):
        """S11: a review on record beyond the core four must pass too"""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "reviews" / "feat"; base.mkdir(parents=True)
            for st in ("reviewer-spec", "reviewer-security", "reviewer-tests", "reviewer-architecture"):
                (base / f"{st}.json").write_text(json.dumps({"station": st, "verdict": "pass", "findings": []}))
            self.assertEqual(review_gate(tmp, "feat"), (True, "All 4 reviews present and passing"))
            (base / "reviewer-design.json").write_text(json.dumps({"station": "reviewer-design", "verdict": "fail", "findings": []}))
            ok, detail = review_gate(tmp, "feat")
            self.assertFalse(ok)
            self.assertIn("reviewer-design", detail)
            (base / "reviewer-design.json").write_text(json.dumps({"station": "reviewer-design", "verdict": "pass", "findings": []}))
            self.assertEqual(review_gate(tmp, "feat"), (True, "All 5 reviews present and passing"))

    def test_content_reviewers_are_not_routed_out_s12(self):
        """S12: reviewers the routing policy does not know are kept at every risk level"""
        from anvil.model import WorkOrder
        from anvil.routing import route_reviewers
        panel = ["reviewer-facts", "reviewer-voice", "reviewer-brand", "reviewer-spec", "reviewer-security"]
        with tempfile.TemporaryDirectory() as tmp:
            for risk in (None, "low", "medium", "high"):
                record = route_reviewers(WorkOrder(id="wo-s12", kind="content", title="T", risk=risk), panel, Path(tmp))
                for reviewer in ("reviewer-facts", "reviewer-voice", "reviewer-brand"):
                    self.assertIn(reviewer, record.selected_reviewers, risk)
                    self.assertNotIn(reviewer, [r["reviewer"] for r in record.routed_out])
            low = route_reviewers(WorkOrder(id="wo-s12", kind="content", title="T", risk="low"), panel, Path(tmp))
            self.assertNotIn("reviewer-security", low.selected_reviewers, "the policy still reduces its own panel")
        with tempfile.TemporaryDirectory() as tmp:
            h = Line(tmp, CONTENT)
            rep = h.run("wo-s12b", kind="content")
            self.assertEqual(rep["verdict"], "approved")
            self.assertEqual(h.calls().count("reviewer-voice"), 1)


if __name__ == "__main__":
    unittest.main()
