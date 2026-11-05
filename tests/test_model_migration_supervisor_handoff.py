"""wo-gh-29 round 4: the supervisor branch hands its runtime a concrete model (R10)."""
import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from anvil.stations import load_registry
from anvil.supervisor import supervise
from test_supervisor import stalled_project

ROOT = Path(__file__).resolve().parent.parent


class Recorder:
    kind = "command"

    def __init__(self):
        self.models = []

    def execute(self, packet_text, station_id, packet_path=None, output_path=None,
                cwd=None, configured_model=None):
        self.models.append(configured_model)
        return {"output": "no proposal", "usage": None}


class LegacyDouble:
    kind = "command"

    def execute(self, packet_text, station_id, packet_path=None, output_path=None, cwd=None):
        return {"output": "no proposal", "usage": None}


class TestSupervisorHandoff(unittest.TestCase):
    def test_supervisor_tier_label_resolved_at_hand_off(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = stalled_project(tmp)
            reg = load_registry(ROOT / "stations")
            ex = Recorder()
            supervise(proj, reg, executor=ex)
            # stations/supervisor/station.json says reasoning-strong
            self.assertEqual(ex.models, ["claude-opus-5-5"])

    def test_executor_without_model_parameter_still_called(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = stalled_project(tmp)
            result = supervise(proj, load_registry(ROOT / "stations"), executor=LegacyDouble())
            self.assertEqual(result["action"], "no_proposal")


if __name__ == "__main__":
    unittest.main()
