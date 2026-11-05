# Quality Charter for Visual Deliverables

Version: 1.0.0  
Status: Active  
Amended: 2026-10-30 (Set consistency requirement added)

## Purpose

This charter states the production quality bar for visual deliverables from the factory. Output the owner could ship as the product's public face without apology, not a sketch of it.

## Scope

This charter applies to:
- Visual deliverables: product renders, interface designs, illustrations, game assets
- Stations that generate imagery: builder, media-producer, brief-writer
- Stations that review imagery: reviewer-design, reviewer-ux

This charter does not apply to:
- API implementations, data processing, security work (no visual output)
- Documentation, internal tools (not customer-facing deliverables)

## Observable Criteria by Product Type

### Physical Consumer Products

For physical consumer products (devices, furniture, packaged goods), the criteria are:

#### Materials
Surfaces read as the materials the product is actually made of. Metal reads as metal, glass as glass, fabric as fabric, plastic as plastic. The surface finish, reflectivity, and texture match the material properties.

#### Light
One coherent light story, with shadows and reflections that agree with it. The direction, quality (hard or soft), and color temperature of the light are consistent. Shadows fall where the light source dictates. Reflections show the environment the light story implies.

#### Contact
Objects meet skin, surfaces and each other the way physical things do, with weight and pressure where they touch. A device resting on a surface makes contact, doesn't float. A hand holding a product shows the grip, the pressure points, the way fingers wrap. Cables drape, they don't hover.

#### Scale
The object's size reads true against its context and against human anatomy where anatomy is in frame. A phone in a hand reads phone-sized, not tablet-sized. A chair next to a table has the right height relationship. An object on a desk doesn't look miniaturized or giant.

### Game and Illustration Products

For games and illustrations, the charter does not impose the physical product criteria above. Instead:

- The project's design system or the work order must state the product's own visual standard in observable form: what materials, light, contact, and scale must read as for that product
- The stated standard is the bar for the run
- The review applies the stated standard, not photorealism

Example stated standard for a game:
> Materials: Cel-shaded with visible hand-painted texture strokes  
> Light: Single dominant directional light with minimal ambient  
> Contact: Stylized contact shadows, not physically accurate  
> Scale: Characters scaled to fit 16:9 viewport, not anatomically precise

## Composition Order

When multiple sources define quality (project anchors, design system, this charter), the order of authority is:

1. **Project reference anchors**: The owner's own pictures of the bar for this project (stored in design/reference/)
2. **Project design system**: The project's documented quality bars, verified brain learnings
3. **Charter floor**: The criteria in this document

If a project's anchors show deliberately stylized work, the stylized reading is the bar, and this charter's realism criteria do not override it.

Anything below the charter floor is a named floor gap in the review record, never silently waived.

## Station Duties

### Generating Stations

A station that produces imagery (builder, media-producer, brief-writer) must:

1. Verify each output against the run's anchors and charter criteria before the review step runs
2. Record the comparison in run evidence per output:
   - The anchor compared against (or charter floor if no anchors)
   - The criteria checked
   - The gaps found, or an explicit statement that no gaps were found at the charter bar
3. Regenerate outputs judged below the bar within the run's normal loopback discipline, or carry the shortfall into the recorded comparison as an open gap
4. Never silently forward imagery it has not looked at

The recorded self-comparison is run evidence, not a verdict. Reviewers judge independently.

### Reviewing Stations

reviewer-design and reviewer-ux (once it exists) must:

1. Compare the output against the run's anchors and charter criteria for the product type
2. Record the comparison in a separate quality section of the review, alongside compliance
3. Name specific gaps by category (materials, light, scale, contact for physical products; stated criteria for games/illustrations), each measured against the anchor or charter criterion it falls short of
4. Never return a generic quality verdict—cite the specific criteria and anchors

A deliverable can pass design system compliance and fail quality in the same run. Both verdicts are recorded distinctly.

### For Sets of Related Deliverables

When a work order produces a set of related deliverables (multiple images of one product, one character across scenes):

1. The work order designates one canonical identity reference inside the set
2. The work order enumerates the identity traits the set must hold constant (finish, detail colors, mounting, proportions, markings for physical products; equivalents for other types)
3. The generating stations produce the remaining assets from that reference
4. reviewer-design runs a same-subject test: every asset compared against the identity reference on each enumerated trait
5. Any divergence fails the quality judgment, with the divergent asset and trait named, even when every asset individually passes the anchor comparison

The same-subject test is part of the quality section, not a separate verdict.

## Runs Without Anchors

A visual run with no anchors available proceeds under the charter floor alone. The run report carries a visible warning that the run had no reference anchors. The absence is recorded in the report's warnings, never silent.

## Runs Without Visual Surfaces

A run whose surfaces include no visual work (no imagery generated, no interface under review) never receives this charter in any packet. The report makes no mention of the quality standard.

## Amendment History

- **2026-10-30**: Added set consistency requirement (same-subject test, identity reference, enumerated traits) as S7 in the spec
- **2026-10-25**: Initial charter established

## References

- Spec: .openspec/specs/quality-standard/spec.md
- Design system scaffolding: anvil/design.py
- Quality module: anvil/quality.py
- Tests: tests/test_quality_standard.py
