# UX Module: Design Knowledge Base and Guided Stations

ANVIL's design work runs through a two-layer UX module. The base is a **design knowledge layer**: reference data holding interface styles, color palettes organized by product type, font pairings, UX guidelines and product type notes. The guide is the **set of design stations** that apply that base, running on the design model from the factory's routing policy.

Knowledge without guidance is a library nobody opens; guidance without knowledge is taste without memory. This module integrates both.

## The Knowledge Base Layer

### Built-in Starter Dataset

The factory ships a starter knowledge dataset at `design-knowledge/` at the factory root, authored for ANVIL in the factory's voice:

- **styles.json**: Named interface styles, each with a description of its character and where it fits (e.g., "modern-minimal", "data-dense", "friendly-conversational")
- **palettes.json**: Color palettes organized by product type, each with named colors and hex values
- **fonts.json**: Font pairings (display face, text face, and the character they give a page)
- **guidelines.json**: UX guidelines grouped by concern (accessibility, spacing, hierarchy, responsive, motion, forms, feedback), each a single checkable sentence
- **product-types.json**: Per product type notes describing which styles, palettes and font pairings suit it, and why

This is a starter dataset; growing it is future work.

### Data Validation

The knowledge loader validates each file's shape at load time. Every entry must have its required fields:

- Styles: `name`, `description`
- Palettes: `name` (may have `colors` array or direct `hex` field)
- Fonts: `name`, `display`, `text`, `character`
- Guidelines: `guideline`, `concern`
- Product types: `product_type`, `styles`, `palettes`, `fonts`, `why`

A malformed entry fails loudly at load with the file and entry named, never silently in a packet.

### Operator-Supplied Knowledge Packs

An operator may hand a knowledge pack in with a work order. A pack is a directory living **outside any repository tree**, containing:

- **manifest.json**: Pack name, format version, product types it covers, and data files it contains
- **Data files**: Any subset of the five kinds (styles.json, palettes.json, fonts.json, guidelines.json, product-types.json)

A work order names its pack via a `knowledge_pack` field (filesystem path). The runner:

1. Resolves the path at run start
2. Loads and validates the pack with the same loader discipline as the built-in data
3. Records the pack in the run report as an operator-supplied input (name, manifest product types, file list)

A pack path that doesn't resolve or a pack that fails validation **stops the run at intake** with the failure recorded. A run never silently proceeds on knowledge it couldn't read.

**Pack isolation**: Pack contents are runtime inputs, never repository content. The runner never writes pack files into the project or factory tree. Packets carry the matched slice as packet text. When the run ends, the repository tree contains no pack file. Nothing about the pack (name, origin, contents) appears in committed artifacts beyond the run report's operator-supplied inputs record in the run evidence.

## Slice Matching and Injection

### Deterministic Product Type Matching

A project declares its product type in:
- `brain/project.md` (line: "Product type: X")
- `design/tokens.json` (field: `product_type`)
- `design/DESIGN.md` (line: "Product type: X")

Matching is **deterministic**: the same product type with the same inputs always selects the same slice.

**Matched slice includes**:
- The product type note (which styles/palettes/fonts suit it, and why)
- The styles, palettes and fonts the note references
- The general guidelines (always included)

**Undeclared or unknown product type**: selects general guidelines only, and the packet records that no product type slice matched.

**Pack preference**: When an operator-supplied pack covers the project's product type, the slice is drawn from the pack. Product types the pack doesn't cover fall back to the built-in dataset.

### Packet Injection

When a station packet is built for:
- **reviewer-design** (on every run)
- **reviewer-ux** (on every run)
- **builder** (when work is a UI surface)
- **writer** (when authoring or revising design/DESIGN.md)

...the packet gains a **Design knowledge** section carrying:
- The matched slice (computed once per run, like the project design section)
- An **authority statement**: The project's own design system (design/DESIGN.md, design/tokens.json) is the authority. The knowledge base is reference material the design system may draw from. On any conflict, the project's system wins. A deviation from the knowledge base alone is not a finding; a deviation from the project's design system is.

Other stations' packets are unchanged.

### How Design Stations Use the Knowledge

