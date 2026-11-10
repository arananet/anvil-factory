"""Curated craft skills (.openspec/specs/curated-skills/spec.md).

Scenario map:
S1 catalog soundness        -> ShippedCatalogTests
S2 resolution by scope      -> ResolutionTests
S3 packet injection         -> PacketTests
S4 project catalog/override -> ProjectCatalogTests
S5 malformed entries        -> MalformedCatalogTests
S6 product type detection   -> ProductTypeTests
S7 run context              -> RunContextTests
S8 producer write access    -> WriteAccessTests
S9 report recording         -> ReportTests
"""

import json
import re
import tempfile
import unittest
from pathlib import Path

from anvil.model import WorkOrder
from anvil.pipeline import load_pipeline
from anvil.quality import (detect_product_type, get_product_type,
                           packet_quality_charter_section, load_quality_charter)
from anvil.runner import _packet_text, packet_run_context_section, run_pipeline
from anvil.scaffold import init_project
from anvil.skills import (MAX_SKILL_CHARS, check_skills, load_catalog,
                          packet_skills_section, resolve_skills, skills_by_id)
from anvil.stations import load_registry

ROOT = Path(__file__).resolve().parent.parent
SDLC = ["intake", "spec-writer", "test-writer", "builder", "reviewer-spec",
        "reviewer-security", "reviewer-tests", "reviewer-architecture",
        "reviewer-design", "approver"]
CONTENT = ["intake", "brief-writer", "researcher", "writer", "media-producer",
           "reviewer-facts", "reviewer-voice"]


def order(title="Change", description="", surfaces=None, kind="feature"):
    return WorkOrder(id="wo-skill-test", kind=kind, title=title,
                     description=description, surfaces=surfaces or [])


def write_skill(root, sid, body="Do the work well.", **scope):
    skill_dir = Path(root) / "skills" / sid
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {sid}\ndescription: test skill\n---\n\n{body}\n", encoding="utf-8")
    entry = {"id": sid, "source": "test fixture"}
    entry.update(scope)
    return entry


def write_catalog(root, entries):
    path = Path(root) / "skills" / "catalog.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"version": 1, "skills": entries}), encoding="utf-8")


class ShippedCatalogTests(unittest.TestCase):
    def test_shipped_catalog_has_no_problems(self):
        self.assertEqual(check_skills(), [])

    def test_shipped_catalog_covers_the_five_domains(self):
        domains = {e["domain"] for e in load_catalog()[0]}
        for domain in ("architecture", "design", "web", "gaming", "content"):
            self.assertIn(domain, domains)

    def test_every_shipped_skill_is_scoped_sourced_and_within_the_cap(self):
        registry = load_registry(ROOT / "stations")
        for e in load_catalog()[0]:
            self.assertTrue(e["source"], e["id"])
            self.assertTrue(e["description"], e["id"])
            self.assertLessEqual(len(e["body"]), MAX_SKILL_CHARS, e["id"])
            for station in e["stations"]:
                self.assertIn(station, registry, f"{e['id']} names unknown station {station}")

    def test_every_skill_directory_is_listed_in_the_catalog(self):
        listed = {e["id"] for e in load_catalog()[0]}
        on_disk = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
        self.assertEqual(on_disk, listed)

    def test_shipped_skills_carry_no_em_or_en_dash(self):
        for path in list((ROOT / "skills").rglob("*.md")) + [ROOT / "skills" / "catalog.json"]:
            self.assertIsNone(re.search("[\u2013\u2014]", path.read_text(encoding="utf-8")), str(path))

    def test_every_producing_station_receives_at_least_one_skill(self):
        web = resolve_skills(ROOT, order("Landing page", "Build a landing page", ["ui"]), SDLC)
        for station in ("spec-writer", "test-writer", "builder"):
            self.assertTrue(web["resolved"][station], station)
        content = resolve_skills(ROOT, order("Post", "Write a post", ["content"], kind="content"), CONTENT)
        for station in ("brief-writer", "researcher", "writer", "media-producer"):
            self.assertTrue(content["resolved"][station], station)


