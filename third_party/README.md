# Third party inventory

This directory holds third party material vendored into the ANVIL factory repository. Each entry keeps its upstream license file inside its own directory.

## teardown

- What it is: a simulator kit that builds machines as interactive 3D pages you can take apart, with deterministic frame capture for films and review sheets.
- What ANVIL uses it for: interactive simulator builds, and deterministic frame capture as run evidence.
- Upstream: https://github.com/elvarofficial/teardown
- License: MIT (see teardown/LICENSE).
- Vendored commit: e7e668cd44f48ba79a3c575e9f55c7e194d26eef
- Location in this repo: third_party/teardown/, copied verbatim from the upstream tree at that commit.

## taste-skill

- What it is: the Taste Skill (install name design-taste-frontend, version 2.5.1), an anti-template art direction skill for company and marketing websites, shipped upstream with a Node checker kit.
- What ANVIL uses it for: the catalog skill design-taste, an adaptation under skills/design-taste/. The vendored SKILL.md is the provenance record and the full rule source; its scripts, dealers, assets and gate hook are not run by the line.
- Upstream: https://github.com/Leonxlnx/taste-skill
- License: MIT (see taste-skill/LICENSE).
- Vendored commit: f6b76575f949707b4e3c37cd86cb44b0b98643e8
- Location in this repo: third_party/taste-skill/, SKILL.md and LICENSE copied verbatim from the upstream tree at that commit.

## image-to-code

- What it is: an image-first design to code skill: take or generate reference images, extract their design system, implement to match, and hold the result against the reference.
- What ANVIL uses it for: the catalog skill image-to-code, an adaptation under skills/image-to-code/ for work orders that arrive with reference images or an approved image pack. The vendored SKILL.md is the provenance record; its Codex image generation rules are not adopted.
- Upstream: https://github.com/Leonxlnx/imagegen-skills (skills/image-to-code)
- License: MIT (see image-to-code/LICENSE).
- Vendored commit: beb16b0d0f4dae9a6f5cb04ea41e97b93a54ab8e
- Location in this repo: third_party/image-to-code/, SKILL.md and LICENSE copied verbatim from the upstream tree at that commit.

## web-interface-guidelines

- What it is: Vercel's Web Interface Guidelines as a single rules file (command.md), the rule source of the web-design-guidelines agent skill.
- What ANVIL uses it for: the catalog skill web-design-guidelines under skills/web-design-guidelines/, a distilled audit checklist for reviewer-design and reviewer-ux. The rules are pinned here so a verdict is reproducible; the upstream skill fetches them fresh at review time instead. The companion skill in vercel-labs/agent-skills is referenced, not vendored: that repository has no LICENSE file.
- Upstream: https://github.com/vercel-labs/web-interface-guidelines
- License: MIT (see web-interface-guidelines/LICENSE).
- Vendored commit: 434b7f91364665f2f733b310ec54809bf8f37937
- Location in this repo: third_party/web-interface-guidelines/, command.md and LICENSE copied verbatim from the upstream tree at that commit.
