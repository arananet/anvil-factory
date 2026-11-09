"""Tests for the practice skills base (spec: .openspec/specs/practice-skills/spec.md).

Written before the implementation. Every test drives the real brain module,
the real CLI and the real runner; nothing is mocked. The interface these
tests pin down, which the builder must provide:

anvil.brain
    propose_practice(project, topic, rule, enforcement="prompt", languages=(),
                     surfaces=(), stations=(), source="", supersedes=None) -> inbox file name
        Source is "run <run-id>, artifact <path>, evidence <evidence>" or
        "decision brain/decisions/<file>".
    promote_practice(project, inbox_name) -> practice id such as "P-1"
        Raises ValueError naming the reason on refusal; nothing changes on disk.
    parse_practices(project) -> list of dicts with keys id, topic, rule,
        enforcement, languages, surfaces, stations, source, status
    resolve_practices(project, work_order, station_ids, config) ->
        {"resolved": {station: [ids]}, "excluded_topics": [...], "active_count": n}
    check_brain(project) also returns ok False on a bad practices base.

anvil.cli: propose-practice and promote-practice commands.

Language signal: the "languages" list in anvil.yaml. Override list:
"practice_overrides" in anvil.yaml. report.json "practices" and routing.json
"practices" both hold the resolution dict above.
"""
import io, json, sys, tempfile, unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from anvil.brain import (check_brain, parse_practices, promote_practice,
                         propose_practice, resolve_practices)
from anvil.cli import main as cli_main
from anvil.executor import create_executor
from anvil.model import WorkOrder
from anvil.pipeline import load_pipeline
from anvil.runner import run_pipeline
from anvil.scaffold import init_project
from anvil.stations import load_registry

ROOT = Path(__file__).resolve().parent.parent

FAKE_EXECUTOR = '''
import json, sys
station = ""
for line in open(sys.argv[1], encoding="utf-8"):
    if line.startswith("# Task packet:"):
        station = line.split(":", 1)[1].strip()
        break
if station.startswith("reviewer"):
    print(json.dumps({"station": station, "verdict": "pass", "findings": ["ok"]}))
else:
    print("Executed " + station)
'''

SOURCE = "run wo-seed-001, artifact runs/wo-seed-001/notes.md, evidence verdict approved"


def seed_run(proj, run_id="wo-seed-001"):
    run_dir = Path(proj) / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    report = {"work_order_id": run_id, "pipeline": "hotfix", "verdict": "approved",
              "verify_results": [], "steps": []}
    (run_dir / "report.json").write_text(json.dumps(report), encoding="utf-8")
    (run_dir / "notes.md").write_text("notes\n", encoding="utf-8")


def make_project(tmp, config=None):
    proj = Path(tmp) / "proj"
    init_project(proj, "Demo")
    seed_run(proj)
    if config:
        path = proj / "anvil.yaml"
        data = json.loads(path.read_text(encoding="utf-8"))
        data.update(config)
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return proj


def add_practice(proj, topic, rule, **kw):
    kw.setdefault("source", SOURCE)
    name = propose_practice(proj, topic, rule, **kw)
    return promote_practice(proj, name)


def executor(tmp):
    script = Path(tmp) / "fake_executor.py"
    script.write_text(FAKE_EXECUTOR, encoding="utf-8")
    return create_executor({"kind": "command",
                            "command": f"{sys.executable} {script} {{packet}}",
                            "timeout_seconds": 60})


def run(proj, tmp, wo_id, surfaces=("data",)):
    reg = load_registry(ROOT / "stations")
    pipe = load_pipeline(ROOT / "pipelines" / "sdlc-default.json", known_stations=set(reg.ids()))
    wo = WorkOrder(id=wo_id, kind="feature", title="Practice run", surfaces=list(surfaces))
    run_pipeline(proj, pipe, wo, registry=reg, executor=executor(tmp))
    run_dir = proj / "runs" / wo_id
    report = json.loads((run_dir / "report.json").read_text(encoding="utf-8"))
    return run_dir, report


def packet(run_dir, station):
    return (run_dir / f"{station}.packet.md").read_text(encoding="utf-8")


