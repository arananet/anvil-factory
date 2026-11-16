"""wo-gh-43 attribution-default: tests mapped to spec scenarios S1 to S7.

Spec: .openspec/specs/attribution-default/spec.md
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from anvil.blueprints import get_blueprint
from anvil.gates import checks_gate
from anvil.onboard import onboard_project
from anvil.scaffold import new_project

ROOT = Path(__file__).resolve().parent.parent
LINE = "Made with ANVIL, an open source software factory."
LANDING = "https://anvil-landing-7x1.pages.dev"
SENTIA = ("Sentia is a concept product, designed and built end to end by ANVIL, "
          "an open source software factory. Developed by Eduardo Arana.")
EXCEPTION = ("Attribution exception: approved by Eduardo Arana on 2026-11-16: "
             "brand-neutral kiosk build")
EM_DASH = "—"


def page(footer):
    return f"<!doctype html><html><head><title>t</title></head><body><main>Hi</main>{footer}</body></html>"


def gate(project, deliverable_html=None, where="public/index.html", spec_text=None):
    project = Path(project)
    if deliverable_html is not None:
        f = project / where
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(deliverable_html, encoding="utf-8")
    if spec_text is not None:
        s = project / ".openspec" / "specs" / "site-shell" / "spec.md"
        s.parent.mkdir(parents=True, exist_ok=True)
        s.write_text(spec_text, encoding="utf-8")
    return checks_gate("pre-review", {"checks": ["exit 0"], "protected_paths": []},
                       set(), str(project), "wo-attr", base_ref=None)


class S1ScaffoldSeedsRule(unittest.TestCase):
    def _assert_rule(self, text, label):
        for needle in (LINE, LANDING, "footer", "bespoke"):
            self.assertIn(needle, text, f"{label} lacks {needle!r}")

    def test_s1_static_site_seeds_spec_and_brain(self):
        """S1: static-site scaffold carries the requirement in site-shell spec and brain/project.md"""
        bp = get_blueprint(ROOT / "blueprints", "static-site")
        with tempfile.TemporaryDirectory() as tmp:
            root = new_project(Path(tmp) / "demo", "Demo", bp, idea="A site")
            self._assert_rule((root / ".openspec/specs/site-shell/spec.md").read_text(), "site-shell spec")
            self._assert_rule((root / "brain/project.md").read_text(), "brain/project.md")

    def test_s1_non_web_blueprint_not_seeded(self):
        """S1: a non web blueprint (python-service) does not get the web footer requirement"""
        bp = get_blueprint(ROOT / "blueprints", "python-service")
        with tempfile.TemporaryDirectory() as tmp:
            root = new_project(Path(tmp) / "demo", "Demo", bp, idea="A service")
            self.assertNotIn(LINE, (root / "brain/project.md").read_text())

    def test_s1_onboard_web_project_records_requirement_without_overwriting(self):
        """S1: onboard on a web project records the requirement and leaves existing files byte-identical"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "legacy"
            (root / "public").mkdir(parents=True)
            (root / "README.md").write_text("# Legacy\n\nA site.\n")
            (root / "public/index.html").write_text(page("<footer>none</footer>"))
            (root / "brain").mkdir()
            (root / "brain/project.md").write_text("# Mine\n")
            before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
            onboard_project(root)
            for p, data in before.items():
                self.assertEqual(p.read_bytes(), data, f"{p} changed")
            self._assert_rule((root / "ONBOARDING.md").read_text(), "ONBOARDING.md")

    _assert_rule = _assert_rule


class S2CheckPasses(unittest.TestCase):
    def test_s2_default_line_with_landing_link_passes(self):
        """S2: default footer line linked to the landing passes"""
        with tempfile.TemporaryDirectory() as tmp:
            r = gate(tmp, page(f'<footer><a href="{LANDING}">{LINE}</a></footer>'))
            self.assertEqual(r["gate_verdict"], "pass", r["output"])

    def test_s2_sentia_bespoke_credit_passes(self):
        """S2: Sentia style bespoke credit naming ANVIL as builder passes"""
        with tempfile.TemporaryDirectory() as tmp:
            r = gate(tmp, page(f"<footer><p>{SENTIA}</p></footer>"))
            self.assertEqual(r["gate_verdict"], "pass", r["output"])

    def test_s2_dist_and_root_layouts_checked(self):
        """S2: deliverable found under dist/ and at project root"""
        for where in ("dist/index.html", "index.html"):
            with tempfile.TemporaryDirectory() as tmp:
                r = gate(tmp, page("<footer>nothing</footer>"), where=where)
                self.assertEqual(r["gate_verdict"], "fail", where)


