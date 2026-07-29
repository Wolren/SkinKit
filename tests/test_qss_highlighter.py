"""Tests for the QSS syntax highlighter in qss_highlighter.py.

Exercises _fmt(), _color_fmt(), and QSSHighlighter pattern matching
using stub QGIS/PyQt classes.
"""

from qgis.PyQt.QtCore import QRegularExpression
from qgis.PyQt.QtGui import QFont, QTextCharFormat

from SkinKit.qss_highlighter import QSSHighlighter, _color_fmt, _fmt

# ── _fmt ──────────────────────────────────────────────────────────────────────


class TestFmt:
    """_fmt() creates a QTextCharFormat with the requested styling."""

    def test_returns_qtextcharformat(self):
        result = _fmt("#ff0000")
        assert isinstance(result, QTextCharFormat)

    def test_sets_foreground_color(self):
        result = _fmt("#ff0000")
        assert result._foreground is not None
        assert result._foreground.name() == "#ff0000"

    def test_default_not_bold(self):
        result = _fmt("#00ff00")
        assert result._font_weight < QFont.Bold

    def test_bold_true(self):
        result = _fmt("#0000ff", bold=True)
        assert result._font_weight >= QFont.Bold

    def test_default_not_italic(self):
        result = _fmt("#ffffff")
        assert result._font_italic is False

    def test_italic_true(self):
        result = _fmt("#000000", italic=True)
        assert result._font_italic is True

    def test_bold_and_italic_together(self):
        result = _fmt("#123456", bold=True, italic=True)
        assert result._font_weight >= QFont.Bold
        assert result._font_italic is True

    def test_correct_color_for_different_inputs(self):
        colors = ["#ff0000", "#00ff00", "#0000ff", "#ffffff", "#000000"]
        for c in colors:
            result = _fmt(c)
            assert result._foreground is not None
            assert result._foreground.name() == c


# ── _color_fmt ────────────────────────────────────────────────────────────────


class TestColorFmt:
    """_color_fmt() creates a format with a background colour swatch."""

    def test_returns_qtextcharformat(self):
        result = _color_fmt("#ff0000")
        assert isinstance(result, QTextCharFormat)

    def test_sets_background_color(self):
        result = _color_fmt("#ff0000")
        assert result._background is not None

    def test_sets_foreground_to_white_for_dark_colors(self):
        """Black background → white text (luma <= 128)."""
        result = _color_fmt("#000000")
        assert result._foreground.name() == "#ffffff"

    def test_sets_foreground_to_black_for_light_colors(self):
        """White background → black text (luma > 128)."""
        result = _color_fmt("#ffffff")
        assert result._foreground.name() == "#000000"

    def test_medium_brightness(self):
        """#777777 has luma ~119.4, so foreground should be white."""
        result = _color_fmt("#777777")
        assert result._foreground.name() == "#ffffff"

    def test_bright_pastel(self):
        """#ffcc00 is bright → black foreground."""
        result = _color_fmt("#ffcc00")
        assert result._foreground.name() == "#000000"

    def test_invalid_hex_does_not_raise(self):
        """Garbage hex should be silently handled."""
        # This should not raise an exception due to the try/except
        result = _color_fmt("not-a-color")
        assert isinstance(result, QTextCharFormat)

    def test_short_hex_3_digit(self):
        """3-digit hex codes are valid CSS colors."""
        result = _color_fmt("#f00")  # equivalent to #ff0000
        assert result._background is not None
        assert result._background.isValid()
        assert result._background.name() == "#ff0000"

    def test_8_digit_hex(self):
        result = _color_fmt("#ff000080")  # red with alpha
        assert result._background is not None


# ── QSSHighlighter rules ─────────────────────────────────────────────────────


class TestQSSHighlighterRules:
    """QSSHighlighter.RULES compile into valid QRegularExpressions."""

    def test_rules_is_list_of_tuples(self):
        assert isinstance(QSSHighlighter.RULES, list)
        assert len(QSSHighlighter.RULES) > 0
        for rule in QSSHighlighter.RULES:
            assert isinstance(rule, tuple)
            assert len(rule) == 2
            pattern, fmt = rule
            assert isinstance(pattern, str)
            assert isinstance(fmt, QTextCharFormat)

    def test_all_patterns_compile(self):
        """Every pattern string is a valid regular expression."""
        for pattern, _ in QSSHighlighter.RULES:
            rx = QRegularExpression(pattern)
            # Compilation check: match empty string, no exception
            rx.match("")

    def test_all_patterns_produce_text_char_format(self):
        for _, fmt in QSSHighlighter.RULES:
            assert isinstance(fmt, QTextCharFormat)


# ── QSSHighlighter construction ───────────────────────────────────────────────


