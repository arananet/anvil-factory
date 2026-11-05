"""wo-gh-29 gate loopback round 3: tier resolution at hand-off, OpenAI runtime gateway env.

Maps to model-migration R10, R11, S8, S9 (and S10 for provenance staying intact).
"""
import io, json, os, sys, tempfile, unittest
from pathlib import Path
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from anvil.executor import create_executor
from anvil.model import WorkOrder
from anvil.pipeline import load_pipeline
from anvil.runner import run_pipeline
from anvil.scaffold import init_project
from anvil.stations import load_registry

ROOT = Path(__file__).resolve().parent.parent
CONCRETE = {"claude-opus-5-5", "claude-sonnet-5-5", "openai/gpt-6.1-sol"}
TIER_MAP = {
    "review-balanced": "claude-sonnet-5-5",
    "review-strong": "claude-sonnet-5-5",
    "fast-builder": "claude-opus-5-5",
    "reasoning-strong": "claude-opus-5-5",
    "writing-strong": "claude-sonnet-5-5",
    "fast-reader": "claude-sonnet-5-5",
    "media-gen": "claude-sonnet-5-5",
    "default": "claude-sonnet-5-5",
}

RECORDER = """import json, os, sys
station = ""
for line in open(sys.argv[1], encoding="utf-8"):
    if line.startswith("# Task packet:"):
        station = line.split(":", 1)[1].strip()
        break
open(os.environ["RECORD_PATH"], "a").write(station + " " + os.environ.get("ANVIL_CONFIGURED_MODEL", "") + "\\n")
if station.startswith("reviewer"):
    print(json.dumps({"station": station, "verdict": "pass", "findings": ["ok"]}))
else:
    print(json.dumps({"note": "done by " + station}))
"""


def run_recorded(tmp, wo_id, mutate=None):
    proj = Path(tmp) / "proj"
    init_project(proj, "Demo")
    script = Path(tmp) / "rt.py"
    script.write_text(RECORDER)
    record = Path(tmp) / "record.txt"
    os.environ["RECORD_PATH"] = str(record)
    try:
        ex = create_executor({"kind": "command",
                              "command": f"{sys.executable} {script} {{packet}}",
                              "timeout_seconds": 60})
        reg = load_registry(ROOT / "stations")
        if mutate:
            mutate(reg)
        pipe = load_pipeline(ROOT / "pipelines" / "hotfix.json", known_stations=set(reg.ids()))
        wo = WorkOrder(id=wo_id, kind="bug", title="Tier resolution")
        report = run_pipeline(proj, pipe, wo, registry=reg, executor=ex)
    finally:
        os.environ.pop("RECORD_PATH", None)
    handed = {}
    if record.exists():
        for line in record.read_text().splitlines():
            st, _, model = line.partition(" ")
            handed[st] = model
    return report, handed


class TestTierResolutionAtHandoff(unittest.TestCase):
    def test_every_tier_label_resolves_per_table_s8(self):
        """R10/S8: each label a station can carry reaches the runtime as its concrete model"""
        for label, expected in TIER_MAP.items():
            with self.subTest(label=label):
                def mutate(reg, label=label):
                    reg.get("builder").model = label
                with tempfile.TemporaryDirectory() as tmp:
                    _, handed = run_recorded(tmp, "wo-tier-" + label.replace("_", "-"), mutate)
                    self.assertEqual(handed.get("builder"), expected)

    def test_concrete_models_pass_through_unchanged_s8(self):
        for model in sorted(CONCRETE):
            with self.subTest(model=model):
                def mutate(reg, model=model):
                    reg.get("builder").model = model
                with tempfile.TemporaryDirectory() as tmp:
                    _, handed = run_recorded(tmp, "wo-pass-" + model.split("/")[-1].replace(".", "-"), mutate)
                    self.assertEqual(handed.get("builder"), model)

    def test_no_station_receives_an_unresolved_label_s8(self):
        """R10: the map is total, nothing handed to the runtime is a tier label"""
        with tempfile.TemporaryDirectory() as tmp:
            _, handed = run_recorded(tmp, "wo-tier-total")
            self.assertTrue(handed)
            for station, model in handed.items():
                self.assertIn(model, CONCRETE, f"{station} got {model!r}")

    def test_routed_reviewers_hand_off_concrete_model_s8(self):
        """R10/S8: a reviewer whose model comes from routing (review-balanced/strong) is handed a concrete model"""
        with tempfile.TemporaryDirectory() as tmp:
            report, handed = run_recorded(tmp, "wo-tier-routed")
            reviewers = {s: m for s, m in handed.items() if s.startswith("reviewer")}
            self.assertTrue(reviewers, "no reviewer reached the runtime")
            for station, model in reviewers.items():
                self.assertEqual(model, "claude-sonnet-5-5", station)

    def test_report_configured_model_concrete_for_routed_reviewers_s8(self):
        with tempfile.TemporaryDirectory() as tmp:
            report, _ = run_recorded(tmp, "wo-tier-report")
            reviewer_steps = [s for s in report.steps
                              if s["station"].startswith("reviewer") and s.get("executor")]
            self.assertTrue(reviewer_steps)
            for step in reviewer_steps:
                self.assertIn(step["configured_model"], CONCRETE, step["station"])

    def test_executed_model_not_copied_from_resolved_label_s10(self):
        """S10: resolution does not turn the hand-off into a record; no self-report means null"""
        with tempfile.TemporaryDirectory() as tmp:
            report, _ = run_recorded(tmp, "wo-tier-prov")
            builder = [s for s in report.steps if s["station"] == "builder"][0]
            self.assertIsNone(builder["executed_model"])

    def test_dispatcher_still_rejects_tier_labels_s8(self):
        """R10: the dispatcher keeps failing loudly on anything not a known concrete model"""
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            packet = Path(tmp) / "p.md"
            packet.write_text("# Task packet: builder\n\n- id: wo-x\n")
            env = dict(os.environ, ANVIL_CONFIGURED_MODEL="review-balanced")
            proc = subprocess.run([sys.executable, str(ROOT / "tools" / "dispatch_station.py"),
                                   str(packet), str(Path(tmp) / "o.md")],
                                  env=env, capture_output=True, text=True, timeout=60)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("review-balanced", proc.stderr + proc.stdout)