class S3CheckFails(unittest.TestCase):
    def test_s3_no_attribution_fails_and_names_reason(self):
        """S3: no attribution fails the gate and output names the missing attribution"""
        with tempfile.TemporaryDirectory() as tmp:
            r = gate(tmp, page("<footer>Copyright 2026</footer>"))
            self.assertEqual(r["gate_verdict"], "fail")
            self.assertEqual(r["status"], "failed")
            self.assertIn("attribution", r["output"].lower())
            self.assertIn("ANVIL", r["output"])

    def test_s3_anvil_only_in_comment_fails(self):
        """S3: ANVIL only inside an HTML comment does not count"""
        with tempfile.TemporaryDirectory() as tmp:
            r = gate(tmp, page(f"<!-- {LINE} --><footer>Copyright</footer>"))
            self.assertEqual(r["gate_verdict"], "fail")

    def test_s3_anvil_only_in_script_or_attribute_fails(self):
        """S3: ANVIL only in script or attribute does not count"""
        with tempfile.TemporaryDirectory() as tmp:
            r = gate(tmp, page(f'<footer title="{LINE}">x</footer><script>var a="built by ANVIL";</script>'))
            self.assertEqual(r["gate_verdict"], "fail")

    def test_s3_anvil_mentioned_without_building_does_not_pass(self):
        """S3: the word ANVIL in a sentence not stating it built the project fails"""
        with tempfile.TemporaryDirectory() as tmp:
            r = gate(tmp, page("<footer>We compared ANVIL with a forge catalogue.</footer>"))
            self.assertEqual(r["gate_verdict"], "fail")


class S4ExceptionHonoured(unittest.TestCase):
    def test_s4_recorded_exception_passes_and_is_named(self):
        """S4: exception line in the project spec passes and appears in output"""
        with tempfile.TemporaryDirectory() as tmp:
            r = gate(tmp, page("<footer>Kiosk</footer>"),
                     spec_text=f"# Shell\n\n## Requirements\n{EXCEPTION}\n")
            self.assertEqual(r["gate_verdict"], "pass", r["output"])
            self.assertIn(EXCEPTION, r["output"])

    def test_s4_malformed_exception_is_not_honoured(self):
        """S4: only the exact line prefix counts"""
        with tempfile.TemporaryDirectory() as tmp:
            r = gate(tmp, page("<footer>Kiosk</footer>"),
                     spec_text="Attribution waived because we said so\n")
            self.assertEqual(r["gate_verdict"], "fail")


class S5NonWebUnaffected(unittest.TestCase):
    def test_s5_no_html_deliverable_no_attribution_output(self):
        """S5: no HTML deliverable, gate passes with no attribution failure or output"""
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "app.py").write_text("print(1)\n")
            r = gate(tmp)
            self.assertEqual(r["gate_verdict"], "pass", r["output"])
            self.assertNotIn("attribution", r["output"].lower())


class S6StationGuidance(unittest.TestCase):
    def test_s6_builder_and_publisher_prompts(self):
        """S6: both prompts carry the line, placement, keep-bespoke rule and exception wording"""
        for station in ("builder", "publisher"):
            text = (ROOT / "stations" / station / "PROMPT.md").read_text()
            self.assertIn(LINE, text, station)
            self.assertIn("owner approved exception", text, station)
            self.assertIn("footer", text, station)
            self.assertIn("bespoke", text, station)
        self.assertIn("defect", (ROOT / "stations/publisher/PROMPT.md").read_text())


class S7DecisionRecord(unittest.TestCase):
    def test_s7_decision_record_exists_in_format(self):
        """S7: 0012 record has the sections of 0011, mentions audit and line, no em dash"""
        ref = (ROOT / "brain/decisions/0011-station-timeout.md").read_text().lower()
        rec = ROOT / "brain/decisions/0012-anvil-attribution-default.md"
        self.assertTrue(rec.is_file())
        text = rec.read_text()
        for section in ("context", "decision", "consequences"):
            if section in ref:
                self.assertIn(section, text.lower())
        self.assertIn("2026-11-15", text)
        self.assertIn(LINE, text)
        self.assertNotIn(EM_DASH, text)


if __name__ == "__main__":
    unittest.main()
