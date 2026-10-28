import io, json, os, tempfile, unittest
from contextlib import redirect_stdout
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from anvil.cli import main as cli_main
from anvil.pipeline import load_pipeline
from anvil.scaffold import init_project
from anvil.stations import load_registry
from anvil.supervisor import detect_stalls, supervise, validate_proposal

ROOT = Path(__file__).resolve().parent.parent

_tick = [0]


def write_report(proj, run_id, verdict="approved", counted=None, loopbacks=0,
                 max_loopbacks=2, deployment_status=None):
    """Write one synthetic run report with an increasing mtime (latest = newest)."""
    run_dir = Path(proj) / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    report = {"work_order_id": run_id, "pipeline": "sdlc-default", "title": run_id,
              "kind": "bug", "verdict": verdict, "human_required": False,
              "loopbacks": loopbacks, "max_loopbacks": max_loopbacks,
              "deployment_status": deployment_status, "verify_results": [],
              "risk_hints": [], "steps": [],
              "decision": {"approver": {"reviews_counted": counted or [],
                                        "reviews_expected": [], "rule": "synthetic"},
                           "human_gate": {"required": False, "rule": "synthetic"}}}
    path = run_dir / "report.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    _tick[0] += 10
    os.utime(path, (_tick[0], _tick[0]))
    return path


class StubExecutor:
    """Returns a fixed proposal text, like a configured runtime would."""
    kind = "command"
    name = "command"

    def __init__(self, text):
        self.text = text

    def execute(self, packet_text, station_id, packet_path=None, output_path=None, cwd=None):
        return {"output": self.text, "usage": None}


def proposal_text(stages, name="rebalanced-line", addresses="reviewer_fail_repeated",
                  rationale="Move the security review earlier and add a scout pass."):
    return json.dumps({"name": name,
                       "pipeline": {"name": name, "stages": stages},
                       "rationale": rationale, "addresses": addresses})


REVIEWERS = ["reviewer-spec", "reviewer-security", "reviewer-tests", "reviewer-architecture"]


def stages_of(*items):
    """Build a stage list in the shipped object form: {"station": id} or {"parallel": [...]}."""
    out = []
    for item in items:
        if isinstance(item, list):
            out.append({"parallel": list(item)})
        else:
            out.append({"station": item})
    return out


def sdlc_stages():
    return stages_of("intake", "spec-writer", "test-writer", "builder", REVIEWERS,
                     "approver", "triage-human", "deployer", "observer")


def stalled_project(tmp):
    """Project whose record shows reviewer-security failing in two runs."""
    proj = Path(tmp) / "proj"
    init_project(proj, "Demo")
    fail = [{"station": "reviewer-security", "verdict": "fail"}]
    write_report(proj, "wo-a-001", counted=fail)
    write_report(proj, "wo-a-002", counted=fail)
    return proj


class TestStallDetection(unittest.TestCase):
    def test_reviewer_fail_repeated_s1(self):
        """bounded-supervisor S1: a reviewer failing in 2+ runs is a stall signal with run evidence"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = stalled_project(tmp)
            signals = detect_stalls(proj)
            kinds = {s["kind"]: s for s in signals}
            self.assertIn("reviewer_fail_repeated", kinds)
            self.assertEqual(kinds["reviewer_fail_repeated"]["evidence"], ["wo-a-001", "wo-a-002"])

    def test_single_fail_is_not_a_signal_s1(self):
        """bounded-supervisor S1: one failing run is noise, not a stall"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            init_project(proj, "Demo")
            write_report(proj, "wo-a-001", counted=[{"station": "reviewer-security", "verdict": "fail"}])
            self.assertEqual(detect_stalls(proj), [])

    def test_loopbacks_exhausted_s1(self):
        """bounded-supervisor S1: the latest run exhausting its loopbacks is a signal"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            init_project(proj, "Demo")
            write_report(proj, "wo-a-001")
            write_report(proj, "wo-a-002", loopbacks=2, max_loopbacks=2)
            kinds = {s["kind"] for s in detect_stalls(proj)}
            self.assertIn("loopbacks_exhausted", kinds)

    def test_no_reviews_repeated_s1(self):
        """bounded-supervisor S1: no_reviews in 2 of the last 3 runs is a signal"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            init_project(proj, "Demo")
            write_report(proj, "wo-a-001", verdict="no_reviews")
            write_report(proj, "wo-a-002", verdict="approved")
            write_report(proj, "wo-a-003", verdict="no_reviews")
            kinds = {s["kind"]: s for s in detect_stalls(proj)}
            self.assertIn("no_reviews_repeated", kinds)
            self.assertEqual(kinds["no_reviews_repeated"]["evidence"], ["wo-a-001", "wo-a-003"])

    def test_deployed_unverified_s1(self):
        """bounded-supervisor S1: the latest run deployed_unverified is a signal"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            init_project(proj, "Demo")
            write_report(proj, "wo-a-001", deployment_status="deployed_unverified")
            kinds = {s["kind"] for s in detect_stalls(proj)}
            self.assertIn("deployed_unverified", kinds)

    def test_no_runs_no_signals_s2(self):
        """bounded-supervisor S2: no runs means no signals, and supervise writes nothing"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            init_project(proj, "Demo")
            reg = load_registry(ROOT / "stations")
            result = supervise(proj, reg)
            self.assertEqual(result["signals"], [])
            self.assertEqual(result["action"], "none")
            self.assertFalse((proj / "work-orders").exists())
            out = io.StringIO()
            with redirect_stdout(out):
                code = cli_main(["supervise", str(proj)])
            self.assertEqual(code, 0)
            self.assertIn("no stalls detected", out.getvalue())


