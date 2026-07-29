"""Tests for SkinKit plugin structure that do not require QGIS.

Validates metadata, file existence, module syntax, and entry-point signatures
using only Python stdlib.
"""

import ast
import configparser
import os
import sys

import pytest

# ── Path setup ────────────────────────────────────────────────────────────────
# Find the plugin directory relative to this test file.
_tests_dir = os.path.dirname(os.path.abspath(__file__))
_repo_root = os.path.dirname(_tests_dir)
_plugin_dir = os.path.join(_repo_root, "SkinKit")

# Ensure repo root is on sys.path so we can import SkinKit.__init__
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)


# ── metadata.txt ──────────────────────────────────────────────────────────────


class TestMetadataTxt:
    """metadata.txt must contain all fields required by QGIS plugin manager."""

    REQUIRED_FIELDS = [
        "name",
        "qgisMinimumVersion",
        "description",
        "version",
        "author",
        "email",
        "about",
        "tracker",
        "repository",
        "tags",
        "icon",
        "category",
        "experimental",
    ]

    @pytest.fixture
    def metadata(self):
        """Parse metadata.txt."""
        path = os.path.join(_plugin_dir, "metadata.txt")
        assert os.path.isfile(path), f"metadata.txt not found at {path}"
        config = configparser.ConfigParser()
        config.read(path, encoding="utf-8")
        return config

    def test_file_exists(self):
        path = os.path.join(_plugin_dir, "metadata.txt")
        assert os.path.isfile(path), "metadata.txt is missing"

    def test_has_general_section(self, metadata):
        assert "general" in metadata, "metadata.txt missing [general] section"

    def test_required_fields_present(self, metadata):
        section = metadata["general"]
        missing = [f for f in self.REQUIRED_FIELDS if f not in section]
        assert not missing, f"metadata.txt missing fields: {missing}"

    def test_name_is_skin_kit(self, metadata):
        assert metadata["general"].get("name", "").lower() == "skinkit"

    def test_version_is_non_empty(self, metadata):
        assert metadata["general"].get("version", "").strip(), "version is empty"

    def test_version_follows_semver(self, metadata):
        version = metadata["general"].get("version", "")
        # Accept x.y or x.y.z
        parts = version.split(".")
        assert len(parts) >= 2, f"version '{version}' is not semver"
        assert all(p.isdigit() for p in parts), f"version '{version}' has non-numeric parts"

    def test_qgis_min_version_is_reasonable(self, metadata):
        min_ver = metadata["general"].get("qgisMinimumVersion", "")
        parts = min_ver.split(".")
        assert len(parts) == 2, f"qgisMinimumVersion '{min_ver}' should be X.Y"
        major, minor = int(parts[0]), int(parts[1])
        assert major >= 3, "QGIS version should be 3.x or higher"
        assert 0 <= minor <= 99

    def test_email_looks_valid(self, metadata):
        email = metadata["general"].get("email", "")
        assert "@" in email, f"email '{email}' missing @"
        assert "." in email.split("@")[-1], f"email '{email}' missing domain"

    def test_license_is_gpl(self, metadata):
        assert metadata["general"].get("license", "") == "GPL-3.0-only"

    def test_category_is_plugins(self, metadata):
        assert metadata["general"].get("category", "").lower() == "plugins"

    def test_icon_path_is_relative(self, metadata):
        icon = metadata["general"].get("icon", "")
        assert icon, "icon field is empty"
        assert not icon.startswith("/"), "icon should be a relative path"
        assert not icon.startswith("\\"), "icon should be a relative path"

    def test_experimental_is_false(self, metadata):
        assert metadata["general"].get("experimental", "").lower() == "false"

    def test_deprecated_is_false(self, metadata):
        assert metadata["general"].get("deprecated", "").lower() == "false"

    def test_tags_are_comma_separated(self, metadata):
        tags = metadata["general"].get("tags", "")
        assert tags, "tags field is empty"
        assert "," in tags, "tags should be comma-separated"
        assert len(tags.split(",")) >= 5, "should have at least 5 tags"

    def test_tracker_is_github_issues(self, metadata):
        url = metadata["general"].get("tracker", "")
        assert "github.com" in url.lower() or "issues" in url.lower()

    def test_repository_is_github(self, metadata):
        url = metadata["general"].get("repository", "")
        assert "github.com/Wolren/SkinKit" in url


