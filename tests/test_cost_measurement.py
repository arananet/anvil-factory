import json, tempfile, unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from anvil.cost import validate_price_table, load_price_table, calculate_cost, build_cost_section
from anvil.model import WorkOrder
from anvil.pipeline import load_pipeline
from anvil.stations import load_registry
from anvil.scaffold import init_project, scaffold_spec
from anvil.runner import run_pipeline
from anvil.executor import create_executor

ROOT = Path(__file__).resolve().parent.parent

def make_project(tmp):
    proj = Path(tmp) / "proj"
    init_project(proj, "Demo")
    scaffold_spec(proj, "demo-feature", "Demo Feature")
    return proj

class TestPriceTableValidation(unittest.TestCase):
    """S5: Prices carry their source and date"""

    def test_valid_price_table_s5(self):
        """cost-measurement S5: price table with source and date is valid"""
        table = {
            "claude-sonnet-4-5": {
                "input_per_million": 3.0,
                "output_per_million": 15.0,
                "source": "anthropic-pricing-2024-01",
                "date_recorded": "2024-01-15"
            }
        }
        errors = validate_price_table(table)
        self.assertEqual(errors, [])

    def test_missing_source_rejected_s5(self):
        """cost-measurement S5: loader rejects entry missing source"""
        table = {
            "claude-sonnet-4-5": {
                "input_per_million": 3.0,
                "output_per_million": 15.0,
                "date_recorded": "2024-01-15"
            }
        }
        errors = validate_price_table(table)
        self.assertTrue(any("source" in e for e in errors))

    def test_missing_date_rejected_s5(self):
        """cost-measurement S5: loader rejects entry missing date_recorded"""
        table = {
            "claude-sonnet-4-5": {
                "input_per_million": 3.0,
                "output_per_million": 15.0,
                "source": "anthropic-pricing-2024-01"
            }
        }
        errors = validate_price_table(table)
        self.assertTrue(any("date_recorded" in e for e in errors))

    def test_load_price_table_raises_on_invalid_s5(self):
        """cost-measurement S5: load_price_table raises ValueError on invalid entry"""
        config = {
            "prices": {
                "bad-model": {
                    "input_per_million": 1.0,
                    "output_per_million": 5.0
                    # missing source and date_recorded
                }
            }
        }
        with self.assertRaises(ValueError) as cm:
            load_price_table(config)
        self.assertIn("Invalid price table", str(cm.exception))


class TestCostCalculation(unittest.TestCase):
    """S1 and S3: Cost calculation with measured and unmeasured steps"""

    def setUp(self):
        self.price_table = {
            "claude-sonnet-4-5": {
                "input_per_million": 3.0,
                "output_per_million": 15.0,
                "source": "anthropic-pricing-2024-01",
                "date_recorded": "2024-01-15"
            }
        }

    def test_transcript_usage_priced_s1(self):
        """cost-measurement S1: transcript usage is summed and priced"""
        usage = {"input_tokens": 1000, "output_tokens": 500}
        result = calculate_cost(usage, "claude-sonnet-4-5", self.price_table)

        # (1000 * 3.0 + 500 * 15.0) / 1_000_000 = 0.0105
        expected_cost = (1000 * 3.0 + 500 * 15.0) / 1_000_000
        self.assertEqual(result["measured"], True)
        self.assertEqual(result["cost"], expected_cost)
        self.assertEqual(result["usage"]["input_tokens"], 1000)
        self.assertEqual(result["usage"]["output_tokens"], 500)
        self.assertEqual(result["model"], "claude-sonnet-4-5")
        self.assertIsNone(result["reason"])

    def test_gateway_usage_format_s2(self):
        """cost-measurement S2: gateway usage with prompt_tokens/completion_tokens is priced"""
        usage = {"prompt_tokens": 2000, "completion_tokens": 1000}
        result = calculate_cost(usage, "claude-sonnet-4-5", self.price_table)

        # Gateway format should be normalized to input/output
        expected_cost = (2000 * 3.0 + 1000 * 15.0) / 1_000_000
        self.assertEqual(result["measured"], True)
        self.assertEqual(result["cost"], expected_cost)
        self.assertEqual(result["usage"]["input_tokens"], 2000)
        self.assertEqual(result["usage"]["output_tokens"], 1000)

    def test_no_usage_reported_s3(self):
        """cost-measurement S3: step with no usage stays unmeasured"""
        result = calculate_cost(None, "claude-sonnet-4-5", self.price_table)

        self.assertEqual(result["measured"], False)
        self.assertIsNone(result["cost"])
        self.assertEqual(result["reason"], "no usage reported")
        self.assertIsNone(result["usage"])

    def test_no_price_for_model_s3(self):
        """cost-measurement S3: model with no price table entry stays unmeasured"""
        usage = {"input_tokens": 1000, "output_tokens": 500}
        result = calculate_cost(usage, "unknown-model", self.price_table)

        self.assertEqual(result["measured"], False)
        self.assertIsNone(result["cost"])
        self.assertIn("no price recorded for model", result["reason"])
        self.assertEqual(result["usage"]["input_tokens"], 1000)
        self.assertEqual(result["usage"]["output_tokens"], 500)

    def test_zero_usage_measured_as_zero_s1(self):
        """cost-measurement S1: zero usage is measured with zero cost"""
        usage = {"input_tokens": 0, "output_tokens": 0}
        result = calculate_cost(usage, "claude-sonnet-4-5", self.price_table)

        self.assertEqual(result["measured"], True)
        self.assertEqual(result["cost"], 0.0)


