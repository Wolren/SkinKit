#!/usr/bin/env python3
"""Build a clean QGIS plugin zip for publishing."""

import configparser
import os
import re
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
PLUGIN_DIR = os.path.join(ROOT, "SkinKit")
METADATA = os.path.join(PLUGIN_DIR, "metadata.txt")
OUTPUT_DIR = ROOT

SKIP_DIRS = {
    "__pycache__",
    ".git",
    ".idea",
    ".vscode",
    ".ruff_cache",
    "__MACOSX",
}
SKIP_FILES = {
    ".DS_Store",
    "Thumbs.db",
    "*.pyc",
    "*.pyo",
}


def _should_skip(name, is_dir):
    if is_dir and name in SKIP_DIRS:
        return True
    if not is_dir and name in SKIP_FILES:
        return True
    if not is_dir and re.search(r"\.pyc$|\.pyo$", name):
        return True
    return False


def read_version():
    cfg = configparser.ConfigParser()
    cfg.read(METADATA, encoding="utf-8")
    return cfg.get("general", "version", fallback="0.0")


def build_zip():
    version = read_version()
    zip_name = f"SkinKit-{version}.zip"
    zip_path = os.path.join(OUTPUT_DIR, zip_name)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(PLUGIN_DIR):
            dirs[:] = [d for d in dirs if not _should_skip(d, True)]
            for f in files:
                if _should_skip(f, False):
                    continue
                full = os.path.join(root, f)
                arcname = os.path.relpath(full, ROOT)
                zf.write(full, arcname)

    print(f"Created: {zip_path}")
    return zip_path


if __name__ == "__main__":
    build_zip()