# ── Icon file ─────────────────────────────────────────────────────────────────


class TestIconFile:
    """Plugin icon must exist and be a valid file."""

    def test_icon_png_exists(self):
        path = os.path.join(_plugin_dir, "icons", "icon.png")
        assert os.path.isfile(path), f"Icon not found at {path}"

    def test_icon_is_non_empty(self):
        path = os.path.join(_plugin_dir, "icons", "icon.png")
        size = os.path.getsize(path)
        assert size > 0, "icon.png is empty"
        assert size > 100, f"icon.png is only {size} bytes — likely a placeholder"

    def test_icon_metadata_matches(self):
        """The icon declared in metadata.txt matches the filesystem."""
        icon_field = _read_metadata_value("icon")
        expected = os.path.normpath(icon_field)
        full = os.path.join(_plugin_dir, expected)
        assert os.path.isfile(full), f"Icon path '{expected}' resolves to {full} which doesn't exist"


# ── __init__.py — entry points ────────────────────────────────────────────────


class TestInitPy:
    """__init__.py must expose classFactory with the correct signature."""

    @pytest.fixture
    def plugin_init(self):
        """Import the plugin's __init__ module."""
        import SkinKit  # noqa: F811
        return SkinKit

    def test_classFactory_exists(self, plugin_init):
        assert hasattr(plugin_init, "classFactory"), "classFactory not found in __init__"

    def test_classFactory_is_callable(self, plugin_init):
        assert callable(plugin_init.classFactory)

    def test_classFactory_takes_one_arg(self, plugin_init):
        import inspect
        sig = inspect.signature(plugin_init.classFactory)
        params = list(sig.parameters.keys())
        assert len(params) == 1, f"classFactory expects {len(params)} params, expected 1"
        assert params[0] == "iface"

    def test_metadata_function_exists(self, plugin_init):
        assert hasattr(plugin_init, "metadata")

    def test_metadata_is_callable(self, plugin_init):
        assert callable(plugin_init.metadata)

    def test_metadata_returns_dict(self, plugin_init):
        result = plugin_init.metadata()
        assert isinstance(result, dict)

    def test_metadata_has_name(self, plugin_init):
        result = plugin_init.metadata()
        assert "name" in result
        assert result["name"] == "SkinKit"

    def test_metadata_has_version(self, plugin_init):
        result = plugin_init.metadata()
        assert "version" in result
        assert result["version"] == "1.0.1"

    def test_module_level_name_constant(self, plugin_init):
        assert plugin_init.name == "SkinKit"


# ── Source file syntax validation ─────────────────────────────────────────────


class TestSourceSyntax:
    """All source files must be syntactically valid Python."""

    SOURCE_FILES = [
        "__init__.py",
        "skin_kit.py",
        "bg_painter.py",
        "qss_highlighter.py",
        "skin_kit_dialog.py",
    ]

    def test_all_source_files_listed_exist(self):
        for fname in self.SOURCE_FILES:
            path = os.path.join(_plugin_dir, fname)
            assert os.path.isfile(path), f"Source file {fname} missing"

    def test_each_file_parses_as_valid_python(self):
        for fname in self.SOURCE_FILES:
            path = os.path.join(_plugin_dir, fname)
            with open(path, encoding="utf-8") as f:
                source = f.read()
            try:
                ast.parse(source, filename=fname)
            except SyntaxError as e:
                pytest.fail(f"Syntax error in {fname}: {e}")

    def test_no_tab_indentation(self):
        """All source files use spaces (not tabs)."""
        for fname in self.SOURCE_FILES:
            path = os.path.join(_plugin_dir, fname)
            with open(path, encoding="utf-8") as f:
                for lineno, line in enumerate(f, 1):
                    if "\t" in line:
                        pytest.fail(f"Tab found in {fname} at line {lineno}")

    def test_no_trailing_whitespace(self):
        """Source files should not have trailing whitespace."""
        for fname in self.SOURCE_FILES:
            path = os.path.join(_plugin_dir, fname)
            with open(path, encoding="utf-8") as f:
                for lineno, line in enumerate(f, 1):
                    if line.rstrip("\n").endswith((" ", "\t")):
                        pytest.fail(f"Trailing whitespace in {fname} at line {lineno}")

    def test_files_end_with_newline(self):
        for fname in self.SOURCE_FILES:
            path = os.path.join(_plugin_dir, fname)
            with open(path, encoding="utf-8") as f:
                content = f.read()
            assert content.endswith("\n"), f"{fname} does not end with a newline"


