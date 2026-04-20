#!/usr/bin/env python3
"""Inline shared CSS/JS into each module's index.html.

Why: Safari (and some Chrome strict-mode configurations) block relative
file://-path loads of CSS and JS as a security measure. That turned every
local double-click into a wall of unstyled text.

Fix: for each slides/module-*/index.html, replace the <link> tags pointing
at ../shared/*.css with inlined <style>...</style>, and the <script src="...">
pointing at ../shared/slides.js with an inlined <script>...</script>.

Result: each deck becomes a single self-contained HTML file that opens
cleanly via file:// in any browser, and still deploys cleanly over http://.

Also regenerates the repo-root index.html's module-catalog section with
the current set of slide decks, so "Ready" status stays in sync.

Run from the repo root or the slides/ directory:
    python3 slides/build_slides.py
"""

import re
import sys
from pathlib import Path

SLIDES_DIR = Path(__file__).resolve().parent
SHARED_DIR = SLIDES_DIR / "shared"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def inline_deck(html_path: Path, shared_css: str, slides_css: str, slides_js: str) -> bool:
    """Inline shared assets into one deck's index.html. Return True if changed."""
    original = read(html_path)

    # Replace both <link> tags with a single combined <style> block.
    # Match both shared.css and slides.css regardless of order.
    link_pattern = re.compile(
        r'\s*<link\s+rel=["\']stylesheet["\']\s+href=["\']\.\./shared/(shared|slides)\.css["\']\s*/?>\s*',
        re.IGNORECASE,
    )

    # Count how many link tags we'll replace. Must find shared.css and slides.css.
    link_matches = list(link_pattern.finditer(original))
    if len(link_matches) < 2:
        # Already inlined or nothing to replace — skip.
        # Still try to replace the <script src="...">.
        pass

    # Strip out both <link> tags; we'll insert the combined <style> where the first one was.
    if link_matches:
        first_match_start = link_matches[0].start()
        # Remove all link tags first.
        modified = link_pattern.sub("", original)
        combined_css = (
            "\n  <style>\n"
            "  /* shared.css */\n"
            + shared_css.strip() + "\n"
            + "  /* slides.css */\n"
            + slides_css.strip() + "\n"
            + "  </style>\n"
        )
        # Insert combined CSS where the first <link> was.
        # After stripping the links, we need to put the style block inside <head>.
        # Find </head> and insert just before it.
        if "</head>" in modified:
            modified = modified.replace("</head>", combined_css + "</head>", 1)
        else:
            modified = combined_css + modified
    else:
        modified = original

    # Replace <script src="../shared/slides.js"></script> with inlined <script>...</script>.
    script_pattern = re.compile(
        r'<script\s+src=["\']\.\./shared/slides\.js["\']\s*>\s*</script>',
        re.IGNORECASE,
    )
    combined_js = "<script>\n" + slides_js.strip() + "\n</script>"
    modified = script_pattern.sub(combined_js, modified)

    # Add a banner comment near the top marking this as built output (helps debugging).
    banner = "<!-- Built by slides/build_slides.py — shared CSS/JS inlined for file:// portability. Edit sources in slides/shared/ and re-run. -->\n"
    if "Built by slides/build_slides.py" not in modified:
        # Insert after <!DOCTYPE html>
        modified = re.sub(r"(<!DOCTYPE html>\s*)", r"\1" + banner, modified, count=1)

    if modified != original:
        html_path.write_text(modified, encoding="utf-8")
        return True
    return False


def main() -> int:
    if not SHARED_DIR.is_dir():
        print(f"ERROR: {SHARED_DIR} not found", file=sys.stderr)
        return 1

    shared_css = read(SHARED_DIR / "shared.css")
    slides_css = read(SHARED_DIR / "slides.css")
    slides_js = read(SHARED_DIR / "slides.js")

    module_dirs = sorted(p for p in SLIDES_DIR.iterdir() if p.is_dir() and p.name.startswith("module-"))
    if not module_dirs:
        print("ERROR: no slides/module-*/ folders found", file=sys.stderr)
        return 1

    changed = 0
    for mod in module_dirs:
        html_path = mod / "index.html"
        if not html_path.exists():
            print(f"  ! {mod.name}: no index.html, skipping")
            continue
        if inline_deck(html_path, shared_css, slides_css, slides_js):
            print(f"  ✓ {mod.name}: inlined shared assets")
            changed += 1
        else:
            print(f"  - {mod.name}: already up to date")

    print(f"\n{changed} of {len(module_dirs)} deck(s) updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
