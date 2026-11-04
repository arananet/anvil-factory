Spec revision complete. I've clarified the guide designation requirements to address the implementation gaps from GATE LOOPBACK 2:

**Key revisions:**

1. **The guide designation section** now explicitly states:
   - The Station dataclass must preserve `guided` and `designation` fields
   - The registry loader reads these from station.json alongside existing fields
   - The runner wires this to runtime by checking `guided` and applying the design model from the routing policy (via `get_design_model_from_routing`) instead of the station's default model field

2. **S10 scenario** now verifies three things:
   - station.json files have `guided: true` and `designation` strings
   - Station dataclass preserves these through registry loading
   - Runner actually applies the design model from routing when spawning guided stations

The revised spec makes explicit what was implicit: the designation isn't just catalog metadata—it's runtime wiring that must flow through the dataclass and be enforced by the runner.

Output written to: `runs/wo-gh-11/spec-writer.output.md`
