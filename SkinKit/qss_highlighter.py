# -*- coding: utf-8 -*-
"""CSS/QSS syntax highlighter — colour swatches, multiline comments, line numbers."""

import re

from qgis.PyQt.QtCore import QRegularExpression
from qgis.PyQt.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat


def _fmt(color, bold=False, italic=False):
    f = QTextCharFormat()
    f.setForeground(QColor(color))
    if bold:
        f.setFontWeight(QFont.Bold)
    if italic:
        f.setFontItalic(True)
    return f


def _color_fmt(hex_str):
    f = QTextCharFormat()
    try:
        c = QColor(hex_str)
        if c.isValid():
            luma = 0.299 * c.red() + 0.587 * c.green() + 0.114 * c.blue()
            f.setBackground(c)
            f.setForeground(QColor("#000000" if luma > 128 else "#ffffff"))
    except Exception:
        pass
    return f


class QSSHighlighter(QSyntaxHighlighter):
    COMMENT_START = QRegularExpression(r"/\*")
    COMMENT_END = QRegularExpression(r"\*/")
    RULES = [
        (
            r"\b(QWidget|QMainWindow|QDialog|QDockWidget|QToolBar|QMenuBar|QMenu"
            r"|QStatusBar|QTabBar|QTabWidget|QTreeView|QListView|QTableView"
            r"|QScrollBar|QSlider|QProgressBar|QPushButton|QToolButton"
            r"|QComboBox|QLineEdit|QPlainTextEdit|QTextEdit|QSpinBox"
            r"|QDoubleSpinBox|QAbstractSpinBox|QAbstractScrollArea"
            r"|QHeaderView|QGroupBox|QFrame|QLabel|QCheckBox|QRadioButton"
            r"|QSplitter|QSizeGrip|QAbstractItemView|QMdiArea"
            r"|QgsMapCanvas|QgsLayerTreeView)\b",
            _fmt("#4fc1e9", bold=True),
        ),
        (
            r"::(hover|pressed|checked|unchecked|selected|disabled|focus"
            r"|enabled|active|on|off|read-only|flat|open|closed|first|last"
            r"|middle|only-one|handle|groove|chunk|title|tab|pane"
            r"|indicator|separator|branch|add-line|sub-line)\b",
            _fmt("#a29bfe"),
        ),
        (
            r"\b(color|background|background-color|background-image"
            r"|border|border-color|border-style|border-width|border-radius"
            r"|border-image|margin|padding|font|font-family|font-size|font-weight"
            r"|min-width|min-height|max-width|max-height|width|height"
            r"|image|icon|icon-size|spacing|selection-color"
            r"|selection-background-color|alternate-background-color"
            r"|gridline-color|text-align|subcontrol-origin|subcontrol-position)\b",
            _fmt("#74b9ff"),
        ),
        (
            r"\b(solid|dashed|dotted|none|transparent|inherit|auto|bold|italic"
            r"|normal|underline|left|right|top|bottom|center|fixed|scroll"
            r"|repeat|no-repeat|stretch|qlineargradient|qradialgradient)\b",
            _fmt("#55efc4"),
        ),
        (r"\b\d+(\.\d+)?(px|pt|em|%)?\b", _fmt("#fdcb6e")),
        (r"url\([^)]*\)", _fmt("#a8e6cf")),
        (r'"[^"]*"|\'[^\']*\'', _fmt("#fab1a0")),
        (r"[{}:;,]", _fmt("#dfe6e9")),
    ]

    def __init__(self, document):
        super().__init__(document)
        self._rules = [(QRegularExpression(p), f) for p, f in self.RULES]
        self._comment_fmt = _fmt("#636e72", italic=True)
        self._hex_rx = QRegularExpression(
            r"#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b"
        )
        self._rgb_rx = QRegularExpression(
            r"rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+(?:\s*,\s*[\d.]+)?\s*\)"
        )

    def highlightBlock(self, text):
        for rx, fmt in self._rules:
            it = rx.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)
        it = self._hex_rx.globalMatch(text)
        while it.hasNext():
            m = it.next()
            self.setFormat(
                m.capturedStart(), m.capturedLength(), _color_fmt(m.captured(0))
            )
        it = self._rgb_rx.globalMatch(text)
        while it.hasNext():
            m = it.next()
            raw = m.captured(0)
            nums = re.findall(r"[\d.]+", raw)
            if len(nums) >= 3:
                try:
                    self.setFormat(
                        m.capturedStart(),
                        m.capturedLength(),
                        _color_fmt(
                            QColor(int(nums[0]), int(nums[1]), int(nums[2])).name()
                        ),
                    )
                except Exception:
                    pass
        self.setCurrentBlockState(0)
        start = 0
        if self.previousBlockState() != 1:
            m = self.COMMENT_START.match(text)
            start = m.capturedStart() if m.hasMatch() else -1
        while start >= 0:
            end_m = self.COMMENT_END.match(text, start)
            if end_m.hasMatch():
                length = end_m.capturedStart() - start + end_m.capturedLength()
                self.setFormat(start, length, self._comment_fmt)
                nx = self.COMMENT_START.match(text, start + length)
                start = nx.capturedStart() if nx.hasMatch() else -1
            else:
                self.setCurrentBlockState(1)
                self.setFormat(start, len(text) - start, self._comment_fmt)
                break
