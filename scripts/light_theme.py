"""Remove Widoco's dark-mode switching so the docs always use Widoco's default (light) styling.

Widoco 1.4.26 picks dark.css when the reader's OS prefers dark mode and adds a toggle;
it has no option to turn this off.

usage: light_theme.py SITE_DIR
"""
import re
import sys
from pathlib import Path

EDITS = [
    (r'<link rel="stylesheet" href="([./]*)resources/dark\.css"[^>]*/?>\s*', ""),
    (r'<link rel="stylesheet" href="([./]*)resources/slider\.css"[^>]*/?>\s*', ""),
    (r'(<link rel="stylesheet" href="[./]*resources/light\.css") media="\(prefers-color-scheme: light\)"',
     r'\1 media="screen"'),
    (r'<meta name="color-scheme" content="dark light">', '<meta name="color-scheme" content="light">'),
    (r'<script type="module" src="[./]*resources/dark-mode-toggle\.mjs"></script>', ""),
    (r'<div class="darkmode">\s*<dark-mode-toggle[^>]*></dark-mode-toggle>\s*</div>\s*', ""),
]

site = Path(sys.argv[1])
for page in site.rglob("*.html"):
    html = page.read_text(encoding="utf-8")
    new = html
    for pattern, repl in EDITS:
        new = re.sub(pattern, repl, new)
    if new != html:
        page.write_text(new, encoding="utf-8")
        print(f"light theme: {page}")
for asset in ["dark.css", "slider.css", "dark-mode-toggle.mjs", "moon.svg", "sun.svg"]:
    (site / "resources" / asset).unlink(missing_ok=True)
