"""Landing page checks (spec: landing-page, R5, scenarios S1-S4, S6).

These tests open the real site/index.html and the real trees. Nothing here
asserts against a copy of the page content.

Contract the builder must follow (the spec leaves anchor ids open):
section ids, in order: hero, problem, how-it-works, different, proof,
quickstart, not, footer. Printed counts use the phrases "N stations",
"N pipelines" and "N reviewers" (reviewers in parallel in sdlc-default).
"""
import json
import re
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "site" / "index.html"
README = ROOT / "README.md"
ANCHORS = ["hero", "problem", "how-it-works", "different", "proof",
           "quickstart", "not", "footer"]


def page_text():
    assert PAGE.is_file(), "site/index.html does not exist"
    return PAGE.read_text(encoding="utf-8")


class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []   # (tag, attrs dict)
        self.ids = []
        self.in_quickstart = False
        self.depth = 0
        self.qs_depth = None
        self.qs_code = []
        self._pre = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.append((tag, a))
        if "id" in a:
            self.ids.append(a["id"])
        if tag not in ("meta", "link", "img", "br", "hr", "input", "path",
                       "rect", "line", "circle", "polygon", "polyline", "use"):
            self.depth += 1
        if a.get("id") == "quickstart":
            self.in_quickstart = True
            self.qs_depth = self.depth
        if self.in_quickstart and tag == "pre":
            self._pre = True
            self.qs_code.append("")

    def handle_endtag(self, tag):
        if tag == "pre":
            self._pre = False
        if tag not in ("meta", "link", "img", "br", "hr", "input"):
            if self.in_quickstart and self.depth == self.qs_depth:
                self.in_quickstart = False
            self.depth -= 1

    def handle_data(self, data):
        if self._pre and self.qs_code:
            self.qs_code[-1] += data


def parse():
    c = Collector()
    c.feed(page_text())
    return c


def count_dirs(sub, marker):
    return len([p for p in (ROOT / sub).iterdir() if p.is_dir() and (p / marker).exists()])


class TestPageStandsAlone(unittest.TestCase):
    """S1 / R1"""

    def test_file_exists_single_document_with_viewport(self):
        t = page_text()
        self.assertEqual(len(re.findall(r"<html\b", t, re.I)), 1)
        self.assertEqual(len(re.findall(r"</html>", t, re.I)), 1)
        self.assertTrue(t.lstrip().lower().startswith("<!doctype html"))
        c = parse()
        vp = [a for tag, a in c.tags if tag == "meta" and a.get("name") == "viewport"]
        self.assertEqual(len(vp), 1)
        self.assertIn("width=device-width", vp[0].get("content", ""))

    def test_title_and_description_name_anvil(self):
        c = parse()
        self.assertIn("ANVIL", re.search(r"<title>(.*?)</title>", page_text(), re.S | re.I).group(1))
        desc = [a.get("content", "") for tag, a in c.tags
                if tag == "meta" and a.get("name") == "description"]
        self.assertEqual(len(desc), 1)
        self.assertIn("ANVIL", desc[0])
        self.assertIn("Agentic Network for Verified Implementation Lifecycle", desc[0])

    def test_english(self):
        self.assertRegex(page_text(), r"<html[^>]*\blang=[\"']en")

    def test_no_external_assets(self):
        c = parse()
        self.assertFalse([1 for tag, _ in c.tags if tag == "script"], "no script elements")
        self.assertFalse([1 for tag, _ in c.tags if tag in ("iframe", "object", "embed")])
        for tag, a in c.tags:
            if tag == "link":
                self.assertNotIn("stylesheet", a.get("rel", "").lower())
                self.assertNotIn("preload", a.get("rel", "").lower())
            if tag in ("img", "source", "video", "audio", "track"):
                src = a.get("src", "")
                self.assertTrue(src == "" or src.startswith("data:"), f"external {tag} src {src}")
                self.assertFalse(a.get("srcset", "").strip().startswith("http"))
            for k in a:
                self.assertFalse(k.startswith("on"), f"inline handler {k}")
        t = page_text()
        self.assertNotRegex(t, r"@import")
        for m in re.finditer(r"url\(\s*['\"]?([^)'\"]+)", t):
            self.assertTrue(m.group(1).startswith(("data:", "#")), f"css url {m.group(1)}")
        self.assertNotRegex(t, r"(?i)javascript:")

    def test_inline_css_present(self):
        self.assertRegex(page_text(), r"(?s)<style[^>]*>.+</style>")

    def test_mobile_rules_present(self):
        t = page_text()
        self.assertIn("@media", t)
        self.assertRegex(t, r"(?i)#?FF5C00")


