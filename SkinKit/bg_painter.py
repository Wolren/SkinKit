"""BackgroundPainter — apply a background image to QMainWindow via QPalette."""

from qgis.PyQt.QtCore import QEvent, QObject, Qt, QTimer
from qgis.PyQt.QtGui import QBrush, QPalette, QPixmap

BG_MODES = ["stretch", "tile", "center", "fit"]

_RESIZE_DEBOUNCE_MS = 80


class BackgroundPainter(QObject):
    def __init__(self, window):
        super().__init__(window)
        self._window = window
        self._pixmap = None
        self._mode = "stretch"
        self._original_palette = QPalette(window.palette())
        self._resize_timer = QTimer()
        self._resize_timer.setSingleShot(True)
        self._resize_timer.setInterval(_RESIZE_DEBOUNCE_MS)
        self._resize_timer.timeout.connect(self._apply)

    def set_image(self, path, mode="stretch", opacity=1.0):
        if not path:
            self.clear()
            return
        px = QPixmap(path)
        if px.isNull():
            return
        self._pixmap = px
        self._mode = mode if mode in BG_MODES else "stretch"
        self._apply()
        self._window.installEventFilter(self)

    def clear(self):
        self._pixmap = None
        self._resize_timer.stop()
        window = self._window
        if window:
            window.setPalette(self._original_palette)
            window.setAutoFillBackground(False)
            window.removeEventFilter(self)

    def _apply(self):
        if not self._pixmap:
            return
        win = self._window
        if not win:
            return
        mode = self._mode
        sz = win.size()
        if mode == "stretch":
            scaled = self._pixmap.scaled(
                sz, Qt.IgnoreAspectRatio, Qt.SmoothTransformation
            )
        elif mode == "fit":
            scaled = self._pixmap.scaled(
                sz, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        else:
            scaled = self._pixmap
        pal = win.palette()
        pal.setBrush(QPalette.Window, QBrush(scaled))
        win.setPalette(pal)
        win.setAutoFillBackground(True)

    def eventFilter(self, obj, event):
        if obj is self._window and event.type() == QEvent.Resize and self._pixmap and self._mode in ("stretch", "fit"):
            self._resize_timer.start()
        return False
