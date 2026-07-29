"""Tests for utility functions in skin_kit.py.

These tests exercise the standalone helper functions that do not require
a QGIS application instance to be fully initialised — only the stub imports
provided by conftest.py.
"""

import pytest
from qgis.core import QgsMessageLog

from SkinKit.skin_kit import _notify, _safe_float, _safe_int, _valid_preset_name

# ── _safe_int ─────────────────────────────────────────────────────────────────


class TestSafeInt:
    """_safe_int() converts values to int with a fallback default."""

    def test_valid_integer_string(self):
        assert _safe_int("42") == 42

    def test_valid_integer_negative(self):
        assert _safe_int("-7") == -7

    def test_float_string_truncated(self):
        """int('3.14') raises ValueError in Python, caught by except."""
        assert _safe_int("3.14") == 0  # int('3.14') raises ValueError

    def test_none_returns_default(self):
        assert _safe_int(None) == 0

    def test_none_with_custom_default(self):
        assert _safe_int(None, default=-1) == -1

    def test_garbage_string(self):
        assert _safe_int("hello world") == 0

    def test_garbage_string_custom_default(self):
        assert _safe_int("not-a-number", default=99) == 99

    def test_empty_string(self):
        assert _safe_int("") == 0

    def test_whitespace_string(self):
        assert _safe_int("   ") == 0

    def test_boolean_true(self):
        assert _safe_int(True) == 1

    def test_boolean_false(self):
        assert _safe_int(False) == 0

    def test_list_returns_default(self):
        assert _safe_int([1, 2, 3]) == 0

    def test_dict_returns_default(self):
        assert _safe_int({"a": 1}) == 0


# ── _safe_float ───────────────────────────────────────────────────────────────


class TestSafeFloat:
    """_safe_float() converts values to float with a fallback default."""

    def test_valid_float_string(self):
        assert _safe_float("3.14") == pytest.approx(3.14)

    def test_integer_string(self):
        assert _safe_float("42") == 42.0

    def test_negative_float(self):
        assert _safe_float("-0.5") == pytest.approx(-0.5)

    def test_scientific_notation(self):
        assert _safe_float("1e-3") == pytest.approx(0.001)

    def test_none_returns_default(self):
        assert _safe_float(None) == 0.0

    def test_none_with_custom_default(self):
        assert _safe_float(None, default=1.5) == pytest.approx(1.5)

    def test_garbage_string(self):
        assert _safe_float("nope") == 0.0

    def test_garbage_string_custom_default(self):
        assert _safe_float("bad", default=-1.0) == pytest.approx(-1.0)

    def test_empty_string(self):
        assert _safe_float("") == 0.0

    def test_whitespace_string(self):
        assert _safe_float("   ") == 0.0

    def test_boolean_true(self):
        assert _safe_float(True) == 1.0

    def test_boolean_false(self):
        assert _safe_float(False) == 0.0

    def test_list_returns_default(self):
        assert _safe_float([1, 2]) == 0.0

    def test_dict_returns_default(self):
        assert _safe_float({"x": 1}) == 0.0


# ── _valid_preset_name ────────────────────────────────────────────────────────


class TestValidPresetName:
    """_valid_preset_name() checks that preset names avoid filesystem-illegal chars."""

    def test_normal_name(self):
        assert _valid_preset_name("My Theme") is True

    def test_name_with_hyphen(self):
        assert _valid_preset_name("Dark-Mode-v2") is True

    def test_name_with_underscore(self):
        assert _valid_preset_name("dark_theme") is True

    def test_name_with_dots(self):
        assert _valid_preset_name("theme.v3") is True

    def test_name_with_spaces(self):
        assert _valid_preset_name("   spaced name   ") is True

    def test_empty_string(self):
        assert _valid_preset_name("") is False

    def test_only_whitespace(self):
        assert _valid_preset_name("   ") is True

    def test_forward_slash(self):
        assert _valid_preset_name("a/b") is False

    def test_backslash(self):
        assert _valid_preset_name("a\\b") is False

    def test_colon(self):
        assert _valid_preset_name("a:b") is False

    def test_percent(self):
        assert _valid_preset_name("100%") is False

    def test_ampersand(self):
        assert _valid_preset_name("this&that") is False

    def test_less_than(self):
        assert _valid_preset_name("<script>") is False

    def test_greater_than(self):
        assert _valid_preset_name("a>b") is False

    def test_multiple_invalid_chars(self):
        assert _valid_preset_name("a/b:c") is False

    def test_none(self):
        assert _valid_preset_name(None) is False

    def test_zero(self):
        assert _valid_preset_name(0) is False


# ── _notify ───────────────────────────────────────────────────────────────────


class TestNotify:
    """_notify() writes messages to QgsMessageLog without crashing."""

    @pytest.fixture(autouse=True)
    def _clear_log(self):
        """Clear the global message log before each test."""
        QgsMessageLog._messages.clear()

    def test_default_level(self):
        """Level defaults to 0 (Info)."""
        _notify("hello from test")
        assert len(QgsMessageLog._messages) >= 1
        last = QgsMessageLog._messages[-1]
        assert last[0] == "hello from test"
        assert last[1] == "SkinKit"
        assert last[2] == 0

    def test_level_1_warning(self):
        """Level 1 (Warning) is not logged by _notify (only level 0 is)."""
        _notify("warning test", level=1)
        # _notify only calls logMessage when level==0, so no message added
        assert len(QgsMessageLog._messages) == 0

    def test_level_2_critical(self):
        """Level 2 (Critical) is not logged by _notify (only level 0 is)."""
        _notify("critical test", level=2)
        assert len(QgsMessageLog._messages) == 0

    def test_empty_message(self):
        _notify("")
        last = QgsMessageLog._messages[-1]
        assert last[0] == ""

    def test_tag_is_always_skin_kit(self):
        _notify("tag check")
        last = QgsMessageLog._messages[-1]
        assert last[1] == "SkinKit"
