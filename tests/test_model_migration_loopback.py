"""wo-gh-29 gate loopback round 2: provenance, executor signature, no invented prices.

Maps to model-migration R3, R6, S5 and agent-execution S8.
"""
import inspect, json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from anvil.cost import calculate_cost, load_price_table
from anvil.executor import CommandExecutor, HttpExecutor, create_executor
from anvil.model import WorkOrder
from anvil.pipeline import load_pipeline
from anvil.runner import run_pipeline
from anvil.scaffold import init_project
from anvil.stations import load_registry

ROOT = Path(__file__).resolve().parent.parent
NEW_MODELS = ["claude-opus-5-5", "claude-sonnet-5-5", "openai/gpt-6.1-sol"]

RECORDER = """import json, os, sys
open(os.environ["RECORD_PATH"], "a").write(os.environ.get("ANVIL_CONFIGURED_MODEL", "") + "\\n")
print(json.dumps({"station": "x", "verdict": "pass", "findings": ["ok"]}))
"""
REPORTER = """import json, os
open(os.environ["RECORD_PATH"], "a").write(os.environ.get("ANVIL_CONFIGURED_MODEL", "") + "\\n")
print(json.dumps({"station": "x", "verdict": "pass", "findings": ["ok"], "model": "self-reported-1"}))
"""


def project(tmp):
    proj = Path(tmp) / "proj"
    init_project(proj, "Demo")
    return proj


def run_with(tmp, script_text, wo_id):
    import os
    script = Path(tmp) / "rt.py"
    script.write_text(script_text)
    record = Path(tmp) / "record.txt"
    os.environ["RECORD_PATH"] = str(record)
    try:
        ex = create_executor({"kind": "command",
                              "command": f"{sys.executable} {script} {{packet}}",
                              "timeout_seconds": 60})
        reg = load_registry(ROOT / "stations")
        pipe = load_pipeline(ROOT / "pipelines" / "hotfix.json", known_stations=set(reg.ids()))
        wo = WorkOrder(id=wo_id, kind="bug", title="Loopback")
        report = run_pipeline(project(tmp), pipe, wo, registry=reg, executor=ex)
    finally:
        os.environ.pop("RECORD_PATH", None)
    return report, record


class TestProvenanceNotConflatedWithHandoff(unittest.TestCase):
    def test_model_handed_in_but_executed_model_null_without_self_report(self):
        """R3 + S8: runtime receives configured model; executed_model stays null"""
        with tempfile.TemporaryDirectory() as tmp:
            report, record = run_with(tmp, RECORDER, "wo-loop-001")
            builder = [s for s in report.steps if s["station"] == "builder"][0]
            self.assertIsNone(builder["executed_model"])
            self.assertEqual(builder["configured_model"], "fast-builder")
            self.assertIn("fast-builder", record.read_text().split())

    def test_self_reported_model_wins_over_configured_label(self):
        """S8: executed_model is the runtime's self-report, never the configured label"""
        with tempfile.TemporaryDirectory() as tmp:
            report, record = run_with(tmp, REPORTER, "wo-loop-002")
            builder = [s for s in report.steps if s["station"] == "builder"][0]
            self.assertEqual(builder["executed_model"], "self-reported-1")
            self.assertNotEqual(builder["executed_model"], builder["configured_model"])
            self.assertIn("fast-builder", record.read_text().split())


class TestExecutorSignatureConsistency(unittest.TestCase):
    def test_every_executor_accepts_configured_model(self):
        """No executor class raises on the model hand-off argument"""
        for cls in (CommandExecutor, HttpExecutor):
            params = inspect.signature(cls.execute).parameters
            self.assertIn("configured_model", params, cls.__name__)
            self.assertIsNone(params["configured_model"].default, cls.__name__)

    def test_executor_classes_in_module_all_accept_it(self):
        import anvil.executor as mod
        for name, cls in inspect.getmembers(mod, inspect.isclass):
            if cls.__module__ == mod.__name__ and "execute" in cls.__dict__:
                self.assertIn("configured_model", inspect.signature(cls.execute).parameters, name)

    def test_http_executor_call_with_model_does_not_raise_typeerror(self):
        ex = create_executor({"kind": "http", "endpoint": "http://127.0.0.1:9/v1/x",
                              "model": "m", "api_key_env": "ANVIL_NO_SUCH_KEY_VAR",
                              "timeout_seconds": 1})
        try:
            ex.execute("packet", "builder", configured_model="claude-opus-5-5")
        except TypeError as e:
            self.fail(f"unexpected TypeError: {e}")
        except Exception:
            pass  # missing key or connection failure is acceptable here

    def test_legacy_fake_executor_without_parameter_still_works(self):
        """Fake executors predating the hand-off are called without the argument"""
        class Fake:
            kind = "fake"
            name = "fake"
            def execute(self, packet_text, station_id, packet_path=None, output_path=None, cwd=None):
                return json.dumps({"station": station_id, "verdict": "pass", "findings": ["ok"]})
        with tempfile.TemporaryDirectory() as tmp:
            reg = load_registry(ROOT / "stations")
            pipe = load_pipeline(ROOT / "pipelines" / "hotfix.json", known_stations=set(reg.ids()))
            wo = WorkOrder(id="wo-loop-003", kind="bug", title="Fake")
            report = run_pipeline(project(tmp), pipe, wo, registry=reg, executor=Fake())
            self.assertTrue(report.steps)


class TestNoInventedPrices(unittest.TestCase):
    def _config(self):
        return json.loads((ROOT / "anvil.yaml").read_text())

    def test_new_models_absent_unless_sourced_r6(self):
        """R6/S5: an entry may exist only with a checkable source and current date"""
        prices = self._config().get("prices", {})
        for model in NEW_MODELS:
            if model in prices:
                src = str(prices[model].get("source", ""))
                self.assertNotIn("2024", src, f"{model} source looks fabricated")
                self.assertTrue(src.startswith("http"), f"{model} needs a verifiable source URL")
                self.assertFalse(str(prices[model].get("date_recorded", "")).startswith("2024"))

    def test_fabricated_source_labels_not_present(self):
        text = (ROOT / "anvil.yaml").read_text()
        self.assertNotIn("anthropic-pricing-2024-12", text)
        self.assertNotIn("openai-pricing-2024-11", text)

    def test_price_table_still_loads(self):
        load_price_table(self._config())

    def test_unpriced_new_model_is_recorded_unmeasured_with_reason(self):
        table = load_price_table(self._config())
        for model in NEW_MODELS:
            if model in table:
                continue
            rec = calculate_cost({"input_tokens": 10, "output_tokens": 5}, model, table)
            self.assertFalse(rec["measured"])
            self.assertIsNone(rec["cost"])
            self.assertTrue(rec["reason"])


if __name__ == "__main__":
    unittest.main()
