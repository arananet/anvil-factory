import json
from collections import Counter
from pathlib import Path

from .brain import LEARNINGS_HEADER
from .config import render_anvil_yaml
from .scaffold import STATION_IDS
from .design import scaffold_design_system

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}


def _files(root):
    for path in sorted(root.rglob("*")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file():
            yield path


def analyze_project(path):
    """Read only analysis of an existing project. Writes nothing."""
    root = Path(path)
    if not root.is_dir():
        raise ValueError(f"Project not found: {path}")
    names = {p.name for p in root.iterdir()}
    stack = []
    if "pyproject.toml" in names or "setup.py" in names or "requirements.txt" in names:
        stack.append("python")
    if "package.json" in names:
        stack.append("node")
    if "wrangler.toml" in names or "wrangler.json" in names or "wrangler.jsonc" in names:
        stack.append("cloudflare-worker")
    if "index.html" in names and not stack:
        stack.append("static")
    files = list(_files(root))
    has_tests = any(
        ("test" in p.name.lower() or "tests" in p.parts) and p.suffix in (".py", ".js", ".ts")
        for p in files
    )
    return {
        "name": root.name,
        "stack": stack,
        "has_readme": any(n.lower().startswith("readme") for n in names),
        "has_tests": has_tests,
        "has_specs": (root / ".openspec" / "specs").is_dir(),
        "has_ci": (root / ".github" / "workflows").is_dir(),
        "has_brain": (root / "brain").is_dir(),
        "already_onboarded": (root / "anvil.json").exists(),
        "file_types": dict(Counter(p.suffix for p in files if p.suffix).most_common(5)),
        "file_count": len(files),
    }


def _write_if_missing(root, rel, content, created, kept):
    target = root / rel
    if target.exists():
        kept.append(rel)
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    created.append(rel)


def onboard_project(path, name=None):
    """Bring an existing project onto the line. Never overwrites a file."""
    root = Path(path)
    report = analyze_project(root)
    if report["already_onboarded"]:
        raise ValueError(f"{root} is already onboarded (anvil.json exists). Refusing to onboard twice.")
    name = name or report["name"]
    created, kept = [], []

    readme_excerpt = ""
    for candidate in sorted(root.glob("README*")):
        lines = [ln.strip() for ln in candidate.read_text(encoding="utf-8", errors="replace").splitlines() if ln.strip()]
        readme_excerpt = " ".join(lines[1:3]) if len(lines) > 1 else ""
        break

    stack_line = ", ".join(report["stack"]) if report["stack"] else "not detected"
    brain = (
        f"# {name}\n\nOnboarded onto ANVIL from an existing codebase. "
        f"Detected stack: {stack_line}.\n"
    )
    if readme_excerpt:
        brain += f"\nWhat the project says about itself: {readme_excerpt}\n"
    brain += "\nDecisions made before onboarding live in the project history, not here. New decisions go to brain/decisions/ from now on.\n"
    _write_if_missing(root, "brain/project.md", brain, created, kept)
    _write_if_missing(root, "brain/glossary.md", "# Glossary\n\n- Baseline spec: the draft spec written at onboarding that describes the project as found.\n", created, kept)
    _write_if_missing(root, "brain/worklog.md", "# Worklog\n\n", created, kept)
    _write_if_missing(root, "brain/learnings.md", LEARNINGS_HEADER, created, kept)
    (root / "brain" / "decisions").mkdir(parents=True, exist_ok=True)
    (root / "brain" / "inbox").mkdir(parents=True, exist_ok=True)
    _write_if_missing(root, ".openspec/config.yaml", f"project: {name}\nversion: 1\nspecs_dir: .openspec/specs\n", created, kept)

    baseline = (
        f"# Existing Baseline: {name}\n\nStatus: draft\nSlug: existing-baseline\n\n"
        "## Roles\n- implementer: builds the change described here\n- reviewer: checks the change against this spec\n"
        "- qa: checks the scenarios below with tests\n- product_owner: owns the purpose and accepts the result\n\n"
        "## Purpose\nThis draft spec records the project as found at onboarding, so future work has a baseline to be reviewed against. "
        "It was generated from analysis, not from intent: a human should confirm or replace it.\n\n"
        "## Requirements\n"
        f"- Stack as found: {stack_line}.\n"
        f"- Tests present at onboarding: {'yes' if report['has_tests'] else 'no'}.\n"
        f"- CI present at onboarding: {'yes' if report['has_ci'] else 'no'}.\n\n"
        "## Scenarios\n\n### Scenario: Baseline is reviewable\n"
        "- S1: Given this baseline, when a reviewer reads it, then they can tell what the project is, what stack it runs, and what was missing when it arrived.\n"
    )
    _write_if_missing(root, ".openspec/specs/existing-baseline/spec.md", baseline, created, kept)
    _write_if_missing(root, "anvil.yaml", render_anvil_yaml(STATION_IDS), created, kept)
    _write_if_missing(root, "anvil.json", json.dumps({"pipeline": "sdlc-default", "project": name, "mode": "brownfield", "onboarded": True}, indent=2) + "\n", created, kept)
    # Scaffold design system (never overwrites existing files)
    for design_file in scaffold_design_system(root):
        created.append(design_file)
    if (root / "README.md").exists():
        kept.append("README.md")

    gaps, suggested = [], []
    if not report["has_tests"]:
        gaps.append("No tests detected")
        suggested.append("Baseline tests: have the test-writer station cover the existing behavior before the first change (kind: task)")
    if not report["has_ci"]:
        gaps.append("No CI detected")
        suggested.append("Add CI: run the project tests and anvil check on every push (kind: task)")
    if not report["has_specs"]:
        gaps.append("No specs existed before onboarding")
        suggested.append("Confirm the baseline spec: review .openspec/specs/existing-baseline/spec.md and set it to approved or replace it (kind: task)")
    if not report["stack"]:
        gaps.append("Stack not detected")
        suggested.append("Name the stack: record the runtime and test command in brain/project.md (kind: task)")

    lines = [f"# Onboarding report: {name}", "", "## Detected", f"- Stack: {stack_line}",
             f"- Files scanned: {report['file_count']}", f"- Top file types: {report['file_types']}",
             f"- Tests: {'yes' if report['has_tests'] else 'no'}", f"- CI: {'yes' if report['has_ci'] else 'no'}", "",
             "## Created by onboarding"] + [f"- {rel}" for rel in created] + [
             "", "## Kept as found (never overwritten)"] + [f"- {rel}" for rel in kept] + [
             "", "## Gaps"] + ([f"- {g}" for g in gaps] or ["- None detected"]) + [
             "", "## Suggested first work orders"] + ([f"- {s}" for s in suggested] or ["- None. The line is ready for normal work orders."]) + [
             "", "Pipeline: sdlc-default (brownfield). The baseline spec is a draft until a human confirms it."]
    (root / "ONBOARDING.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    created.append("ONBOARDING.md")
    return {"analysis": report, "created": created, "kept": kept, "gaps": gaps, "suggested_work_orders": suggested}
