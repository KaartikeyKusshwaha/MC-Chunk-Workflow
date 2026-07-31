#!/usr/bin/env python3
"""
build_release.py
~~~~~~~~~~~~~~~~
Build the installable Blender addon .zip for MC Chunk Workflow.

Usage (run from the repo root):
    python scripts/build_release.py

Output:
    dist/mc_chunk_workflow_v1.0.0.zip

The zip contains the `mc_chunk_workflow/` package at its root so Blender
can install it directly via Edit → Preferences → Add-ons → Install…
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
ADDON_DIR = REPO_ROOT / "mc_chunk_workflow"
DIST_DIR = REPO_ROOT / "dist"

# Files / dirs to exclude from the zip
EXCLUDES = {
    "__pycache__",
    ".DS_Store",
    "Thumbs.db",
}


# ---------------------------------------------------------------------------
# Version detection
# ---------------------------------------------------------------------------

def read_version() -> str:
    """Parse the version tuple from __init__.py and return it as a string."""
    init_text = (ADDON_DIR / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r'"version":\s*\((\d+),\s*(\d+),\s*(\d+)\)', init_text)
    if not match:
        sys.exit("ERROR: Could not parse version from mc_chunk_workflow/__init__.py")
    return ".".join(match.groups())


# ---------------------------------------------------------------------------
# Zip builder
# ---------------------------------------------------------------------------

def build_zip(version: str) -> Path:
    DIST_DIR.mkdir(exist_ok=True)
    zip_path = DIST_DIR / f"mc_chunk_workflow_v{version}.zip"

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for src in sorted(ADDON_DIR.rglob("*")):
            # Skip excluded names anywhere in the path
            if any(part in EXCLUDES for part in src.parts):
                continue
            if src.is_file():
                # Arc name keeps mc_chunk_workflow/ as the root inside the zip
                arc_name = src.relative_to(REPO_ROOT)
                zf.write(src, arc_name)
                print(f"  + {arc_name}")

    return zip_path


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    version = read_version()
    print(f"Building MC Chunk Workflow v{version} …")
    zip_path = build_zip(version)
    size_kb = zip_path.stat().st_size / 1024
    print(f"\nRelease zip created: {zip_path}  ({size_kb:.1f} KB)")
    print("\nInstall in Blender:")
    print("  Edit > Preferences > Add-ons > Install > select the .zip")


if __name__ == "__main__":
    main()
