"""Run evidence stays with its run (operator check, decision 0018).

A test that compares the tree with a base ref, or with factory main, states a
fact about one work order's run. Left unconditional in the suite it fails
every later order at the checks gate: it stopped wo-gh-47 twice and would
have stopped any order whose operator touched an existing test. The rule a
test-writer is given in its prompt is enforced here, deterministically: a
test file that carries such a comparison must also carry a guard that binds
it to its order.
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# A full commit id written into a test, or a comparison with factory main.
COMMIT_LITERAL = re.compile(r"(?<![0-9a-fA-F])[0-9a-f]{40}(?![0-9a-fA-F])")
MAIN_COMPARISON = re.compile("origin" + "/main|merge" + "-base")
# What binds a test to its order: the work order id of the run, or the run branch name.
GUARD = re.compile("ANVIL_WORK_ORDER" + "_ID|--abbrev" + "-ref")


def evidence_markers(text):
    """The reasons a test file counts as run evidence, empty when it does not."""
    found = []
    if COMMIT_LITERAL.search(text):
        found.append("a full commit id")
    if MAIN_COMPARISON.search(text):
        found.append("a comparison with factory main")
    return found


def unguarded(text):
    """The markers of a file that carries run evidence without a guard, else []."""
    markers = evidence_markers(text)
    return markers if markers and not GUARD.search(text) else []


class RuleTests(unittest.TestCase):
    SHA = "0123456789abcdef0123456789abcdef01234567"

    def test_a_commit_id_without_a_guard_is_caught(self):
        text = f'BASE_REF = "{self.SHA}"\nsubprocess.run(["git", "diff", BASE_REF])\n'
        self.assertEqual(unguarded(text), ["a full commit id"])

    def test_a_comparison_with_main_without_a_guard_is_caught(self):
        self.assertEqual(unguarded('git("merge" "-base")'), [])
        self.assertEqual(unguarded('git("diff", "origin' + '/main...HEAD")'), ["a comparison with factory main"])

    def test_a_guard_by_work_order_or_by_branch_clears_the_file(self):
        base = f'BASE_REF = "{self.SHA}"\n'
        self.assertEqual(unguarded(base + 'os.environ.get("ANVIL_WORK_ORDER' + '_ID")'), [])
        self.assertEqual(unguarded(base + 'git("rev-parse", "--abbrev' + '-ref", "HEAD")'), [])

    def test_a_longer_digest_and_plain_tests_are_not_evidence(self):
        self.assertEqual(evidence_markers('DIGEST = "' + "ab" * 32 + '"'), [])
        self.assertEqual(evidence_markers('subprocess.run(["git", "init"], cwd=tmp)'), [])


class SuiteTests(unittest.TestCase):
    def test_every_run_evidence_test_file_is_bound_to_its_order(self):
        offenders = {}
        files = sorted((ROOT / "tests").glob("test_*.py"))
        self.assertGreater(len(files), 20)
        for path in files:
            if path == Path(__file__).resolve():
                continue
            found = unguarded(path.read_text(encoding="utf-8"))
            if found:
                offenders[path.name] = found
        self.assertEqual(offenders, {}, "run evidence without a guard: add a skip unless ANVIL_WORK_ORDER" "_ID "
                                        "names the order that wrote the test")

    def test_no_dashes_in_this_file(self):
        self.assertNotRegex(Path(__file__).read_text(encoding="utf-8"), "[\\u2013\\u2014]")


if __name__ == "__main__":
    unittest.main()
