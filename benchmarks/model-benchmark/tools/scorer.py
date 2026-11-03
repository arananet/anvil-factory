#!/usr/bin/env python3
"""
Scorer for the Meridian Patch design fixture.
Evaluates 12 checks (K1-K12) against the fixture contract.
Python standard library only.
"""

import json
import re
import sys
from html.parser import HTMLParser


TYPE_SCALE = [12, 14, 16, 20, 24, 32, 40, 56, 64]
PALETTE = ["#FAFAF6", "#14201B", "#53685C", "#0E7C66", "#FF6B4A", "#E3E6DF"]
RADIUS_TOKENS = [4, 8, 12, 16, 999]
CONTRACT_ELEMENTS = [
    "page", "hero-title", "hero-sub", "cta-primary", "price-badge",
    "section", "heading-2", "body-text", "caption", "link-inline", "card"
]


def normalize_hex(color):
    """Normalize hex color to uppercase with #"""
    if not color:
        return None
    color = color.strip().upper()
    if color.startswith("#"):
        return color
    return "#" + color


def parse_px_value(value):
    """Extract numeric value from px string"""
    if not value:
        return None
    match = re.match(r"^(\d+(?:\.\d+)?)px$", value.strip())
    if match:
        return float(match.group(1))
    return None


def parse_number(value):
    """Parse a unitless number"""
    if not value:
        return None
    try:
        return float(value.strip())
    except ValueError:
        return None


def calculate_luminance(hex_color):
    """Calculate relative luminance per WCAG formula"""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

    def adjust(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)


