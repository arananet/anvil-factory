import json
from pathlib import Path

REQUIRED = {"id", "name", "stack", "structure", "first_specs"}


def load_blueprints(directory):
    root = Path(directory)
    if not root.is_dir():
        raise ValueError(f"Blueprints directory not found: {directory}")
    blueprints = {}
    for file in sorted(root.glob("*.json")):
        data = json.loads(file.read_text(encoding="utf-8"))
        missing = REQUIRED - set(data)
        if missing:
            raise ValueError(f"Blueprint {file.name} is missing fields: {sorted(missing)}")
        if data["id"] in blueprints:
            raise ValueError(f"Duplicate blueprint id: {data['id']}")
        if not data["first_specs"]:
            raise ValueError(f"Blueprint {data['id']} must name at least one first spec")
        blueprints[data["id"]] = data
    if not blueprints:
        raise ValueError(f"No blueprints found in {directory}")
    return blueprints


def get_blueprint(directory, blueprint_id):
    blueprints = load_blueprints(directory)
    if blueprint_id not in blueprints:
        raise ValueError(f"Unknown blueprint: {blueprint_id}. Known: {sorted(blueprints)}")
    return blueprints[blueprint_id]
