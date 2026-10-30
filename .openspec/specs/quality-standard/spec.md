# A Standing Quality Standard for Visual Deliverables

Status: approved
Slug: quality-standard

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
The factory can prove a visual deliverable complies with a project's design system and still ship work the owner rejects on sight: a product render that reads as a toy, surfaces that look like molded plastic where the product is metal and glass, light that could not fall that way in the physical world. Compliance has a checklist; quality, today, has none. This spec gives visual work a standing bar. A factory level charter states what production quality means per product type in observable terms. Reference anchors carry the owner's own pictures of that bar into every run. And the stations that generate and review imagery gain the duty to compare their work against the anchors and to say, in named terms, where it falls short, so a quality judgment becomes recorded evidence instead of taste asserted after the fact.

## Requirements

### The quality charter
- A factory level charter document for visual deliverables lives in the factory as a versioned standing document, written once and amended like any other factory contract. It states production quality as the default bar for visual deliverables: output the owner could ship as the product's public face without apology, not a sketch of it.
- The charter defines the bar per product type with observable criteria, criteria a reviewer can check by looking at the work, not adjectives. For a physical consumer product the criteria are: materials (surfaces read as the materials the product is actually made of), light (one coherent light story, with shadows and reflections that agree with it), contact (objects meet skin, surfaces and each other the way physical things do, with weight and pressure where they touch), and scale (the object's size reads true against its context and against human anatomy where anatomy is in frame).
- For a game or illustration product the charter does not impose the physical product criteria. It requires instead that the project's design system or the work order state that product's own standard in the same observable form (what its materials, light, contact and scale must read as), and that stated standard is the bar for the run. The bar is per type, never one global style, and the charter text says so.
- Pipelines that serve visual work include the charter by reference in the packets of the stations that generate or review imagery: the software pipeline when a run carries visual surfaces, and the content pipelines when a run produces imagery. Inclusion is by reference to the charter document, so an amendment to the charter reaches future runs without editing pipeline definitions.

### Reference anchors
- A project stores its reference anchors under design/reference/: owner supplied boards or prior approved outputs that show the bar for that project. The project design system scaffolding creates the directory alongside design/DESIGN.md, under the same never overwrite discipline as the rest of the design system: scaffolding and onboard create it when missing and never replace what a project already keeps there.
- A visual work order names its anchors by path under design/reference/, or inherits the project's stored set when it names none. The runner puts the anchors into the packets of the stations that generate or review imagery for the run. In runtimes whose packets can carry images, the images themselves are attached; where the packet is text only, the paths are the citation targets and the executing runtime is expected to open them.
- A visual run with no anchors available proceeds under the charter floor alone, and the run report carries a visible warning that the run had no reference anchors. The absence is a fact of record in the report's warnings, never a silent gap, and no part of the run may claim anchor based judgment for a run that had none.

### Reviewer duty
- reviewer-design's contract gains the anchor comparison duty for visual deliverables. Beyond design system compliance, the reviewer compares the output against the run's anchors and against the charter criteria for the product type, and judges the gaps. Where an anchor demands production realism, stylized, cartoon or toy-like output fails the quality judgment, and the recorded review names the specific gaps by category (materials, light, scale, contact), each measured against the anchor or charter criterion it falls short of, rather than returning a generic quality verdict.
- The anchor comparison is a separate, named section of reviewer-design's recorded review, alongside the design system compliance judgment. A deliverable can therefore pass compliance and fail quality in the same run, and the record shows both verdicts distinctly, so the approver and the human gate see which lens failed.
- reviewer-ux, once it exists in the catalog, carries the same duty for the experiential side of the comparison (whether the page or scene reads at the anchored quality in use, at real sizes and in sequence), under the same named gap categories where they apply, recorded in its own review section.

### Generation duty
- A station that produces imagery verifies each output it produces, by reading the output against the run's anchors and the charter criteria for the product type, before the review step runs. The comparison is recorded in the run evidence per output: the anchor compared against, the criteria checked, and the gaps found, or an explicit statement that no gaps were found at the charter bar.
- An output the generating station itself judges below the bar is regenerated within the run's normal loopback discipline, or the shortfall is carried into the recorded comparison as an open gap. The station never silently forwards imagery it has not looked at.
- The recorded self comparison is run evidence, not a verdict. Reviewers judge independently, a station's claim of no gaps does not bind them, and the approver weighs the reviewers' sections as it weighs any other review.

### Composition with design systems and learnings
- The order of authority for a visual deliverable is: the project's reference anchors first (the owner's pictures of this product), then the project's design system and its verified brain learnings, then the charter floor. On conflict the anchor wins: if an anchor shows a deliberately stylized product, the stylized reading is the bar for that project, and the charter's realism criteria for the type do not override it.
- The charter supplies the floor below which no visual deliverable may fall. A project may hold itself above the charter through its anchors and design system; a deliverable that falls below the charter floor is a named floor gap in the review record, never silently waived by any station.
- The charter is injected only where visual work happens. A run whose surfaces include no visual work (no imagery generated, no interface or scene under design review) never receives the charter in any packet, and its report makes no mention of the quality standard.

## Scenarios

### Scenario: Anchored realism makes a toy render fail the quality judgment
- S1: Given a fixture visual run for a physical consumer product whose anchors under design/reference/ show photoreal product boards, and an output render that reads stylized and toy-like, when reviewer-design's recorded review is checked against its contract, then a pass on the quality section is non conformant: the quality section must fail the deliverable, naming gap categories from materials, light, scale and contact, each measured against the cited anchor, even when the design system compliance section passes.

### Scenario: A visual run without anchors applies the floor and warns
- S2: Given a fixture visual run whose project stores no anchors under design/reference/ and whose work order names none, when the run executes, then the charter criteria for the product type are present in the generating and reviewing packets, reviewer-design judges against the charter floor alone, and the run report carries a visible warning that the run had no reference anchors.

### Scenario: A non visual run never receives the charter
- S3: Given a fixture run with no visual surfaces (no imagery generated and no interface or scene under design review), when its packets are built, then no packet contains the charter text or its criteria, and the run report makes no mention of the quality standard.

### Scenario: The generating station records its own anchor comparison before review
- S4: Given a fixture visual run with anchors and an imagery generating station, when the builder completes an output, then the run evidence holds a recorded comparison for that output (anchor cited, criteria checked, gaps found or an explicit none at the charter bar) before any reviewer step executes, and the reviewers' packets reference that record without being bound by it.

### Scenario: The anchor wins over the charter default
- S5: Given a fixture project whose anchors show a deliberately stylized product, when reviewer-design judges a stylized output that matches the anchors, then the charter's realism criteria for the product type do not by themselves fail it: the review measures against the anchors first, and anything below the charter floor is named as a floor gap rather than silently waived.

### Scenario: A game product is judged by its own stated standard
- S6: Given a fixture visual run for a game product whose design system states its standard in observable terms, when reviewer-design judges its output, then the review applies the stated standard, and the charter's photorealism criteria for physical products are absent from the judgment.