class TestSuperviseFlow(unittest.TestCase):
    def test_packet_mode_writes_packet_and_work_order_s3(self):
        """bounded-supervisor S3: packet mode writes the supervisor packet and proposal work order"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = stalled_project(tmp)
            reg = load_registry(ROOT / "stations")
            result = supervise(proj, reg)
            self.assertEqual(result["action"], "packet")
            packet = (proj / "work-orders" / "supervisor.packet.md").read_text()
            self.assertIn("reviewer_fail_repeated", packet)
            self.assertIn("wo-a-001", packet)
            wo = json.loads((proj / "work-orders" / "supervisor-proposal.json").read_text())
            self.assertEqual(wo["kind"], "task")
            self.assertIn("reviewer_fail_repeated", wo["title"])

    def test_valid_proposal_accepted_and_not_applied_s4(self):
        """bounded-supervisor S4: a catalog only, constitution passing proposal is filed, never applied"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = stalled_project(tmp)
            reg = load_registry(ROOT / "stations")
            stages = stages_of("intake", "scout", "spec-writer", "test-writer", "builder",
                               REVIEWERS, "approver", "triage-human", "deployer", "observer")
            text = proposal_text(stages)
            before = (proj / "anvil.json").read_text()
            result = supervise(proj, reg, executor=StubExecutor(text))
            self.assertEqual(result["action"], "accepted")
            accepted = proj / "pipelines" / "proposals" / "rebalanced-line.json"
            self.assertTrue(accepted.exists())
            doc = (proj / "pipelines" / "proposals" / "PROPOSAL.md").read_text()
            self.assertIn("Move the security review earlier", doc)
            self.assertIn("reviewer_fail_repeated", doc)
            self.assertIn("wo-a-001", doc)
            self.assertIn("Nothing auto applies", doc)
            self.assertEqual((proj / "anvil.json").read_text(), before)

    def test_second_execute_reads_the_new_output_not_a_stale_one(self):
        """bounded-supervisor S4 and S5: repeated supervise runs judge the latest runtime output"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = stalled_project(tmp)
            reg = load_registry(ROOT / "stations")
            good = proposal_text(sdlc_stages())
            first = supervise(proj, reg, executor=StubExecutor(good))
            self.assertEqual(first["action"], "accepted")

            class FilePreferringExecutor(StubExecutor):
                """Emulates the command executor: a stale output file would win."""

                def execute(self, packet_text, station_id, packet_path=None, output_path=None, cwd=None):
                    if output_path is not None and Path(output_path).exists():
                        stale = Path(output_path).read_text()
                        if stale.strip():
                            return {"output": stale, "usage": None}
                    return {"output": self.text, "usage": None}

            bad = proposal_text(stages_of("intake", "builder"), name="second-run")
            second = supervise(proj, reg, executor=FilePreferringExecutor(bad))
            self.assertEqual(second["action"], "rejected")

    def test_reordered_reviewers_still_accepted_s4(self):
        """bounded-supervisor S4: reordering reviewers keeps the set, so the proposal is valid"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = stalled_project(tmp)
            reg = load_registry(ROOT / "stations")
            stages = stages_of("intake", "spec-writer", "test-writer", "builder",
                               list(reversed(REVIEWERS)), "approver", "triage-human",
                               "deployer", "observer")
            result = supervise(proj, reg, executor=StubExecutor(proposal_text(stages)))
            self.assertEqual(result["action"], "accepted")


