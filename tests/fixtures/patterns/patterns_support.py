"""Shared fixtures for the proven patterns tests (spec: proven-patterns, work order wo-gh-50).

Everything is built in temporary directories at test time: fixture packs,
fixture git projects and fixture runs. Nothing here touches the factory's
own patterns/ directory.

Interface these tests pin where the spec leaves a name to the builder:
  ANVIL_PATTERNS_DIR  environment variable naming the patterns root that
      harvest, promote-pattern, check-patterns, init --pattern and the
      runner's selection read and write. Unset, the root is
      <factory root>/patterns. The inbox is <root>/inbox, a promoted pack is
      <root>/<id>, history is <root>/<id>/history/<version>.
  dead end "check" field: the path of the check file relative to the pack
      root, for example "guardrails/check_routes.py" (R1.3).
  the CLI is driven in process through anvil.cli.main(argv); a refusal is a
      return value or SystemExit code of 1, messages go to stdout or stderr
      (the tests read both).
  AUTHORITY below is the R6.1 sentence, carried verbatim by every packet
      section of R5.1.
"""
import contextlib
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PATTERNS_ENV = "ANVIL_PATTERNS_DIR"
WO = "wo-pp"
MODEL = "claude-opus-5-5"
AUTHORITY = ("The project's own brain, practices and specs win over a pattern on any conflict; "
             "a deviation from a pattern alone is not a finding.")

# A commit id shaped value built at run time (no literal in the source).
FAKE_COMMIT = "ab" * 20

STRUCTURE_MARKER = "Stage order: script, proof, master, pack."
STRUCTURE = (
    "# Explainer video line\n\n"
    f"{STRUCTURE_MARKER}\n\n"
    "Every stage is gated. Deterministic checks run before any reviewer.\n"
    "An independent reviewer is limited to one automatic revision, then the line stops for the owner.\n"
)
STAGES_MD = "# Stages\n\nscript, proof, master, pack\n"
CHECK_SCRIPT = "import sys\nprint('routes ok')\nsys.exit(0)\n"

DITHER = {
    "id": "dither-overlay",
    "route": "A dither overlay over every frame",
    "why": "Rejected by the owner: it reads as noise at phone size",
    "evidence": "review record of episode 2, 2026-11-18",
    "enforcement": "check",
    "check": "guardrails/check_routes.py",
}
CRT = {
    "id": "crt-curvature",
    "route": "A curved CRT frame around the picture",
    "why": "Rejected: it crops captions on small screens",
    "evidence": "run ep-03 review",
    "enforcement": "prompt",
}
FIGURES = [
    {"stage": "builder", "metric": "tokens", "value": 900000, "unit": "budget",
     "cache_read_weight": 0.1, "source": "runs/ep-04/usage.json"},
    {"stage": "intake", "metric": "tokens", "value": 300000, "unit": "raw",
     "source": "runs/ep-04/usage.json"},
    {"stage": "master", "metric": "cost_usd", "value": 1.25, "source": "cost ledger of ep-04"},
]
EVIDENCE = [{"kind": "published_artifact", "reference": "https://example.invalid/episode-1"}]


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def pattern_doc(pack_id, title="Explainer video line", version="1", product_types=("explainer-video",),
                success_evidence=None, blueprint=None, commits=None):
    return {
        "id": pack_id,
        "title": title,
        "version": version,
        "product_types": list(product_types),
        "blueprint": blueprint,
        "source": {"project": "fixture-explainer", "commits": list(commits or [FAKE_COMMIT])},
        "success_evidence": list(EVIDENCE if success_evidence is None else success_evidence),
    }


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def write_pack(patterns_root, dir_name, pack_id=None, version="1", product_types=("explainer-video",),
               title="Explainer video line", dead_ends=None, figures=None, structure=STRUCTURE,
               guardrails=None, promoted=True, forbidden_values=(), source_files=None,
               success_evidence=None, extra_files=None, pattern=None):
    """Write one complete, valid pack (unless arguments make it otherwise).

    promoted=True writes it at <root>/<dir_name> with provenance.json, source/
    and promotion.json; promoted=False writes it as a proposal under <root>/inbox.
    source_files maps a relative path to bytes; each is listed in provenance.json
    with its sha256. extra_files maps a path relative to the pack to bytes and is
    written last, without any bookkeeping (used to plant content rule breaches).
    """
    base = Path(patterns_root) / ("" if promoted else "inbox") / dir_name
    base.mkdir(parents=True, exist_ok=True)
    doc = pattern if pattern is not None else pattern_doc(
        pack_id or dir_name, title=title, version=version, product_types=product_types,
        success_evidence=success_evidence)
    write_json(base / "pattern.json", doc)
    (base / "structure.md").write_text(structure, encoding="utf-8")
    write_json(base / "dead-ends.json", [dict(DITHER), dict(CRT)] if dead_ends is None else dead_ends)
    write_json(base / "calibration.json", {"figures": [dict(f) for f in (FIGURES if figures is None else figures)]})
    for name, text in ({"check_routes.py": CHECK_SCRIPT} if guardrails is None else guardrails).items():
        target = base / "guardrails" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    sources = {"docs/stages.md": STAGES_MD.encode("utf-8")} if source_files is None else source_files
    files = []
    for rel, data in sources.items():
        target = base / "source" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        files.append({"path": rel, "commit": FAKE_COMMIT, "sha256": sha256(data)})
    write_json(base / "provenance.json", {
        "project": "/fixtures/explainer", "head": FAKE_COMMIT, "provenance": "outside_line",
        "provenance_note": "The source work was authored outside the line.",
        "forbidden_values": list(forbidden_values), "files": files,
    })
    if promoted:
        write_json(base / "promotion.json", {"by": "owner", "date": "2026-11-25", "version": doc.get("version")})
    for rel, data in (extra_files or {}).items():
        target = base / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return base