class ResolutionTests(unittest.TestCase):
    def test_web_order_gives_the_builder_design_and_web_skills_not_game_skills(self):
        res = resolve_skills(ROOT, order("Landing page", "A landing page for the product", ["ui"]), SDLC)
        builder = res["resolved"]["builder"]
        self.assertIn("interface-design", builder)
        self.assertIn("web-engineering", builder)
        self.assertNotIn("game-design-feel", builder)
        self.assertNotIn("game-engineering", builder)

    def test_game_order_gives_the_builder_game_skills_not_web_skills(self):
        res = resolve_skills(ROOT, order("Platformer", "Product type: game. A 2D platformer", ["ui"]), SDLC)
        builder = res["resolved"]["builder"]
        self.assertIn("game-design-feel", builder)
        self.assertIn("game-engineering", builder)
        self.assertNotIn("interface-design", builder)
        self.assertIn("game-design-feel", res["resolved"]["spec-writer"])

    def test_backend_order_gets_no_design_or_game_skills(self):
        res = resolve_skills(ROOT, order("Add endpoint", "Add a JSON endpoint", ["api"]), SDLC)
        builder = res["resolved"]["builder"]
        self.assertIn("implementation-craft", builder)
        self.assertIn("architecture-fundamentals", builder)
        for sid in ("interface-design", "web-engineering", "game-design-feel", "game-engineering"):
            self.assertNotIn(sid, builder)

    def test_backend_order_that_mentions_a_dashboard_or_a_game_gets_no_visual_skills(self):
        wo = order("Intake outcomes", "Parse outcomes; the dashboard and the game example are untouched", ["data"])
        res = resolve_skills(ROOT, wo, SDLC)
        self.assertEqual(res["signals"]["product_types"], [])
        for sid in ("interface-design", "web-engineering", "game-design-feel", "game-engineering"):
            self.assertNotIn(sid, res["resolved"]["builder"])

    def test_game_project_gets_game_skills_on_every_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            init_project(proj, "Proj")
            brain = proj / "brain" / "project.md"
            brain.write_text(brain.read_text(encoding="utf-8") + "\n\nProduct type: game\n", encoding="utf-8")
            res = resolve_skills(proj, order("Fix collision", "Resolve the floor tunnelling", ["data"]), SDLC)
            self.assertIn("game-engineering", res["resolved"]["builder"])
            self.assertIn("game-engineering", res["resolved"]["test-writer"])

    def test_skills_reach_only_the_stations_they_name(self):
        res = resolve_skills(ROOT, order("Landing page", "A landing page", ["ui"]), SDLC)
        for station in ("intake", "approver", "reviewer-design", "reviewer-spec"):
            self.assertEqual(res["resolved"][station], [], station)
        self.assertNotIn("interface-design", res["resolved"]["test-writer"])

    def test_resolution_is_deterministic(self):
        wo = order("Landing page", "A landing page", ["ui"])
        self.assertEqual(resolve_skills(ROOT, wo, SDLC), resolve_skills(ROOT, wo, SDLC))


class PacketTests(unittest.TestCase):
    def test_section_carries_authority_note_and_the_skill_bodies(self):
        res = resolve_skills(ROOT, order("Landing page", "A landing page", ["ui"]), SDLC)
        entries = skills_by_id(ROOT)
        section = packet_skills_section(res, "builder", entries)
        self.assertTrue(section.startswith("## Craft skills"))
        self.assertIn("Order of authority", section)
        self.assertIn("### Skill: interface-design", section)
        self.assertIn(entries["interface-design"]["body"], section)

    def test_station_with_no_skill_gets_no_section(self):
        res = resolve_skills(ROOT, order("Landing page", "A landing page", ["ui"]), SDLC)
        self.assertEqual(packet_skills_section(res, "approver", skills_by_id(ROOT)), "")

    def test_packet_places_skills_in_the_stable_prefix_before_the_work_order(self):
        wo = order("Landing page", "A landing page", ["ui"])
        text = _packet_text("builder", "prompt", wo, [], skills_section="## Craft skills\n\nbody")
        self.assertIn("## Craft skills", text)
        self.assertLess(text.index("## Craft skills"), text.index("## Work order"))

    def test_packet_without_skills_is_unchanged(self):
        wo = order("Change", "x", ["api"])
        self.assertEqual(_packet_text("builder", "prompt", wo, []),
                         _packet_text("builder", "prompt", wo, [], skills_section="", run_context_section=""))


