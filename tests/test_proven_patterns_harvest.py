"""Proven patterns: harvest into quarantine and promotion by the owner (spec: proven-patterns, wo-gh-50).

The tests run the real commands `anvil harvest`, `anvil promote-pattern` and
`anvil check-patterns` against a fixture git project with two commits, built
in a temporary directory, with ANVIL_PATTERNS_DIR naming a temporary
patterns root (interface notes in tests/fixtures/patterns/patterns_support.py).

Scenario map:
  S3 (R2.1 to R2.4)  test_s3_harvest_writes_proposal_with_provenance, test_s3_harvest_makes_no_model_or_network_call,
                     test_s3_harvest_is_deterministic, test_s3_second_harvest_same_id_refuses,
                     test_s3_refusals_write_nothing, test_s3_line_provenance_note,
                     test_s3_design_tokens_become_forbidden_values
  S5 (R3.1 to R3.3)  test_s5_open_version_refuses_and_changes_nothing, test_s5_edited_source_refuses_naming_path,
                     test_s5_empty_success_evidence_refuses, test_s5_refusal_lists_every_unmet_condition,
                     test_s5_content_rule_blocks_promotion, test_s5_complete_proposal_promotes,
                     test_s5_new_version_keeps_history_and_older_version_refuses
"""
import hashlib
import json
import re
import socket
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent / "fixtures" / "patterns"))
import patterns_support as ps  # noqa: E402

PID = "explainer-video"


def is_open(value):
    """An open field: a string starting with OPEN:, or a non-empty list of such strings."""
    if isinstance(value, str):
        return value.startswith("OPEN:")
    if isinstance(value, list) and value:
        return all(isinstance(v, str) and v.startswith("OPEN:") for v in value)
    return False


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.root = self.tmp / "patterns"
        (self.root / "inbox").mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def harvest(self, project, pid=PID, root=None, extra=()):
        return ps.cli(["harvest", str(project), "--as", pid, *extra], root or self.root)

    def promote(self, pid=PID):
        return ps.cli(["promote-pattern", pid, "--by", "owner"], self.root)

    def harvested(self, project=None, **kwargs):
        project = project or ps.make_git_project(self.tmp, **kwargs)
        code, out = self.harvest(project)
        self.assertEqual(code, 0, f"harvest must succeed; output:\n{out}")
        return project, self.root / "inbox" / PID


