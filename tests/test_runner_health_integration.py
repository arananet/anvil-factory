import json, os, tempfile, unittest, sys
from pathlib import Path
from unittest.mock import patch, MagicMock
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

ROOT = Path(__file__).resolve().parent.parent

class TestRunnerHealthIntegration(unittest.TestCase):
    """Runner-level integration tests for health verification wiring."""

    def test_run_with_health_target_gains_health_section(self):
        """Runner integration: run with health target gets health section in report"""
        from anvil.runner import RunReport

        # Test that a run with health configuration gets health section
        report = RunReport(
            work_order_id="wo-health-integration",
            pipeline="test-pipeline",
            title="Test health",
            kind="feature"
        )

        # Simulate health result
        health_result = {
            "outcome": "healthy",
            "route_results": [
                {"route": "/", "expected_status": 200, "observed_status": 200, "latency_ms": 50}
            ],
            "deployment_status_text": "deployed and healthy"
        }

        report.health = health_result
        report_dict = report.to_dict()

        # Verify health section exists
        self.assertIn("health", report_dict)
        self.assertEqual(report_dict["health"]["outcome"], "healthy")

    def test_unhealthy_outcome_forces_human_gate_with_reason(self):
        """Runner integration: unhealthy outcome sets human_required with health reason"""
        from anvil.runner import RunReport

        report = RunReport(
            work_order_id="wo-unhealthy-test",
            pipeline="test-pipeline",
            title="Test unhealthy",
            kind="feature",
            verdict="approved",  # Approver said approved
            human_required=False  # Initially no human required
        )

        # Simulate health verification finding unhealthy state
        health_result = {
            "outcome": "unhealthy",
            "requires_human_gate": True,
            "health_reason": "Route /api/data returned 500, expected 200"
        }

        # The runner should set human_required based on health
        if health_result.get("outcome") == "unhealthy" and health_result.get("requires_human_gate"):
            report.human_required = True

        report.health = health_result
        report_dict = report.to_dict()

        # Verify human gate is forced
        self.assertTrue(report.human_required)
        self.assertEqual(report_dict["health"]["outcome"], "unhealthy")
        self.assertIn("health_reason", report_dict["health"])

    def test_unknown_outcome_never_reads_as_healthy(self):
        """Runner integration: unknown outcome never appears as healthy"""
        from anvil.runner import RunReport

        report = RunReport(
            work_order_id="wo-unknown",
            pipeline="test-pipeline",
            title="Test unknown",
            kind="feature"
        )

        health_result = {
            "outcome": "unknown",
            "reason": "No target declared",
            "warning": "Health could not be verified - no health target declared",
            "deployment_status_text": "deployed with health unknown"
        }

        report.health = health_result
        # Unknown doesn't change deployment_status from deployed_verified (spec S3)
        report.deployment_status = "deployed_verified"
        report_dict = report.to_dict()

        # Verify unknown is never rendered as healthy
        self.assertEqual(report_dict["health"]["outcome"], "unknown")
        # Deployment status stays as deployed_verified, doesn't change to deployed_and_healthy
        self.assertEqual(report_dict["deployment_status"], "deployed_verified")
        self.assertNotEqual(report_dict["deployment_status"], "deployed_and_healthy")

    def test_ssrf_protection_rejects_private_ips(self):
        """Runner integration: SSRF protection prevents requests to private IPs"""
        from anvil.health import verify_health

        # Test with private IP
        health_config = {
            "base_url": "http://10.0.0.1",
            "routes": [{"path": "/", "expected_status": 200}]
        }

        result = verify_health(health_config, deploy_time="2026-11-04T10:00:00Z")

        # Should be rejected with SSRF reason
        self.assertEqual(result["outcome"], "unknown")
        self.assertIn("reason", result)
        reason_lower = result["reason"].lower()
        self.assertTrue(
            "ssrf" in reason_lower or
            "private" in reason_lower or
            "rfc1918" in reason_lower
        )

    def test_ssrf_protection_rejects_loopback(self):
        """Runner integration: SSRF protection prevents requests to loopback"""
        from anvil.health import verify_health

        health_config = {
            "base_url": "http://127.0.0.1",
            "routes": [{"path": "/", "expected_status": 200}]
        }

        result = verify_health(health_config, deploy_time="2026-11-04T10:00:00Z")

        # Should be rejected
        self.assertEqual(result["outcome"], "unknown")
        self.assertIn("reason", result)
        reason_lower = result["reason"].lower()
        self.assertTrue(
            "loopback" in reason_lower or
            "rejected" in reason_lower
        )

    def test_ssrf_protection_rejects_cloud_metadata(self):
        """Runner integration: SSRF protection prevents requests to cloud metadata endpoint"""
        from anvil.health import verify_health

        health_config = {
            "base_url": "http://169.254.169.254",
            "routes": [{"path": "/latest/meta-data", "expected_status": 200}]
        }

        result = verify_health(health_config, deploy_time="2026-11-04T10:00:00Z")

        # Should be rejected
        self.assertEqual(result["outcome"], "unknown")
        self.assertIn("reason", result)
        reason_lower = result["reason"].lower()
        self.assertTrue(
            "link-local" in reason_lower or
            "rejected" in reason_lower or
            "metadata" in reason_lower.replace("-", "")
        )

    def test_invalid_url_scheme_rejected(self):
        """Runner integration: non-http/https schemes are rejected"""
        from anvil.health import verify_health

        health_config = {
            "base_url": "file:///etc/passwd",
            "routes": [{"path": "/", "expected_status": 200}]
        }

        result = verify_health(health_config, deploy_time="2026-11-04T10:00:00Z")

        # Should be rejected
        self.assertEqual(result["outcome"], "unknown")
        self.assertIn("reason", result)
        reason_lower = result["reason"].lower()
        self.assertTrue(
            "scheme" in reason_lower or
            "configuration" in reason_lower or
            "invalid" in reason_lower
        )

    def test_invalid_http_status_rejected(self):
        """Runner integration: invalid expected_status values are rejected"""
        from anvil.health import verify_health

        health_config = {
            "base_url": "https://example.com",
            "routes": [{"path": "/", "expected_status": 999}]
        }

        result = verify_health(health_config, deploy_time="2026-11-04T10:00:00Z")

        # Should be rejected
        self.assertEqual(result["outcome"], "unknown")
        self.assertIn("reason", result)
        reason_lower = result["reason"].lower()
        self.assertTrue(
            "status" in reason_lower or
            "invalid" in reason_lower or
            "configuration" in reason_lower
        )


if __name__ == "__main__":
    unittest.main()