class ProjectCatalogTests(unittest.TestCase):
    def test_project_skill_adds_to_and_replaces_factory_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            proj.mkdir()
            write_catalog(proj, [
                write_skill(proj, "house-style", stations=["builder"]),
                write_skill(proj, "implementation-craft", body="Project version.", stations=["builder"]),
            ])
            entries = skills_by_id(proj)
            self.assertEqual(entries["house-style"]["origin"], "project")
            self.assertEqual(entries["implementation-craft"]["body"], "Project version.")
            self.assertEqual(entries["test-design"]["origin"], "factory")
            res = resolve_skills(proj, order("Change", "x", ["api"]), SDLC)
            self.assertIn("house-style", res["resolved"]["builder"])

    def test_skill_overrides_switch_a_skill_off_and_are_recorded(self):
        res = resolve_skills(ROOT, order("Landing page", "A landing page", ["ui"]), SDLC,
                             {"skill_overrides": ["interface-design"]})
        self.assertNotIn("interface-design", res["resolved"]["builder"])
        self.assertIn("web-engineering", res["resolved"]["builder"])
        self.assertEqual(res["disabled"], ["interface-design"])


class MalformedCatalogTests(unittest.TestCase):
    def check(self, entries, expected):
        with tempfile.TemporaryDirectory() as tmp:
            write_catalog(tmp, entries(tmp))
            loaded, problems = load_catalog(root=tmp)
            self.assertEqual(loaded, [])
            self.assertTrue(any(expected in p for p in problems), problems)

    def test_missing_file_is_reported_and_never_resolves(self):
        self.check(lambda tmp: [{"id": "ghost", "stations": ["builder"], "source": "x"}], "not found")

    def test_missing_source_is_refused(self):
        self.check(lambda tmp: [dict(write_skill(tmp, "nosrc", stations=["builder"]), source="")], "source")

    def test_missing_stations_is_refused(self):
        self.check(lambda tmp: [write_skill(tmp, "nostation")], "at least one station")

    def test_oversized_body_is_refused(self):
        self.check(lambda tmp: [write_skill(tmp, "big", body="x" * (MAX_SKILL_CHARS + 1), stations=["builder"])], "cap")

    def test_path_outside_the_root_is_refused(self):
        self.check(lambda tmp: [{"id": "esc", "path": "../outside/SKILL.md", "stations": ["builder"], "source": "x"}],
                   "leaves the catalog root")

    def test_absent_catalog_is_empty_and_sound(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(load_catalog(root=tmp), ([], []))


class ProductTypeTests(unittest.TestCase):
    def test_landing_page_order_is_an_interface_not_a_physical_product(self):
        wo = order("ANVIL landing page", "One self contained HTML page", ["ui", "content"])
        self.assertEqual(get_product_type(wo), "interface")

    def test_explicit_declaration_wins(self):
        wo = order("Hero image for the landing page", "Product type: physical_product", ["ui"])
        self.assertEqual(get_product_type(wo), "physical_product")

    def test_project_declared_type_is_honored(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            init_project(proj, "Proj")
            brain = proj / "brain" / "project.md"
            brain.write_text(brain.read_text(encoding="utf-8") + "\n\nProduct type: dashboard\n", encoding="utf-8")
            self.assertEqual(get_product_type(order("Add a chart", "", ["ui"]), proj), "interface")
            brain.write_text(brain.read_text(encoding="utf-8").replace("dashboard", "game"), encoding="utf-8")
            self.assertEqual(get_product_type(order("Add a level", "", ["ui"]), proj), "game")

    def test_ui_only_run_with_a_known_project_defaults_to_interface(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            init_project(proj, "Proj")
            self.assertEqual(get_product_type(order("Settings", "", ["ui"]), proj), "interface")
            self.assertEqual(get_product_type(order("Asset set", "", ["content"]), proj), "physical_product")

    def test_nothing_detected_means_none(self):
        self.assertIsNone(detect_product_type(order("Add endpoint", "Add a JSON endpoint", ["api"])))

    def test_interface_charter_reaches_the_builder_without_physical_criteria(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            init_project(proj, "Proj")
            wo = order("Landing page", "A landing page", ["ui"])
            section = packet_quality_charter_section(proj, "builder", wo)
            self.assertIn("Product type: interface", section)
            self.assertIn("Hierarchy", section)
            self.assertNotIn("Contact", section)
        self.assertIn("interface", load_quality_charter()["criteria"])


class RunContextTests(unittest.TestCase):
    def test_lists_existing_upstream_outputs_spec_and_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp)
            (proj / "runs" / "wo-skill-test").mkdir(parents=True)
            (proj / "runs" / "wo-skill-test" / "spec-writer.output.md").write_text("spec", encoding="utf-8")
            (proj / "specs").mkdir()
            (proj / "specs" / "s.md").write_text("spec", encoding="utf-8")
            wo = order()
            wo.spec_path = "specs/s.md"
            steps = [{"station": "intake", "status": "executed"}, {"station": "spec-writer", "status": "executed"}]
            section = packet_run_context_section(proj, wo, steps, "builder", ["make test"])
            self.assertIn("specs/s.md", section)
            self.assertIn("runs/wo-skill-test/spec-writer.output.md", section)
            self.assertNotIn("intake.output.md", section)
            self.assertIn("`make test`", section)
            other = packet_run_context_section(proj, wo, steps, "reviewer-spec", ["make test"])
            self.assertNotIn("make test", other)

    def test_nothing_on_disk_means_no_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(packet_run_context_section(tmp, order(), [], "spec-writer", []), "")


class WriteAccessTests(unittest.TestCase):
    PRODUCERS = {"builder", "test-writer", "spec-writer", "blueprint",
                 "brief-writer", "researcher", "writer", "media-producer"}

    def load(self, name):
        import importlib.util
        spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_producing_stations_may_write_and_reviewers_may_not(self):
        registry = load_registry(ROOT / "stations")
        for name in ("claude_station", "codex_station"):
            write_stations = self.load(name).WRITE_STATIONS
            self.assertEqual(write_stations, self.PRODUCERS, name)
            for station in registry.ids():
                if station.startswith("reviewer") or station in {"scout", "observer", "supervisor"}:
                    self.assertNotIn(station, write_stations, f"{name}: {station}")


class ReportTests(unittest.TestCase):
    def test_packet_run_records_the_resolution_and_writes_skills_into_packets(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            init_project(proj, "Proj")
            wo = order("Landing page", "A landing page for the product", ["ui"])
            pipeline = load_pipeline(ROOT / "pipelines" / "sdlc-default.json")
            run_pipeline(proj, pipeline, wo, registry=load_registry(ROOT / "stations"))
            report = json.loads((proj / "runs" / wo.id / "report.json").read_text(encoding="utf-8"))
            skills = report["skills"]
            self.assertIn("interface-design", skills["resolved"]["builder"])
            self.assertEqual(skills["signals"]["product_types"], ["interface"])
            self.assertGreater(skills["catalog_count"], 0)
            builder_packet = (proj / "runs" / wo.id / "builder.packet.md").read_text(encoding="utf-8")
            self.assertIn("### Skill: interface-design", builder_packet)
            self.assertIn("### Skill: implementation-craft", builder_packet)
            spec_packet = (proj / "runs" / wo.id / "spec-writer.packet.md").read_text(encoding="utf-8")
            self.assertIn("### Skill: spec-writing", spec_packet)
            self.assertNotIn("### Skill: interface-design", spec_packet)
            self.assertNotIn("## Craft skills",
                             (proj / "runs" / wo.id / "reviewer-spec.packet.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
