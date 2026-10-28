import json
from dataclasses import dataclass, field
from pathlib import Path
from .config import default_model

KINDS = {"deterministic", "agent", "gate"}

@dataclass
class Station:
    id: str
    name: str
    kind: str
    inputs: list = field(default_factory=list)
    outputs: list = field(default_factory=list)
    description: str = ""
    path: str = ""
    prompt: str = ""
    context: list = field(default_factory=list)
    model: str = ""
    prompt_path: str = ""
    tools: list = field(default_factory=list)

class StationRegistry:
    def __init__(self, stations):
        self._stations = {s.id: s for s in stations}
    def get(self, station_id):
        return self._stations[station_id]
    def ids(self):
        return sorted(self._stations.keys())
    def all(self):
        return [self._stations[k] for k in self.ids()]
    def __len__(self):
        return len(self._stations)
    def __contains__(self, station_id):
        return station_id in self._stations

def load_registry(stations_dir):
    root = Path(stations_dir)
    if not root.is_dir():
        raise ValueError(f"Stations directory not found: {root}")
    stations = []
    for folder in sorted(p for p in root.iterdir() if p.is_dir()):
        manifest = folder / "station.json"
        if not manifest.exists():
            raise ValueError(f"Missing station.json in {folder}")
        data = json.loads(manifest.read_text(encoding="utf-8"))
        for field_name in ("id", "name", "kind"):
            if field_name not in data:
                raise ValueError(f"Station manifest missing field {field_name}: {manifest}")
        if data["kind"] not in KINDS:
            raise ValueError(f"Invalid station kind {data['kind']} in {manifest}")
        if data["id"] != folder.name:
            raise ValueError(f"Station id {data['id']} does not match folder {folder.name}")
        prompt = ""
        prompt_file = folder / "PROMPT.md"
        if data["kind"] == "agent":
            if not prompt_file.exists():
                raise ValueError(f"Agent station {data['id']} is missing PROMPT.md")
            prompt = prompt_file.read_text(encoding="utf-8")
        elif prompt_file.exists():
            prompt = prompt_file.read_text(encoding="utf-8")
        stations.append(Station(id=data["id"], name=data["name"], kind=data["kind"],
                                inputs=list(data.get("inputs", [])), outputs=list(data.get("outputs", [])),
                                description=data.get("description", ""), path=str(folder), prompt=prompt,
                                context=list(data.get("context", ["brain/project.md", ".openspec/specs/"])),
                                model=str(data.get("model", default_model(data["id"]))),
                                prompt_path=str(data.get("prompt", f"stations/{data['id']}/PROMPT.md")),
                                tools=list(data.get("tools", []))))
    return StationRegistry(stations)

load_stations = load_registry