def contrast_ratio(hex1, hex2):
    """Calculate contrast ratio between two colors"""
    l1 = calculate_luminance(hex1)
    l2 = calculate_luminance(hex2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def extract_first_font_family(font_family_value):
    """Extract the first font family from a font-family value"""
    if not font_family_value:
        return None
    families = font_family_value.split(",")
    first = families[0].strip().strip('"').strip("'")
    return first


class StyleExtractor(HTMLParser):
    """Parse HTML and extract styles from style block and inline styles"""

    def __init__(self):
        super().__init__()
        self.in_style = False
        self.style_content = ""
        self.element_styles = {}
        self.current_element_id = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        element_id = attrs_dict.get("id")

        if tag == "style":
            self.in_style = True

        # Parse body element for background check
        if tag == "body":
            if "body" not in self.element_styles:
                self.element_styles["body"] = {}
            if "style" in attrs_dict:
                inline_styles = self.parse_inline_style(attrs_dict["style"])
                self.element_styles["body"].update(inline_styles)

        if element_id in CONTRACT_ELEMENTS:
            self.current_element_id = element_id
            if element_id not in self.element_styles:
                self.element_styles[element_id] = {}

            if "style" in attrs_dict:
                inline_styles = self.parse_inline_style(attrs_dict["style"])
                self.element_styles[element_id].update(inline_styles)

    def handle_data(self, data):
        if self.in_style:
            self.style_content += data

    def handle_endtag(self, tag):
        if tag == "style":
            self.in_style = False
            self.parse_stylesheet()

    def parse_inline_style(self, style_str):
        """Parse inline style attribute"""
        styles = {}
        for decl in style_str.split(";"):
            if ":" in decl:
                prop, value = decl.split(":", 1)
                styles[prop.strip().lower()] = value.strip()
        return styles

    def parse_stylesheet(self):
        """Parse style block and extract rules for contract elements"""
        lines = self.style_content.replace("\n", " ").replace("\r", "")

        # Parse body element styles
        body_pattern = r"\bbody\s*\{([^}]+)\}"
        body_match = re.search(body_pattern, lines)
        if body_match:
            if "body" not in self.element_styles:
                self.element_styles["body"] = {}
            declarations = body_match.group(1)
            for decl in declarations.split(";"):
                if ":" in decl:
                    prop, value = decl.split(":", 1)
                    prop = prop.strip().lower()
                    value = value.strip()
                    if prop not in self.element_styles["body"]:
                        self.element_styles["body"][prop] = value

        # Parse contract element styles
        rule_pattern = r"#([\w-]+)\s*\{([^}]+)\}"
        for match in re.finditer(rule_pattern, lines):
            element_id = match.group(1)
            declarations = match.group(2)

            if element_id in CONTRACT_ELEMENTS:
                if element_id not in self.element_styles:
                    self.element_styles[element_id] = {}

                for decl in declarations.split(";"):
                    if ":" in decl:
                        prop, value = decl.split(":", 1)
                        prop = prop.strip().lower()
                        value = value.strip()
                        if prop not in self.element_styles[element_id]:
                            self.element_styles[element_id][prop] = value


def score_page(html_file_path):
    """Score a page against the 12 checks"""

    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    parser = StyleExtractor()
    parser.feed(html_content)

    styles = parser.element_styles
    stylesheet = parser.style_content

    checks = []

    # K1: hero-title font-size on type scale and >= 56
    hero_title_size = styles.get("hero-title", {}).get("font-size")
    hero_size_px = parse_px_value(hero_title_size) if hero_title_size else None
    k1_pass = False
    if hero_size_px is not None and hero_size_px >= 56 and int(hero_size_px) in TYPE_SCALE:
        k1_pass = True
    checks.append({
        "check_id": "K1",
        "passed": k1_pass,
        "measured": hero_title_size or "missing",
        "expectation": "on type scale and >= 56px"
    })

    # K2: body-text font-size on type scale and >= 16
    body_text_size = styles.get("body-text", {}).get("font-size")
    body_size_px = parse_px_value(body_text_size) if body_text_size else None
    k2_pass = False
    if body_size_px is not None and body_size_px >= 16 and int(body_size_px) in TYPE_SCALE:
        k2_pass = True
    checks.append({
        "check_id": "K2",
        "passed": k2_pass,
        "measured": body_text_size or "missing",
        "expectation": "on type scale and >= 16px"
    })

    # K3: margins/paddings for section, card, hero-title, body-text, cta-primary are multiples of 8
    spacing_elements = ["section", "card", "hero-title", "body-text", "cta-primary"]
    spacing_props = ["margin", "margin-top", "margin-bottom", "margin-left", "margin-right",
                     "padding", "padding-top", "padding-bottom", "padding-left", "padding-right"]
    k3_violations = []
    for elem in spacing_elements:
        if elem in styles:
            for prop in spacing_props:
                if prop in styles[elem]:
                    value = styles[elem][prop]
                    px_val = parse_px_value(value)
                    if px_val is not None and px_val % 8 != 0:
                        k3_violations.append(f"{elem} {prop}={value}")
    checks.append({
        "check_id": "K3",
        "passed": len(k3_violations) == 0,
        "measured": ", ".join(k3_violations) if k3_violations else "all multiples of 8",
        "expectation": "all spacing multiples of 8"
    })

    # K4: all colors from palette
    color_props = ["color", "background-color", "background", "border-color"]
    k4_violations = []
    for elem in CONTRACT_ELEMENTS:
        if elem in styles:
            for prop in color_props:
                if prop in styles[elem]:
                    value = styles[elem][prop]
                    hex_match = re.search(r"#[0-9A-Fa-f]{6}", value)
                    if hex_match:
                        color = normalize_hex(hex_match.group(0))
                        if color not in [normalize_hex(c) for c in PALETTE]:
                            k4_violations.append(f"{elem} {prop}={color}")
    checks.append({
        "check_id": "K4",
        "passed": len(k4_violations) == 0,
        "measured": ", ".join(k4_violations) if k4_violations else "all from palette",
        "expectation": "all colors from palette"
    })

    # K5: coral only on price-badge
    coral = normalize_hex("#FF6B4A")
    k5_violations = []
    for elem in CONTRACT_ELEMENTS:
        if elem == "price-badge":
            continue
        if elem in styles:
            for prop in color_props:
                if prop in styles[elem]:
                    value = styles[elem][prop]
                    if coral.lower() in value.lower():
                        k5_violations.append(f"{elem} {prop}")
    checks.append({
        "check_id": "K5",
        "passed": len(k5_violations) == 0,
        "measured": ", ".join(k5_violations) if k5_violations else "coral only on price-badge",
        "expectation": "coral reserved for price-badge only"
    })

    # K6: :focus-visible rule exists
    k6_pass = ":focus-visible" in stylesheet
    checks.append({
        "check_id": "K6",
        "passed": k6_pass,
        "measured": "present" if k6_pass else "missing",
        "expectation": ":focus-visible rule present"
    })

    # K7: all border-radius are radius tokens
    k7_violations = []
    for elem in CONTRACT_ELEMENTS:
        if elem in styles and "border-radius" in styles[elem]:
            value = styles[elem]["border-radius"]
            px_val = parse_px_value(value)
            if px_val is not None and int(px_val) not in RADIUS_TOKENS:
                k7_violations.append(f"{elem} border-radius={value}")
    checks.append({
        "check_id": "K7",
        "passed": len(k7_violations) == 0,
        "measured": ", ".join(k7_violations) if k7_violations else "all from radius tokens",
        "expectation": "all border-radius from tokens [4, 8, 12, 16, 999]"
    })

    # K8: hero-title line-height 1.2, body-text line-height 1.5
    hero_lh = styles.get("hero-title", {}).get("line-height")
    body_lh = styles.get("body-text", {}).get("line-height")
    hero_lh_val = parse_number(hero_lh) if hero_lh else None
    body_lh_val = parse_number(body_lh) if body_lh else None
    k8_pass = (hero_lh_val == 1.2 if hero_lh_val is not None else False) and \
              (body_lh_val == 1.5 if body_lh_val is not None else False)
    checks.append({
        "check_id": "K8",
        "passed": k8_pass,
        "measured": f"hero-title={hero_lh or 'missing'}, body-text={body_lh or 'missing'}",
        "expectation": "hero-title 1.2, body-text 1.5"
    })

    # K9: caption color contrast >= 4.5:1 on paper
    caption_color = styles.get("caption", {}).get("color")
    paper = normalize_hex("#FAFAF6")
    k9_pass = False
    k9_measured = "missing"
    if caption_color:
        hex_match = re.search(r"#[0-9A-Fa-f]{6}", caption_color)
        if hex_match:
            caption_hex = normalize_hex(hex_match.group(0))
            ratio = contrast_ratio(caption_hex, paper)
            k9_pass = ratio >= 4.5
            k9_measured = f"{caption_hex} on {paper} = {ratio:.2f}:1"
    checks.append({
        "check_id": "K9",
        "passed": k9_pass,
        "measured": k9_measured,
        "expectation": ">= 4.5:1 contrast on paper"
    })

    # K10: heading-2 starts with Space Grotesk, body-text starts with Inter
    h2_font = styles.get("heading-2", {}).get("font-family")
    body_text_font = styles.get("body-text", {}).get("font-family")
    # If body-text doesn't have explicit font-family, check body element (inheritance)
    if not body_text_font and "body" in styles:
        body_text_font = styles.get("body", {}).get("font-family")
    h2_first = extract_first_font_family(h2_font) if h2_font else None
    body_first = extract_first_font_family(body_text_font) if body_text_font else None
    k10_pass = (h2_first == "Space Grotesk" if h2_first else False) and \
               (body_first == "Inter" if body_first else False)
    checks.append({
        "check_id": "K10",
        "passed": k10_pass,
        "measured": f"heading-2={h2_first or 'missing'}, body-text={body_first or 'missing'}",
        "expectation": "heading-2 starts with Space Grotesk, body-text with Inter"
    })

    # K11: page background is paper
    page_bg = styles.get("page", {}).get("background") or styles.get("page", {}).get("background-color")
    body_bg = None
    if "body" in parser.element_styles:
        body_bg = parser.element_styles["body"].get("background") or parser.element_styles["body"].get("background-color")

    k11_pass = False
    k11_measured = "missing"
    bg_to_check = page_bg or body_bg
    if bg_to_check:
        hex_match = re.search(r"#[0-9A-Fa-f]{6}", bg_to_check)
        if hex_match:
            bg_hex = normalize_hex(hex_match.group(0))
            k11_pass = bg_hex == paper
            k11_measured = bg_hex
    checks.append({
        "check_id": "K11",
        "passed": k11_pass,
        "measured": k11_measured,
        "expectation": "paper #FAFAF6"
    })

    # K12: cta-primary background is teal
    cta_bg = styles.get("cta-primary", {}).get("background") or styles.get("cta-primary", {}).get("background-color")
    teal = normalize_hex("#0E7C66")
    k12_pass = False
    k12_measured = "missing"
    if cta_bg:
        hex_match = re.search(r"#[0-9A-Fa-f]{6}", cta_bg)
        if hex_match:
            cta_hex = normalize_hex(hex_match.group(0))
            k12_pass = cta_hex == teal
            k12_measured = cta_hex
    checks.append({
        "check_id": "K12",
        "passed": k12_pass,
        "measured": k12_measured,
        "expectation": "teal #0E7C66"
    })

    passed_count = sum(1 for c in checks if c["passed"])

    return {
        "passed": passed_count,
        "total": len(checks),
        "checks": checks
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: scorer.py <html-file>", file=sys.stderr)
        sys.exit(1)

    result = score_page(sys.argv[1])
    print(json.dumps(result, indent=2))
