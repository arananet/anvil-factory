# Decision 0002: Headless Blender for modeled 3D assets

Status: accepted
Adopted: 2026-10-31, by the owner's order.

## Decision
Headless Blender is a standing production tool of the factory. Any work order in any project may use it, with a pinned Blender version and deterministic Python build scripts, when the deliverable needs modeled 3D assets, scenes or renders. Exports must be byte reproducible across runs.

## Why
Primitive procedural geometry reads as generic blocks when a deliverable represents a real product. A modeled asset built from the owner's approved reference carries the product's silhouette, proportions and materials. In the Sentia take apart product model order, the owner rejected the earlier procedural build as blocks that did not represent the product, and the Blender built asset then passed reviewer-design's same product identity test against that reference.

## Consequences
Build scripts are run inputs and are committed with the run that uses them. Each run records the Blender version it used. Renders against the owner's approved reference are the fidelity evidence, judged by reviewer-design with the same product test. Asset payloads carry a budget stated in the work order's spec, and the run reports the measured size against that budget.