class TestConstitution(unittest.TestCase):
    def run_bad(self, tmp, stages, name):
        proj = stalled_project(tmp)
        reg = load_registry(ROOT / "stations")
        result = supervise(proj, reg, executor=StubExecutor(proposal_text(stages, name=name)))
        self.assertEqual(result["action"], "rejected")
        rejected = proj / "pipelines" / "proposals" / f"rejected-{name}.json"
        self.assertTrue(rejected.exists())
        self.assertFalse((proj / "pipelines" / "proposals" / f"{name}.json").exists())
        return (proj / "pipelines" / "proposals" / "REJECTED.md").read_text(), result

    def test_dropping_triage_human_is_rejected_s5(self):
        """bounded-supervisor S5: a proposal without triage-human fails the constitution"""
        with tempfile.TemporaryDirectory() as tmp:
            stages = stages_of("intake", "spec-writer", "test-writer", "builder", REVIEWERS,
                               "approver", "deployer", "observer")
            doc, result = self.run_bad(tmp, stages, "no-triage")
            self.assertIn("triage-human", doc)
            self.assertTrue(any("triage-human" in f for f in result["failures"]))

    def test_dropping_a_reviewer_is_rejected_s5(self):
        """bounded-supervisor S5: the reviewer set may not shrink below the base pipeline"""
        with tempfile.TemporaryDirectory() as tmp:
            stages = stages_of("intake", "spec-writer", "test-writer", "builder",
                               [r for r in REVIEWERS if r != "reviewer-tests"],
                               "approver", "triage-human", "deployer", "observer")
            doc, result = self.run_bad(tmp, stages, "fewer-reviewers")
            self.assertIn("reviewer-tests", doc)

    def test_unknown_station_is_rejected_s5(self):
        """bounded-supervisor S5: a station outside the catalog fails validation"""
        with tempfile.TemporaryDirectory() as tmp:
            stages = sdlc_stages() + [{"station": "wizard"}]
            doc, result = self.run_bad(tmp, stages, "with-wizard")
            self.assertIn("wizard", doc)

    def test_validate_proposal_names_each_failed_check_s5(self):
        """bounded-supervisor S5: validate_proposal returns every failed check, not just the first"""
        reg = load_registry(ROOT / "stations")
        base = load_pipeline(ROOT / "pipelines" / "sdlc-default.json", known_stations=set(reg.ids()))
        proposal = {"name": "bad", "pipeline": {"name": "bad",
                                                "stages": stages_of("intake", "builder")}}
        failures = validate_proposal(proposal, reg, base)
        joined = "\n".join(failures)
        self.assertIn("approver", joined)
        self.assertIn("triage-human", joined)
        self.assertIn("reviewer-spec", joined)


class TestSupervisorBounds(unittest.TestCase):
    def test_prompt_states_the_bounds_s6(self):
        """bounded-supervisor S6: the station prompt puts gates, risk hints and triage rules out of bounds"""
        prompt = (ROOT / "stations" / "supervisor" / "PROMPT.md").read_text()
        self.assertIn("Out of bounds", prompt)
        self.assertIn("gates", prompt)
        self.assertIn("risk hints", prompt)
        self.assertIn("triage", prompt)

    def test_supervisor_in_no_shipped_pipeline_s6(self):
        """bounded-supervisor S6: the supervisor runs between runs, so no shipped pipeline contains it"""
        reg = load_registry(ROOT / "stations")
        for pipe_file in sorted((ROOT / "pipelines").glob("*.json")):
            pipe = load_pipeline(pipe_file, known_stations=set(reg.ids()))
            self.assertNotIn("supervisor", pipe.topological_order())


if __name__ == "__main__":
    unittest.main()