class TestCostSection(unittest.TestCase):
    """S4: Cost section totals measured steps only"""

    def test_cost_section_sums_measured_only_s4(self):
        """cost-measurement S4: total equals sum of measured steps only"""
        steps = [
            {"station": "intake", "status": "executed", "cost": 0.01},
            {"station": "builder", "status": "executed", "cost": 0.05},
            {"station": "spec-writer", "status": "executed", "cost": None},
            {"station": "reviewer-spec", "status": "executed", "cost": 0.02},
            {"station": "reviewer-tests", "status": "executed", "cost": None}
        ]

        cost_section = build_cost_section(steps)

        self.assertEqual(cost_section["total"], 0.08)  # 0.01 + 0.05 + 0.02
        self.assertEqual(cost_section["measured_steps"], 3)
        self.assertEqual(cost_section["unmeasured_steps"], 2)

    def test_cost_section_all_measured_s4(self):
        """cost-measurement S4: all steps measured shows correct counts"""
        steps = [
            {"station": "intake", "status": "executed", "cost": 0.01},
            {"station": "builder", "status": "executed", "cost": 0.05}
        ]

        cost_section = build_cost_section(steps)

        self.assertAlmostEqual(cost_section["total"], 0.06, places=5)
        self.assertEqual(cost_section["measured_steps"], 2)
        self.assertEqual(cost_section["unmeasured_steps"], 0)

    def test_cost_section_all_unmeasured_s4(self):
        """cost-measurement S4: all steps unmeasured shows zero total"""
        steps = [
            {"station": "intake", "status": "executed", "cost": None},
            {"station": "builder", "status": "executed", "cost": None}
        ]

        cost_section = build_cost_section(steps)

        self.assertEqual(cost_section["total"], 0)
        self.assertEqual(cost_section["measured_steps"], 0)
        self.assertEqual(cost_section["unmeasured_steps"], 2)


class TestCostInRunReport(unittest.TestCase):
    """Integration test: cost section appears in run report"""

    def test_run_report_includes_cost_section(self):
        """cost-measurement S4: run report includes cost section with coverage counts"""
        # Create a test executor that returns usage
        class UsageReportingExecutor:
            kind = "test-usage"
            name = "test-usage"
            def __init__(self):
                pass
            def execute(self, packet_text, station_id, packet_path=None, output_path=None, cwd=None):
                # Simulate an executor that reports usage (like an HTTP gateway or transcript parser)
                usage = {"input_tokens": 1000, "output_tokens": 500}
                output = f"Executed {station_id}"
                return {"output": output, "usage": usage}

        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)

            # Add price table to project config
            config_path = proj / "anvil.yaml"
            config = json.loads(config_path.read_text())
            config["prices"] = {
                "claude-sonnet-4-5": {
                    "input_per_million": 3.0,
                    "output_per_million": 15.0,
                    "source": "anthropic-pricing-2024-01",
                    "date_recorded": "2024-01-15"
                },
                "reasoning-strong": {
                    "input_per_million": 2.0,
                    "output_per_million": 10.0,
                    "source": "test-pricing",
                    "date_recorded": "2024-01-15"
                },
                "fast-builder": {
                    "input_per_million": 1.0,
                    "output_per_million": 5.0,
                    "source": "test-pricing",
                    "date_recorded": "2024-01-15"
                }
            }
            config_path.write_text(json.dumps(config, indent=2))

            executor = UsageReportingExecutor()

            # Create minimal pipeline
            pipe_path = Path(tmp) / "test_pipe.json"
            pipe_data = {
                "name": "test",
                "stages": [{"station": "intake"}, {"station": "builder"}]
            }
            pipe_path.write_text(json.dumps(pipe_data))

            reg = load_registry(ROOT / "stations")
            pipe = load_pipeline(pipe_path, known_stations=set(reg.ids()))
            wo = WorkOrder(id="wo-cost-001", kind="feature", title="Cost test")

            report = run_pipeline(proj, pipe, wo, registry=reg, executor=executor)

            # Check that cost section exists in to_dict output
            report_dict = report.to_dict()
            self.assertIn("cost", report_dict)
            cost = report_dict["cost"]
            self.assertIn("total", cost)
            self.assertIn("measured_steps", cost)
            self.assertIn("unmeasured_steps", cost)

            # Per S3 and S4: intake uses 'default' model (no price entry) so unmeasured,
            # builder uses 'fast-builder' (priced) so measured
            self.assertEqual(cost["measured_steps"], 1)
            self.assertEqual(cost["unmeasured_steps"], 1)

            # Total equals measured step cost only: (1000 * 1.0 + 500 * 5.0) / 1_000_000
            expected_builder_cost = (1000 * 1.0 + 500 * 5.0) / 1_000_000
            self.assertAlmostEqual(cost["total"], expected_builder_cost, places=6)


