"""wo-gh-31: tier map totality regression.

Maps to model-tier-map R1 (review-cheap resolves to claude-sonnet-5-5),
R2 (every label in routing's vocabulary resolves to a concrete model) and
R3 (unmapped non-concrete values still pass through for the dispatcher to reject).
"""
import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from anvil import routing
from anvil.config import CONCRETE_MODELS, MODEL_TIER_MAP, resolve_model


def routing_vocabulary():
    labels = set(routing.MODEL_HIERARCHY)
    labels.update(routing.MODEL_POLICY.values())
    with tempfile.TemporaryDirectory() as d:
        cfg = routing.load_routing_config(Path(d))
    labels.update(cfg["models"].values())
    labels.update(cfg.get("policy_ceilings", {}).values())
    return labels


class TierMapTotality(unittest.TestCase):
    def test_review_cheap_resolves_to_sonnet(self):
        self.assertEqual(resolve_model("review-cheap"), "claude-sonnet-5-5")

    def test_vocabulary_includes_review_cheap(self):
        self.assertIn("review-cheap", routing_vocabulary())

    def test_every_routing_label_resolves_to_concrete_model(self):
        for label in sorted(routing_vocabulary()):
            with self.subTest(label=label):
                self.assertIn(resolve_model(label), CONCRETE_MODELS)

    def test_unmapped_value_still_passes_through(self):
        self.assertEqual(resolve_model("no-such-tier"), "no-such-tier")
        self.assertNotIn("no-such-tier", MODEL_TIER_MAP)


if __name__ == "__main__":
    unittest.main()
