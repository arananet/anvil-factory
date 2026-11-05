# Design Knowledge Base and the UX Module

Status: approved
Slug: design-knowledge

## Roles
- implementer: builds the change described here
- reviewer: checks the change against this spec
- qa: checks the scenarios below with tests
- product_owner: owns the purpose and accepts the result

## Purpose
ANVIL's design work runs through a module with two layers. The base is a design knowledge layer: reference data holding interface styles, color palettes organized by product type, font pairings, UX guidelines and product type notes, held as model agnostic data that any runtime can read. The guide is the set of design stations that apply that base, and per the factory's model routing policy they are guided stations: the design system authoring and revision step, the builder when its work is a UI surface, and reviewer-design all run on the design model (openai/gpt-6-astra, as catalogued in the Cloudflare AI Gateway and recorded in the project design system spec). Knowledge without guidance is a library nobody opens; guidance without knowledge is taste without memory. This spec builds the base layer, the runtime knowledge pack mechanism that feeds it, and records the guide designation in the design stations' catalog entries so the module's shape is explicit in the factory itself.

## Requirements

### The base: built in starter dataset
- The factory ships a starter knowledge dataset of its own, authored for ANVIL in the factory's voice, as data files under design-knowledge/ at the factory root: styles.json (named interface styles, each with a short description of its character and where it fits), palettes.json (color palettes organized by product type, each with named colors and hex values), fonts.json (font pairings: a display face, a text face, and the character they give a page), guidelines.json (UX guidelines grouped by concern, each a single checkable sentence), and product-types.json (per product type notes: which styles, palettes and pairings suit it, and why). A starter dataset is the scope; growing it is future work.
- The knowledge loader validates each file's shape (required fields per entry) and fails with the file and entry named when an entry is malformed, so a bad edit to the data breaks loudly at load, not silently in a packet.

### The base: operator supplied knowledge packs at runtime
- An operator may hand a knowledge pack in with a work order. A pack is a directory living OUTSIDE any repository tree, containing a manifest.json and the pack's data files. The manifest declares: the pack's name, its format version, the product types it covers, and the data files it contains (drawn from the same five kinds as the built in dataset: styles, palettes, fonts, guidelines, product types). A pack may carry a subset of the kinds; the built in dataset fills the kinds and the product types the pack does not cover.
- A work order names its pack by a filesystem path field (knowledge_pack). The runner resolves that path at run start, loads and validates the pack with the same loader discipline as the built in data, and records the pack in the run report as an operator supplied input: the pack name, its manifest product types, and its file list. A pack path that does not resolve or a pack that fails validation stops the run at intake with the failure recorded; a run never silently proceeds on a pack it could not read.
- Pack contents are runtime inputs, never repository content: the runner never writes pack files into the project tree or the factory tree, packets carry the matched slice as packet text the same way they carry the built in slice, and when the run ends the repository tree contains no pack file. Nothing about the pack (its name, its origin, its contents) appears in any committed artifact beyond the run report's operator supplied inputs record, which lives with the run evidence.

### Matching and injection
- A project declares its product type in its design system (a product_type field in design/tokens.json or a line in design/DESIGN.md) or in its project brain. Matching is deterministic: the declared product type selects the slice (the product type note plus the styles, palettes and pairings the note references, and the general guidelines), drawn from the pack when a supplied pack covers that product type and from the built in dataset otherwise. The same product type with the same inputs always selects the same slice. An undeclared or unknown product type selects the general guidelines only, and the packet records that no product type slice matched.
- When a station packet is built for the design authoring path (the builder or writer whose work order targets design/DESIGN.md) and for reviewer-design on every run, the packet gains a Design knowledge section carrying the matched slice, computed once per run like the project design section. The builder on a UI surface also receives the slice, because the guide stations work from the same base. Other stations' packets are unchanged.
- Authoring draws on the base plus the project's locked brand: the design authoring path takes the product type slice and the project's own brand identity inputs (palette, typography, voice as locked in its brain and design system) and writes DESIGN.md from both. The builder builds with DESIGN.md and the slice in its packet. reviewer-design judges against DESIGN.md, the slice, and, where the run produced rendered screenshots, the screenshots.

