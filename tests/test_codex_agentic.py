"""wo-gh-29 round 5, Part B: the OpenAI station runtime is the agentic Codex CLI.

Maps to model-migration R12 and S12. A fake `codex` executable on PATH stands in
for the CLI; it records argv, cwd and the child environment.
"""
import json, os, shutil, stat, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CODEX = ROOT / "tools" / "codex_station.py"
DISPATCH = ROOT / "tools" / "dispatch_station.py"
TOKEN = "tok-secret-value-xyz"
GATEWAY = "https://gateway.example.test/v1/acct123/gw-name/anthropic"
MODEL = "openai/gpt-6.1-sol"

FAKE = '''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
rec = Path(os.environ["FAKE_RECORD"])
n = len(rec.read_text().splitlines()) if rec.exists() else 0
with rec.open("a") as fh:
    fh.write(json.dumps({"argv": sys.argv[1:], "cwd": os.getcwd(), "env": dict(os.environ)}) + "\\n")
mode = os.environ.get("FAKE_MODE", "")
wo, st = os.environ.get("FAKE_WO"), os.environ.get("FAKE_STATION")
if wo and st:
    p = Path(os.getcwd()) / "runs" / wo / (st + ".review.json")
    p.parent.mkdir(parents=True, exist_ok=True)
    if mode == "invalid_then_valid" and n == 0:
        p.write_text("not json")
    elif mode != "never_valid":
        p.write_text(json.dumps({"station": st, "verdict": "pass", "findings": []}))
print("codex did some work")
'''


class Harness:
    def __init__(self, tc):
        self.tmp = tempfile.mkdtemp()
        tc.addCleanup(shutil.rmtree, self.tmp, True)
        self.bin = Path(self.tmp) / "bin"
        self.bin.mkdir()
        fake = self.bin / "codex"
        fake.write_text(FAKE)
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        self.record = Path(self.tmp) / "record.jsonl"
        self.wo = "wo-codex-test-" + os.path.basename(self.tmp)
        tc.addCleanup(shutil.rmtree, ROOT / "runs" / self.wo, True)

    def packet(self, station):
        p = Path(self.tmp) / (station + ".packet.md")
        p.write_text(f"# Task packet: {station}\n\n- id: {self.wo}\n\nDo the work.\n")
        return p

    def env(self, with_codex=True, **extra):
        env = {k: v for k, v in os.environ.items()
               if k not in ("CF_AIG_TOKEN", "ANTHROPIC_BASE_URL", "ANTHROPIC_CUSTOM_HEADERS",
                            "ANVIL_GATEWAY_OPENAI_URL") and not k.startswith("OPENAI_")}
        # python3 keeps working; PATH is only the fake dir plus the interpreter's dir
        path = str(Path(sys.executable).parent)
        env["PATH"] = (str(self.bin) + os.pathsep + path) if with_codex else path
        env.update({"ANVIL_CONFIGURED_MODEL": MODEL, "ANTHROPIC_BASE_URL": GATEWAY,
                    "CF_AIG_TOKEN": TOKEN, "FAKE_RECORD": str(self.record)})
        env.update(extra)
        return env

    def run(self, station, script=CODEX, **kw):
        out = Path(self.tmp) / (station + ".out.md")
        extra = kw.pop("extra", {})
        if station.startswith("reviewer"):
            extra.setdefault("FAKE_WO", self.wo)
            extra.setdefault("FAKE_STATION", station)
        proc = subprocess.run([sys.executable, str(script), str(self.packet(station)), str(out)],
                              env=self.env(**extra, **kw),
                              capture_output=True, text=True, timeout=60)
        return proc, out

    def calls(self):
        if not self.record.exists():
            return []
        return [json.loads(l) for l in self.record.read_text().splitlines()]


