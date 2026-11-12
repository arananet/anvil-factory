#!/usr/bin/env python3
"""Runtime dispatcher: runs a station on the Claude runtime for its configured model.

This dispatcher reads ANVIL_CONFIGURED_MODEL from the environment (set by the
runner) and dispatches to the appropriate runtime:

- Anthropic models (claude-opus-5-5, claude-sonnet-5-5): claude_station.py
- Any other model: fails loudly with no fallback

The configured model and executed model are the same by construction because
the runtime receives the model from the runner and has no other source.

Exit codes:
- 0: success
- 1: unknown model family (loud failure, no fallback)
- other: propagated from underlying runtime
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def _self_report(output_path, model):
    """Self-report the model actually dispatched through the existing channel:
    a JSON object with a "model" field in the runtime output."""
    line = json.dumps({"model": model})
    try:
        path = Path(output_path)
        if path.exists():
            text = path.read_text(encoding="utf-8")
            sep = "" if text.endswith("\n") or not text else "\n"
            path.write_text(text + sep + line + "\n", encoding="utf-8")
    except OSError:
        pass
    print(line)


def dispatch_runtime(packet_path, output_path, configured_model):
    """Dispatch to appropriate runtime based on model family.

    Args:
        packet_path: Path to station packet
        output_path: Path for output
        configured_model: Model identifier from ANVIL_CONFIGURED_MODEL

    Returns:
        Exit code from runtime
    """
    if not configured_model:
        print("dispatch_station: ANVIL_CONFIGURED_MODEL not set", file=sys.stderr)
        return 1

    tools_dir = Path(__file__).parent

    # Dispatch by model family
    if configured_model in ["claude-opus-5-5", "claude-sonnet-5-5"]:
        # Anthropic models -> Claude runtime
        runtime = tools_dir / "claude_station.py"
        env = os.environ.copy()
        env["ANVIL_CONFIGURED_MODEL"] = configured_model

        try:
            proc = subprocess.run(
                [sys.executable, str(runtime), str(packet_path), str(output_path)],
                env=env,
                capture_output=True,
                text=True
            )
            # Forward output
            if proc.stdout:
                print(proc.stdout, end="")
            if proc.stderr:
                print(proc.stderr, end="", file=sys.stderr)
            if proc.returncode == 0:
                _self_report(output_path, configured_model)
            return proc.returncode

        except Exception as e:
            print(f"dispatch_station: failed to invoke Claude runtime: {e}", file=sys.stderr)
            return 2

    else:
        # Unknown model - loud failure, no fallback
        print(f"dispatch_station: unknown model '{configured_model}'. " +
              f"Known models: claude-opus-5-5, claude-sonnet-5-5",
              file=sys.stderr)
        return 1


def main():
    if len(sys.argv) != 3:
        print("usage: dispatch_station.py <packet> <output>", file=sys.stderr)
        return 64

    packet_path = sys.argv[1]
    output_path = sys.argv[2]
    configured_model = os.environ.get("ANVIL_CONFIGURED_MODEL")

    return dispatch_runtime(packet_path, output_path, configured_model)


if __name__ == "__main__":
    sys.exit(main())
