# Curated craft skills

A skill is a short craft guide for one domain. The runner puts the skills that match a station and a work order into that station's packet, in a Craft skills section, before the model starts. Practices (brain/practices.md) are single rules a project earned from run evidence; skills are the curated baseline every project starts from.

## What ships

| Skill | Domain | Stations | Applies when |
|---|---|---|---|
| architecture-fundamentals | architecture | blueprint, spec-writer, builder, reviewer-architecture | always |
| spec-writing | architecture | spec-writer, blueprint | always |
| test-design | architecture | test-writer, reviewer-tests | always |
| implementation-craft | architecture | builder | always |
| security-baseline | architecture | builder, reviewer-security | always |
| interface-design | design | builder | product type interface, ui surface |
| web-engineering | web | builder | product type interface, ui surface |
| game-design-feel | gaming | spec-writer, builder | product type game |
| game-engineering | gaming | builder, test-writer | product type game |
| content-briefing | content | brief-writer | always |
| source-research | content | researcher | always |
| content-writing | content | writer | always |
| media-production | content | media-producer | always |

## The curation rule

A skill reaches a packet only when skills/catalog.json lists it. Every entry records:

- `id` and, optionally, `path` (default `skills/<id>/SKILL.md`)
- `stations`: required, the stations that receive it
- `surfaces`, `product_types`, `kinds`: optional scope; empty means unrestricted
- `source`: required, where the guidance comes from
- `license`

The body is capped at 6000 characters so one skill cannot crowd a packet. `anvil check-skills <project>` validates the catalog and, with `--work-order` and `--pipeline`, prints what each station would receive.

## Product type

The interface and game skills match on product type. Declare it once in the project brain (brain/project.md) on its own line:

```
Product type: game
```

Recognized values: `game`, `illustration`, `physical_product`, `interface`, and the interface kinds `dashboard`, `marketing-site`, `landing-page`, `website`, `web-app`, `mobile-app`. A work order can override the project with the same line in its description. Without a declaration, a work order on the ui surface is treated as interface work.

## Adding or replacing a skill in a project

Create `skills/catalog.json` and `skills/<id>/SKILL.md` in the project. An entry with a factory id replaces the factory skill; a new id adds one. To switch a factory skill off, list its id in the project's anvil.yaml:

```json
{"skill_overrides": ["interface-design"]}
```

## Adding an external skill

SKILL.md uses the common skill format (name and description frontmatter, then the body), so a published skill can be adopted. Vendor it under third_party/ with its license file, record it in third_party/README.md, and add a catalog entry whose `path` points at the vendored SKILL.md and whose `source` names the upstream and the commit. Read it first: a skill is prompt text every matching station will follow.

## Authority

Skills are the lowest authority in a packet: the work order and its spec, the project design system and decisions, and promoted practices all win over a skill.
