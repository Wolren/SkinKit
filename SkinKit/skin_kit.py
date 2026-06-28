"""SkinKit — Main plugin class."""

import os

from qgis.core import QgsMessageLog, QgsSettings
from qgis.PyQt.QtCore import QFileSystemWatcher, QSize, QTimer
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QApplication

from .bg_painter import BackgroundPainter

NS = "SkinKit"
CFG_KEYS = [
    "qss_path",
    "qss_inline",
    "icon_pack_dir",
    "icon_path",
    "icon_size",
    "bg_image_path",
    "bg_mode",
    "bg_opacity",
    "font_family",
    "font_size",
    "opacity",
    "live_reload",
]

PLUGIN_TAG = "SkinKit"


def _safe_int(val, default=0):
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def _safe_float(val, default=0.0):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _valid_preset_name(name):
    return bool(name) and not any(c in name for c in r"/\:%&<>")


def _notify(msg, level=0):
    if level == 0:
        QgsMessageLog.logMessage(msg, PLUGIN_TAG, level)


class SkinKit:
    def __init__(self, iface):
        self.iface = iface
        self.dialog = None
        self.action = None
        self._watcher = QFileSystemWatcher()
        self._watcher.fileChanged.connect(self._on_file_changed_debounced)
        self._watched_path = ""
        self._bg_painter = None
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(200)
        self._debounce_timer.timeout.connect(self._on_file_changed)

    def initGui(self):
        icon_path = os.path.join(os.path.dirname(__file__), "icons", "icon.png")
        self.action = QAction(QIcon(icon_path), "SkinKit", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu("&SkinKit", self.action)
        self.iface.addToolBarIcon(self.action)
        self._ensure_default_preset()
        self._apply_saved()

    def unload(self):
        if self.dialog:
            self.dialog.close()
            self.dialog.deleteLater()
            self.dialog = None
        self.iface.removePluginMenu("&SkinKit", self.action)
        self.iface.removeToolBarIcon(self.action)
        self._remove_watcher()
        if self._bg_painter:
            self._bg_painter.clear()
            self._bg_painter = None
        self._debounce_timer.stop()

    def run(self):
        if self.dialog is None:
            from .skin_kit_dialog import SkinKitDialog

            self.dialog = SkinKitDialog(self.iface, self)
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()

    def apply_all(self, cfg):
        s = QgsSettings()
        app = QApplication.instance()
        win = self.iface.mainWindow() if self.iface else None
        if cfg.get("reset"):
            self._reset_to_previous(s)
            return

        if not app or not win:
            _notify("apply_all: QApplication or mainWindow not available")
            return

        qss_path = cfg.get("qss_path", "")
        qss_inline = cfg.get("qss_inline", "")
        icon_pack = cfg.get("icon_pack_dir", "")
        combined = ""
        if qss_path and os.path.isfile(qss_path):
            try:
                with open(qss_path, encoding="utf-8") as fh:
                    combined = fh.read()
                if icon_pack and os.path.isdir(icon_pack):
                    combined = combined.replace("url(icons/", f"url({icon_pack}/")
            except Exception as e:
                self._push_warning(f"Cannot read QSS: {e}")
        combined += "\n" + qss_inline
        app.setStyleSheet(combined)

        if cfg.get("live_reload") and qss_path:
            self._set_watcher(qss_path)
        else:
            self._remove_watcher()

        bg_path = cfg.get("bg_image_path", "")
        bg_mode = cfg.get("bg_mode", "stretch")
        bg_op = _safe_float(cfg.get("bg_opacity", 1.0), 1.0)
        if self._bg_painter is None:
            self._bg_painter = BackgroundPainter(win)
        if bg_path and os.path.isfile(bg_path):
            self._bg_painter.set_image(bg_path, bg_mode, bg_op)
        else:
            self._bg_painter.clear()

        icon_path = cfg.get("icon_path", "")
        if icon_path and os.path.isfile(icon_path):
            win.setWindowIcon(QIcon(icon_path))

        icon_size = _safe_int(cfg.get("icon_size", 0))
        if icon_size > 0:
            win.setIconSize(QSize(icon_size, icon_size))

        font_family = cfg.get("font_family", "")
        font_size = _safe_int(cfg.get("font_size", 0))
        if font_family or font_size:
            font = app.font()
            if font_family:
                font.setFamily(font_family)
            if font_size > 0:
                font.setPointSize(font_size)
            app.setFont(font)

        opacity = max(0.1, min(1.0, _safe_float(cfg.get("opacity", 1.0), 1.0)))
        win.setWindowOpacity(opacity)

        for k in CFG_KEYS:
            if k in cfg:
                s.setValue(f"{NS}/{k}", cfg[k])
        s.setValue(f"{NS}/live_reload", bool(cfg.get("live_reload", False)))

    def load_settings(self):
        s = QgsSettings()
        return {
            "qss_path": s.value(f"{NS}/qss_path", ""),
            "qss_inline": s.value(f"{NS}/qss_inline", ""),
            "icon_pack_dir": s.value(f"{NS}/icon_pack_dir", ""),
            "icon_path": s.value(f"{NS}/icon_path", ""),
            "icon_size": s.value(f"{NS}/icon_size", 0, type=int),
            "bg_image_path": s.value(f"{NS}/bg_image_path", ""),
            "bg_mode": s.value(f"{NS}/bg_mode", "stretch"),
            "bg_opacity": s.value(f"{NS}/bg_opacity", 1.0, type=float),
            "font_family": s.value(f"{NS}/font_family", ""),
            "font_size": s.value(f"{NS}/font_size", 0, type=int),
            "opacity": s.value(f"{NS}/opacity", 1.0, type=float),
            "live_reload": s.value(f"{NS}/live_reload", False, type=bool),
        }

    def save_preset(self, name, cfg):
        if not _valid_preset_name(name):
            raise ValueError(f"Invalid preset name: {name!r}")
        s = QgsSettings()
        for k, v in cfg.items():
            s.setValue(f"{NS}/presets/{name}/{k}", v)

    def load_preset(self, name):
        s = QgsSettings()
        out = {}
        for k in CFG_KEYS:
            default = (
                False
                if k == "live_reload"
                else (
                    0
                    if k in ("icon_size", "font_size")
                    else (1.0 if k in ("opacity", "bg_opacity") else "")
                )
            )
            out[k] = s.value(f"{NS}/presets/{name}/{k}", default)
        return out

    def list_presets(self):
        s = QgsSettings()
        s.beginGroup(f"{NS}/presets")
        names = s.childGroups()
        s.endGroup()
        return sorted(names)

    def delete_preset(self, name):
        QgsSettings().remove(f"{NS}/presets/{name}")

    def _ensure_default_preset(self):
        s = QgsSettings()
        if not s.value(f"{NS}/presets/QGIS Default/qss_path", None):
            self.save_preset(
                "QGIS Default",
                {
                    k: (
                        1.0
                        if k in ("opacity", "bg_opacity")
                        else (
                            0
                            if k in ("icon_size", "font_size")
                            else (False if k == "live_reload" else "")
                        )
                    )
                    for k in CFG_KEYS
                },
            )

    def _save_previous_builtin(self, s):
        if s.value(f"{NS}/previous_builtin_theme", None) is None:
            current = s.value("/qgis/UITheme", "default")
            s.setValue(f"{NS}/previous_builtin_theme", current)

    def _reset_to_previous(self, s):
        app = QApplication.instance()
        win = self.iface.mainWindow() if self.iface else None
        if app:
            app.setStyleSheet("")
        if win:
            win.setWindowOpacity(1.0)
        self._remove_watcher()
        if self._bg_painter:
            self._bg_painter.clear()
        prev = s.value(f"{NS}/previous_builtin_theme", "default")
        s.setValue("/qgis/UITheme", prev)
        for k in CFG_KEYS:
            s.remove(f"{NS}/{k}")
        self._push_success(
            f'Reset complete. QGIS will use theme "{prev}" after restart.'
        )

    def _apply_saved(self):
        s = QgsSettings()
        self._save_previous_builtin(s)
        cfg = self.load_settings()
        if any(
            cfg.get(k) for k in ("qss_path", "qss_inline", "icon_path", "bg_image_path")
        ):
            self.apply_all(cfg)

    def _set_watcher(self, path):
        if self._watched_path and self._watched_path != path:
            self._watcher.removePath(self._watched_path)
        if path not in self._watcher.files():
            self._watcher.addPath(path)
        self._watched_path = path

    def _remove_watcher(self):
        if self._watched_path:
            self._watcher.removePath(self._watched_path)
            self._watched_path = ""

    def _on_file_changed_debounced(self, path):
        self._debounce_timer.stop()
        self._pending_path = path
        self._debounce_timer.start()

    def _on_file_changed(self):
        path = getattr(self, "_pending_path", "")
        if not path:
            return
        if path not in self._watcher.files():
            self._watcher.addPath(path)
        cfg = self.load_settings()
        try:
            with open(path, encoding="utf-8") as fh:
                combined = fh.read()
            ip = cfg.get("icon_pack_dir", "")
            if ip and os.path.isdir(ip):
                combined = combined.replace("url(icons/", f"url({ip}/")
            combined += "\n" + cfg.get("qss_inline", "")
            app = QApplication.instance()
            if app:
                app.setStyleSheet(combined)
        except Exception as e:
            self._push_warning(f"Live-reload failed: {e}")

    def _push_warning(self, msg):
        iface = self.iface
        if iface and hasattr(iface, "messageBar"):
            iface.messageBar().pushWarning(PLUGIN_TAG, msg)
        _notify(msg, 1)

    def _push_success(self, msg):
        iface = self.iface
        if iface and hasattr(iface, "messageBar"):
            iface.messageBar().pushSuccess(PLUGIN_TAG, msg)
        _notify(msg)
