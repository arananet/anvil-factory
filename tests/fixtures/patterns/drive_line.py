"""Drive one factory tree (the base ref or the working tree) for the proven patterns S9 comparison.

Usage: python -I drive_line.py <factory-root> <workdir> <init|run> [product-type]

init: runs `anvil init <workdir>/project --name Same` through that tree's CLI.
run: inits the same project with that tree's scaffold, appends the product
type line when given, runs sdlc-default with a fake runtime and prints JSON:
packets (station -> text the runtime received), events (kind sequence),
report_keys (sorted top level keys of report.json).
ANVIL_PATTERNS_DIR is set to a directory that does not exist.
"""
import contextlib
import io
import json
import os
import sys
from pathlib import Path

root, workdir, mode = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
product_type = sys.argv[4] if len(sys.argv) > 4 else None
sys.path.insert(0, str(root))
os.environ["ANVIL_PATTERNS_DIR"] = str(workdir / "no-patterns-here")
project = workdir / "project"

if mode == "init":
    from anvil import cli
    with contextlib.redirect_stdout(io.StringIO()):
        cli.main(["init", str(project), "--name", "Same"])
    sys.exit(0)

from anvil import runner  # noqa: E402
from anvil.model import WorkOrder  # noqa: E402
from anvil.pipeline import load_pipeline  # noqa: E402
from anvil.scaffold import init_project  # noqa: E402
from anvil.stations import load_registry  # noqa: E402

init_project(project, "Same")
if product_type:
    brain = project / "brain" / "project.md"
    brain.write_text(brain.read_text(encoding="utf-8") + f"\nProduct type: {product_type}\n", encoding="utf-8")


class Fake:
    name = "fake"

    def __init__(self):
        self.packets = {}

    def execute(self, text, station_id, **kwargs):
        self.packets.setdefault(station_id, text)
        output = json.dumps({"intake_outcome": {"outcome": "accepted"}}) if station_id == "intake" else "done"
        return {"output": output, "usage": {"input_tokens": 100, "output_tokens": 10}, "model": "claude-opus-5-5"}


reg = load_registry(root / "stations")
pipeline = load_pipeline(root / "pipelines" / "sdlc-default.json", known_stations=set(reg.ids()))
fake = Fake()
with contextlib.redirect_stdout(io.StringIO()):
    try:
        runner.run_pipeline(project, pipeline, WorkOrder(id="wo-pp", kind="feature", title="Same"),
                            registry=reg, executor=fake, max_loopbacks=0)
    except Exception:
        pass
run_dir = project / "runs" / "wo-pp"
events = [json.loads(l).get("event") for l in (run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
report = json.loads((run_dir / "report.json").read_text(encoding="utf-8"))
print(json.dumps({"packets": fake.packets, "events": events, "report_keys": sorted(report)}))