class TestProposeAndPromote(unittest.TestCase):
    def test_proposal_lands_in_inbox_only_s1(self):
        """practice-skills S1: propose writes to brain/inbox/ and leaves practices.md unchanged"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            name = propose_practice(proj, "error-handling", "Wrap I/O errors with context",
                                    source=SOURCE)
            self.assertTrue((proj / "brain" / "inbox" / name).is_file())
            self.assertFalse((proj / "brain" / "practices.md").exists())
            self.assertEqual(parse_practices(proj), [])

    def test_cli_propose_then_promote_s1(self):
        """practice-skills S1: the CLI propose-practice and promote-practice commands work end to end"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            out = io.StringIO()
            with redirect_stdout(out), redirect_stderr(io.StringIO()):
                code = cli_main(["propose-practice", str(proj), "--topic", "logging",
                                 "--rule", "Log structured events", "--enforcement", "prompt",
                                 "--source", SOURCE])
            self.assertEqual(code, 0)
            inbox = sorted((proj / "brain" / "inbox").iterdir())
            self.assertEqual(len(inbox), 1)
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                code = cli_main(["promote-practice", str(proj), inbox[0].name])
            self.assertEqual(code, 0)
            practices = parse_practices(proj)
            self.assertEqual([p["topic"] for p in practices], ["logging"])
            self.assertEqual(practices[0]["status"], "active")

    def test_promotion_with_run_report_provenance_resolves_s2(self):
        """practice-skills S2: a supported proposal promotes and then resolves for a matching order"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            pid = add_practice(proj, "error-handling", "Wrap I/O errors with context",
                               languages=["python"], stations=["builder"])
            self.assertEqual(pid, "P-1")
            self.assertFalse(any((proj / "brain" / "inbox").iterdir()))
            wo = WorkOrder(id="wo-r-1", kind="feature", title="t", surfaces=["data"])
            res = resolve_practices(proj, wo, ["builder", "test-writer"], {"languages": ["python"]})
            self.assertEqual(res["resolved"]["builder"], [pid])

    def test_promotion_with_decision_record_provenance_s2(self):
        """practice-skills S2: an owner decision record under brain/decisions/ is valid provenance"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            dec = proj / "brain" / "decisions"
            dec.mkdir(parents=True, exist_ok=True)
            (dec / "0001-adopt-logging.md").write_text("# Decision 0001\n\nStatus: accepted\n")
            pid = add_practice(proj, "logging", "Log structured events",
                               source="decision brain/decisions/0001-adopt-logging.md")
            self.assertEqual(pid, "P-1")

    def test_promotion_refused_without_real_provenance_s2(self):
        """practice-skills S2: a missing run report or decision record refuses, reason named, nothing changes"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            for source in ("run wo-ghost-9, artifact runs/wo-ghost-9/notes.md, evidence verdict approved",
                           "decision brain/decisions/9999-nothing.md"):
                name = propose_practice(proj, "logging", "Log structured events", source=source)
                with self.assertRaises(ValueError) as cm:
                    promote_practice(proj, name)
                self.assertTrue(str(cm.exception))
                self.assertTrue((proj / "brain" / "inbox" / name).exists())
            self.assertEqual(parse_practices(proj), [])

    def test_promotion_refused_when_evidence_unsupported_s2(self):
        """practice-skills S2: a run report that exists but does not support the claim refuses"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            name = propose_practice(
                proj, "logging", "Log structured events",
                source="run wo-seed-001, artifact runs/wo-seed-001/notes.md, evidence verdict rejected")
            with self.assertRaises(ValueError) as cm:
                promote_practice(proj, name)
            self.assertIn("verdict", str(cm.exception))
            self.assertEqual(parse_practices(proj), [])

    def test_malformed_proposal_refused_s2(self):
        """practice-skills S2: a proposal missing required fields or with a bad enforcement is refused"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            for kwargs in ({"topic": "", "rule": "Do a thing", "enforcement": "prompt"},
                           {"topic": "logging", "rule": "", "enforcement": "prompt"},
                           {"topic": "logging", "rule": "Do a thing", "enforcement": "vibes"}):
                name = propose_practice(proj, source=SOURCE, **kwargs)
                with self.assertRaises(ValueError):
                    promote_practice(proj, name)
            self.assertEqual(parse_practices(proj), [])


class TestConflictAndSupersede(unittest.TestCase):
    def test_conflict_refused_naming_active_practice_s3(self):
        """practice-skills S3: same topic and overlapping scope without Supersedes is refused, naming the practice"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            first = add_practice(proj, "error-handling", "Wrap I/O errors", languages=["python"])
            name = propose_practice(proj, "error-handling", "Never wrap errors",
                                    languages=["python"], source=SOURCE)
            with self.assertRaises(ValueError) as cm:
                promote_practice(proj, name)
            self.assertIn(first, str(cm.exception))
            self.assertEqual(len(parse_practices(proj)), 1)
            self.assertTrue((proj / "brain" / "inbox" / name).exists())

    def test_same_topic_disjoint_scope_is_not_a_conflict_s3(self):
        """practice-skills S3: scope overlap needs a shared value on every dimension; disjoint languages coexist"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            add_practice(proj, "error-handling", "Wrap I/O errors", languages=["python"])
            second = add_practice(proj, "error-handling", "Return error values", languages=["go"])
            self.assertEqual(second, "P-2")
            self.assertTrue(check_brain(proj)["ok"])

    def test_unrestricted_dimension_overlaps_s3(self):
        """practice-skills S3: an empty (unrestricted) language dimension overlaps a restricted one"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            add_practice(proj, "error-handling", "Wrap I/O errors", languages=["python"])
            name = propose_practice(proj, "error-handling", "Any language rule", source=SOURCE)
            with self.assertRaises(ValueError):
                promote_practice(proj, name)

    def test_supersedes_replaces_and_check_brain_passes_s4(self):
        """practice-skills S4: Supersedes marks the old practice superseded, it stops resolving, check-brain passes"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            old = add_practice(proj, "error-handling", "Wrap I/O errors", languages=["python"])
            name = propose_practice(proj, "error-handling", "Wrap and log I/O errors",
                                    languages=["python"], source=SOURCE, supersedes=old)
            new = promote_practice(proj, name)
            by_id = {p["id"]: p for p in parse_practices(proj)}
            self.assertEqual(by_id[old]["status"], "superseded")
            self.assertEqual(by_id[new]["status"], "active")
            wo = WorkOrder(id="wo-s-1", kind="feature", title="t", surfaces=["data"])
            res = resolve_practices(proj, wo, ["builder"], {"languages": ["python"]})
            self.assertEqual(res["resolved"]["builder"], [new])
            self.assertEqual(res["active_count"], 1)
            self.assertTrue(check_brain(proj)["ok"])

    def test_supersedes_must_name_an_active_practice_s4(self):
        """practice-skills S4: Supersedes naming an unknown practice is a refusal"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            name = propose_practice(proj, "logging", "Log structured events",
                                    source=SOURCE, supersedes="P-42")
            with self.assertRaises(ValueError) as cm:
                promote_practice(proj, name)
            self.assertIn("P-42", str(cm.exception))


