"""Proven patterns: the pack and its validation (spec: proven-patterns, work order wo-gh-50).

Every pack is a fixture written in a temporary patterns root; the loader is
exercised through the real command `anvil check-patterns` (R3.3), which loads
and validates every promoted pack with anvil/patterns.py. The pinned
interface (ANVIL_PATTERNS_DIR, the check path form) is documented in
tests/fixtures/patterns/patterns_support.py.

Scenario map:
  S1 (R1.2 to R1.5)  test_s1_complete_pack_loads, test_s1_dead_end_without_evidence_fails,
                     test_s1_figure_without_source_fails, test_s1_token_figure_without_unit_fails,
                     test_s1_budget_figure_without_weight_fails, test_s1_duplicate_ids_fail_naming_both,
                     and the further R1.5 cases named s1 below
  S2 (R1.6)          test_s2_* (media, secret, design token file, NUL bytes, forbidden values)
"""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "fixtures" / "patterns"))
import patterns_support as ps  # noqa: E402


class PackLoading(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "patterns"
        (self.root / "inbox").mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def check(self):
        return ps.cli(["check-patterns"], self.root)

    def assert_fails_naming(self, *names):
        code, out = self.check()
        self.assertEqual(code, 1, f"check-patterns must fail; output:\n{out}")
        for name in names:
            self.assertIn(name, out, f"the failure must name {name!r}; output:\n{out}")
        return out

    def test_s1_complete_pack_loads(self):
        """S1: a complete pack loads and check-patterns exits 0 naming it."""
        ps.write_pack(self.root, "explainer-video")
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertIn("explainer-video", out)

    def test_s1_dead_end_without_evidence_fails(self):
        """S1: dead end "dither-overlay" with evidence "" fails naming dead-ends.json and the id."""
        ps.write_pack(self.root, "explainer-video", dead_ends=[dict(ps.DITHER, evidence=""), dict(ps.CRT)])
        self.assert_fails_naming("explainer-video", "dead-ends.json", "dither-overlay")

    def test_s1_dead_end_missing_evidence_key_fails(self):
        """S1: a dead end with no evidence key at all fails the same way."""
        entry = dict(ps.DITHER)
        del entry["evidence"]
        ps.write_pack(self.root, "explainer-video", dead_ends=[entry])
        self.assert_fails_naming("dead-ends.json", "dither-overlay")

    def test_s1_figure_without_source_fails(self):
        """S1: the builder budget token figure without source fails naming calibration.json, builder, tokens."""
        figure = {"stage": "builder", "metric": "tokens", "value": 900000, "unit": "budget", "cache_read_weight": 0.1}
        ps.write_pack(self.root, "explainer-video", figures=[figure])
        self.assert_fails_naming("explainer-video", "calibration.json", "builder", "tokens")

    def test_s1_token_figure_without_unit_fails(self):
        """S1: a token figure without unit fails naming the figure."""
        figure = {"stage": "proof", "metric": "tokens", "value": 1200, "source": "runs/ep-01/usage.json"}
        ps.write_pack(self.root, "explainer-video", figures=[figure])
        self.assert_fails_naming("calibration.json", "proof", "tokens")

    def test_s1_budget_figure_without_weight_fails(self):
        """S1: a budget token figure without cache_read_weight fails naming the figure."""
        figure = {"stage": "proof", "metric": "tokens", "value": 1200, "unit": "budget",
                  "source": "runs/ep-01/usage.json"}
        ps.write_pack(self.root, "explainer-video", figures=[figure])
        self.assert_fails_naming("calibration.json", "proof", "tokens")

    def test_s1_budget_figures_with_two_weights_fail(self):
        """S1 (R1.4): all budget figures of one calibration.json carry the same cache_read_weight."""
        figures = [dict(ps.FIGURES[0]), dict(ps.FIGURES[0], stage="spec-writer", cache_read_weight=0.5)]
        ps.write_pack(self.root, "explainer-video", figures=figures)
        self.assert_fails_naming("calibration.json", "cache_read_weight")

    def test_s1_weight_outside_zero_to_one_fails(self):
        """S1 (R1.4): cache_read_weight is a number from 0 to 1."""
        ps.write_pack(self.root, "explainer-video", figures=[dict(ps.FIGURES[0], cache_read_weight=1.5)])
        self.assert_fails_naming("calibration.json", "builder")

    def test_s1_unknown_metric_fails(self):
        """S1 (R1.4): metric is one of tokens, cost_usd, wall_seconds."""
        ps.write_pack(self.root, "explainer-video",
                      figures=[{"stage": "master", "metric": "frames", "value": 3, "source": "ledger"}])
        self.assert_fails_naming("calibration.json", "master")

    def test_s1_duplicate_ids_fail_naming_both(self):
        """S1: two packs with id "explainer-video" fail loading naming both directories."""
        ps.write_pack(self.root, "first-pack", pack_id="explainer-video")
        ps.write_pack(self.root, "second-pack", pack_id="explainer-video")
        self.assert_fails_naming("first-pack", "second-pack")

    def test_s1_missing_required_file_fails(self):
        """S1 (R1.5): a pack without dead-ends.json fails naming the file."""
        pack = ps.write_pack(self.root, "explainer-video")
        (pack / "dead-ends.json").unlink()
        self.assert_fails_naming("explainer-video", "dead-ends.json")

    def test_s1_missing_required_field_fails(self):
        """S1 (R1.2): pattern.json without product_types fails naming the file and the field."""
        doc = ps.pattern_doc("explainer-video")
        del doc["product_types"]
        ps.write_pack(self.root, "explainer-video", pattern=doc)
        self.assert_fails_naming("pattern.json", "product_types")

    def test_s1_bad_version_fails(self):
        """S1 (R1.2): version is one to three dot separated integers; "v1" is rejected."""
        ps.write_pack(self.root, "explainer-video", version="v1")
        self.assert_fails_naming("pattern.json", "version")

    def test_s1_version_with_four_parts_fails(self):
        """S1 (R1.2): one past the boundary of three parts is rejected."""
        ps.write_pack(self.root, "explainer-video", version="1.2.3.4")
        self.assert_fails_naming("pattern.json", "version")

    def test_s1_three_part_version_loads(self):
        """S1 (R1.2): a three part version is at the boundary and loads."""
        ps.write_pack(self.root, "explainer-video", version="1.2.0")
        code, out = self.check()
        self.assertEqual(code, 0, out)

    def test_s1_short_commit_id_fails(self):
        """S1 (R1.2): source.commits holds full 40 character commit ids."""
        doc = ps.pattern_doc("explainer-video", commits=["abc1234"])
        ps.write_pack(self.root, "explainer-video", pattern=doc)
        self.assert_fails_naming("pattern.json", "commits")

    def test_s1_unknown_evidence_kind_fails(self):
        """S1 (R1.2): a success_evidence kind outside the set is rejected."""
        ps.write_pack(self.root, "explainer-video", success_evidence=[{"kind": "vibes", "reference": "x"}])
        self.assert_fails_naming("pattern.json", "success_evidence")

    def test_s1_id_must_equal_directory(self):
        """S1 (R1.2): the id equals the directory name."""
        ps.write_pack(self.root, "explainer-video", pack_id="other-id")
        self.assert_fails_naming("explainer-video", "other-id")

    def test_s1_unknown_blueprint_fails(self):
        """S1 (R1.2): blueprint names a directory under blueprints/, or is null."""
        doc = ps.pattern_doc("explainer-video", blueprint="no-such-blueprint")
        ps.write_pack(self.root, "explainer-video", pattern=doc)
        self.assert_fails_naming("pattern.json", "blueprint")

    def test_s1_check_that_does_not_exist_fails(self):
        """S1 (R1.3): an entry with enforcement "check" whose check file is missing fails naming it."""
        ps.write_pack(self.root, "explainer-video", guardrails={"other.py": ps.CHECK_SCRIPT})
        self.assert_fails_naming("dead-ends.json", "dither-overlay")

    def test_s1_prompt_dead_end_with_check_fails(self):
        """S1 (R1.3): an entry with enforcement "prompt" carries no check."""
        ps.write_pack(self.root, "explainer-video",
                      dead_ends=[dict(ps.CRT, check="guardrails/check_routes.py")])
        self.assert_fails_naming("dead-ends.json", "crt-curvature")

    def test_s1_duplicate_dead_end_ids_fail(self):
        """S1 (R1.3): dead end ids are unique within the file."""
        ps.write_pack(self.root, "explainer-video", dead_ends=[dict(ps.CRT), dict(ps.CRT)])
        self.assert_fails_naming("dead-ends.json", "crt-curvature")

    def test_s1_unknown_enforcement_fails(self):
        """S1 (R1.3): enforcement is one of "check" or "prompt"."""
        ps.write_pack(self.root, "explainer-video", dead_ends=[dict(ps.CRT, enforcement="hope")])
        self.assert_fails_naming("dead-ends.json", "crt-curvature")

    def test_s1_unknown_top_level_entry_fails(self):
        """S1 (R1.1): no other top level entry is allowed in a pack."""
        ps.write_pack(self.root, "explainer-video", extra_files={"notes.md": b"stray\n"})
        self.assert_fails_naming("explainer-video", "notes.md")

    def test_s1_malformed_json_fails(self):
        """S1 (R1.5): a pack file that is not JSON fails naming the file."""
        pack = ps.write_pack(self.root, "explainer-video")
        (pack / "calibration.json").write_text("{not json", encoding="utf-8")
        self.assert_fails_naming("explainer-video", "calibration.json")

    def test_s1_inbox_and_history_are_not_loaded(self):
        """S1 (R3.3): a broken proposal in the inbox is not a promoted pack; check-patterns ignores it."""
        ps.write_pack(self.root, "explainer-video")
        ps.write_pack(self.root, "broken", promoted=False, dead_ends=[dict(ps.DITHER, evidence="")])
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertNotIn("broken", out)

    def test_s1_no_promoted_pack_prints_none_and_passes(self):
        """S1 (R3.3): with no promoted pack check-patterns says so and exits 0."""
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertRegex(out.lower(), r"\bno\b|\bnone\b")

    def test_s1_missing_patterns_root_passes(self):
        """S1 (R3.3): a patterns root that does not exist holds no promoted pack."""
        code, out = ps.cli(["check-patterns"], Path(self._tmp.name) / "absent")
        self.assertEqual(code, 0, out)


class ContentRule(unittest.TestCase):
    """S2: a pack never carries the source project's content or identity (R1.6)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "patterns"
        (self.root / "inbox").mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def assert_rejected(self, name, **kwargs):
        ps.write_pack(self.root, "explainer-video", **kwargs)
        code, out = ps.cli(["check-patterns"], self.root)
        self.assertEqual(code, 1, f"the content rule must reject {name}; output:\n{out}")
        self.assertIn(name, out)
        return out

    def test_s2_media_in_guardrails_is_rejected(self):
        """S2: guardrails/logo.png fails validation naming the file."""
        self.assert_rejected("logo.png", guardrails={"check_routes.py": ps.CHECK_SCRIPT, "logo.png": "not really"})

    def test_s2_every_listed_media_extension_is_rejected(self):
        """S2: each R1.6 media, font, design or archive extension is rejected."""
        for ext in (".jpg", ".svg", ".mp4", ".wav", ".woff2", ".pdf", ".zip"):
            with self.subTest(ext=ext):
                name = "asset" + ext
                self.tearDown()
                self.setUp()
                self.assert_rejected(name, source_files={"docs/stages.md": ps.STAGES_MD.encode(),
                                                         "media/" + name: b"plain"})

    def test_s2_env_file_in_source_is_rejected(self):
        """S2: source/.env fails validation naming the file."""
        self.assert_rejected(".env", source_files={"docs/stages.md": ps.STAGES_MD.encode(), ".env": b"KEY=1\n"})

    def test_s2_secret_named_files_are_rejected(self):
        """S2: .env.local, *.pem, *.key, *.p12 and names with secret, credential or password are rejected."""
        for name in (".env.local", "deploy.pem", "signing.key", "store.p12", "My_Secret.txt",
                     "aws-credentials.md", "PASSWORDS.txt"):
            with self.subTest(name=name):
                self.tearDown()
                self.setUp()
                self.assert_rejected(name, source_files={"docs/stages.md": ps.STAGES_MD.encode(),
                                                         "conf/" + name: b"x\n"})

    def test_s2_design_token_file_in_source_is_rejected(self):
        """S2: source/design-tokens.json fails validation naming the file."""
        self.assert_rejected("design-tokens.json",
                             source_files={"docs/stages.md": ps.STAGES_MD.encode(),
                                           "design-tokens.json": b'{"brand": "#1A2B3C"}\n'})

    def test_s2_other_design_token_names_are_rejected(self):
        """S2: tokens.json and *.tokens.json are design token files too."""
        for name in ("tokens.json", "brand.tokens.json"):
            with self.subTest(name=name):
                self.tearDown()
                self.setUp()
                self.assert_rejected(name, source_files={"docs/stages.md": ps.STAGES_MD.encode(),
                                                         "design/" + name: b"{}\n"})

    def test_s2_binary_file_is_rejected(self):
        """S2: a file with a NUL byte in its first 8192 bytes is rejected."""
        self.assert_rejected("frame.dat", source_files={"docs/stages.md": ps.STAGES_MD.encode(),
                                                        "frame.dat": b"head\x00tail"})

    def test_s2_forbidden_value_in_structure_is_rejected(self):
        """S2: a structure.md containing a design token value recorded in forbidden_values fails naming both."""
        out = self.assert_rejected("structure.md", forbidden_values=["#1A2B3C"],
                                   structure=ps.STRUCTURE + "\nBrand colour #1A2B3C on every title card.\n")
        self.assertIn("#1A2B3C", out)

    def test_s2_forbidden_value_in_dead_ends_or_source_is_rejected(self):
        """S2: dead-ends.json and files under source/ are scanned for forbidden values too."""
        out = self.assert_rejected("dead-ends.json", forbidden_values=["#1A2B3C"],
                                   dead_ends=[dict(ps.CRT, why="Clashed with #1A2B3C")])
        self.assertIn("#1A2B3C", out)
        self.tearDown()
        self.setUp()
        out = self.assert_rejected("stages.md", forbidden_values=["#1A2B3C"],
                                   source_files={"docs/stages.md": b"title colour #1A2B3C\n"})
        self.assertIn("#1A2B3C", out)

    def test_s2_clean_pack_with_forbidden_values_passes(self):
        """S2: a pack without the media, secrets, token files or forbidden values passes."""
        ps.write_pack(self.root, "explainer-video", forbidden_values=["#1A2B3C"])
        code, out = ps.cli(["check-patterns"], self.root)
        self.assertEqual(code, 0, out)


class OwnFiles(unittest.TestCase):
    def test_no_dashes_in_the_proven_patterns_test_files(self):
        """Project style rule: no em dash or en dash in the files this test-writer produced."""
        here = Path(__file__).resolve().parent
        files = sorted(here.glob("test_proven_patterns*.py")) + [here / "fixtures" / "patterns" / "patterns_support.py"]
        self.assertGreaterEqual(len(files), 2)
        for path in files:
            self.assertIsNone(re.search("[\u2013\u2014]", path.read_text(encoding="utf-8")), path.name)


if __name__ == "__main__":
    unittest.main()