class TestCodexAgenticRuntime(unittest.TestCase):
    def test_headless_invocation_targets_bare_model_in_repo_tree_s12(self):
        h = Harness(self)
        proc, out = h.run("reviewer-design")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        call = h.calls()[0]
        self.assertEqual(Path(call["cwd"]).resolve(), ROOT)
        argv = " ".join(call["argv"])
        self.assertIn("gpt-6.1-sol", argv)
        self.assertNotIn("openai/gpt-6.1-sol", argv)
        self.assertIn("exec", call["argv"])
        self.assertIn("Do the work.", argv)  # the packet is the task

    def test_gateway_openai_route_configured_s12(self):
        h = Harness(self)
        h.run("reviewer-design")
        call = h.calls()[0]
        blob = " ".join(call["argv"]) + json.dumps(
            {k: v for k, v in call["env"].items() if "BASE_URL" in k or "OPENAI" in k})
        self.assertIn("https://gateway.example.test/v1/acct123/gw-name/openai", blob)
        self.assertNotIn("/anthropic", " ".join(call["argv"]))

    def test_credential_only_in_child_environment_s12(self):
        h = Harness(self)
        proc, out = h.run("reviewer-design")
        call = h.calls()[0]
        self.assertNotIn(TOKEN, " ".join(call["argv"]))
        self.assertIn(TOKEN, "".join(call["env"].values()))
        self.assertNotIn(TOKEN, proc.stdout + proc.stderr)
        self.assertNotIn(TOKEN, out.read_text())

    def test_credential_from_custom_headers_reaches_child_s12(self):
        h = Harness(self)
        env_extra = {"ANTHROPIC_CUSTOM_HEADERS": "cf-aig-authorization: Bearer hdr-tok-777"}
        env = h.env(**env_extra)
        env.pop("CF_AIG_TOKEN")
        env.update({"FAKE_WO": h.wo, "FAKE_STATION": "reviewer-design"})
        out = Path(h.tmp) / "o.md"
        proc = subprocess.run([sys.executable, str(CODEX), str(h.packet("reviewer-design")), str(out)],
                              env=env, capture_output=True, text=True, timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        call = h.calls()[0]
        self.assertIn("hdr-tok-777", "".join(call["env"].values()))
        self.assertNotIn("hdr-tok-777", " ".join(call["argv"]) + proc.stdout + proc.stderr)

    def test_write_permission_only_for_builder_and_test_writer_s12(self):
        argvs = {}
        for station in ("builder", "test-writer", "reviewer-design", "supervisor"):
            h = Harness(self)
            proc, _ = h.run(station)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            argvs[station] = [a for a in h.calls()[0]["argv"] if "Task packet" not in a and "Do the work" not in a]
        self.assertEqual(argvs["builder"], argvs["test-writer"])
        self.assertEqual(argvs["reviewer-design"], argvs["supervisor"])
        self.assertNotEqual(argvs["builder"], argvs["reviewer-design"])

    def test_reviewer_review_file_validated_s12(self):
        h = Harness(self)
        proc, _ = h.run("reviewer-design")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        review = ROOT / "runs" / h.wo / "reviewer-design.review.json"
        self.assertEqual(json.loads(review.read_text())["station"], "reviewer-design")
        self.assertEqual(len(h.calls()), 1)
        self.assertFalse((ROOT / "runs" / h.wo / "reviewer-design.correction.json").exists())

    def test_one_in_session_correction_s12(self):
        h = Harness(self)
        proc, _ = h.run("reviewer-design", extra={"FAKE_MODE": "invalid_then_valid"})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(len(h.calls()), 2)
        meta = json.loads((ROOT / "runs" / h.wo / "reviewer-design.correction.json").read_text())
        self.assertTrue(meta["correction_used"])
        self.assertIn("correction", " ".join(h.calls()[1]["argv"]).lower())

    def test_no_second_correction_s12(self):
        h = Harness(self)
        h.run("reviewer-design", extra={"FAKE_MODE": "never_valid"})
        self.assertEqual(len(h.calls()), 2)

    def test_absent_codex_cli_fails_loudly_without_completion_fallback_s12(self):
        h = Harness(self)
        proc, out = h.run("reviewer-design", with_codex=False)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("codex", (proc.stderr + proc.stdout).lower())
        self.assertFalse(out.exists() and out.read_text().strip())
        self.assertEqual(h.calls(), [])

    def test_missing_gateway_environment_fails_loudly_s12(self):
        h = Harness(self)
        env = h.env()
        for k in ("CF_AIG_TOKEN", "ANTHROPIC_BASE_URL"):
            env.pop(k)
        out = Path(h.tmp) / "o.md"
        proc = subprocess.run([sys.executable, str(CODEX), str(h.packet("builder")), str(out)],
                              env=env, capture_output=True, text=True, timeout=60)
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(h.calls(), [])

    def test_codex_station_has_no_completion_path_s12(self):
        text = CODEX.read_text()
        self.assertNotIn("chat/completions", text)
        self.assertNotIn("urlopen", text)

    def test_dispatcher_self_reports_model_for_codex_runs_s12(self):
        h = Harness(self)
        proc, out = h.run("reviewer-design", script=DISPATCH)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        reported = [json.loads(l) for l in out.read_text().splitlines() if l.startswith("{")]
        self.assertIn({"model": MODEL}, reported)

    def test_dispatcher_does_not_self_report_when_codex_absent_s12(self):
        h = Harness(self)
        proc, out = h.run("reviewer-design", script=DISPATCH, with_codex=False)
        self.assertNotEqual(proc.returncode, 0)
        self.assertNotIn('"model"', proc.stdout)


if __name__ == "__main__":
    unittest.main()