class _FakeResp(io.BytesIO):
    def __enter__(self):
        return self
    def __exit__(self, *a):
        return False


GATEWAY = "https://gateway.example.test/v1/acct123/gw-name/anthropic"
TOKEN = "tok-secret-value-xyz"


class TestOpenAIRuntimeGatewayEnv(unittest.TestCase):
    def _call(self, env):
        import codex_station
        captured = {}

        def fake_urlopen(req, timeout=None):
            captured["url"] = req.full_url
            captured["auth"] = req.get_header("Authorization")
            captured["body"] = json.loads(req.data.decode("utf-8"))
            return _FakeResp(json.dumps({"choices": [{"message": {"content": "hello"}}]}).encode())

        clean = {k: v for k, v in os.environ.items()
                 if not k.startswith("OPENAI_") and k not in
                 ("CF_AIG_TOKEN", "ANTHROPIC_BASE_URL", "ANVIL_GATEWAY_OPENAI_URL",
                                  "ANTHROPIC_CUSTOM_HEADERS")}
        clean.update(env)
        with mock.patch.dict(os.environ, clean, clear=True), \
             mock.patch("urllib.request.urlopen", fake_urlopen):
            out = codex_station.call_openai_api("hi", "openai/gpt-6.1-sol")
        return out, captured

    def test_config_built_from_cf_aig_token_and_anthropic_base_url_alone_s9(self):
        out, cap = self._call({"CF_AIG_TOKEN": TOKEN, "ANTHROPIC_BASE_URL": GATEWAY})
        self.assertEqual(out, "hello")
        self.assertTrue(cap["url"].startswith("https://gateway.example.test/v1/acct123/gw-name/"))
        self.assertIn("/openai", cap["url"])
        self.assertNotIn("anthropic", cap["url"])
        self.assertIn(TOKEN, cap["auth"])
        self.assertEqual(cap["body"]["model"], "gpt-6.1-sol")

    def test_explicit_gateway_openai_url_is_honoured_s9(self):
        explicit = "https://other.example.test/custom/openai"
        _, cap = self._call({"CF_AIG_TOKEN": TOKEN, "ANTHROPIC_BASE_URL": GATEWAY,
                             "ANVIL_GATEWAY_OPENAI_URL": explicit})
        self.assertTrue(cap["url"].startswith(explicit))
        self.assertNotIn("gateway.example.test", cap["url"])

    def test_missing_gateway_env_fails_loudly_without_values_s9(self):
        # Error naming follows the credential sources actually checked (R11, R13).
        for env, missing in (({}, "CF_AIG_TOKEN"),
                             ({}, "ANTHROPIC_CUSTOM_HEADERS"),
                             ({"ANTHROPIC_BASE_URL": GATEWAY}, "CF_AIG_TOKEN"),
                             ({"ANTHROPIC_BASE_URL": GATEWAY}, "cf-aig-authorization"),
                             ({"CF_AIG_TOKEN": TOKEN}, "ANTHROPIC_BASE_URL")):
            with self.subTest(env=sorted(env), missing=missing):
                with self.assertRaises(RuntimeError) as ctx:
                    self._call(env)
                msg = str(ctx.exception)
                self.assertIn(missing, msg)
                self.assertNotIn(TOKEN, msg)
                self.assertNotIn("OPENAI_API_KEY", msg)

    def test_credential_from_custom_headers_when_token_unset_s9(self):
        headers = "x-other: 1\ncf-aig-authorization: Bearer " + TOKEN + "\n"
        out, cap = self._call({"ANTHROPIC_BASE_URL": GATEWAY, "ANTHROPIC_CUSTOM_HEADERS": headers})
        self.assertEqual(out, "hello")
        self.assertIn(TOKEN, cap["auth"])

    def test_direct_token_wins_over_headers_s9(self):
        headers = "cf-aig-authorization: Bearer header-token-abc"
        _, cap = self._call({"CF_AIG_TOKEN": TOKEN, "ANTHROPIC_BASE_URL": GATEWAY,
                             "ANTHROPIC_CUSTOM_HEADERS": headers})
        self.assertIn(TOKEN, cap["auth"])
        self.assertNotIn("header-token-abc", cap["auth"])

    def test_openai_env_variables_are_not_required_s9(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            for k in [k for k in os.environ if k.startswith("OPENAI_")]:
                os.environ.pop(k)
            out, _ = self._call({"CF_AIG_TOKEN": TOKEN, "ANTHROPIC_BASE_URL": GATEWAY})
        self.assertEqual(out, "hello")


if __name__ == "__main__":
    unittest.main()
