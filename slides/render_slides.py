#!/usr/bin/env python3
"""Render every slide in every deck to a JPG (or PNG) for video editing.

Produces one image per slide at 1920×1080 under `slides-jpg/module-NN-slug/NN.jpg`.
Useful when you're recording a voiceover from the speaker notes and need
per-slide stills to drop into a video editor.

Under the hood: headless Chromium (via Playwright). Each deck's self-contained
HTML is loaded, each slide is shown one at a time (via direct DOM manipulation
so we don't fight the deck's navigation IIFE), and each frame is screenshot.

Usage:
    # Render all decks to JPG at 1920×1080, quality 92
    python3 slides/render_slides.py

    # Render a single module
    python3 slides/render_slides.py --module 01

    # Output PNG instead of JPG (lossless; bigger files)
    python3 slides/render_slides.py --format png

    # Different resolution (e.g. 1280×720 for smaller drafts)
    python3 slides/render_slides.py --width 1280 --height 720

First-time setup:
    pip install playwright
    python3 -m playwright install chromium
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    sys.stderr.write(
        "ERROR: Playwright is not installed. Install it with:\n"
        "    pip install playwright\n"
        "    python3 -m playwright install chromium\n"
    )
    sys.exit(1)


SLIDES_DIR = Path(__file__).resolve().parent
OUT_DIR_DEFAULT = SLIDES_DIR.parent / "slides-jpg"


async def render_deck(
    browser,
    module_dir: Path,
    out_root: Path,
    viewport: dict,
    fmt: str,
    quality: int,
) -> int:
    """Render one deck. Returns number of slides rendered."""
    html_path = (module_dir / "index.html").resolve()
    if not html_path.exists():
        print(f"  ! {module_dir.name}: no index.html, skipping")
        return 0

    out_dir = out_root / module_dir.name
    out_dir.mkdir(parents=True, exist_ok=True)

    context = await browser.new_context(viewport=viewport, device_scale_factor=1)
    page = await context.new_page()
    await page.goto(html_path.as_uri(), wait_until="domcontentloaded")

    # Wait for web fonts (Nunito via Google Fonts @import) to finish loading
    # so the first screenshot doesn't catch a fallback-font flash.
    await page.evaluate("() => document.fonts.ready")

    count = await page.evaluate("() => document.querySelectorAll('.slide').length")
    if count == 0:
        print(f"  ! {module_dir.name}: zero slides found, skipping")
        await context.close()
        return 0

    # Hide the progress strip so the slide uses the full 1920×1080 frame.
    # (Comment out this line if you WANT the strip visible — it's a one-liner.)
    await page.add_style_tag(
        content=".progress-strip, .font-controls { display: none !important; } "
        ".slide-viewport { top: 0 !important; }"
    )

    for n in range(1, count + 1):
        # Swap which slide is .active directly via the DOM.
        # This avoids fighting the deck's IIFE navigation functions.
        await page.evaluate(
            f"""() => {{
                const slides = document.querySelectorAll('.slide');
                slides.forEach(s => s.classList.remove('active'));
                slides[{n - 1}].classList.add('active');
                window.scrollTo(0, 0);
            }}"""
        )
        # A short pause lets any fadeIn animation settle.
        await page.wait_for_timeout(120)

        out_path = out_dir / f"{n:02d}.{fmt}"
        if fmt == "jpg":
            await page.screenshot(
                path=str(out_path), type="jpeg", quality=quality, full_page=False
            )
        else:
            await page.screenshot(path=str(out_path), type="png", full_page=False)

    await context.close()
    print(f"  ✓ {module_dir.name}: {count} slide(s) → {out_dir.relative_to(SLIDES_DIR.parent)}/")
    return count


async def main_async(args) -> int:
    viewport = {"width": args.width, "height": args.height}
    out_root = Path(args.out).resolve()
    fmt = "jpg" if args.format == "jpg" else "png"

    all_mods = sorted(p for p in SLIDES_DIR.iterdir() if p.is_dir() and p.name.startswith("module-"))
    if args.module:
        needle = args.module.strip()
        mods = [p for p in all_mods if p.name.startswith(f"module-{needle.zfill(2)}-")]
        if not mods:
            sys.stderr.write(f"ERROR: no module found matching '{needle}'\n")
            return 1
    else:
        mods = all_mods

    print(f"Rendering {len(mods)} deck(s) at {args.width}×{args.height} as {fmt.upper()}")
    print(f"Output: {out_root}\n")
    t0 = time.time()
    total = 0

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        try:
            for mod in mods:
                total += await render_deck(
                    browser=browser,
                    module_dir=mod,
                    out_root=out_root,
                    viewport=viewport,
                    fmt=fmt,
                    quality=args.quality,
                )
        finally:
            await browser.close()

    elapsed = time.time() - t0
    print(f"\n{total} slide(s) rendered in {elapsed:.1f}s "
          f"(~{elapsed / max(total, 1):.2f}s per slide)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render all slides to images for video editing.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--module", help="Only render this module (e.g. '01', '05', '11')")
    parser.add_argument("--out", default=str(OUT_DIR_DEFAULT),
                        help=f"Output directory (default: {OUT_DIR_DEFAULT})")
    parser.add_argument("--format", choices=["jpg", "png"], default="jpg",
                        help="Output format (default: jpg)")
    parser.add_argument("--width", type=int, default=1920, help="Viewport width (default: 1920)")
    parser.add_argument("--height", type=int, default=1080, help="Viewport height (default: 1080)")
    parser.add_argument("--quality", type=int, default=92,
                        help="JPG quality 1–100, ignored for PNG (default: 92)")
    args = parser.parse_args()

    return asyncio.run(main_async(args))


if __name__ == "__main__":
    raise SystemExit(main())
