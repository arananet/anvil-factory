#!/usr/bin/env python3
"""Refresh public project usage snapshots with GitHub CLI; makes no model calls."""
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from anvil.telemetry import public_report
from anvil.statuspage import generate_status_page


def github(path):
    proc = subprocess.run(["gh", "api", "--method", "GET", path],
                          capture_output=True, text=True, timeout=60)
    if proc.returncode:
        raise RuntimeError(f"GitHub report read failed for {path}: exit {proc.returncode}")
    return json.loads(proc.stdout)


def sync_project(entry, destination):
    repository = entry["repository"]
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repository) or not re.fullmatch(r"[a-z0-9_-]+", entry["id"]):
        raise ValueError("Invalid project catalog identifier")
    metadata = github(f"repos/{repository}")
    if metadata.get("private"):
        raise ValueError(f"Private repository {repository} cannot be imported into the public status site")
    branch = quote(metadata["default_branch"], safe="")
    tree = github(f"repos/{repository}/git/trees/{branch}?recursive=1")
    if tree.get("truncated"):
        raise ValueError(f"GitHub returned an incomplete tree for {repository}")
    files = [item for item in tree.get("tree", []) if item.get("type") == "blob" and
             item["path"].startswith("runs/") and (item["path"].endswith("/report.json") or
             ("/history/" in item["path"] and item["path"].endswith(".json")))]

    def read_report(item):
        blob = github(f"repos/{repository}/git/blobs/{item['sha']}")
        report = json.loads(base64.b64decode(blob["content"]))
        if not isinstance(report, dict) or "work_order_id" not in report:
            raise ValueError(f"Invalid report: {repository}/{item['path']}")
        return public_report(report)

    with ThreadPoolExecutor(max_workers=4) as pool:
        reports = list(pool.map(read_report, files))
    root = destination / entry["id"]
    root.mkdir(parents=True, exist_ok=True)
    (root / "anvil.json").write_text(json.dumps({"project": entry["name"]}, indent=2) + "\n", encoding="utf-8")
    snapshot = {"schema": "anvil/project-reports@1", "repository": repository,
                "source_tree": tree["sha"], "imported_at": datetime.now(timezone.utc).isoformat(),
                "reports": reports}
    (root / "report_exports.json").write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    print(f"{entry['name']}: {len(reports)} reports imported")
    return root


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", default=str(ROOT / "project-reports" / "catalog.json"))
    parser.add_argument("--out", default=str(ROOT / "project-reports"))
    parser.add_argument("--status-out", default=str(ROOT / "status"))
    args = parser.parse_args(argv)
    entries = json.loads(Path(args.catalog).read_text(encoding="utf-8"))["projects"]
    roots = [sync_project(entry, Path(args.out)) for entry in entries]
    summary = generate_status_page(ROOT, args.status_out, projects=roots)
    print(f"Status page: {summary['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