def snapshot(directory):
    """Every file under directory, relative path to bytes (empty when it does not exist)."""
    directory = Path(directory)
    if not directory.exists():
        return {}
    return {str(p.relative_to(directory)).replace(os.sep, "/"): p.read_bytes()
            for p in sorted(directory.rglob("*")) if p.is_file()}


def cli(argv, patterns_root):
    """Run anvil.cli.main(argv) in process with ANVIL_PATTERNS_DIR set. Returns (code, output)."""
    from anvil import cli as anvil_cli
    out, err = io.StringIO(), io.StringIO()
    with mock.patch.dict(os.environ, {PATTERNS_ENV: str(patterns_root)}):
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = anvil_cli.main([str(a) for a in argv])
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
    return (0 if code is None else code), out.getvalue() + err.getvalue()


GIT_ENV = {"GIT_AUTHOR_NAME": "Fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
           "GIT_COMMITTER_NAME": "Fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
           "GIT_AUTHOR_DATE": "2026-11-20T10:00:00+00:00", "GIT_COMMITTER_DATE": "2026-11-20T10:00:00+00:00"}


def git(project, *args):
    env = dict(os.environ, **GIT_ENV)
    done = subprocess.run(["git", *args], cwd=project, env=env, capture_output=True, text=True, check=True)
    return done.stdout.strip()


def make_git_project(tmp, manifest=None, design_tokens=None):
    """A finished project with two commits.

    Commit one adds docs/stages.md; commit two adds tools/check_routes.py and
    the harvest manifest (and design/brand.json when design_tokens is given).
    Returns the absolute project path.
    """
    project = Path(tmp) / "explainer"
    (project / "docs").mkdir(parents=True)
    (project / "tools").mkdir()
    git(project, "init", "-q")
    git(project, "config", "commit.gpgsign", "false")
    (project / "docs" / "stages.md").write_text(STAGES_MD, encoding="utf-8")
    (project / "README.md").write_text("# Explainer\n", encoding="utf-8")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "stages")
    (project / "tools" / "check_routes.py").write_text(CHECK_SCRIPT, encoding="utf-8")
    if design_tokens is not None:
        write_json(project / "design" / "brand.json", design_tokens)
    data = manifest if manifest is not None else {
        "files": ["docs/stages.md", "tools/check_routes.py"], "provenance": "outside_line"}
    if design_tokens is not None and "design_tokens" not in data:
        data = dict(data, design_tokens="design/brand.json")
    write_json(project / "anvil-harvest.json", data)
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "route check")
    return project.resolve()


