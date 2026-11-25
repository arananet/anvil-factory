"""Proven patterns on the line: quarantine, selection, packet slices (spec: proven-patterns, wo-gh-50).

Every test drives a scripted sdlc-default run through the real runner
(anvil.runner.run_pipeline) with a fake runtime, no network and no model, on a
fresh project in a temporary directory, with ANVIL_PATTERNS_DIR naming a
temporary patterns root (see tests/fixtures/patterns/patterns_support.py).
"Patterns absent" is a run with ANVIL_PATTERNS_DIR naming a directory that
does not exist. Packets are compared as the runtime received them and as
written to runs/<wo>/<station>.packet.md.

Scenario map:
  S4 (R2.5, R4.3, R4.4)  test_s4_inbox_proposal_is_never_selected, test_s4_init_refuses_unpromoted_pattern
  S6 (R4.1 to R4.3)      test_s6_most_specific_wins_and_is_stable, test_s6_highest_version_compares_numerically,
                         test_s6_only_candidate, test_s6_id_order_breaks_a_full_tie,
                         test_s6_no_product_type_selects_none, test_s6_history_is_never_selected
  S7 (R5.1 to R5.3, R6.1) test_s7_each_station_gets_its_slice, test_s7_other_stations_unchanged,
                         test_s7_unmatched_project_packets_unchanged, test_s7_over_budget_trims_pattern_section
  S9 (R4.4)              test_s9_no_match_same_packets_events_and_report_keys
"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "fixtures" / "patterns"))
import patterns_support as ps  # noqa: E402

PATTERN_STATIONS = {"intake", "spec-writer", "builder"}


class LineBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.root = self.tmp / "patterns"
        (self.root / "inbox").mkdir(parents=True)
        self.absent = self.tmp / "no-patterns-here"

    def tearDown(self):
        self._tmp.cleanup()

    def video_a(self, **kwargs):
        return ps.write_pack(self.root, "video-a", title="Explainer video line", version="1",
                             product_types=("explainer-video",), **kwargs)


class Quarantine(LineBase):
    def test_s4_inbox_proposal_is_never_selected(self):
        """S4: a complete proposal in the inbox is not selected and changes no packet."""
        ps.write_pack(self.root, "explainer-video", promoted=False)
        with_inbox = ps.run_line(self.tmp, self.root, product_type="explainer-video")
        pattern = with_inbox["report"].get("pattern")
        self.assertIsInstance(pattern, dict, "report.json carries a pattern key")
        self.assertIsNone(pattern["id"])
        self.assertIsNone(pattern["version"])
        self.assertIn("explainer-video", pattern["rule"])
        without = ps.run_line(self.tmp, self.absent, product_type="explainer-video")
        self.assertEqual(with_inbox["files"], without["files"])
        self.assertEqual(with_inbox["packets"], without["packets"])
        self.assertTrue(with_inbox["packets"])

    def test_s4_init_refuses_unpromoted_pattern(self):
        """S4 (R2.5): init --pattern with an id only in the inbox refuses naming it as unpromoted."""
        ps.write_pack(self.root, "explainer-video", promoted=False)
        target = self.tmp / "new"
        code, out = ps.cli(["init", target, "--name", "New", "--pattern", "explainer-video"], self.root)
        self.assertEqual(code, 1, out)
        self.assertIn("explainer-video", out)
        self.assertRegex(out.lower(), r"unpromoted|not promoted")
        self.assertFalse(target.exists())


class Selection(LineBase):
    def selected(self, product_type="explainer-video"):
        return ps.run_line(self.tmp, self.root, product_type=product_type)["report"].get("pattern")

    def test_s6_most_specific_wins_and_is_stable(self):
        """S6: video-a (one product type) beats video-b (two, higher version); two runs agree."""
        self.video_a()
        ps.write_pack(self.root, "video-b", version="3", product_types=("explainer-video", "short-video"))
        first, second = self.selected(), self.selected()
        expected = {"id": "video-a", "version": "1", "rule": "most specific"}
        self.assertEqual(first, expected)
        self.assertEqual(second, expected)

    def test_s6_highest_version_compares_numerically(self):
        """S6: versions 1.2 and 1.10 serving only that type: 1.10 wins by highest version."""
        ps.write_pack(self.root, "video-c", version="1.2")
        ps.write_pack(self.root, "video-d", version="1.10")
        self.assertEqual(self.selected(), {"id": "video-d", "version": "1.10", "rule": "highest version"})

    def test_s6_missing_parts_read_as_zero(self):
        """S6 (R1.2): "2" and "2.0.1": missing parts are 0, so 2.0.1 is higher."""
        ps.write_pack(self.root, "video-c", version="2")
        ps.write_pack(self.root, "video-d", version="2.0.1")
        self.assertEqual(self.selected()["id"], "video-d")

    def test_s6_only_candidate(self):
        """S6 (R4.2): a single serving pack wins as the only candidate; a pack for another type is ignored."""
        self.video_a()
        ps.write_pack(self.root, "landing", product_types=("landing-page",), version="9")
        self.assertEqual(self.selected(), {"id": "video-a", "version": "1", "rule": "only candidate"})

    def test_s6_id_order_breaks_a_full_tie(self):
        """S6 (R4.2): equal specificity and version: the lowest id in string order wins."""
        ps.write_pack(self.root, "video-z", version="1")
        ps.write_pack(self.root, "video-m", version="1")
        self.assertEqual(self.selected(), {"id": "video-m", "version": "1", "rule": "id order"})

    def test_s6_match_is_exact(self):
        """S6 (R4.1): product_types must contain the declared value exactly."""
        ps.write_pack(self.root, "video-a", product_types=("explainer-video-long",))
        pattern = self.selected()
        self.assertIsNone(pattern["id"])
        self.assertIn("explainer-video", pattern["rule"])

    def test_s6_no_product_type_selects_none(self):
        """S6: a project with no "Product type:" line selects none and the rule names the missing type."""
        self.video_a()
        pattern = ps.run_line(self.tmp, self.root, product_type=None)["report"].get("pattern")
        self.assertIsNone(pattern["id"])
        self.assertIsNone(pattern["version"])
        self.assertIn("product type", pattern["rule"].lower())

    def test_s6_history_is_never_selected(self):
        """S6 (R3.2): a pack under history/ stays on record and is never selected."""
        self.video_a(version="2")
        ps.write_pack(self.root / "video-a" / "history", "1", pack_id="video-a", version="1")
        self.assertEqual(self.selected(), {"id": "video-a", "version": "2", "rule": "only candidate"})


class Slices(LineBase):
    def test_s7_each_station_gets_its_slice(self):
        """S7: spec-writer and builder get the pattern, reviewers the dead ends, intake one line."""
        self.video_a()
        result = ps.run_line(self.tmp, self.root, product_type="explainer-video")
        packets = result["packets"]
        for station in ("spec-writer", "builder"):
            text = packets[station]
            self.assertIn("## Proven pattern", text, station)
            section = text[text.index("## Proven pattern"):]
            self.assertIn(ps.STRUCTURE_MARKER, section, station)
            self.assertIn("dither-overlay", section, station)
            self.assertIn("crt-curvature", section, station)
            self.assertIn(ps.DITHER["evidence"], section, station)
            self.assertIn(ps.AUTHORITY, section, station)
        reviewers = sorted(s for s in packets if s.startswith("reviewer-"))
        self.assertGreaterEqual(len(reviewers), 3, reviewers)
        for station in reviewers:
            text = packets[station]
            self.assertIn("## Proven pattern: dead ends to check", text, station)
            section = text[text.index("## Proven pattern: dead ends to check"):]
            self.assertIn("dither-overlay", section, station)
            self.assertIn(ps.AUTHORITY, section, station)
            self.assertNotIn(ps.STRUCTURE_MARKER, text, f"{station} gets the dead ends, not the structure")
        self.assertIn("Proven pattern: Explainer video line 1", packets["intake"])
        self.assertNotIn(ps.STRUCTURE_MARKER, packets["intake"])
        # the packet files on disk carry the same slices
        self.assertIn(b"## Proven pattern", result["files"]["builder"])

    def test_s7_other_stations_unchanged(self):
        """S7 (R5.1): no station other than intake, spec-writer, builder and reviewer-* changes."""
        self.video_a()
        with_pattern = ps.run_line(self.tmp, self.root, product_type="explainer-video")
        without = ps.run_line(self.tmp, self.absent, product_type="explainer-video")
        others = sorted(s for s in without["files"] if s not in PATTERN_STATIONS and not s.startswith("reviewer-"))
        self.assertIn("test-writer", others)
        for station in others:
            self.assertEqual(with_pattern["files"].get(station), without["files"][station], station)

    def test_s7_unmatched_project_packets_unchanged(self):
        """S7, R4.4: a landing-page project's packets equal those built with patterns absent."""
        self.video_a()
        matched = ps.run_line(self.tmp, self.root, product_type="landing-page")
        absent = ps.run_line(self.tmp, self.absent, product_type="landing-page")
        self.assertEqual(matched["files"], absent["files"])
        self.assertEqual(matched["packets"], absent["packets"])
        self.assertIsNone(matched["report"]["pattern"]["id"])
        self.assertIn("landing-page", matched["report"]["pattern"]["rule"])

    def test_s7_over_budget_trims_pattern_section(self):
        """S7 (R5.3): a builder packet over budget only by structure.md is trimmed to routes and why."""
        base = ps.run_line(self.tmp, self.absent, product_type="explainer-video")
        base_tokens = ps.step(base["report"], "builder")["measured_tokens"]
        self.assertGreater(base_tokens, 0)
        budget = base_tokens + 1500
        # structure.md alone is larger than the whole budget, so no earlier trim can make room for it
        filler_line = "Gate detail: every stage output passes the deterministic checks first.\n"
        filler = filler_line * (int((budget + 2000) * 3.5 / len(filler_line)) + 1)
        self.video_a(structure=ps.STRUCTURE + filler)
        result = ps.run_line(self.tmp, self.root, product_type="explainer-video",
                             station_budgets={"builder": budget})
        builder_step = ps.step(result["report"], "builder")
        self.assertEqual(builder_step["budget_action"], "trimmed", builder_step)
        self.assertIs(builder_step.get("pattern_trimmed"), True, builder_step)
        self.assertLessEqual(builder_step["measured_tokens"], budget)
        text = result["packets"]["builder"]
        self.assertIn("## Proven pattern", text)
        self.assertIn("dither-overlay", text)
        self.assertIn(ps.DITHER["route"], text)
        self.assertIn(ps.DITHER["why"], text)
        self.assertNotIn(ps.STRUCTURE_MARKER, text)
        self.assertNotIn(filler_line, text)
        self.assertNotIn(ps.DITHER["evidence"], text)

    def test_s7_within_budget_is_not_pattern_trimmed(self):
        """S7 (R5.3): a builder packet that fits is sent with the full section and no pattern trim."""
        self.video_a()
        result = ps.run_line(self.tmp, self.root, product_type="explainer-video")
        builder_step = ps.step(result["report"], "builder")
        self.assertEqual(builder_step["budget_action"], "sent", builder_step)
        self.assertNotEqual(builder_step.get("pattern_trimmed"), True)
        self.assertIn(ps.STRUCTURE_MARKER, result["packets"]["builder"])


class NoPatternNoChange(LineBase):
    def test_s9_no_match_same_packets_events_and_report_keys(self):
        """S9: a project matching no pattern: same packets, event kinds and report keys apart from pattern."""
        self.video_a()
        matched = ps.run_line(self.tmp, self.root, product_type="landing-page")
        shutil.rmtree(self.root)
        absent = ps.run_line(self.tmp, self.absent, product_type="landing-page")
        self.assertEqual(matched["files"], absent["files"])
        self.assertEqual(matched["events"], absent["events"])
        self.assertTrue(matched["events"])
        self.assertEqual(set(matched["report"]), set(absent["report"]))
        self.assertIn("pattern", matched["report"])

    def test_s9_selection_adds_no_event_kind(self):
        """S9 (R4.3): a selected pattern adds no event kind; the event sequence is unchanged."""
        self.video_a()
        matched = ps.run_line(self.tmp, self.root, product_type="explainer-video")
        absent = ps.run_line(self.tmp, self.absent, product_type="explainer-video")
        self.assertEqual(matched["report"]["pattern"]["id"], "video-a")
        self.assertEqual(matched["events"], absent["events"])


if __name__ == "__main__":
    unittest.main()
