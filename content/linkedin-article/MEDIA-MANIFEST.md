# Media Manifest

This document records how each media asset for the LinkedIn article was created, for full disclosure and reproducibility.

## Production Method

All diagrams were created as **hand-coded SVG files** using:
- **Validated color palette** from the dataviz skill reference (`references/palette.md`)
- **Light mode colors** for article compatibility
- **System fonts** (system-ui, sans-serif stack)
- **Accessible contrast ratios** following WCAG guidelines

## Asset Inventory

### 1. cover.svg
**Purpose**: Article cover image showing ANVIL branding  
**Created**: 2026-10-29  
**Method**: Hand-coded SVG  
**Dimensions**: 1200x630 (standard social media cover size)  
**Colors used**:
- Surface: `#fcfcfb`
- Primary ink: `#0b0b0b`
- Secondary ink: `#52514e`
- Accent (blue): `#2a78d6`

**Elements**:
- Stylized assembly line (circles and connecting bars)
- Light grid pattern suggesting factory structure
- ANVIL title and tagline
- No external assets or fonts required

**Reproducibility**: File is self-contained SVG with embedded styles

---

### 2. diagram-1-the-line.svg
**Purpose**: Illustrates the ANVIL workflow from work order to deployment  
**Created**: 2026-10-29  
**Method**: Hand-coded SVG  
**Dimensions**: 1400x800  
**Colors used**:
- Station boxes (blue): `#2a78d6`
- Reviewer boxes (aqua): `#1baf7a`
- Gate (yellow): `#eda100`
- Loop path (magenta): `#e87ba4`
- Arrows (secondary ink): `#52514e`

**Elements**:
- Sequential stations: Work Order → Spec Writer → Test Writer → Builder
- Four parallel reviewers (spec, security, tests, architecture)
- Approver aggregation
- Human gate (diamond shape)
- Deployer and Observer
- Feedback loop path
- Legend explaining visual encoding

**Reproducibility**: File is self-contained SVG with embedded styles and SVG marker definitions

---

### 3. diagram-6-station-catalog.svg
**Purpose**: Shows all 25 stations in the catalog  
**Created**: 2026-10-29  
**Method**: Hand-coded SVG  
**Dimensions**: 1200x900  
**Colors used**:
- All station boxes (blue): `#2a78d6`
- Text labels (white): `#ffffff`
- Annotations (gray): `#898781`

**Elements**:
- 5x5 grid layout showing all 25 stations by name
- Title and count
- Explanatory footer text

**Station names displayed** (as verified in article fact 1):
- intake, spec-writer, test-writer, builder, reviewer-spec
- reviewer-security, reviewer-tests, reviewer-architecture, reviewer-design, approver
- triage, deployer, observer, supervisor, blueprint
- scaffolder, onboard, brief-writer, researcher, writer
- media-producer, reviewer-facts, reviewer-voice, reviewer-platform, reviewer-brand-risk

**Reproducibility**: File is self-contained SVG with embedded styles

---

### 4. diagram-3-station.svg
**Purpose**: Illustrates single station anatomy and contract  
**Created**: 2026-10-29  
**Method**: Hand-coded SVG  
**Dimensions**: 900x700  
**Colors used**:
- Station core (blue): `#2a78d6`
- Input boxes (aqua): `#1baf7a`
- Output boxes (orange): `#eb6834`
- Container outline (blue): `#2a78d6`
- Arrows (secondary ink): `#52514e`

**Elements**:
- Input column: Packet, Context, Upstream Outputs
- Central station box with components listed
- Output column: Artifact, Metadata, Provenance
- Arrows showing data flow
- "Never approves itself" principle noted

**Reproducibility**: File is self-contained SVG with embedded styles and SVG marker definitions

---