class TestStoryInOrder(unittest.TestCase):
    """S2 / R2"""

    def test_eight_anchors_in_order(self):
        ids = parse().ids
        positions = []
        for a in ANCHORS:
            self.assertIn(a, ids, f"missing anchor #{a}")
            positions.append(ids.index(a))
        self.assertEqual(positions, sorted(positions))

    def test_cta_links_target_repo_and_quickstart(self):
        c = parse()
        hrefs = [a.get("href", "") for tag, a in c.tags if tag == "a"]
        self.assertIn("https://github.com/arananet/anvil-factory", hrefs)
        self.assertIn("#quickstart", hrefs)

    def test_hero_and_footer_content(self):
        t = page_text()
        self.assertIn("Agentic Network for Verified Implementation Lifecycle", t)
        self.assertRegex(t, r"(?i)no agent approves its own work")
        self.assertIn("Apache 2.0", t)
        self.assertIn("Copyright Eduardo Arana", t)
        self.assertIn("Developer Eduardo Arana", t)
        self.assertIn("v0.1.0", t)

    def test_pipeline_labels_in_inline_svg(self):
        t = page_text()
        svg = re.search(r"(?is)<svg\b.*?</svg>", t)
        self.assertIsNotNone(svg, "inline SVG diagram missing")
        s = svg.group(0).lower()
        for label in ["intake", "spec writer", "test writer", "builder",
                      "approver", "human gate", "deployer", "observer"]:
            self.assertIn(label, s, f"diagram label {label}")

    def test_no_employer_or_unmerged_work(self):
        t = page_text().lower()
        self.assertNotIn("preflight", t)
        self.assertNotIn("consolidation", t)


class TestPrintedCountsEqualTree(unittest.TestCase):
    """S3 / R3 / R5: counts computed from the trees at test time"""

    def _printed(self, noun):
        text = re.sub(r"<[^>]+>", " ", page_text())
        nums = {int(n) for n in re.findall(rf"\b(\d+)\s+{noun}\b", text, re.I)}
        self.assertTrue(nums, f"page prints no '<N> {noun}' count")
        return nums

    def test_station_count(self):
        actual = count_dirs("stations", "station.json")
        self.assertGreater(actual, 0)
        self.assertEqual(self._printed("stations"), {actual})

    def test_pipeline_count(self):
        actual = len(list((ROOT / "pipelines").glob("*.json")))
        self.assertGreater(actual, 0)
        self.assertEqual(self._printed("pipelines"), {actual})

    def test_parallel_reviewer_count_matches_sdlc_default(self):
        d = json.loads((ROOT / "pipelines" / "sdlc-default.json").read_text())
        par = [s["parallel"] for s in d["stages"] if "parallel" in s]
        self.assertEqual(len(par), 1)
        words = {"five": 5, "six": 6, "seven": 7, "four": 4}
        text = re.sub(r"<[^>]+>", " ", page_text())
        found = {int(n) for n in re.findall(r"\b(\d+)\s+reviewers\b", text, re.I)}
        found |= {words[w.lower()] for w in re.findall(r"\b(four|five|six|seven)\s+reviewers\b", text, re.I)}
        self.assertTrue(found, "page prints no reviewer count")
        self.assertEqual(found, {len(par[0])})

    def test_release_tag_exists(self):
        out = subprocess.run(["git", "tag", "--list", "v0.1.0"], cwd=ROOT,
                             capture_output=True, text=True).stdout
        if not out.strip():
            self.skipTest("tag not available in this checkout")
        self.assertIn("v0.1.0", page_text())


class TestQuickstartIsReal(unittest.TestCase):
    """S4 / R5"""

    def test_commands_appear_in_readme_quickstart(self):
        readme = README.read_text(encoding="utf-8")
        sec = re.search(r"(?ms)^## Quickstart\s*$(.*?)^## ", readme).group(1)
        blocks = re.findall(r"(?s)```\w*\n(.*?)```", sec)
        self.assertTrue(blocks)
        readme_cmds = {l.strip() for b in blocks for l in b.splitlines() if l.strip()}
        import html
        c = parse()
        page_cmds = [html.unescape(l).strip() for b in c.qs_code for l in b.splitlines() if l.strip()]
        self.assertTrue(page_cmds, "no <pre> command block inside #quickstart")
        for cmd in page_cmds:
            self.assertIn(cmd, readme_cmds)
        self.assertEqual(set(page_cmds), readme_cmds, "page should print the exact README commands")


class TestStyleAndFence(unittest.TestCase):
    def test_no_em_or_en_dash_in_produced_files(self):
        for p in [PAGE, ROOT / "docs" / "LANDING-PAGE.md", Path(__file__)]:
            self.assertTrue(p.is_file(), f"{p} missing")
            t = p.read_text(encoding="utf-8")
            self.assertNotIn("\u2014", t, p.name)
            self.assertNotIn("\u2013", t, p.name)
            self.assertNotRegex(t, r"&(mdash|ndash|#8211|#8212|#x2013|#x2014);", p.name)

    def test_hosting_doc(self):
        t = (ROOT / "docs" / "LANDING-PAGE.md").read_text(encoding="utf-8")
        low = t.lower()
        self.assertIn("cloudflare pages", low)
        self.assertIn("github pages", low)
        self.assertIn("recommend", low)
        self.assertIn("site/", t)
        self.assertRegex(low, r"deploys? nothing|deployed nothing")
        self.assertIn("homepage", low)
        self.assertIn("OPERATOR-REQUIREMENTS", t)

    def test_run_delta_stays_in_fence(self):
        r = subprocess.run(["git", "diff", "--name-only", "origin/main...HEAD"],
                           cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            self.skipTest("origin/main not available")
        for f in r.stdout.split():
            ok = (f.startswith("site/") or f == "docs/LANDING-PAGE.md"
                  or re.fullmatch(r"tests/test_landing_page\w*\.py", f)
                  or f.startswith(("work_orders/", "runs/", ".openspec/", ".github/workflows/execute"))
                  or f in ("run-diff.txt",))
            self.assertTrue(ok, f"out of fence change: {f}")
            self.assertFalse(f.startswith("anvil/") or f == "README.md")


if __name__ == "__main__":
    unittest.main()
