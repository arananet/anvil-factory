import json
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class Pipeline:
    name: str
    stages: list = field(default_factory=list)
    def topological_order(self):
        order = []
        for stage in self.stages:
            if "station" in stage:
                order.append(stage["station"])
            elif "parallel" in stage:
                order.extend(stage["parallel"])
            else:
                raise ValueError(f"Invalid stage: {stage}")
        return order
    def validate(self, known_stations=None):
        if not self.stages:
            raise ValueError("Pipeline is empty: at least one stage is required")
        seen = []
        for stage in self.stages:
            ids = []
            if "station" in stage:
                ids = [stage["station"]]
            elif "parallel" in stage:
                group = stage["parallel"]
                if len(group) < 2:
                    raise ValueError("Parallel group must contain at least 2 stations")
                ids = list(group)
            else:
                raise ValueError(f"Invalid stage: {stage}")
            for sid in ids:
                if known_stations is not None and sid not in known_stations:
                    raise ValueError(f"Unknown station: {sid}")
                if sid in seen:
                    raise ValueError(f"Duplicate station: {sid}")
                seen.append(sid)
        return True

def load_pipeline(path, known_stations=None):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, list):
        name, stages = Path(path).stem, data
    else:
        name, stages = data.get("name", Path(path).stem), data.get("stages", [])
    pipe = Pipeline(name=name, stages=stages)
    pipe.validate(known_stations=known_stations)
    return pipe

def validate_pipeline(path, known_stations=None):
    return load_pipeline(path, known_stations=known_stations)
