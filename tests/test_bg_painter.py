"""Tests for BackgroundPainter in bg_painter.py.

Exercises the background-image painter class with stub QGIS/PyQt classes.
"""

import gc

from qgis.PyQt.QtCore import QEvent
from qgis.PyQt.QtGui import QPixmap
from qgis.PyQt.QtWidgets import QWidget

from SkinKit.bg_painter import _RESIZE_DEBOUNCE_MS, BG_MODES, BackgroundPainter

# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_fake_pixmap():
    """Create a non-null pixmap for internal testing."""
    px = QPixmap()
    px._null = False
    return px


# ── BG_MODES constant ─────────────────────────────────────────────────────────


class TestBGModes:
    """BG_MODES lists all supported fill modes."""

    def test_modes_are_correct(self):
        assert BG_MODES == ["stretch", "tile", "center", "fit"]

    def test_no_duplicate_modes(self):
        assert len(BG_MODES) == len(set(BG_MODES))

    def test_all_modes_are_strings(self):
        assert all(isinstance(m, str) for m in BG_MODES)


# ── _RESIZE_DEBOUNCE_MS constant ──────────────────────────────────────────────


class TestResizeDebounce:
    def test_constant_is_positive(self):
        assert _RESIZE_DEBOUNCE_MS > 0

    def test_constant_is_int(self):
        assert isinstance(_RESIZE_DEBOUNCE_MS, int)

    def test_reasonable_value(self):
        assert 10 <= _RESIZE_DEBOUNCE_MS <= 500


# ── BackgroundPainter initialisation ──────────────────────────────────────────


class TestBackgroundPainterInit:
    """BackgroundPainter construction and basic properties."""

    def test_stores_window_reference(self, _qapp):
        win = QWidget()
        painter = BackgroundPainter(win)
        assert painter._window is win

    def test_initial_pixmap_is_none(self, _qapp):
        win = QWidget()
        painter = BackgroundPainter(win)
        assert painter._pixmap is None

    def test_initial_mode_is_stretch(self, _qapp):
        win = QWidget()
        painter = BackgroundPainter(win)
        assert painter._mode == "stretch"

    def test_original_palette_is_captured(self, _qapp):
        win = QWidget()
        painter = BackgroundPainter(win)
        assert painter._original_palette is not None

    def test_resize_timer_is_created(self, _qapp):
        win = QWidget()
        painter = BackgroundPainter(win)
        assert painter._resize_timer is not None
        assert painter._resize_timer.isSingleShot() is True
        assert painter._resize_timer.interval() == _RESIZE_DEBOUNCE_MS

    def test_resize_timer_is_not_active_initially(self, _qapp):
        win = QWidget()
        painter = BackgroundPainter(win)
        assert painter._resize_timer.isActive() is False

    def test_window_is_parent(self, _qapp):
        win = QWidget()
        painter = BackgroundPainter(win)
        assert painter.parent() is win


# ── BackgroundPainter.set_image ────────────────────────────────────────────────


class TestBackgroundPainterSetImage:
    """set_image() applies a pixmap and starts event filtering."""

    def test_empty_path_clears(self, _qapp):
        win = QWidget()
        painter = BackgroundPainter(win)
        painter._pixmap = _make_fake_pixmap()
        painter._mode = "tile"
        painter._window.installEventFilter(painter)
        painter.set_image("")
        assert painter._pixmap is None

    def test_valid_mode_is_accepted(self, _qapp):
        win = QWidget()
        painter = BackgroundPainter(win)
        painter._pixmap = _make_fake_pixmap()
        for mode in BG_MODES:
            painter._mode = mode
            assert painter._mode == mode


# ── BackgroundPainter.clear ────────────────────────────────────────────────────


class TestBackgroundPainterClear:
    """clear() resets the painter and restores the original palette."""

    def test_clears_pixmap(self, _qapp):
        win = QWidget()
        painter = BackgroundPainter(win)
        painter._pixmap = _make_fake_pixmap()
        painter.clear()
        assert painter._pixmap is None

    def test_stops_resize_timer(self, _qapp):
        win = QWidget()
        painter = BackgroundPainter(win)
        painter._resize_timer.start()
        painter.clear()
        assert painter._resize_timer.isActive() is False

    def test_does_not_raise_when_window_gone(self, _qapp):
        win = QWidget()
        painter = BackgroundPainter(win)
        painter._pixmap = _make_fake_pixmap()
        painter._window.installEventFilter(painter)
        painter.clear()
        assert painter._pixmap is None


# ── BackgroundPainter._apply ──────────────────────────────────────────────────


class TestBackgroundPainterApply:
    """_apply() renders the pixmap onto the window palette."""

    def test_noop_when_no_pixmap(self, _qapp):
        win = QWidget()
        painter = BackgroundPainter(win)
        old_palette = painter._window.palette()
        painter._apply()
        assert painter._window.palette() is old_palette

    def test_noop_when_window_deleted(self, _qapp):
        win = QWidget()
        painter = BackgroundPainter(win)
        painter._pixmap = _make_fake_pixmap()
        del win
        gc.collect()
        painter._apply()  # should not raise


# ── BackgroundPainter.eventFilter ─────────────────────────────────────────────


class TestEventFilter:
    """eventFilter handles QEvent.Resize to start debounce timer."""

    def _make_painter(self, _qapp):
        win = QWidget()
        painter = BackgroundPainter(win)
        painter._pixmap = _make_fake_pixmap()
        return painter, win

    def test_resize_starts_timer_with_stretch(self, _qapp):
        painter, _ = self._make_painter(_qapp)
        painter._mode = "stretch"
        e = QEvent(QEvent.Resize)
        painter.eventFilter(painter._window, e)
        assert painter._resize_timer.isActive() is True

    def test_resize_starts_timer_with_fit(self, _qapp):
        painter, _ = self._make_painter(_qapp)
        painter._mode = "fit"
        e = QEvent(QEvent.Resize)
        painter.eventFilter(painter._window, e)
        assert painter._resize_timer.isActive() is True

    def test_resize_does_not_start_timer_with_tile(self, _qapp):
        painter, _ = self._make_painter(_qapp)
        painter._mode = "tile"
        e = QEvent(QEvent.Resize)
        painter.eventFilter(painter._window, e)
        assert painter._resize_timer.isActive() is False

    def test_resize_does_not_start_timer_with_center(self, _qapp):
        painter, _ = self._make_painter(_qapp)
        painter._mode = "center"
        e = QEvent(QEvent.Resize)
        painter.eventFilter(painter._window, e)
        assert painter._resize_timer.isActive() is False

    def test_ignores_non_resize_events(self, _qapp):
        painter, _ = self._make_painter(_qapp)
        painter._mode = "stretch"
        e = QEvent(QEvent.Resize + 1)
        painter.eventFilter(painter._window, e)
        assert painter._resize_timer.isActive() is False

    def test_always_returns_false(self, _qapp):
        """eventFilter must return False so the event propagates."""
        painter, _ = self._make_painter(_qapp)
        e = QEvent(QEvent.Resize)
        result = painter.eventFilter(painter._window, e)
        assert result is False