class Harvest(Base):
    def test_s3_harvest_writes_proposal_with_provenance(self):
        """S3: the proposal holds byte identical copies, per file commit and sha256, and open fields."""
        project, inbox = self.harvested()
        for rel in ("docs/stages.md", "tools/check_routes.py"):
            self.assertEqual((inbox / "source" / rel).read_bytes(), (project / rel).read_bytes(), rel)
        prov = json.loads((inbox / "provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(prov["provenance"], "outside_line")
        self.assertEqual(prov["head"], ps.git(project, "rev-parse", "HEAD"))
        self.assertEqual(prov["project"], str(project))
        self.assertEqual(prov["forbidden_values"], [])
        by_path = {entry["path"]: entry for entry in prov["files"]}
        self.assertEqual(sorted(by_path), ["docs/stages.md", "tools/check_routes.py"])
        for rel, entry in by_path.items():
            self.assertEqual(entry["commit"], ps.git(project, "log", "-1", "--format=%H", "--", rel), rel)
            self.assertEqual(entry["sha256"], hashlib.sha256((project / rel).read_bytes()).hexdigest(), rel)
        # the two files were last touched by different commits of the fixture
        self.assertNotEqual(by_path["docs/stages.md"]["commit"], by_path["tools/check_routes.py"]["commit"])
        self.assertIn("outside", prov["provenance_note"].lower())
        doc = json.loads((inbox / "pattern.json").read_text(encoding="utf-8"))
        self.assertEqual(doc["id"], PID)
        self.assertEqual(doc["source"]["commits"], [prov["head"]])
        for field in ("title", "version", "product_types", "success_evidence", "blueprint"):
            self.assertTrue(is_open(doc[field]), f"pattern.json {field} must be open, got {doc[field]!r}")
        self.assertRegex((inbox / "structure.md").read_text(encoding="utf-8"), r"(?m)^OPEN:")
        self.assertIn("OPEN:", (inbox / "dead-ends.json").read_text(encoding="utf-8"))
        self.assertIn("OPEN:", (inbox / "calibration.json").read_text(encoding="utf-8"))
        self.assertFalse((self.root / PID).exists(), "harvest never writes a promoted pack")

    def test_s3_line_provenance_note(self):
        """S3 (R2.4): provenance "line" is stated in provenance_note, which then does not say outside."""
        manifest = {"files": ["docs/stages.md"], "provenance": "line"}
        _, inbox = self.harvested(manifest=manifest)
        prov = json.loads((inbox / "provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(prov["provenance"], "line")
        self.assertTrue(prov["provenance_note"].strip())
        self.assertNotIn("outside", prov["provenance_note"].lower())

    def test_s3_harvest_makes_no_model_or_network_call(self):
        """S3: harvest makes no model call and no network call."""
        project = ps.make_git_project(self.tmp)
        network, runtimes = [], []

        def refuse_network(*args, **kwargs):
            network.append(args)
            raise OSError("network is not allowed in this test")

        def record_runtime(*args, **kwargs):
            runtimes.append(args)
            raise AssertionError("harvest must not create a runtime")

        with mock.patch.object(socket.socket, "connect", refuse_network), \
                mock.patch.object(socket, "create_connection", refuse_network), \
                mock.patch("anvil.executor.create_executor", record_runtime), \
                mock.patch("anvil.cli.create_executor", record_runtime):
            code, out = self.harvest(project)
        self.assertEqual(code, 0, out)
        self.assertEqual(network, [])
        self.assertEqual(runtimes, [])

    def test_s3_harvest_is_deterministic(self):
        """S3: a second harvest into a fresh patterns root writes byte identical files."""
        project, _ = self.harvested()
        other = self.tmp / "patterns-two"
        (other / "inbox").mkdir(parents=True)
        code, out = self.harvest(project, root=other)
        self.assertEqual(code, 0, out)
        first, second = ps.snapshot(self.root / "inbox" / PID), ps.snapshot(other / "inbox" / PID)
        self.assertTrue(first)
        self.assertEqual(first, second)

    def test_s3_second_harvest_same_id_refuses(self):
        """S3 (R2.3): an existing inbox entry is refused, not overwritten."""
        project, inbox = self.harvested()
        (inbox / "structure.md").write_text("operator notes in progress\n", encoding="utf-8")
        before = ps.snapshot(self.root)
        code, out = self.harvest(project)
        self.assertNotEqual(code, 0, out)
        self.assertIn(PID, out)
        self.assertEqual(ps.snapshot(self.root), before)

    def assert_refused(self, project, cause, extra=()):
        before = ps.snapshot(self.root)
        code, out = self.harvest(project, extra=extra)
        self.assertEqual(code, 1, f"harvest must refuse; output:\n{out}")
        self.assertIn(cause, out)
        self.assertEqual(ps.snapshot(self.root), before, "a refused harvest writes nothing")
        self.assertFalse((self.root / "inbox" / PID).exists())

    def test_s3_refusals_write_nothing(self):
        """S3 (R2.1): a path leaving the project, uncommitted edits, missing files and bad manifests refuse."""
        cases = {
            "leaves the project": ({"files": ["../outside.md"], "provenance": "outside_line"}, "../outside.md"),
            "absolute path": ({"files": ["/etc/hostname"], "provenance": "outside_line"}, "/etc/hostname"),
            "missing file": ({"files": ["docs/missing.md"], "provenance": "outside_line"}, "docs/missing.md"),
            "empty files": ({"files": [], "provenance": "outside_line"}, "files"),
            "bad provenance": ({"files": ["docs/stages.md"], "provenance": "maybe"}, "provenance"),
        }
        for label, (manifest, cause) in cases.items():
            with self.subTest(label):
                self.tearDown()
                self.setUp()
                (self.tmp / "outside.md").write_text("outside\n", encoding="utf-8")
                project = ps.make_git_project(self.tmp, manifest=manifest)
                self.assert_refused(project, cause)

    def test_s3_uncommitted_edit_refuses(self):
        """S3 (R2.1): a listed file with uncommitted edits refuses naming it."""
        project = ps.make_git_project(self.tmp)
        (project / "docs" / "stages.md").write_text(ps.STAGES_MD + "draft line\n", encoding="utf-8")
        self.assert_refused(project, "docs/stages.md")

    def test_s3_missing_or_malformed_manifest_refuses(self):
        """S3 (R2.1): no anvil-harvest.json, or one that is not JSON, refuses."""
        project = ps.make_git_project(self.tmp)
        (project / "anvil-harvest.json").unlink()
        self.assert_refused(project, "anvil-harvest.json")
        (project / "anvil-harvest.json").write_text("{nope", encoding="utf-8")
        self.assert_refused(project, "anvil-harvest.json")

    def test_s3_manifest_option_is_honoured(self):
        """S3 (R2.1): --manifest names another manifest file."""
        project = ps.make_git_project(self.tmp)
        other = self.tmp / "only-stages.json"
        ps.write_json(other, {"files": ["docs/stages.md"], "provenance": "line"})
        code, out = self.harvest(project, extra=("--manifest", str(other)))
        self.assertEqual(code, 0, out)
        copied = ps.snapshot(self.root / "inbox" / PID / "source")
        self.assertEqual(sorted(copied), ["docs/stages.md"])

    def test_s3_design_tokens_become_forbidden_values(self):
        """S3, S2 (R1.6): every string value of length 4 or more in the design token file is recorded."""
        _, inbox = self.harvested(design_tokens={"brand": "#1A2B3C", "accent": "red", "type": {"title": "Pixel Sans"}})
        prov = json.loads((inbox / "provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(sorted(prov["forbidden_values"]), ["#1A2B3C", "Pixel Sans"])
        self.assertFalse((inbox / "source" / "design" / "brand.json").exists(),
                         "the design token file is never copied into the proposal")


class Promote(Base):
    def complete(self, **kwargs):
        project, inbox = self.harvested()
        ps.complete_proposal(inbox, **kwargs)
        return project, inbox

    def assert_refused(self, *names):
        before = ps.snapshot(self.root)
        code, out = self.promote()
        self.assertEqual(code, 1, f"promote-pattern must refuse; output:\n{out}")
        for name in names:
            self.assertIn(name, out)
        self.assertEqual(ps.snapshot(self.root), before, "a refused promotion changes nothing on disk")
        return out

    def test_s5_untouched_harvest_refuses(self):
        """S5: a fresh harvest still has open fields and is refused."""
        self.harvested()
        self.assert_refused("pattern.json", "OPEN")

    def test_s5_open_version_refuses_and_changes_nothing(self):
        """S5: version "OPEN: pick a version" refuses naming pattern.json and version."""
        _, inbox = self.complete()
        doc = json.loads((inbox / "pattern.json").read_text(encoding="utf-8"))
        doc["version"] = "OPEN: pick a version"
        ps.write_json(inbox / "pattern.json", doc)
        self.assert_refused("pattern.json", "version")

    def test_s5_open_line_in_structure_refuses(self):
        """S5 (R3.1): an OPEN: line left in structure.md refuses naming the file."""
        self.complete(structure=ps.STRUCTURE + "OPEN: decide the gate after master\n")
        self.assert_refused("structure.md")

    def test_s5_edited_source_refuses_naming_path(self):
        """S5: source/docs/stages.md edited after harvest refuses naming that path."""
        _, inbox = self.complete()
        (inbox / "source" / "docs" / "stages.md").write_text("edited after harvest\n", encoding="utf-8")
        self.assert_refused("docs/stages.md")

    def test_s5_missing_source_refuses_naming_path(self):
        """S5 (R3.1): a copied file removed after harvest refuses naming that path."""
        _, inbox = self.complete()
        (inbox / "source" / "tools" / "check_routes.py").unlink()
        self.assert_refused("tools/check_routes.py")

    def test_s5_empty_success_evidence_refuses(self):
        """S5: an empty success_evidence refuses naming success_evidence."""
        self.complete(success_evidence=[])
        self.assert_refused("success_evidence")

    def test_s5_evidence_without_reference_refuses(self):
        """S5 (R3.1): evidence needs a verifiable outcome: a known kind with a non-empty reference."""
        self.complete(success_evidence=[{"kind": "owner_acceptance", "reference": ""}])
        self.assert_refused("success_evidence")

    def test_s5_refusal_lists_every_unmet_condition(self):
        """S5 (R3.1): the refusal lists every unmet condition, not only the first."""
        _, inbox = self.complete(success_evidence=[])
        doc = json.loads((inbox / "pattern.json").read_text(encoding="utf-8"))
        doc["version"] = "OPEN: pick a version"
        ps.write_json(inbox / "pattern.json", doc)
        (inbox / "source" / "docs" / "stages.md").write_text("edited\n", encoding="utf-8")
        self.assert_refused("version", "success_evidence", "docs/stages.md")

    def test_s5_content_rule_blocks_promotion(self):
        """S5, S2: a structure.md holding a design token value of the source project refuses naming both."""
        project = ps.make_git_project(self.tmp, design_tokens={"brand": "#1A2B3C"})
        _, inbox = self.harvested(project=project)
        ps.complete_proposal(inbox, structure=ps.STRUCTURE + "Title cards use #1A2B3C.\n")
        self.assert_refused("structure.md", "#1A2B3C")

    def test_s5_media_file_blocks_promotion(self):
        """S5, S2: a media file planted in the proposal refuses naming it."""
        _, inbox = self.complete()
        (inbox / "guardrails" / "logo.png").write_bytes(b"png")
        self.assert_refused("logo.png")

    def test_s5_unknown_id_refuses(self):
        """S5 (R3.1): promoting an id with no proposal refuses naming it."""
        code, out = ps.cli(["promote-pattern", "nope", "--by", "owner"], self.root)
        self.assertEqual(code, 1, out)
        self.assertIn("nope", out)

    def test_s5_complete_proposal_promotes(self):
        """S5: a complete proposal promotes, records the owner and version, and check-patterns lists it."""
        _, inbox = self.complete()
        proposal = ps.snapshot(inbox)
        code, out = self.promote()
        self.assertEqual(code, 0, out)
        promoted = self.root / PID
        self.assertFalse(inbox.exists(), "the inbox entry no longer exists")
        record = json.loads((promoted / "promotion.json").read_text(encoding="utf-8"))
        self.assertEqual(record["by"], "owner")
        self.assertEqual(record["version"], "1")
        self.assertRegex(record["date"], r"^\d{4}-\d{2}-\d{2}$")
        moved = ps.snapshot(promoted)
        moved.pop("promotion.json")
        self.assertEqual(moved, proposal, "the proposal moves unchanged")
        code, out = ps.cli(["check-patterns"], self.root)
        self.assertEqual(code, 0, out)
        line = next((l for l in out.splitlines() if PID in l), "")
        self.assertTrue(line, out)
        # version 1, one dead end enforced by a check, one by prompt text
        self.assertIn("1", re.findall(r"\b\d+\b", line), line)

    def test_s5_counts_check_and_prompt_dead_ends(self):
        """S5 (R3.3, R5.5): check-patterns counts dead ends by check and by prompt separately."""
        extra = [dict(ps.CRT, id=f"route-{n}") for n in range(3)]
        self.complete(version="7", dead_ends=[dict(ps.DITHER)] + extra)
        self.assertEqual(self.promote()[0], 0)
        code, out = ps.cli(["check-patterns"], self.root)
        self.assertEqual(code, 0, out)
        line = next((l for l in out.splitlines() if PID in l), "")
        numbers = re.findall(r"\b\d+\b", line)
        for expected in ("7", "1", "3"):
            self.assertIn(expected, numbers, f"version 7, 1 by check, 3 by prompt: {line}")

    def test_s5_new_version_keeps_history_and_older_version_refuses(self):
        """S5 (R3.2): version 2 over 1 keeps 1 at history/1 unchanged; promoting 1 over 2 refuses."""
        project, _ = self.complete()
        self.assertEqual(self.promote()[0], 0)
        first = ps.snapshot(self.root / PID)
        code, out = self.harvest(project)
        self.assertEqual(code, 0, out)
        ps.complete_proposal(self.root / "inbox" / PID, version="2")
        code, out = self.promote()
        self.assertEqual(code, 0, out)
        self.assertEqual(ps.snapshot(self.root / PID / "history" / "1"), first)
        current = json.loads((self.root / PID / "pattern.json").read_text(encoding="utf-8"))
        self.assertEqual(current["version"], "2")
        code, out = ps.cli(["check-patterns"], self.root)
        self.assertEqual(code, 0, out)
        self.assertEqual(len([l for l in out.splitlines() if PID in l]), 1, "history is never a second pack")
        code, out = self.harvest(project)
        self.assertEqual(code, 0, out)
        ps.complete_proposal(self.root / "inbox" / PID, version="1")
        self.assert_refused("version")


if __name__ == "__main__":
    unittest.main()