class TestCheckBrain(unittest.TestCase):
    def test_absent_base_passes_s8(self):
        """practice-skills R2: check-brain passes on a repository with no practices base"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            self.assertFalse((proj / "brain" / "practices.md").exists())
            self.assertTrue(check_brain(proj)["ok"])
            with redirect_stdout(io.StringIO()):
                self.assertEqual(cli_main(["check-brain", str(proj)]), 0)

    def test_hand_edited_conflict_fails_s9(self):
        """practice-skills S9: two active practices with one topic and overlapping scope fail check-brain"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            add_practice(proj, "error-handling", "Wrap I/O errors", languages=["python"])
            add_practice(proj, "error-handling", "Return error values", languages=["go"])
            path = proj / "brain" / "practices.md"
            text = path.read_text(encoding="utf-8")
            self.assertIn("go", text)
            path.write_text(text.replace("go", "python"), encoding="utf-8")
            self.assertGreaterEqual(len([p for p in parse_practices(proj) if p["status"] == "active"]), 1)
            result = check_brain(proj)
            self.assertFalse(result["ok"])
            self.assertTrue(any("error-handling" in p for p in result["problems"]))
            with redirect_stdout(io.StringIO()):
                self.assertNotEqual(cli_main(["check-brain", str(proj)]), 0)

    def test_malformed_base_fails_s9(self):
        """practice-skills R2: a malformed practices.md fails check-brain"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            add_practice(proj, "logging", "Log structured events")
            path = proj / "brain" / "practices.md"
            path.write_text(path.read_text(encoding="utf-8") + "\n## P-9\nthis entry has no fields\n",
                            encoding="utf-8")
            self.assertFalse(check_brain(proj)["ok"])


class TestResolution(unittest.TestCase):
    STATIONS = ["spec-writer", "test-writer", "builder"]

    def wo(self, surfaces=("data",)):
        return WorkOrder(id="wo-res-1", kind="feature", title="t", surfaces=list(surfaces))

    def test_language_scope_s5(self):
        """practice-skills S5: a language scoped practice reaches a matching order, not another language's"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            pid = add_practice(proj, "typing", "Annotate public functions", languages=["python"])
            hit = resolve_practices(proj, self.wo(), self.STATIONS, {"languages": ["python"]})
            miss = resolve_practices(proj, self.wo(), self.STATIONS, {"languages": ["go"]})
            self.assertTrue(all(hit["resolved"][s] == [pid] for s in self.STATIONS))
            self.assertTrue(all(miss["resolved"].get(s, []) == [] for s in self.STATIONS))

    def test_station_scope_s5(self):
        """practice-skills S5: a station scoped practice reaches only that station"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            pid = add_practice(proj, "tdd", "Write the failing test first", stations=["builder"])
            res = resolve_practices(proj, self.wo(), self.STATIONS, {})
            self.assertEqual(res["resolved"]["builder"], [pid])
            self.assertEqual(res["resolved"].get("test-writer", []), [])
            self.assertEqual(res["resolved"].get("spec-writer", []), [])

    def test_surface_scope_and_conjunction_s5(self):
        """practice-skills S5: dimensions are conjunctive, so one failing dimension excludes the practice"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            pid = add_practice(proj, "a11y", "Label every control", surfaces=["ui"],
                               languages=["python"])
            cfg = {"languages": ["python"]}
            self.assertEqual(resolve_practices(proj, self.wo(["ui"]), self.STATIONS, cfg)
                             ["resolved"]["builder"], [pid])
            self.assertEqual(resolve_practices(proj, self.wo(["data"]), self.STATIONS, cfg)
                             ["resolved"].get("builder", []), [])
            self.assertEqual(resolve_practices(proj, self.wo(["ui"]), self.STATIONS, {"languages": ["go"]})
                             ["resolved"].get("builder", []), [])

    def test_values_within_a_dimension_are_disjunctive_s5(self):
        """practice-skills S5: any one listed language matching is enough"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            pid = add_practice(proj, "typing", "Annotate", languages=["python", "go"])
            res = resolve_practices(proj, self.wo(), self.STATIONS, {"languages": ["go"]})
            self.assertEqual(res["resolved"]["builder"], [pid])

    def test_resolution_is_deterministic_s5(self):
        """practice-skills R3: identical inputs give identical output, ordered by practice id"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            ids = [add_practice(proj, f"topic-{n}", f"Rule {n}") for n in range(3)]
            a = resolve_practices(proj, self.wo(), self.STATIONS, {})
            b = resolve_practices(proj, self.wo(), self.STATIONS, {})
            self.assertEqual(a, b)
            self.assertEqual(a["resolved"]["builder"], ids)
            self.assertEqual(a["active_count"], 3)

    def test_override_excludes_topic_s7(self):
        """practice-skills S7: an overridden topic resolves nothing and the exclusion is reported"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            add_practice(proj, "styling", "Use the base style rule")
            keep = add_practice(proj, "logging", "Log structured events")
            res = resolve_practices(proj, self.wo(), self.STATIONS,
                                    {"practice_overrides": ["styling"]})
            self.assertEqual(res["resolved"]["builder"], [keep])
            self.assertEqual(res["excluded_topics"], ["styling"])
            self.assertEqual(res["active_count"], 2)

    def test_override_is_explicit_names_only_s7(self):
        """practice-skills R5: a topic is excluded only by exact name, never by substring or inference"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            pid = add_practice(proj, "styling", "Use the base style rule")
            res = resolve_practices(proj, self.wo(), self.STATIONS,
                                    {"practice_overrides": ["style"]})
            self.assertEqual(res["resolved"]["builder"], [pid])


