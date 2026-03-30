# -*- coding: utf-8 -*-
"""UI Themes+ — Main plugin class."""
import os
from qgis.PyQt.QtWidgets import QAction, QApplication
from qgis.PyQt.QtGui import QIcon, QFont
from qgis.PyQt.QtCore import QFileSystemWatcher, QSize
from qgis.core import QgsSettings
from .bg_painter import BackgroundPainter

NS = "UIThemesPlus"
BUILTIN_THEMES = ["default", "Night Mapping", "Blend of Gray"]
CFG_KEYS = ["qss_path","qss_inline","icon_pack_dir","icon_path","icon_size",
            "bg_image_path","bg_mode","bg_opacity","font_family","font_size",
            "opacity","live_reload"]

class UIThemesPlus:
    def __init__(self, iface):
        self.iface = iface
        self.dialog = None
        self.action = None
        self._watcher = QFileSystemWatcher()
        self._watcher.fileChanged.connect(self._on_file_changed)
        self._watched_path = ""
        self._bg_painter = None

    def initGui(self):
        icon_path = os.path.join(os.path.dirname(__file__), "icons", "icon.png")
        self.action = QAction(QIcon(icon_path), "UI Themes+", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu("&UI Themes+", self.action)
        self.iface.addToolBarIcon(self.action)
        self._ensure_default_preset()
        self._apply_saved()

    def unload(self):
        self.iface.removePluginMenu("&UI Themes+", self.action)
        self.iface.removeToolBarIcon(self.action)
        self._remove_watcher()
        if self._bg_painter:
            self._bg_painter.clear()

    def run(self):
        if self.dialog is None:
            from .ui_themes_plus_dialog import UIThemesPlusDialog
            self.dialog = UIThemesPlusDialog(self.iface, self)
        self.dialog.show(); self.dialog.raise_(); self.dialog.activateWindow()

    def apply_all(self, cfg):
        s = QgsSettings()
        app = QApplication.instance()
        win = self.iface.mainWindow()
        if cfg.get("reset"):
            self._reset_to_previous(s); return

        qss_path   = cfg.get("qss_path","")
        qss_inline = cfg.get("qss_inline","")
        icon_pack  = cfg.get("icon_pack_dir","")
        combined   = ""
        if qss_path and os.path.isfile(qss_path):
            try:
                with open(qss_path,"r",encoding="utf-8") as fh:
                    combined = fh.read()
                if icon_pack and os.path.isdir(icon_pack):
                    combined = combined.replace("url(icons/", f"url({icon_pack}/")
            except Exception as e:
                self.iface.messageBar().pushWarning("UI Themes+", f"Cannot read QSS: {e}")
        combined += "\n" + qss_inline
        app.setStyleSheet(combined)

        if cfg.get("live_reload") and qss_path:
            self._set_watcher(qss_path)
        else:
            self._remove_watcher()

        bg_path = cfg.get("bg_image_path","")
        bg_mode = cfg.get("bg_mode","stretch")
        bg_op   = float(cfg.get("bg_opacity",1.0))
        if self._bg_painter is None:
            self._bg_painter = BackgroundPainter(win)
        if bg_path and os.path.isfile(bg_path):
            self._bg_painter.set_image(bg_path, bg_mode, bg_op)
        else:
            self._bg_painter.clear()

        icon_path = cfg.get("icon_path","")
        if icon_path and os.path.isfile(icon_path):
            win.setWindowIcon(QIcon(icon_path))

        icon_size = int(cfg.get("icon_size",0))
        if icon_size > 0:
            win.setIconSize(QSize(icon_size, icon_size))

        font_family = cfg.get("font_family","")
        font_size   = int(cfg.get("font_size",0))
        if font_family or font_size:
            font = app.font()
            if font_family: font.setFamily(font_family)
            if font_size > 0: font.setPointSize(font_size)
            app.setFont(font)

        opacity = max(0.1, min(1.0, float(cfg.get("opacity",1.0))))
        win.setWindowOpacity(opacity)

        for k in CFG_KEYS:
            if k in cfg:
                s.setValue(f"{NS}/{k}", cfg[k])
        s.setValue(f"{NS}/live_reload", bool(cfg.get("live_reload",False)))

    def load_settings(self):
        s = QgsSettings()
        return {
            "qss_path":      s.value(f"{NS}/qss_path",""),
            "qss_inline":    s.value(f"{NS}/qss_inline",""),
            "icon_pack_dir": s.value(f"{NS}/icon_pack_dir",""),
            "icon_path":     s.value(f"{NS}/icon_path",""),
            "icon_size":     s.value(f"{NS}/icon_size",0,type=int),
            "bg_image_path": s.value(f"{NS}/bg_image_path",""),
            "bg_mode":       s.value(f"{NS}/bg_mode","stretch"),
            "bg_opacity":    s.value(f"{NS}/bg_opacity",1.0,type=float),
            "font_family":   s.value(f"{NS}/font_family",""),
            "font_size":     s.value(f"{NS}/font_size",0,type=int),
            "opacity":       s.value(f"{NS}/opacity",1.0,type=float),
            "live_reload":   s.value(f"{NS}/live_reload",False,type=bool),
        }

    def save_preset(self, name, cfg):
        s = QgsSettings()
        for k, v in cfg.items():
            s.setValue(f"{NS}/presets/{name}/{k}", v)

    def load_preset(self, name):
        s = QgsSettings()
        out = {}
        for k in CFG_KEYS:
            default = False if k=="live_reload" else (0 if k in("icon_size","font_size") else
                      (1.0 if k in("opacity","bg_opacity") else ""))
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
            self.save_preset("QGIS Default",
                {k: (1.0 if k in("opacity","bg_opacity") else
                     (0 if k in("icon_size","font_size") else
                      (False if k=="live_reload" else ""))) for k in CFG_KEYS})

    def _save_previous_builtin(self, s):
        if s.value(f"{NS}/previous_builtin_theme", None) is None:
            current = s.value("/qgis/UITheme","default")
            s.setValue(f"{NS}/previous_builtin_theme", current)

    def _reset_to_previous(self, s):
        app = QApplication.instance()
        win = self.iface.mainWindow()
        app.setStyleSheet("")
        win.setWindowOpacity(1.0)
        self._remove_watcher()
        if self._bg_painter: self._bg_painter.clear()
        prev = s.value(f"{NS}/previous_builtin_theme","default")
        s.setValue("/qgis/UITheme", prev)
        for k in CFG_KEYS:
            s.remove(f"{NS}/{k}")
        self.iface.messageBar().pushSuccess(
            "UI Themes+",
            f'Reset complete. QGIS will use theme "{prev}" after restart.')

    def _apply_saved(self):
        s = QgsSettings()
        self._save_previous_builtin(s)
        cfg = self.load_settings()
        if any(cfg.get(k) for k in ("qss_path","qss_inline","icon_path","bg_image_path")):
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

    def _on_file_changed(self, path):
        if path not in self._watcher.files():
            self._watcher.addPath(path)
        cfg = self.load_settings()
        try:
            with open(path,"r",encoding="utf-8") as fh:
                combined = fh.read()
            ip = cfg.get("icon_pack_dir","")
            if ip and os.path.isdir(ip):
                combined = combined.replace("url(icons/", f"url({ip}/")
            combined += "\n" + cfg.get("qss_inline","")
            QApplication.instance().setStyleSheet(combined)
        except Exception as e:
            self.iface.messageBar().pushWarning("UI Themes+", f"Live-reload failed: {e}")
