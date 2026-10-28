import json
from pathlib import Path
from .brain import ensure_brain_memory
from .config import render_anvil_yaml

STATION_IDS = ["intake","spec-writer","test-writer","builder","reviewer-spec","reviewer-security","reviewer-tests","reviewer-architecture","approver","triage-human","deployer","observer","scout","blueprint","brief-writer","researcher","writer","media-producer","reviewer-facts","reviewer-voice","reviewer-platform","reviewer-brand","publisher","supervisor"]
TEMPLATE = """# {title}

Status: draft
Slug: {slug}

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
TODO: state the problem and the outcome in plain language.

## Requirements
- TODO: first requirement

## Scenarios

### Scenario: First scenario
- S1: Given a starting state, when the action runs, then the expected result holds.
"""

def init_project(path, name):
    root = Path(path)
    root.mkdir(parents=True, exist_ok=True)
    (root / ".openspec" / "specs").mkdir(parents=True, exist_ok=True)
    (root / ".openspec" / "config.yaml").write_text("project: " + name + "\nversion: 1\nspecs_dir: .openspec/specs\n", encoding="utf-8")
    (root / "brain" / "decisions").mkdir(parents=True, exist_ok=True)
    (root / "brain" / "project.md").write_text(f"# {name}\n\nProject brain for {name}. Principles, context and decisions live here.\n", encoding="utf-8")
    (root / "brain" / "glossary.md").write_text("# Glossary\n\n- Work order: a single unit of work moving down the line.\n", encoding="utf-8")
    (root / "brain" / "worklog.md").write_text("# Worklog\n\n", encoding="utf-8")
    ensure_brain_memory(root)
    (root / "tests").mkdir(exist_ok=True)
    (root / "reviews").mkdir(exist_ok=True)
    (root / "anvil.json").write_text(json.dumps({"pipeline": "sdlc-default", "project": name}, indent=2) + "\n", encoding="utf-8")
    (root / "anvil.yaml").write_text(render_anvil_yaml(STATION_IDS), encoding="utf-8")
    (root / "README.md").write_text(f"# {name}\n\nProject created with ANVIL. Pipeline: sdlc-default (see anvil.json). Station settings: see anvil.yaml. Specs live under .openspec/specs/.\n", encoding="utf-8")
    note = root / "PIPELINES.md"
    note.write_text("# Pipelines\n\nThis project uses the sdlc-default pipeline by default. Copy a pipeline JSON into pipelines/ to compose a different line from the same stations.\n", encoding="utf-8")
    return root

def scaffold_spec(project, slug, title):
    root = Path(project)
    spec_dir = root / ".openspec" / "specs" / slug
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_file = spec_dir / "spec.md"
    # Prefer the factory template when available next to the package
    factory_template = Path(__file__).resolve().parent.parent / "templates" / "spec.md"
    if factory_template.exists():
        text = factory_template.read_text(encoding="utf-8").replace("{{TITLE}}", title).replace("{{SLUG}}", slug)
    else:
        text = TEMPLATE.format(title=title, slug=slug)
    spec_file.write_text(text, encoding="utf-8")
    return spec_file


def new_project(path, name, blueprint, idea=""):
    """Greenfield entry: scaffold a project from zero around a blueprint.

    blueprint is a catalog dict (see anvil/blueprints.py). The idea brief
    seeds the brain, BLUEPRINT.md records the starting shape, anvil.json
    points at the greenfield pipeline, and the first spec is scaffolded
    so the line can start at spec-writer, not at a blank page.
    """
    root = init_project(path, name)
    lines = [f"# Blueprint: {name}", "", f"Catalog blueprint: {blueprint['name']} ({blueprint['id']})", ""]
    if idea:
        lines += ["## Idea", idea, ""]
    lines += ["## Stack"] + [f"- {item}" for item in blueprint["stack"]]
    lines += ["", "## Structure"] + [f"- {item}" for item in blueprint["structure"]]
    lines += ["", "## First specs"] + [f"- {slug}" for slug in blueprint["first_specs"]]
    if blueprint.get("notes"):
        lines += ["", "## Notes", blueprint["notes"]]
    lines += ["", "Pipeline: greenfield. Next station after intake is blueprint review of this file, then spec-writer."]
    (root / "BLUEPRINT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if idea:
        brain = root / "brain" / "project.md"
        brain.write_text(brain.read_text(encoding="utf-8") + f"\n## Idea\n{idea}\n", encoding="utf-8")
    (root / "anvil.json").write_text(json.dumps({"pipeline": "greenfield", "project": name, "blueprint": blueprint["id"]}, indent=2) + "\n", encoding="utf-8")
    for slug in blueprint["first_specs"]:
        scaffold_spec(root, slug, slug.replace("-", " ").title())
    return root