### 5. diagram-2-domains-modes.svg
**Purpose**: Shows software and content domains sharing the same core  
**Created**: 2026-10-29  
**Method**: Hand-coded SVG  
**Dimensions**: 1200x800  
**Colors used**:
- Core infrastructure (blue): `#2a78d6`
- Software domain (aqua): `#1baf7a`
- Content domain (magenta): `#e87ba4`
- Connecting arrows (dashed, secondary ink): `#52514e`

**Elements**:
- Central ANVIL Core box with shared infrastructure listed
- Left: Software Factory with its stations and truth source
- Right: Content Factory with its stations and truth source
- Dashed arrows showing domain connection to core
- Footer explaining the rhyming structure

**Reproducibility**: File is self-contained SVG with embedded styles

---

### 6. diagram-4-design-system.svg
**Purpose**: Illustrates per-project design system architecture  
**Created**: 2026-10-29  
**Method**: Hand-coded SVG  
**Dimensions**: 1200x900  
**Colors used**:
- Design files (yellow): `#eda100`
- Stations (blue): `#2a78d6`
- Reviewer-design (aqua): `#1baf7a`
- Warning boxes (red): `#e34948`
- Dogfooding section (aqua border): `#1baf7a`

**Elements**:
- Design file representation (DESIGN.md, tokens.json)
- Scaffolding behavior box
- Station packet enhancement flow
- Interface-producing stations
- reviewer-design station
- Warning path for missing design system
- Dogfooding confirmation box

**Reproducibility**: File is self-contained SVG with embedded styles and SVG marker definitions

---

### 7. diagram-5-model-routing.svg
**Purpose**: Documents model routing policy across stations  
**Created**: 2026-10-29  
**Method**: Hand-coded SVG  
**Dimensions**: 1400x900  
**Colors used**:
- Model pool boxes (violet): `#6250d6`
- Station boxes (blue): `#2a78d6`
- Gateway detail box (yellow): `#eda100`
- Arrows (secondary ink): `#52514e`

**Elements**:
- Three model pools: GPT-6 Astra, Claude Opus 5.5, Claude Sonnet 5.5
- Station assignments by model
- Migration rationale box (Sonnet 4.5 deprecation)
- Cloudflare AI Gateway access details
- Arrows showing routing from models to stations

**Reproducibility**: File is self-contained SVG with embedded styles and SVG marker definitions

---

## Color Palette Attribution

All colors are from the validated reference palette in the dataviz skill:
- Categorical colors validated for CVD safety (Delta E >= 8 OKLab ×100)
- Light mode surface and ink colors
- Contrast ratios meet WCAG AA minimums for normal text
- Full palette documentation: `/tmp/claude-1001/bundled-skills/2.1.312/25a09072b8972783086f2cd7fddff179/dataviz/references/palette.md`

## File Format Note

**Current format**: SVG (Scalable Vector Graphics)  
**Article references**: PNG format

**Production step required**: Convert SVG to PNG at appropriate resolution (suggested 2x for retina displays).  
**Conversion command** (if using ImageMagick or similar):
```bash
for file in *.svg; do
  convert -density 300 -background none "$file" "${file%.svg}.png"
done
```

**Or using rsvg-convert**:
```bash
for file in *.svg; do
  rsvg-convert -w 2400 -h 0 "$file" -o "${file%.svg}.png"
done
```

## Disclosure Statement

All diagrams were:
- Created by Claude Sonnet 4.5 (media-producer station)
- Based on verified facts from work order wo-gh-4
- Using the validated dataviz palette
- Hand-coded as SVG (no image generation models used)
- Self-contained with no external dependencies
- Reproducible from source code

No generative image models (DALL-E, Midjourney, Stable Diffusion, etc.) were used.  
All visual elements are geometric primitives (rectangles, circles, paths, text).

## Source Control

All SVG source files are version controlled in the repository at:
`content/linkedin-article/`

Created as part of work order wo-gh-4, media-producer station output.

---

**Station**: media-producer  
**Run**: wo-gh-4  
**Date**: 2026-10-29  
**Model**: claude-sonnet-4-5  
**Provenance**: This manifest and all referenced assets
