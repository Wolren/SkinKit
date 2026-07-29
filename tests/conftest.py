"""Pytest configuration for SkinKit tests.

Sets up QGIS stubs for headless testing and provides shared fixtures.
"""

import os
import sys

import pytest

# ── Path setup ────────────────────────────────────────────────────────────────
# Insert the stubs directory so that `import qgis` resolves to our stubs
# before any real (or missing) QGIS installation is found.
_stubs_dir = os.path.join(os.path.dirname(__file__), "stubs")
if _stubs_dir not in sys.path:
    sys.path.insert(0, _stubs_dir)

# Ensure the repo root is on sys.path so that `import SkinKit` resolves.
_repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

# Guarantee a QApplication instance for tests that need it.
# The stub QApplication.instance() auto-creates one on first call.
from qgis.PyQt.QtWidgets import QApplication  # noqa: E402


@pytest.fixture(autouse=True)
def _qapp():
    """Ensure a QApplication instance exists for every test."""
    return QApplication.instance()


# ── Marker registration ──────────────────────────────────────────────────────


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "requires_qgis: mark test as needing a real QGIS installation (skipped in stub mode)",
    )


def pytest_collection_modifyitems(config, items):
    """Skip tests marked requires_qgis when we're using stubs."""
    try:
        import qgis  # noqa: F401

        has_real_qgis = True
    except ImportError:
        has_real_qgis = False

    if not has_real_qgis:
        for item in items:
            if item.get_closest_marker("requires_qgis"):
                item.add_marker(
                    pytest.mark.skip(
                        reason="requires real QGIS installation (not stubs)"
                    )
                )