class TestQSSHighlighterInit:
    """QSSHighlighter initialisation."""

    def test_initialises_with_document(self):
        doc = _FakeDocument()
        hl = QSSHighlighter(doc)
        assert hl._document is doc

    def test_rules_are_compiled(self):
        doc = _FakeDocument()
        hl = QSSHighlighter(doc)
        assert hasattr(hl, "_rules")
        assert len(hl._rules) == len(QSSHighlighter.RULES)
        for rx, _ in hl._rules:
            assert isinstance(rx, QRegularExpression)

    def test_comment_format_exists(self):
        doc = _FakeDocument()
        hl = QSSHighlighter(doc)
        assert hl._comment_fmt is not None
        assert isinstance(hl._comment_fmt, QTextCharFormat)
        assert hl._comment_fmt._font_italic is True  # italic=True

    def test_hex_regex_is_compiled(self):
        doc = _FakeDocument()
        hl = QSSHighlighter(doc)
        assert hl._hex_rx is not None

    def test_rgb_regex_is_compiled(self):
        doc = _FakeDocument()
        hl = QSSHighlighter(doc)
        assert hl._rgb_rx is not None

    def test_rules_contain_widget_selectors(self):
        """RULES include common QWidget-derived class names."""
        all_patterns = "|".join(p for p, _ in QSSHighlighter.RULES)
        assert "QWidget" in all_patterns
        assert "QMainWindow" in all_patterns
        assert "QPushButton" in all_patterns
        assert "QLabel" in all_patterns

    def test_rules_contain_pseudo_states(self):
        all_patterns = "|".join(p for p, _ in QSSHighlighter.RULES)
        assert "hover" in all_patterns
        assert "pressed" in all_patterns
        assert "checked" in all_patterns
        assert "focus" in all_patterns

    def test_rules_contain_css_properties(self):
        all_patterns = "|".join(p for p, _ in QSSHighlighter.RULES)
        assert "color" in all_patterns
        assert "border" in all_patterns
        assert "background" in all_patterns
        assert "font" in all_patterns

    def test_rules_contain_numeric_values(self):
        """RULES should include a pattern matching numeric QSS values."""
        assert any(r"\d+" in p for p, _ in QSSHighlighter.RULES)


# ── QSSHighlighter.highlightBlock ─────────────────────────────────────────────


class TestHighlightBlock:
    """highlightBlock applies format rules to text."""

    def test_widget_name_is_formatted(self):
        hl = _make_highlighter()
        hl.highlightBlock("QMainWindow {")
        # Some position should have a format set
        assert any(hl._formats)

    def test_pseudo_state_is_formatted(self):
        hl = _make_highlighter()
        hl.highlightBlock("QPushButton::hover {")
        assert any(hl._formats)

    def test_css_property_is_formatted(self):
        hl = _make_highlighter()
        hl.highlightBlock("    color: red;")
        assert any(hl._formats)

    def test_numeric_value_is_formatted(self):
        hl = _make_highlighter()
        hl.highlightBlock("    font-size: 14px;")
        assert any(hl._formats)

    def test_url_is_formatted(self):
        hl = _make_highlighter()
        hl.highlightBlock("    border-image: url(icons/foo.png);")
        assert any(hl._formats)

    def test_string_is_formatted(self):
        hl = _make_highlighter()
        hl.highlightBlock('    content: "hello";')
        assert any(hl._formats)

    def test_punctuation_is_formatted(self):
        hl = _make_highlighter()
        hl.highlightBlock("{}:;")
        assert any(hl._formats)

    def test_hex_color_is_formatted(self):
        hl = _make_highlighter()
        hl.highlightBlock("    color: #ff0000;")
        assert any(hl._formats)

    def test_rgb_color_is_formatted(self):
        hl = _make_highlighter()
        hl.highlightBlock("    background: rgb(255, 0, 0);")
        assert any(hl._formats)

    def test_comment_is_formatted(self):
        hl = _make_highlighter()
        hl.highlightBlock("/* this is a comment */")
        assert any(hl._formats)

    def test_multiline_comment_first_block(self):
        """A block starting a comment should set block state to 1."""
        hl = _make_highlighter()
        hl.highlightBlock("/* start comment")
        assert hl._current_block_state == 1

    def test_empty_text_no_crash(self):
        hl = _make_highlighter()
        # Should not raise
        hl.highlightBlock("")

    def test_complex_qss_no_error(self):
        hl = _make_highlighter()
        qss = """
        QMainWindow {
            background-color: #2d3436;
            color: #dfe6e9;
        }
        QPushButton::hover {
            background: rgb(100, 100, 100);
            border: 1px solid #74b9ff;
        }
        /* Status bar */
        QStatusBar {
            font-size: 10pt;
        }
        """
        hl.highlightBlock(qss)
        assert any(hl._formats)


# ── Helpers ───────────────────────────────────────────────────────────────────


class _FakeDocument:
    """Minimal document stub for QSSHighlighter construction."""

    def __init__(self):
        self._blocks = []


def _make_highlighter():
    """Create a QSSHighlighter with a fake document."""
    doc = _FakeDocument()
    hl = QSSHighlighter(doc)
    # Override the stub's highlightBlock to call the real one
    # Our stub version is a no-op, so we need to ensure the real
    # QSSHighlighter.highlightBlock is called. Since the stub
    # QSyntaxHighlighter.highlightBlock is a no-op, and the real
    # QSSHighlighter defines its own highlightBlock, our subclass's
    # method should be called.
    return hl