class TestGatewayUsageHandling(unittest.TestCase):
    """S2: Gateway usage is consumed when response reports it"""

    def test_gateway_response_with_usage(self):
        """cost-measurement S2: HTTP gateway response with usage is priced"""
        # Test executor that simulates HTTP gateway returning usage
        class GatewayWithUsageExecutor:
            kind = "test-gateway"
            name = "test-gateway"
            def execute(self, packet_text, station_id, packet_path=None, output_path=None, cwd=None):
                # Simulate gateway response with usage (prompt_tokens/completion_tokens format)
                usage = {"prompt_tokens": 1500, "completion_tokens": 750}
                return {"output": f"Gateway executed {station_id}", "usage": usage}

        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)

            # Add price table with fast-builder (builder station's model)
            config_path = proj / "anvil.yaml"
            config = json.loads(config_path.read_text())
            config["prices"] = {
                "fast-builder": {
                    "input_per_million": 3.0,
                    "output_per_million": 15.0,
                    "source": "anthropic-pricing-2024-01",
                    "date_recorded": "2024-01-15"
                }
            }
            config_path.write_text(json.dumps(config, indent=2))

            executor = GatewayWithUsageExecutor()

            pipe_path = Path(tmp) / "test_pipe.json"
            pipe_data = {"name": "test", "stages": [{"station": "builder"}]}
            pipe_path.write_text(json.dumps(pipe_data))

            reg = load_registry(ROOT / "stations")
            pipe = load_pipeline(pipe_path, known_stations=set(reg.ids()))
            wo = WorkOrder(id="wo-gateway-001", kind="feature", title="Gateway test")

            report = run_pipeline(proj, pipe, wo, registry=reg, executor=executor)

            # Find builder step and verify S2: gateway usage is priced
            builder_step = next((s for s in report.steps if s["station"] == "builder"), None)
            self.assertIsNotNone(builder_step)
            self.assertIsNotNone(builder_step.get("cost"))
            self.assertGreater(builder_step.get("cost"), 0)

            # Check usage was recorded with expected cost
            self.assertIn("usage", builder_step)
            usage = builder_step["usage"]
            self.assertIn("prompt_tokens", usage)
            self.assertIn("completion_tokens", usage)

            # Verify the cost calculation: (1500 * 3.0 + 750 * 15.0) / 1_000_000
            expected_cost = (1500 * 3.0 + 750 * 15.0) / 1_000_000
            self.assertAlmostEqual(builder_step["cost"], expected_cost, places=6)

    def test_gateway_response_without_usage_unmeasured_s2(self):
        """cost-measurement S2: gateway response with no usage records unmeasured"""
        # Test executor that returns no usage
        class GatewayWithoutUsageExecutor:
            kind = "test-gateway-no-usage"
            name = "test-gateway-no-usage"
            def execute(self, packet_text, station_id, packet_path=None, output_path=None, cwd=None):
                # Gateway response without usage
                return {"output": f"Gateway executed {station_id}", "usage": None}

        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)

            # Add price table
            config_path = proj / "anvil.yaml"
            config = json.loads(config_path.read_text())
            config["prices"] = {
                "reasoning-strong": {
                    "input_per_million": 3.0,
                    "output_per_million": 15.0,
                    "source": "anthropic-pricing-2024-01",
                    "date_recorded": "2024-01-15"
                }
            }
            config_path.write_text(json.dumps(config, indent=2))

            executor = GatewayWithoutUsageExecutor()

            pipe_path = Path(tmp) / "test_pipe.json"
            pipe_data = {"name": "test", "stages": [{"station": "intake"}]}
            pipe_path.write_text(json.dumps(pipe_data))

            reg = load_registry(ROOT / "stations")
            pipe = load_pipeline(pipe_path, known_stations=set(reg.ids()))
            wo = WorkOrder(id="wo-gateway-002", kind="feature", title="Gateway no usage")

            report = run_pipeline(proj, pipe, wo, registry=reg, executor=executor)

            # Find intake step and check cost is None (unmeasured)
            intake_step = next((s for s in report.steps if s["station"] == "intake"), None)
            self.assertIsNotNone(intake_step)
            self.assertIsNone(intake_step.get("cost"))


if __name__ == "__main__":
    unittest.main()