### Authority and citation
- The project's own design system is the authority in every packet and every judgment. The knowledge base (built in or pack supplied) is reference material the design system draws from, never an override. On any conflict the project's system wins, and reviewer-design's contract states that a deviation from the knowledge base is never by itself a finding; a deviation from the project's design system is.
- When a design system is authored or revised using the knowledge base, DESIGN.md cites the entries it drew from (by data kind and entry name) in a short Design knowledge sources note, and notes when a slice came from an operator supplied pack (cited as an operator supplied pack entry, without naming the pack's origin). reviewer-design's contract asks it to name the knowledge entry behind any suggestion it makes.

### The guide designation
- The catalog entries of the design stations that apply the base (the design authoring stations, the builder's UI surface role, and reviewer-design) record the module's guide designation: they are guided design stations whose designated model is the design model from the recorded model routing policy. The designation lives in the station catalog data so project runtime configs and readers can see the module's shape without reading prose; wiring a given project's runtime to that model stays that project's configuration act, as the policy already states.

## Scenarios

### Scenario: The built in dataset ships as validated original data
- S1: Given the factory as shipped by this change, when the knowledge loader runs, then design-knowledge/ holds styles, palettes, fonts, guidelines and product types data, every entry carries its required fields, and a deliberately malformed entry makes the loader fail naming the file and the entry.

### Scenario: Matching is deterministic per product type
- S2: Given a project declaring a product type present in the active knowledge (pack or built in), when the slice is computed twice, then both computations return the same entries: the product type note, the styles, palettes and pairings it references, and the general guidelines.

### Scenario: Design packets carry the knowledge slice, others do not
- S3: Given a project with a declared product type, when packets are built for a run, then reviewer-design's packet, the UI builder's packet and the packet of a station authoring the design system contain a Design knowledge section with the matched slice and the authority statement, and the packet of a station outside that set (for example scout) contains no Design knowledge section.

### Scenario: The project design system wins on conflict
- S4: Given a project design system whose tokens conflict with a knowledge palette in its slice, when reviewer-design's contract and the injected section are read, then both state that the project's system is the authority, and the reviewer contract states that deviation from the knowledge base alone is not a finding.

### Scenario: Undeclared product type gets the general guidelines and says so
- S5: Given a project with no declared product type, when the slice is computed, then it contains the general guidelines only and the packet records that no product type slice matched.

### Scenario: Design systems cite the knowledge they drew from
- S6: Given a design authoring packet that includes a knowledge slice, when the station contracts are read, then the authoring contract requires a Design knowledge sources note in DESIGN.md citing entries by data kind and entry name, and reviewer-design's contract asks it to name the entry behind any suggestion it makes.

### Scenario: A pack handed in with a work order reaches the design packets
- S7: Given a work order naming a knowledge pack whose data covers the project's product type, when a run executes, then the design packets' knowledge slice contains entries from the pack for that product type, the run report records the pack under operator supplied inputs with its name, manifest product types and file list, and product types the pack does not cover fall back to the built in dataset.

### Scenario: A pack leaves no trace in the repository tree
- S8: Given a run that consumed an operator supplied pack, when the run ends and the project tree and factory tree are examined, then no pack file exists in either tree and no committed file contains pack content; the pack's only record is the run report's operator supplied inputs entry in the run evidence.

### Scenario: An unreadable pack stops the run honestly
- S9: Given a work order naming a pack path that does not resolve or whose manifest fails validation, when the run starts, then the run stops at intake with the failure recorded in the report, and no station is spawned on knowledge the runner could not read.

### Scenario: The guide designation is recorded in the catalog
- S10: Given the station catalog as shipped by this change, when the entries for the design authoring stations and reviewer-design are read, then they carry the guided design station designation naming the design model from the recorded routing policy as their designated model.
