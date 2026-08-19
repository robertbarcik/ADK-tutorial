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

The script is idempotent — on repeat runs it strips any previously-inlined
blocks and re-inlines fresh content from the canonical sources. That means
editing slides/shared/shared.css (say, to change a font) and re-running the
script will propagate the change to every deck.

Run from the repo root or the slides/ directory:
    python3 slides/build_slides.py
"""

import re
import sys
from pathlib import Path

SLIDES_DIR = Path(__file__).resolve().parent
SHARED_DIR = SLIDES_DIR / "shared"

# Sentinel comments so we can find + replace our own blocks on repeat runs.
STYLE_SENTINEL_START = "<!-- BEGIN-INLINED-STYLES -->"
STYLE_SENTINEL_END = "<!-- END-INLINED-STYLES -->"
SCRIPT_SENTINEL_START = "<!-- BEGIN-INLINED-SCRIPT -->"
SCRIPT_SENTINEL_END = "<!-- END-INLINED-SCRIPT -->"
BUILD_BANNER = "<!-- Built by slides/build_slides.py — shared CSS/JS inlined for file:// portability. Edit sources in slides/shared/ and re-run. -->"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_style_block(shared_css: str, slides_css: str) -> str:
    return (
        f"{STYLE_SENTINEL_START}\n"
        "  <style>\n"
        "  /* shared.css — generated; edit slides/shared/shared.css */\n"
        f"{shared_css.strip()}\n"
        "  /* slides.css — generated; edit slides/shared/slides.css */\n"
        f"{slides_css.strip()}\n"
        "  </style>\n"
        f"  {STYLE_SENTINEL_END}"
    )


def build_script_block(slides_js: str) -> str:
    return (
        f"{SCRIPT_SENTINEL_START}\n"
        "<script>\n"
        f"{slides_js.strip()}\n"
        "</script>\n"
        f"{SCRIPT_SENTINEL_END}"
    )


def inline_deck(html_path: Path, style_block: str, script_block: str) -> bool:
    """Inline shared assets into one deck's index.html. Return True if changed."""
    original = html_path.read_text(encoding="utf-8")
    modified = original

    # 1) Strip any previously-inlined style block.
    modified = re.sub(
        re.escape(STYLE_SENTINEL_START) + r".*?" + re.escape(STYLE_SENTINEL_END),
        "",
        modified,
        flags=re.DOTALL,
    )
    # 2) Strip any previously-inlined script block.
    modified = re.sub(
        re.escape(SCRIPT_SENTINEL_START) + r".*?" + re.escape(SCRIPT_SENTINEL_END),
        "",
        modified,
        flags=re.DOTALL,
    )

    # 3) Strip any <link rel=stylesheet> pointing at ../shared/*.css.
    modified = re.sub(
        r'\s*<link\s+rel=["\']stylesheet["\']\s+href=["\']\.\./shared/(shared|slides)\.css["\']\s*/?>\s*',
        "",
        modified,
    )
    # 4) Strip any <script src=../shared/slides.js>.
    modified = re.sub(
        r'\s*<script\s+src=["\']\.\./shared/slides\.js["\']\s*>\s*</script>\s*',
        "",
        modified,
    )

    # 5) Inject style block just before </head>.
    if "</head>" in modified:
        modified = modified.replace(
            "</head>", f"\n  {style_block}\n</head>", 1
        )
    else:
        modified = style_block + modified

    # 6) Inject script block just before </body>.
    if "</body>" in modified:
        modified = modified.replace(
            "</body>", f"\n  {script_block}\n</body>", 1
        )
    else:
        modified = modified + "\n" + script_block

    # 7) Ensure the build banner is present right after <!DOCTYPE html>.
    modified = re.sub(
        r"<!-- Built by slides/build_slides\.py.*?-->\n?",
        "",
        modified,
    )
    modified = re.sub(
        r"(<!DOCTYPE html>\s*)",
        r"\1" + BUILD_BANNER + "\n",
        modified,
        count=1,
    )

    # 8) Collapse excessive blank lines the re-write can introduce.
    modified = re.sub(r"\n{3,}", "\n\n", modified)

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

    style_block = build_style_block(shared_css, slides_css)
    script_block = build_script_block(slides_js)

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
        if inline_deck(html_path, style_block, script_block):
            print(f"  ✓ {mod.name}: rebuilt")
            changed += 1
        else:
            print(f"  - {mod.name}: already up to date")

    print(f"\n{changed} of {len(module_dirs)} deck(s) updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
