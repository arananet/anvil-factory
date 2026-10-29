# Design Knowledge Base

Status: approved
Slug: design-knowledge

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
The design stations judge and build from the project's own design system and nothing else. That discipline is right, a project's system must stay the authority, but it leaves the stations with no craft knowledge to draw on: a thin design system produces thin design work because nothing in the packet knows what good combinations look like. This spec gives the factory a design knowledge base of its own: original reference data, authored for ANVIL in the factory's voice, that the design stations consult when a design system is written and when design work is judged. The knowledge informs; the project's system decides.

## Requirements
- The knowledge base lives in the factory as data files under design-knowledge/ at the factory root: styles.json (named interface styles, each with a short description of its character and where it fits), palettes.json (color palettes organized by product type, each with named colors and hex values), fonts.json (font pairings, each with a display face, a text face and the character they give a page), guidelines.json (UX guidelines grouped by concern, each a single checkable sentence), and product-types.json (per product type notes: which styles, palettes and pairings suit it, and why, in the factory's own words). All entries are original content authored for this factory. A starter dataset is the scope of this change; growing it is future work.
- A project declares its product type in its design system (a product_type field in design/tokens.json or a line in design/DESIGN.md) or in its project brain. Matching is deterministic: the declared product type selects the slice, meaning the product type note plus the styles, palettes and pairings that note references and the general guidelines. The same product type always selects the same slice. An undeclared or unknown product type selects the general guidelines only, and the packet records that no product type slice matched.
- Packet injection: when a station packet is built for the design authoring path (the builder or writer working on a design system, and any station whose work order targets design/DESIGN.md) and for reviewer-design on every run, the packet gains a Design knowledge section carrying the matched slice. Other stations' packets are unchanged. The mechanism is the same once per run computation the project design section uses.
- Authority: the injected section states plainly that the project's design system is the authority and the knowledge is reference material. On any conflict between a knowledge entry and the project's design system, the project's system wins, and reviewer-design's contract says a deviation from the knowledge base is never by itself a finding; a deviation from the project's design system is.
- Citation: when a design system is authored or revised using the knowledge base, DESIGN.md cites the entries it drew from (by file and entry name) in a short Design knowledge sources note. reviewer-design's contract asks it to name the knowledge entry behind any suggestion it makes, so suggestions are traceable to the reference they came from.
- The knowledge data is validated like other factory data: the loader checks each file's shape (required fields per entry) and fails with the file and entry named when an entry is malformed, so a bad edit to the data breaks loudly at load, not silently in a packet.

## Scenarios

### Scenario: The knowledge base ships as validated original data files
- S1: Given the factory as shipped by this change, when the knowledge loader runs, then design-knowledge/ holds styles, palettes, fonts, guidelines and product-types data, every entry carries its required fields, and a deliberately malformed entry makes the loader fail naming the file and the entry.

### Scenario: Matching is deterministic per product type
- S2: Given a project declaring a product type present in the knowledge base, when the slice is computed twice, then both computations return the same entries: the product type note, the styles, palettes and pairings it references, and the general guidelines.

### Scenario: Design packets carry the knowledge slice, others do not
- S3: Given a project with a declared product type, when packets are built for a run, then reviewer-design's packet and the packet of a station authoring the design system contain a Design knowledge section with the matched slice and the authority statement, and the packet of a station outside that set (for example scout) contains no Design knowledge section.

### Scenario: The project design system wins on conflict
- S4: Given a project design system whose tokens conflict with a knowledge palette in its slice, when reviewer-design's contract and the injected section are read, then both state that the project's system is the authority, and the reviewer contract states that deviation from the knowledge base alone is not a finding.

### Scenario: Undeclared product type gets the general guidelines and says so
- S5: Given a project with no declared product type, when the slice is computed, then it contains the general guidelines only and the packet records that no product type slice matched.

### Scenario: Design systems cite the knowledge they drew from
- S6: Given a design authoring packet that includes a knowledge slice, when the station contracts are read, then the authoring contract requires a Design knowledge sources note in DESIGN.md citing entries by file and entry name, and reviewer-design's contract asks it to name the entry behind any suggestion it makes.