class TestRunnerIntegration(unittest.TestCase):
    def test_prompt_and_gate_split_s6(self):
        """practice-skills S6: prompt practices reach their stations' packets only; gate practices reach the gate output only"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            add_practice(proj, "tdd", "PROMPTRULE write the failing test first",
                         enforcement="prompt", stations=["builder"])
            add_practice(proj, "lint", "GATERULE keep the linter clean", enforcement="gate")
            run_dir, report = run(proj, tmp, "wo-split-1")
            builder = packet(run_dir, "builder")
            self.assertIn("## Practices", builder)
            self.assertIn("PROMPTRULE", builder)
            for st in ("test-writer", "spec-writer", "reviewer-spec"):
                text = packet(run_dir, st)
                self.assertNotIn("PROMPTRULE", text)
            all_packets = "\n".join(p.read_text(encoding="utf-8") for p in run_dir.glob("*.packet.md"))
            self.assertNotIn("GATERULE", all_packets)
            gate_out = (run_dir / "checks-gate.pre-review.output.md").read_text(encoding="utf-8")
            self.assertIn("P-2", gate_out)
            self.assertIn("lint", gate_out)
            self.assertNotIn("P-1", gate_out)
            self.assertNotIn("PROMPTRULE", gate_out)

    def test_report_and_routing_record_resolution_s7(self):
        """practice-skills R4: report.json and routing.json carry the same resolution, with overrides recorded"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp, {"practice_overrides": ["styling"]})
            add_practice(proj, "styling", "STYLERULE base style")
            keep = add_practice(proj, "logging", "LOGRULE log events", stations=["builder"])
            run_dir, report = run(proj, tmp, "wo-rec-1")
            rec = report["practices"]
            self.assertEqual(rec["resolved"]["builder"], [keep])
            self.assertEqual(rec["excluded_topics"], ["styling"])
            self.assertEqual(rec["active_count"], 2)
            routing = json.loads((run_dir / "routing.json").read_text(encoding="utf-8"))
            self.assertEqual(routing["practices"], rec)
            all_packets = "\n".join(p.read_text(encoding="utf-8") for p in run_dir.glob("*.packet.md"))
            self.assertNotIn("STYLERULE", all_packets)
            self.assertIn("LOGRULE", packet(run_dir, "builder"))

    def test_language_signal_from_config_reaches_packets_s5(self):
        """practice-skills S5: the runner uses the config language signal when resolving"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp, {"languages": ["go"]})
            add_practice(proj, "typing", "PYRULE annotate", languages=["python"])
            run_dir, report = run(proj, tmp, "wo-lang-1")
            all_packets = "\n".join(p.read_text(encoding="utf-8") for p in run_dir.glob("*.packet.md"))
            self.assertNotIn("PYRULE", all_packets)
            self.assertEqual(report["practices"]["resolved"].get("builder", []), [])
            self.assertEqual(report["practices"]["active_count"], 1)

    def test_no_base_changes_nothing_but_the_report_field_s8(self):
        """practice-skills S8: with no practices base, packets carry no Practices section and the report records an empty resolution"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            self.assertFalse((proj / "brain" / "practices.md").exists())
            run_dir, report = run(proj, tmp, "wo-none-1")
            for p in run_dir.glob("*.packet.md"):
                self.assertNotIn("## Practices", p.read_text(encoding="utf-8"))
            rec = report["practices"]
            self.assertEqual(rec["active_count"], 0)
            self.assertEqual(rec["excluded_topics"], [])
            self.assertTrue(all(v == [] for v in rec["resolved"].values()))
            self.assertEqual(report["verdict"], "approved")


class TestShippedState(unittest.TestCase):
    def test_factory_ships_no_practices_r7(self):
        """practice-skills R7: the mechanism ships with no promoted practices in the factory brain"""
        path = ROOT / "brain" / "practices.md"
        if path.exists():
            self.assertEqual(parse_practices(ROOT), [])

    def test_no_dash_characters_in_produced_files_r8(self):
        """practice-skills scope limit: no em dash or en dash in the practice code or this test file"""
        for rel in ("anvil/brain.py", "anvil/runner.py", "anvil/cli.py", "tests/test_practice_skills.py"):
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertNotIn(chr(0x2014), text, rel)
            self.assertNotIn(chr(0x2013), text, rel)


if __name__ == "__main__":
    unittest.main()
