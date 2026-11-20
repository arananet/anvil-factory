"""Operator fix: the station wrapper starts in a project that lacks copilot_runtime.py.

Run wo-gh-1 on ascii-aurora (2026-11-20): the project runs the line from a
pinned factory checkout (.anvil-factory, the runner spine) and executes its
stations through its own synced tools/claude_station.py and
tools/dispatch_station.py. The project had no tools/copilot_runtime.py, the
wrapper imported it unconditionally, and every station died with
ModuleNotFoundError before reaching a model (verdict no_reviews, 0 of 6).

The wrapper now finds copilot_runtime.py beside itself, else in the factory's
tools (ANVIL_FACTORY_ROOT, or next to the running anvil package), else falls
back to the gateway runtime, failing only ANVIL_RUNTIME=copilot with the reason.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

FACTORY = Path(__file__).resolve().parent.parent

PROBE = (
    "import sys; sys.path.insert(0, 'tools'); import claude_station as c; "
    "rt = c.copilot_runtime; "
    "print(getattr(rt, '__file__', type(rt).__name__)); "
    "print(rt.selected_runtime())"
)


def project_with_synced_wrappers(root):
    """A project laid out like ascii-aurora: wrappers synced, copilot_runtime.py absent."""
    tools = Path(root) / "tools"
    tools.mkdir()
    for name in ("claude_station.py", "dispatch_station.py"):
        shutil.copy(FACTORY / "tools" / name, tools / name)
    return Path(root)


def run_probe(project, pythonpath, extra_env=None, runtime=""):
    env = {k: v for k, v in os.environ.items() if k not in ("ANVIL_FACTORY_ROOT", "ANVIL_RUNTIME", "PYTHONPATH")}
    env["PYTHONPATH"] = str(pythonpath)
    if runtime:
        env["ANVIL_RUNTIME"] = runtime
    env.update(extra_env or {})
    return subprocess.run([sys.executable, "-c", PROBE], cwd=project, env=env,
                          capture_output=True, text=True, timeout=60)


class StationRuntimeImportTest(unittest.TestCase):
    def test_finds_factory_copy_through_anvil_factory_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = project_with_synced_wrappers(tmp)
            proc = run_probe(project, FACTORY, {"ANVIL_FACTORY_ROOT": str(FACTORY)})
            self.assertEqual(proc.returncode, 0, proc.stderr)
            loaded, runtime = proc.stdout.split()
            self.assertEqual(Path(loaded).resolve(), (FACTORY / "tools" / "copilot_runtime.py").resolve())
            self.assertEqual(runtime, "claude-gateway")

    def test_finds_factory_copy_next_to_the_running_anvil_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = project_with_synced_wrappers(tmp)
            proc = run_probe(project, FACTORY)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            loaded, runtime = proc.stdout.split()
            self.assertEqual(Path(loaded).resolve(), (FACTORY / "tools" / "copilot_runtime.py").resolve())
            self.assertEqual(runtime, "claude-gateway")

    def test_copilot_runtime_reached_from_factory_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = project_with_synced_wrappers(tmp)
            proc = run_probe(project, FACTORY, {"ANVIL_FACTORY_ROOT": str(FACTORY)}, runtime="copilot")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.stdout.split()[-1], "copilot")

    def test_gateway_still_runs_when_no_copy_exists_anywhere(self):
        with tempfile.TemporaryDirectory() as tmp:
            spine = Path(tmp) / "spine"
            shutil.copytree(FACTORY / "anvil", spine / "anvil",
                            ignore=shutil.ignore_patterns("__pycache__"))
            (Path(tmp) / "project").mkdir()
            project = project_with_synced_wrappers(Path(tmp) / "project")
            proc = run_probe(project, spine)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertNotIn("ModuleNotFoundError", proc.stderr)
            self.assertEqual(proc.stdout.split(), ["_GatewayOnlyRuntime", "claude-gateway"])

    def test_copilot_fails_loudly_naming_the_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            spine = Path(tmp) / "spine"
            shutil.copytree(FACTORY / "anvil", spine / "anvil",
                            ignore=shutil.ignore_patterns("__pycache__"))
            (Path(tmp) / "project").mkdir()
            project = project_with_synced_wrappers(Path(tmp) / "project")
            proc = run_probe(project, spine, runtime="copilot")
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("needs tools/copilot_runtime.py", proc.stderr)
            self.assertNotIn("ModuleNotFoundError", proc.stderr)


if __name__ == "__main__":
    unittest.main()