def complete_proposal(inbox_pack, version="1", structure=STRUCTURE, success_evidence=None, dead_ends=None):
    """Fill every open field of a harvested proposal, keeping provenance.json and source/ as harvested."""
    inbox_pack = Path(inbox_pack)
    skeleton = json.loads((inbox_pack / "pattern.json").read_text(encoding="utf-8"))
    doc = pattern_doc(skeleton["id"], version=version, success_evidence=success_evidence,
                      commits=skeleton["source"]["commits"])
    write_json(inbox_pack / "pattern.json", doc)
    (inbox_pack / "structure.md").write_text(structure, encoding="utf-8")
    write_json(inbox_pack / "dead-ends.json", [dict(DITHER), dict(CRT)] if dead_ends is None else dead_ends)
    write_json(inbox_pack / "calibration.json", {"figures": [dict(f) for f in FIGURES]})
    (inbox_pack / "guardrails").mkdir(exist_ok=True)
    (inbox_pack / "guardrails" / "check_routes.py").write_text(CHECK_SCRIPT, encoding="utf-8")
    return inbox_pack


class FakeRuntime:
    """Scripted fake runtime: accepts intake, records the first packet each station receives."""
    name = "fake"

    def __init__(self):
        self.calls = []
        self.packets = {}

    def execute(self, text, station_id, **kwargs):
        self.calls.append(station_id)
        self.packets.setdefault(station_id, text)
        output = "done"
        if station_id == "intake":
            output = json.dumps({"intake_outcome": {"outcome": "accepted"}})
        return {"output": output, "usage": {"input_tokens": 100, "output_tokens": 10}, "model": MODEL}


def make_project(tmp, product_type=None, station_budgets=None, name="Pattern demo"):
    """A fresh project at <tmp>/project (removed first, so every run starts from the same bytes)."""
    from anvil.scaffold import init_project
    path = Path(tmp) / "project"
    if path.exists():
        shutil.rmtree(path)
    project = init_project(path, name)
    if product_type is not None:
        brain = project / "brain" / "project.md"
        brain.write_text(brain.read_text(encoding="utf-8") + f"\nProduct type: {product_type}\n", encoding="utf-8")
    if station_budgets is not None:
        config = json.loads((project / "anvil.yaml").read_text(encoding="utf-8"))
        config["station_budgets"] = dict(station_budgets)
        (project / "anvil.yaml").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    return project


def run_line(tmp, patterns_root, product_type=None, station_budgets=None):
    """Run sdlc-default on a fresh project with a fake runtime.

    Returns a dict: packets (station -> text the runtime received), files
    (station -> bytes of runs/<wo>/<station>.packet.md), report (report.json),
    events (the event kind sequence), runtime (the fake).
    """
    from anvil import runner as anvil_runner
    from anvil.model import WorkOrder
    from anvil.pipeline import load_pipeline
    from anvil.stations import load_registry
    project = make_project(tmp, product_type=product_type, station_budgets=station_budgets)
    reg = load_registry(ROOT / "stations")
    pipeline = load_pipeline(ROOT / "pipelines" / "sdlc-default.json", known_stations=set(reg.ids()))
    runtime = FakeRuntime()
    with mock.patch.dict(os.environ, {PATTERNS_ENV: str(patterns_root)}):
        try:
            anvil_runner.run_pipeline(project, pipeline, WorkOrder(id=WO, kind="feature", title="Pattern demo"),
                                      registry=reg, executor=runtime, max_loopbacks=0)
        except Exception:
            pass
    run_dir = project / "runs" / WO
    report_path = run_dir / "report.json"
    if not report_path.is_file():
        raise AssertionError("the run left no report.json")
    events = []
    events_path = run_dir / "events.jsonl"
    if events_path.is_file():
        for line in events_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                events.append(json.loads(line).get("event"))
    return {
        "packets": dict(runtime.packets),
        "files": {p.name[: -len(".packet.md")]: p.read_bytes() for p in sorted(run_dir.glob("*.packet.md"))},
        "report": json.loads(report_path.read_text(encoding="utf-8")),
        "events": events,
        "runtime": runtime,
        "project": project,
    }


def step(report, station_id):
    for entry in report.get("steps") or []:
        if entry.get("station") == station_id:
            return entry
    raise AssertionError(f"no step for {station_id}")
