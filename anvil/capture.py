"""Screenshot capture for rendered design review.

Serves a project's web page and captures screenshots at defined breakpoints
for design review evidence. Implements all security constraints from the
rendered-design-review spec.
"""

import json
import os
import shlex
import signal
import socket
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple


DEFAULT_BREAKPOINTS = [
    {"width": 390, "height": 844},   # phone
    {"width": 1440, "height": 900},  # desktop
]


class CaptureError(Exception):
    """Raised when screenshot capture fails."""
    pass


def _find_free_port() -> int:
    """Find a free port dynamically to prevent collisions."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


def _validate_static_root(project_dir: Path, static_root: str) -> Path:
    """Validate static_root stays within project directory.

    Security: prevents path traversal attacks like ../../../etc
    """
    given_project_dir = Path(project_dir)
    project_dir = given_project_dir.resolve()
    static_path = (project_dir / static_root).resolve()

    # Ensure the resolved path is within the project directory
    try:
        static_path.relative_to(project_dir)
    except ValueError:
        raise ValueError(
            f"static_root '{static_root}' escapes project directory. "
            "Path traversal is not allowed."
        )

    if not static_path.exists():
        raise ValueError(f"static_root directory does not exist: {static_path}")

    if not static_path.is_dir():
        raise ValueError(f"static_root is not a directory: {static_path}")

    # Return the path under the project directory as the caller gave it, so a
    # project reached through a symlink (macOS /var -> /private/var) gets back
    # a path in its own terms. Containment was checked on the resolved form.
    return given_project_dir / static_path.relative_to(project_dir)


def _validate_page_path(page_path: str) -> str:
    """Validate page_path for URL safety.

    Security: prevents URL injection like //evil.com or ../admin
    """
    if not page_path.startswith('/'):
        raise ValueError(
            f"page_path must start with '/': {page_path}"
        )

    if '..' in page_path:
        raise ValueError(
            f"page_path must not contain '..': {page_path}"
        )

    return page_path


def _validate_dimensions(width: int, height: int) -> Tuple[int, int]:
    """Validate breakpoint dimensions are within bounds.

    Security: prevents memory exhaustion from extreme values
    Bounds: width 1-7680 (8K), height 1-4320 (8K)
    """
    if not isinstance(width, int) or not isinstance(height, int):
        raise ValueError("width and height must be integers")

    if not (1 <= width <= 7680):
        raise ValueError(
            f"width must be between 1 and 7680, got {width}"
        )

    if not (1 <= height <= 4320):
        raise ValueError(
            f"height must be between 1 and 4320, got {height}"
        )

    return width, height


def _start_static_server(static_root: Path, port: int) -> subprocess.Popen:
    """Start a static HTTP server for the given directory.

    Security: uses shell=False to prevent command injection
    """
    # Use Python's built-in HTTP server with shell=False
    cmd = [
        'python3', '-m', 'http.server',
        str(port),
        '--directory', str(static_root),
        '--bind', '127.0.0.1'
    ]

    # Start new process group for proper cleanup
    # Use DEVNULL for stdout/stderr since we don't need the output
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setsid  # Create new process group
    )

    return process


def _start_serve_command(serve_command: str, project_dir: Path, port: Optional[int] = None) -> subprocess.Popen:
    """Start a custom serve command.

    Security: uses shell=False with shlex.split to prevent command injection
    """
    # Split command safely with shlex
    try:
        cmd_parts = shlex.split(serve_command)
    except ValueError as e:
        raise ValueError(f"Invalid serve_command: {e}")

    if not cmd_parts:
        raise ValueError("serve_command is empty after parsing")

    # Replace {port} placeholder if present
    if port is not None:
        cmd_parts = [part.replace('{port}', str(port)) for part in cmd_parts]

    # Start new process group for proper cleanup
    # Use DEVNULL for stdout/stderr since we don't need the output
    process = subprocess.Popen(
        cmd_parts,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=project_dir,
        preexec_fn=os.setsid  # Create new process group
    )

    return process


def _wait_for_server(url: str, timeout: int = 10) -> bool:
    """Wait for server to respond at the given URL.

    Returns True if server responds, False if timeout reached.
    """
    import urllib.request
    import urllib.error

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return True
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(0.5)

    return False


def _stop_server(process: subprocess.Popen) -> None:
    """Stop server process and all children.

    Security: uses os.killpg to clean up entire process group
    """
    if process.poll() is None:
        try:
            # Terminate the entire process group
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            # Wait for termination with timeout
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if doesn't terminate
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                process.wait(timeout=2)
        except (ProcessLookupError, OSError):
            # Process already terminated
            pass


def _capture_screenshot(
    url: str,
    width: int,
    height: int,
    output_path: Path,
    capture_impl=None
) -> None:
    """Capture a screenshot at the given dimensions.

    Args:
        url: Full URL to capture
        width: Viewport width in pixels
        height: Viewport height in pixels
        output_path: Path to save PNG file
        capture_impl: Optional injectable capture implementation for testing
    """
    if capture_impl is not None:
        # Use injected implementation for testing
        capture_impl(url, width, height, output_path)
        return

    # Real implementation using Playwright
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise CaptureError(
            "Playwright not installed. Install with: pip install playwright && playwright install chromium"
        )

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': width, 'height': height})
            page.goto(url, wait_until='networkidle', timeout=30000)
            page.screenshot(path=str(output_path), full_page=False)
            browser.close()
    except Exception as e:
        raise CaptureError(f"Screenshot capture failed: {e}")


def load_servable_config(project_dir: Path) -> Optional[Dict]:
    """Load servable configuration from project's anvil.yaml.

    Returns None if no servable configuration exists.

    Note: Despite the .yaml extension, anvil.yaml is JSON format.
    """
    project_dir = Path(project_dir)
    config_file = project_dir / "anvil.yaml"

    if not config_file.exists():
        return None

    try:
        with open(config_file, 'r') as f:
            config = json.load(f)

        if not config or 'servable' not in config:
            return None

        return config['servable']
    except Exception:
        return None


def capture_breakpoints(
    project_dir: Path,
    evidence_dir: Path,
    servable_config: Optional[Dict] = None,
    capture_impl=None
) -> Dict:
    """Capture screenshots at configured breakpoints.

    Args:
        project_dir: Project root directory
        evidence_dir: Directory to save screenshots
        servable_config: Servable configuration dict, or None to load from anvil.yaml
        capture_impl: Optional injectable capture implementation for testing

    Returns:
        Dict with:
        - success: bool
        - captures: list of {breakpoint, path} dicts
        - error: str if success=False
    """
    project_dir = Path(project_dir).resolve()
    evidence_dir = Path(evidence_dir)

    # Load config if not provided
    if servable_config is None:
        servable_config = load_servable_config(project_dir)

    if servable_config is None:
        return {
            "success": False,
            "captures": [],
            "error": "no servable configuration found"
        }

    # Create evidence directory with secure permissions
    evidence_dir.mkdir(parents=True, mode=0o700, exist_ok=True)

    # Extract configuration
    serve_command = servable_config.get('serve_command')
    static_root = servable_config.get('static_root')
    page_path = servable_config.get('page_path', '/')
    breakpoints = servable_config.get('breakpoints', DEFAULT_BREAKPOINTS)

    # Validate configuration
    if not serve_command and not static_root:
        return {
            "success": False,
            "captures": [],
            "error": "servable configuration must specify either serve_command or static_root"
        }

    try:
        # Validate page_path
        page_path = _validate_page_path(page_path)

        # Validate breakpoints
        validated_breakpoints = []
        for bp in breakpoints:
            width, height = _validate_dimensions(bp['width'], bp['height'])
            validated_breakpoints.append({'width': width, 'height': height})
        breakpoints = validated_breakpoints

        # Find free port
        port = _find_free_port()

        # Start server
        if static_root:
            # Validate and use static root
            static_path = _validate_static_root(project_dir, static_root)
            process = _start_static_server(static_path, port)
        else:
            # Use serve command
            process = _start_serve_command(serve_command, project_dir, port)

        try:
            # Build URL
            base_url = f"http://127.0.0.1:{port}"
            url = base_url + page_path

            # Wait for server
            if not _wait_for_server(base_url, timeout=10):
                return {
                    "success": False,
                    "captures": [],
                    "error": "server did not answer within timeout"
                }

            # Capture each breakpoint
            captures = []
            for bp in breakpoints:
                width = bp['width']
                height = bp['height']
                filename = f"screenshot-{width}x{height}.png"
                output_path = evidence_dir / filename

                try:
                    _capture_screenshot(url, width, height, output_path, capture_impl)
                    captures.append({
                        "breakpoint": f"{width}x{height}",
                        "path": str(output_path),
                        "width": width,
                        "height": height
                    })
                except CaptureError as e:
                    # Individual breakpoint failure
                    return {
                        "success": False,
                        "captures": captures,  # Return what we got so far
                        "error": f"capture failed for {width}x{height}: {e}"
                    }

            return {
                "success": True,
                "captures": captures,
                "error": None
            }

        finally:
            # Always stop server
            _stop_server(process)

    except ValueError as e:
        # Validation error
        return {
            "success": False,
            "captures": [],
            "error": f"configuration validation failed: {e}"
        }
    except Exception as e:
        # Unexpected error
        return {
            "success": False,
            "captures": [],
            "error": f"unexpected error: {e}"
        }


def packet_rendered_evidence_section(
    project_dir: Path,
    work_order_id: str,
    station_id: str
) -> str:
    """Generate rendered evidence section for design reviewer packets.

    Returns markdown section if captures exist for this run, empty string otherwise.
    If capture was attempted but failed, returns a section documenting the failure.
    """
    # Only design reviewers receive rendered evidence
    if station_id not in ("reviewer-design", "reviewer-ux"):
        return ""

    project_dir = Path(project_dir)
    run_dir = project_dir / "runs" / work_order_id
    evidence_dir = run_dir / "evidence"
    capture_failure_file = run_dir / "capture_failure.txt"

    # Check if capture failed (S3)
    if capture_failure_file.exists():
        try:
            failure_reason = capture_failure_file.read_text(encoding="utf-8").strip()
            lines = ["## Rendered evidence", ""]
            lines.append(
                f"**Note:** Rendered evidence could not be captured for this run. "
                f"Reason: {failure_reason}. "
                f"This review judged source only."
            )
            lines.append("")
            return "\n".join(lines)
        except Exception:
            pass

    # Check if servable was configured at all
    servable_config = load_servable_config(project_dir)
    if servable_config is None:
        # No servable configured, no section (S2)
        return ""

    if not evidence_dir.exists():
        return ""

    # Find screenshot files
    screenshots = sorted(evidence_dir.glob("screenshot-*.png"))

    if not screenshots:
        return ""

    # Build section with captures (S2)
    lines = ["## Rendered evidence", ""]
    lines.append("This run captured screenshots of the served project at the following breakpoints:")
    lines.append("")

    for screenshot in screenshots:
        rel_path = screenshot.relative_to(project_dir)
        lines.append(f"- `{screenshot.name}` at `{rel_path}`")

    lines.append("")

    # Station-specific review instructions
    if station_id == "reviewer-design":
        lines.append(
            "**Design review instruction:** When judging layout, scale, spacing, "
            "or visual hierarchy findings, cite the rendered evidence screenshots "
            "where applicable. The screenshots show what the page actually looks like "
            "at each breakpoint, not just what the source implies."
        )
    elif station_id == "reviewer-ux":
        lines.append(
            "**UX review instruction:** The screenshots show how users will experience "
            "the interface at each breakpoint. Use them to judge flow visibility, "
            "interactive element accessibility, focus states, and copy clarity as rendered. "
            "When citing findings, reference the rendered evidence where applicable."
        )

    lines.append("")

    return "\n".join(lines)
