#!/usr/bin/env python3
"""
Capture tool for the model benchmark fixture.
Renders HTML with Playwright Chromium and captures full page screenshot.
Settings: viewport 1280px, device scale factor 1, reduced motion emulated.
"""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright


def capture_page(html_file_path, output_path):
    """
    Render HTML file and capture full page screenshot.

    Fixed settings for reproducibility:
    - Viewport width: 1280px
    - Device scale factor: 1
    - Reduced motion: emulated
    - Full page capture
    """
    html_file = Path(html_file_path).resolve()
    output_file = Path(output_path).resolve()

    if not html_file.exists():
        print(f"Error: HTML file not found: {html_file}", file=sys.stderr)
        sys.exit(1)

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()

        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            device_scale_factor=1,
            reduced_motion="reduce"
        )

        page = context.new_page()
        page.goto(f"file://{html_file}")

        page.screenshot(path=str(output_file), full_page=True)

        browser.close()

    print(f"Screenshot saved to: {output_file}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: capture.py <html-file> <output-png>", file=sys.stderr)
        sys.exit(1)

    capture_page(sys.argv[1], sys.argv[2])