**Design authoring** (builder/writer targeting design/DESIGN.md):
- Takes the product type slice AND the project's locked brand identity inputs (palette, typography, voice from brain and design system)
- Writes DESIGN.md from both
- Includes a **Design knowledge sources** note citing entries by data kind and entry name (e.g., "Style: modern-minimal", "Palette: metrics-blue", "Guideline: accessibility - contrast ratio")
- Cites operator-supplied pack entries as "operator-supplied pack entry" without naming the pack's origin

**builder** (when building a UI surface):
- Builds with DESIGN.md and the knowledge slice in its packet

**reviewer-design**:
- Judges against DESIGN.md, the knowledge slice, and (when available) rendered screenshots
- **Authority rule**: The project's design system wins. A deviation from the knowledge base alone is not a finding; a deviation from the project's design system is.
- When referencing the knowledge base in a finding or suggestion, names the specific entry (e.g., "metrics-blue palette", "data-dense style", "accessibility guideline for contrast")

**reviewer-ux**:
- Judges user experience: flows and task completion, usability heuristics, accessibility basics, and interface copy clarity
- Uses the UX guidelines slice from the knowledge base and (when available) rendered screenshots
- Explicitly excludes visual system compliance (tokens, type scale, palette) as reviewer-design's lens
- When there are no rendered screenshots, states in the review that it judged from source and knowledge slice without rendered evidence

## The Guide Layer: Guided Design Stations

The stations that apply the knowledge base are **guided design stations**, marked in the catalog with:

```json
{
  "guided": true,
  "designation": "guided design station",
  "design_model": "claude-opus-5-5"
}
```

The designated model is the **design model from the factory's routing policy** (currently `claude-opus-5-5`).

**Guided design stations**:
- **Design authoring stations**: stations whose work order targets design/DESIGN.md
- **builder**: when its work is a UI surface
- **reviewer-design**: always
- **reviewer-ux**: always

Wiring a project's runtime to use that model is the project's configuration act, as the policy states. The designation in the catalog makes the module's shape explicit: which stations are guided, and to which model.

## Authority and Citation

### Authority

**The project's own design system is the authority** in every packet and every judgment.

The knowledge base (built-in or pack-supplied) is **reference material** the design system draws from, never an override. On any conflict, the project's system wins.

**reviewer-design contract states explicitly**: A deviation from the knowledge base alone is not a finding. A deviation from the project's design system is.

### Citation Discipline

**When authoring design/DESIGN.md**:
- Include a "Design knowledge sources" note
- Cite entries by data kind and entry name (e.g., "Style: modern-minimal", "Palette: metrics-blue")
- Cite operator-supplied pack entries as "operator-supplied pack entry" (don't name the pack's origin)

**reviewer-design**:
- When referencing the knowledge base in a finding or suggestion, name the specific entry behind it

## Implementation

**Module code**: `anvil/knowledge.py`

**Key functions**:
- `load_builtin_knowledge()`: Loads and validates built-in data
- `load_knowledge_pack(pack_path)`: Loads and validates operator pack
- `compute_knowledge_slice(product_type, knowledge_pack)`: Deterministic slice matching
- `packet_knowledge_section(project_dir, station_id)`: Generates Design knowledge section for packets
- `get_project_product_type(project_dir)`: Extracts product type from project
- `validate_knowledge_entry(filepath, entry, data_kind)`: Entry validation

**Data location**: `design-knowledge/` at factory root

**Station contracts updated**:
- `stations/reviewer-design/PROMPT.md`: Authority statement and citation requirements
- `stations/builder/PROMPT.md`: Citation requirements for design authoring
- `stations/writer/PROMPT.md`: Citation requirements for design authoring

**Catalog updated**:
- `stations/reviewer-design/station.json`: Guide designation added
- `stations/builder/station.json`: Guide designation added
- `stations/writer/station.json`: Guide designation added

## Spec

Implemented per: `.openspec/specs/design-knowledge/spec.md`

Scenarios S1-S10 covered:
- S1: Built-in validated dataset
- S2: Deterministic slice matching
- S3: Packet injection for design stations
- S4: Authority statement in packets and contracts
- S5: Undeclared product type handling
- S6: Citation discipline
- S7-S8: Operator-supplied packs (runtime only, no repo trace)
- S9: Pack validation failures stop the run
- S10: Guide designation in catalog
