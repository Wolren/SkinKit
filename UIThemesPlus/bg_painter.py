# -*- coding: utf-8 -*-
"""BackgroundPainter — apply a background image to QMainWindow via QPalette."""
from qgis.PyQt.QtCore import QObject, QEvent, Qt
from qgis.PyQt.QtGui import QBrush, QPalette, QPixmap

BG_MODES = ["stretch", "tile", "center", "fit"]

class BackgroundPainter(QObject):
    def __init__(self, window):
        super().__init__(window)
        self._window = window
        self._pixmap = None
        self._mode = "stretch"
        self._original_palette = QPalette(window.palette())

    def set_image(self, path, mode="stretch", opacity=1.0):
        if not path:
            self.clear(); return
        px = QPixmap(path)
        if px.isNull(): return
        self._pixmap = px
        self._mode = mode if mode in BG_MODES else "stretch"
        self._apply()
        self._window.installEventFilter(self)

    def clear(self):
        self._pixmap = None
        self._window.setPalette(self._original_palette)
        self._window.setAutoFillBackground(False)
        self._window.removeEventFilter(self)

    def _apply(self):
        if not self._pixmap: return
        win = self._window
        mode = self._mode
        sz = win.size()
        if mode == "stretch":
            scaled = self._pixmap.scaled(sz, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        elif mode == "fit":
            scaled = self._pixmap.scaled(sz, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            scaled = self._pixmap
        pal = win.palette()
        pal.setBrush(QPalette.Window, QBrush(scaled))
        win.setPalette(pal)
        win.setAutoFillBackground(True)

    def eventFilter(self, obj, event):
        if obj is self._window and event.type() == QEvent.Resize:
            if self._pixmap and self._mode in ("stretch", "fit"):
                self._apply()
        return False