# ── Package structure ─────────────────────────────────────────────────────────


class TestPackageStructure:
    """The SkinKit package directory has the expected layout."""

    def test_plugin_dir_is_correct(self):
        assert os.path.isdir(_plugin_dir)
        assert _plugin_dir.endswith("SkinKit")

    def test_builtin_themes_directory_exists(self):
        themes_dir = os.path.join(_plugin_dir, "builtin_themes")
        assert os.path.isdir(themes_dir), "builtin_themes/ directory missing"

    def test_builtin_themes_have_content(self):
        themes_dir = os.path.join(_plugin_dir, "builtin_themes")
        entries = [d for d in os.listdir(themes_dir) if os.path.isdir(os.path.join(themes_dir, d)) or d.endswith(".qss")]
        assert len(entries) >= 3, f"Only {len(entries)} theme entries found, expected >= 3"

    def test_icons_directory_exists(self):
        icons_dir = os.path.join(_plugin_dir, "icons")
        assert os.path.isdir(icons_dir)

    def test_all_python_files_have_docstrings(self):
        """Every module-level .py file should start with a docstring."""
        for fname in ["__init__.py", "skin_kit.py", "bg_painter.py", "qss_highlighter.py", "skin_kit_dialog.py"]:
            path = os.path.join(_plugin_dir, fname)
            with open(path, encoding="utf-8") as f:
                source = f.read()
            module = ast.parse(source, filename=fname)
            docstring = ast.get_docstring(module)
            assert docstring, f"{fname} is missing a module-level docstring"

    def test_package_exports_classFactory(self):
        """The plugin package exports the symbols QGIS expects."""
        import SkinKit
        assert hasattr(SkinKit, "classFactory")
        assert hasattr(SkinKit, "metadata")
        assert hasattr(SkinKit, "name")


# ── pyproject.toml ────────────────────────────────────────────────────────────


class TestPyproject:
    """pyproject.toml contains project metadata and tool config."""

    @pytest.fixture
    def pyproject_path(self):
        path = os.path.join(_repo_root, "pyproject.toml")
        assert os.path.isfile(path)
        return path

    def test_exists(self):
        assert os.path.isfile(os.path.join(_repo_root, "pyproject.toml"))

    def test_contains_pytest_config(self, pyproject_path):
        """pyproject.toml should configure pytest testpaths."""
        import tomllib
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        testpaths = data.get("tool", {}).get("pytest", {}).get("ini_options", {}).get("testpaths", [])
        assert "tests" in testpaths, "pytest testpaths should include tests/"

    def test_contains_ruff_config(self, pyproject_path):
        import tomllib
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        assert "ruff" in data.get("tool", {}), "pyproject.toml should have [tool.ruff]"

    def test_python_requirement(self, pyproject_path):
        import tomllib
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        req = data.get("project", {}).get("requires-python", "")
        assert req >= ">=3.9", f"requires-python should be >=3.9, got {req}"


# ── Helpers ───────────────────────────────────────────────────────────────────


def _read_metadata_value(field):
    """Read a single field from metadata.txt."""
    path = os.path.join(_plugin_dir, "metadata.txt")
    config = configparser.ConfigParser()
    config.read(path, encoding="utf-8")
    return config["general"].get(field, "")
