# Curated Craft Skills

Status: proposed

## Purpose

The line produced work that passed review and still fell short of the owner's bar. Four causes were found in the run record on 2026-11-09:

1. Producing stations carried no craft guidance. The spec-writer, test-writer, blueprint and researcher prompts were five generic rules, and every promoted practice was scoped to a reviewer or to the checks gate, so the bar was applied only after the work was built.
2. Most producing stations could not write files. Only builder and test-writer had edit tools, while every producer prompt says "Produce the output as a file". In run wo-gh-35 the spec-writer reported that the Write tool was disabled and produced no spec change.
3. Interface work was judged as a physical product. The quality charter defaulted every visual run to physical_product, so the wo-gh-35 landing page builder was told to check materials, light, contact and scale.
4. Packets did not say where upstream work lived or which checks the project runs.

This spec adds a curated skills catalog, resolved deterministically per station, and fixes the other three.

## Requirements

R1. Catalog. Curated skills live under skills/, one directory per skill holding a SKILL.md with name and description frontmatter and a body. skills/catalog.json is the curation record: a skill resolves only when the catalog lists it with an id, a non-empty stations scope and a source. Optional scope dimensions are surfaces, product_types and kinds. A body over 6000 characters, a missing file, a missing source, a missing stations scope, a duplicate id or a path that leaves the catalog root is a catalog problem; that entry never resolves.

R2. Coverage. The shipped catalog covers five domains: architecture, design, web, gaming and content. Every producing station (blueprint, spec-writer, test-writer, builder, brief-writer, researcher, writer, media-producer) receives at least one skill on a matching order.

R3. Deterministic resolution. Before any packet is built the runner resolves the skills for each station from the station id, the work order surfaces, the product type and the work order kind. A skill applies when every non-empty scope dimension matches: conjunctive across dimensions, disjunctive within, an empty dimension unrestricted. No model takes part. Resolution is repeated after intake sets the surfaces.

R4. Product type signal for skills. A product type declared in the work order ("Product type: X") or by the project always counts. Loose keywords count only on the ui surface, where an undeclared type means interface.

R5. Injection and authority. A station's resolved skills are rendered in a Craft skills section in the stable prefix of its packet, after practices. The section states the order of authority: the work order and spec, then the project design system and decisions, then promoted practices, then skills. A station with no resolved skill gets no section and its packet is unchanged.

R6. Project precedence. A project may carry its own skills/catalog.json; an entry with a factory id replaces the factory skill and a new id adds one. A project may name skill ids in anvil.yaml skill_overrides to switch them off. Overrides are recorded.

R7. Recording. report.json gains a skills field with the resolved ids per station, the disabled ids, the catalog size and the signals used. The routing record carries the same resolution.

R8. Interface product type. The quality charter gains an interface type with observable criteria (hierarchy, typography, layout, color, states, character). Product type detection uses, in order: an explicit declaration in the work order, the project's declared type, the existing keywords, then interface phrases. With a known project, a run on the ui surface alone defaults to interface. A work order with no signal and no project keeps the physical_product default.

R9. Run context. Each packet lists what exists on disk for the run: the spec the work order names and the output file of each upstream step. Packets for test-writer, builder and reviewer-tests also list the project check commands.

R10. Producer write access. The station wrappers grant edit tools to every station that is told to produce a file: builder, test-writer, spec-writer, blueprint, brief-writer, researcher, writer and media-producer. Reviewers, scout, observer and supervisor never receive edit tools.

R11. Definitions of done. The producer prompts state when the work is finished and what to verify before handoff. Reviewer prompts and their Output Format sections are unchanged.

## Scenarios

S1. (R1, R2) The shipped catalog loads with no problems, covers the five domains, names only stations that exist, and lists every skill directory on disk.

S2. (R3, R4) A landing page order on the ui surface gives the builder interface-design and web-engineering and no game skill. An order that declares Product type: game gives the builder and spec-writer the game skills and no interface skill. A backend order that merely mentions a dashboard or a game gets no visual skill.

S3. (R5) The builder packet of a matching order contains the Craft skills section before the Work order section, with the authority note and each skill body. A packet with no resolved skill is byte identical to a packet built without the feature.

S4. (R6) A project catalog entry replaces the factory skill of the same id and adds a new one; a skill named in skill_overrides resolves for no station and is recorded as disabled.

S5. (R1) Each malformed catalog entry is reported with its reason and resolves nothing; an absent catalog is empty and sound.

S6. (R8) A landing page order resolves to the interface product type; an explicit Product type: physical_product still wins; a project that declares dashboard resolves to interface and one that declares game resolves to game; the interface charter reaches the builder without the physical criteria.

S7. (R9) The run context lists only upstream outputs that exist, the spec when it exists, and the check commands only for the check aware stations.

S8. (R10) Both wrappers expose the same producer write set, and no reviewer or read only station is in it.

S9. (R7) A packet mode run writes the skills resolution to report.json and the skill bodies into the matching station packets.

## Scope limits

Python standard library only. No pipeline membership changes. No change to the review parse contract, the reviewer Output Format sections, the checks gate or the approver. No em dash or en dash characters in any produced file.
