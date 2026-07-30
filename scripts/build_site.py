#!/usr/bin/env python3
"""Build the public Cloudflare Pages asset directory from an explicit allowlist."""

from __future__ import annotations

import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "dist"
TEMP_DIR = PROJECT_ROOT / ".dist-build"

PUBLIC_FILES = (
    "404.html",
    "_headers",
    "about.html",
    "china-sourcing.html",
    "contact.html",
    "contact.js",
    "d20ec9908a240ebbdc5b5b295ea324b4.txt",
    "ddp-shipping-from-china.html",
    "faq.html",
    "favicon.svg",
    "freight-from-china.html",
    "googlebdcd5011c88334e9.html",
    "hardware-startup-supply-chain-china.html",
    "index.html",
    "insights/china-supplier-evaluation-checklist.html",
    "insights/ddp-vs-dap-shipping-from-china.html",
    "insights/how-to-source-products-from-china-without-an-in-house-team.html",
    "insights/index.html",
    "llms.txt",
    "logo-512.png",
    "og-image.png",
    "privacy.html",
    "quality-inspection.html",
    "robots.txt",
    "services.html",
    "sitemap.xml",
    "styles.css",
)


def remove_build_directory(path: Path) -> None:
    resolved = path.resolve()
    if resolved.parent != PROJECT_ROOT.resolve():
        raise RuntimeError(f"Refusing to remove a directory outside the project root: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)


def main() -> int:
    missing = [relative for relative in PUBLIC_FILES if not (PROJECT_ROOT / relative).is_file()]
    if missing:
        raise SystemExit(f"Build stopped because public source files are missing: {', '.join(missing)}")

    remove_build_directory(TEMP_DIR)
    TEMP_DIR.mkdir()

    for relative in PUBLIC_FILES:
        source = PROJECT_ROOT / relative
        destination = TEMP_DIR / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    copied = sorted(
        path.relative_to(TEMP_DIR).as_posix()
        for path in TEMP_DIR.rglob("*")
        if path.is_file()
    )
    expected = sorted(PUBLIC_FILES)
    if copied != expected:
        raise SystemExit("Build output did not match the public-file allowlist")

    blocked_names = {".github", "seo", "memory", "scripts", "functions", "README.md"}
    if any(part in blocked_names for path in TEMP_DIR.rglob("*") for part in path.relative_to(TEMP_DIR).parts):
        raise SystemExit("Build output contains a blocked internal path")

    remove_build_directory(OUTPUT_DIR)
    TEMP_DIR.rename(OUTPUT_DIR)
    print(f"Built {len(PUBLIC_FILES)} public files in {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
