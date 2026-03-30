# -*- coding: utf-8 -*-
"""UI Themes+ — main dialog (6 tabs)."""
import os
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QLineEdit, QPushButton, QCheckBox, QLabel,
    QSpinBox, QPlainTextEdit, QFileDialog, QComboBox,
    QTabWidget, QWidget, QDialogButtonBox, QMessageBox,
    QFontComboBox, QSlider, QSizePolicy, QFrame, QScrollArea, QTextEdit,
)
from qgis.PyQt.QtGui import QIcon, QFont, QPixmap, QColor, QTextFormat
from qgis.PyQt.QtCore import Qt, QSize
from .qss_highlighter import QSSHighlighter
from .ui_themes_plus import CFG_KEYS

GALLERY = [
    ("QGIS Default",   "Stock QGIS Fusion theme — no QSS file used",          ""),
    ("Night Mapping",  "QGIS built-in dark theme — no QSS file used",         ""),
    ("Blend of Gray",  "QGIS built-in grey theme — no QSS file used",         ""),
    ("Dark Forest",    "Deep forest tones, muted greens",                      "builtin_themes/DarkForest.qss"),
    ("Therian Wolf",   "Wolf-eye amber & dark bark palette",                   "builtin_themes/Therian.qss"),
    ("PrideGIS",       "Unified rainbow pride, deep indigo base",              "builtin_themes/PrideGIS.qss"),
]


# ── Line-number editor ────────────────────────────────────────────────────────

class _LineNumArea(QWidget):
    def __init__(self, ed):
        super().__init__(ed); self._ed = ed
    def sizeHint(self): return QSize(self._ed._gutter_width(), 0)
    def paintEvent(self, e): self._ed._paint_gutter(e)

class QSSEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._gutter = _LineNumArea(self)
        self.blockCountChanged.connect(self._update_gutter_width)
        self.updateRequest.connect(self._update_gutter)
        self.cursorPositionChanged.connect(self._highlight_line)
        self._update_gutter_width(0); self._highlight_line()

    def _gutter_width(self):
        return 6 + self.fontMetrics().horizontalAdvance("9") * len(str(max(1,self.blockCount())))

    def _update_gutter_width(self, _):
        self.setViewportMargins(self._gutter_width(), 0, 0, 0)

    def _update_gutter(self, rect, dy):
        if dy: self._gutter.scroll(0, dy)
        else: self._gutter.update(0, rect.y(), self._gutter.width(), rect.height())
        if rect.contains(self.viewport().rect()): self._update_gutter_width(0)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        cr = self.contentsRect()
        self._gutter.setGeometry(cr.left(), cr.top(), self._gutter_width(), cr.height())

    def _highlight_line(self):
        sels = []
        if not self.isReadOnly():
            sel = QTextEdit.ExtraSelection()
            sel.format.setBackground(QColor("#2d3436").lighter(140))
            sel.format.setProperty(QTextFormat.FullWidthSelection, True)
            sel.cursor = self.textCursor()
            sel.cursor.clearSelection()
            sels.append(sel)
        self.setExtraSelections(sels)

    def _paint_gutter(self, event):
        from qgis.PyQt.QtGui import QPainter
        p = QPainter(self._gutter)
        p.fillRect(event.rect(), QColor("#2d3436"))
        block = self.firstVisibleBlock()
        num   = block.blockNumber()
        top   = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bot   = top + int(self.blockBoundingRect(block).height())
        h     = self.fontMetrics().height()
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bot >= event.rect().top():
                p.setPen(QColor("#636e72"))
                p.setFont(self.font())
                p.drawText(0, top, self._gutter.width()-3, h, Qt.AlignRight, str(num+1))
            block = block.next()
            top = bot
            bot = top + int(self.blockBoundingRect(block).height())
            num += 1


# ── Main dialog ───────────────────────────────────────────────────────────────

class UIThemesPlusDialog(QDialog):
    def __init__(self, iface, plugin, parent=None):
        super().__init__(parent or iface.mainWindow())
        self.iface = iface; self.plugin = plugin
        self._hl = None
        self.setWindowTitle("UI Themes+")
        self.setMinimumWidth(660); self.setMinimumHeight(600)
        self._build_ui(); self._load_current()

    def _build_ui(self):
        root = QVBoxLayout(self); root.setContentsMargins(6,6,6,6)
        self.tabs = QTabWidget(); root.addWidget(self.tabs)
        self.tabs.addTab(self._tab_gallery(),    "🎨 Gallery")
        self.tabs.addTab(self._tab_editor(),     "📝 Stylesheet")
        self.tabs.addTab(self._tab_window(),     "🖼 Icon & Window")
        self.tabs.addTab(self._tab_background(), "🌄 Background")
        self.tabs.addTab(self._tab_font(),       "🔤 Font")
        self.tabs.addTab(self._tab_presets(),    "💾 Presets")
        bb = QDialogButtonBox()
        self._btn_apply = bb.addButton("Apply",      QDialogButtonBox.ApplyRole)
        self._btn_reset = bb.addButton("Reset All",  QDialogButtonBox.ResetRole)
        bb.addButton(QDialogButtonBox.Close)
        self._btn_apply.clicked.connect(self._on_apply)
        self._btn_reset.clicked.connect(self._on_reset)
        bb.rejected.connect(self.hide)
        root.addWidget(bb)

    # ── Gallery ───────────────────────────────────────────────────────────────
    def _tab_gallery(self):
        w = QWidget(); lay = QVBoxLayout(w); lay.setContentsMargins(8,8,8,8)
        lay.addWidget(QLabel("Select a starting theme. Click <b>Load into editor</b> then <b>Apply</b>."))
        sc = QScrollArea(); sc.setWidgetResizable(True)
        inner = QWidget(); gl = QVBoxLayout(inner); gl.setSpacing(6)
        for name, desc, rel in GALLERY:
            fr = QFrame(); fr.setFrameShape(QFrame.StyledPanel)
            fr.setCursor(Qt.PointingHandCursor)
            fl = QHBoxLayout(fr); fl.setContentsMargins(10,6,10,6)
            fl.addWidget(QLabel(f"<b>{name}</b><br><small>{desc}</small>"), stretch=1)
            btn = QPushButton("Load into editor"); btn.setFixedWidth(140)
            btn.clicked.connect(lambda _, n=name, q=rel: self._load_gallery(n,q))
            fl.addWidget(btn); gl.addWidget(fr)
        gl.addStretch(); sc.setWidget(inner); lay.addWidget(sc); return w

    def _load_gallery(self, name, rel):
        if name in ("QGIS Default","Night Mapping","Blend of Gray"):
            self.qss_path_edit.clear()
            self.qss_editor.setPlainText(
                f"/* {name} is a QGIS built-in theme — no QSS file needed.\n"
                f"   Clear this editor and press Apply to remove custom styling. */")
        else:
            plugin_dir = os.path.dirname(os.path.abspath(__file__))
            full = os.path.join(plugin_dir, rel)
            self.qss_path_edit.setText(full if os.path.isfile(full) else "")
            if os.path.isfile(full):
                with open(full,"r",encoding="utf-8") as fh:
                    self.qss_editor.setPlainText(fh.read())
        self.iface.messageBar().pushInfo("UI Themes+", f'"{name}" loaded. Press Apply.')

    # ── Stylesheet editor ─────────────────────────────────────────────────────
    def _tab_editor(self):
        w = QWidget(); lay = QVBoxLayout(w); lay.setContentsMargins(8,8,8,8)
        grp = QGroupBox("QSS File (optional — inline editor below overrides)")
        gl = QHBoxLayout(grp)
        self.qss_path_edit = QLineEdit()
        self.qss_path_edit.setPlaceholderText("External .qss file path…")
        b1 = QPushButton("Browse…"); b1.clicked.connect(self._browse_qss)
        b2 = QPushButton("Load into editor"); b2.clicked.connect(self._load_file_into_editor)
        for w2 in (self.qss_path_edit,b1,b2): gl.addWidget(w2)
        lay.addWidget(grp)
        self.live_reload_cb = QCheckBox("Live-reload — auto-apply on file save")
        lay.addWidget(self.live_reload_cb)
        eg = QGroupBox("Inline QSS editor — syntax highlighting, colour swatches, line numbers")
        el = QVBoxLayout(eg)
        self.qss_editor = QSSEditor()
        self.qss_editor.setFont(QFont("Consolas, Courier New", 10))
        self.qss_editor.setPlaceholderText("/* Write or paste QSS here.\n   Hex colours are shown with background swatches.\n   Changes here are applied directly on Apply — no separate Extra QSS tab needed. */")
        self._hl = QSSHighlighter(self.qss_editor.document())
        self._val_lbl = QLabel(); self._val_lbl.setWordWrap(True)
        self.qss_editor.textChanged.connect(self._validate)
        br = QHBoxLayout()
        bf = QPushButton("Auto-indent"); bf.clicked.connect(self._format)
        bc = QPushButton("Clear"); bc.clicked.connect(self.qss_editor.clear)
        bs = QPushButton("Save to file…"); bs.clicked.connect(self._save_to_file)
        for b in (bf,bc,bs): br.addWidget(b)
        br.addStretch()
        el.addWidget(self.qss_editor); el.addWidget(self._val_lbl); el.addLayout(br)
        lay.addWidget(eg); return w

    # ── Icon & Window ─────────────────────────────────────────────────────────
    def _tab_window(self):
        w = QWidget(); form = QFormLayout(w); form.setContentsMargins(8,8,8,8)
        # Window icon
        ir = QHBoxLayout()
        self.icon_path_edit = QLineEdit(); self.icon_path_edit.setPlaceholderText("PNG/SVG/ICO…")
        bi = QPushButton("Browse…"); bi.clicked.connect(self._browse_icon)
        self.icon_prev = QLabel(); self.icon_prev.setFixedSize(32,32)
        self.icon_path_edit.textChanged.connect(self._upd_icon_prev)
        for x in (self.icon_path_edit,bi,self.icon_prev): ir.addWidget(x)
        form.addRow("Window icon:", ir)
        # Title
        self.title_edit = QLineEdit(); self.title_edit.setPlaceholderText("Leave blank for default")
        form.addRow("Window title:", self.title_edit)
        # Toolbar icon size
        isr = QHBoxLayout()
        self.icon_size_sl = QSlider(Qt.Horizontal); self.icon_size_sl.setRange(0,128)
        self.icon_size_sl.setSingleStep(2); self.icon_size_sl.setTickInterval(16)
        self.icon_size_sl.setTickPosition(QSlider.TicksBelow); self.icon_size_sl.setValue(0)
        self.icon_size_lbl = QLabel("default"); self.icon_size_lbl.setFixedWidth(54)
        self.icon_size_sl.valueChanged.connect(
            lambda v: self.icon_size_lbl.setText(f"{v}px" if v>0 else "default"))
        isr.addWidget(self.icon_size_sl); isr.addWidget(self.icon_size_lbl)
        form.addRow("Toolbar icon size:", isr)
        # Opacity
        opr = QHBoxLayout()
        self.opacity_sl = QSlider(Qt.Horizontal); self.opacity_sl.setRange(10,100)
        self.opacity_sl.setValue(100); self.opacity_sl.setTickInterval(10)
        self.opacity_sl.setTickPosition(QSlider.TicksBelow)
        self.opacity_lbl = QLabel("100 %"); self.opacity_lbl.setFixedWidth(42)
        self.opacity_sl.valueChanged.connect(lambda v: self.opacity_lbl.setText(f"{v} %"))
        opr.addWidget(self.opacity_sl); opr.addWidget(self.opacity_lbl)
        form.addRow("Window opacity:", opr)
        # Icon pack
        pkr = QHBoxLayout()
        self.icon_pack_edit = QLineEdit()
        self.icon_pack_edit.setPlaceholderText("Leave blank = QGIS default icons (reference baseline)")
        bp = QPushButton("Browse…"); bp.clicked.connect(self._browse_pack)
        bd = QPushButton("Use QGIS default"); bd.clicked.connect(lambda: self.icon_pack_edit.clear())
        for x in (self.icon_pack_edit,bp,bd): pkr.addWidget(x)
        form.addRow("Icon pack folder:", pkr)
        hint = QLabel("Each preset stores its own icon pack path.\n"
                       "Blank = QGIS built-in icons (always available as the reference baseline).\n"
                       "Custom folder: PNG files with same names as QGIS icons/; "
                       "url(icons/…) in QSS is rewritten automatically.")
        hint.setWordWrap(True); form.addRow("", hint)
        return w

    # ── Background ────────────────────────────────────────────────────────────
    def _tab_background(self):
        w = QWidget(); form = QFormLayout(w); form.setContentsMargins(8,8,8,8)
        bgr = QHBoxLayout()
        self.bg_path_edit = QLineEdit(); self.bg_path_edit.setPlaceholderText("PNG/JPG/BMP path…")
        bb = QPushButton("Browse…"); bb.clicked.connect(self._browse_bg)
        self.bg_prev = QLabel(); self.bg_prev.setFixedSize(72,46); self.bg_prev.setScaledContents(True)
        self.bg_path_edit.textChanged.connect(self._upd_bg_prev)
        for x in (self.bg_path_edit,bb,self.bg_prev): bgr.addWidget(x)
        form.addRow("Background image:", bgr)
        self.bg_mode = QComboBox(); self.bg_mode.addItems(["stretch","tile","center","fit"])
        form.addRow("Fill mode:", self.bg_mode)
        bor = QHBoxLayout()
        self.bg_op_sl = QSlider(Qt.Horizontal); self.bg_op_sl.setRange(5,100)
        self.bg_op_sl.setValue(100); self.bg_op_sl.setTickInterval(10)
        self.bg_op_sl.setTickPosition(QSlider.TicksBelow)
        self.bg_op_lbl = QLabel("100 %"); self.bg_op_lbl.setFixedWidth(42)
        self.bg_op_sl.valueChanged.connect(lambda v: self.bg_op_lbl.setText(f"{v} %"))
        bor.addWidget(self.bg_op_sl); bor.addWidget(self.bg_op_lbl)
        form.addRow("Image opacity:", bor)
        form.addRow(QLabel("Background uses QPalette.Window — sits behind docked panels.\n"
                           "'stretch' gives a full-bleed wallpaper effect."))
        bc = QPushButton("Clear background"); bc.clicked.connect(lambda: self.bg_path_edit.clear())
        form.addRow(bc); return w

    # ── Font ──────────────────────────────────────────────────────────────────
    def _tab_font(self):
        w = QWidget(); form = QFormLayout(w); form.setContentsMargins(8,8,8,8)
        self.font_combo = QFontComboBox(); form.addRow("Font family:", self.font_combo)
        self.font_sz = QSpinBox(); self.font_sz.setRange(0,72)
        self.font_sz.setSpecialValueText("(keep default)"); form.addRow("Font size (pt):", self.font_sz)
        form.addRow(QLabel("Set size to 0 to leave the system default unchanged.")); return w

    # ── Presets ───────────────────────────────────────────────────────────────
    def _tab_presets(self):
        w = QWidget(); lay = QVBoxLayout(w); lay.setContentsMargins(8,8,8,8)
        lay.addWidget(QLabel(
            "Presets store every setting (stylesheet, icon pack, background, font, opacity).\n"
            "<b>QGIS Default</b> is always present as the baseline reference."))
        r1 = QHBoxLayout()
        self.preset_name = QLineEdit(); self.preset_name.setPlaceholderText("New preset name…")
        bs = QPushButton("Save current as preset"); bs.clicked.connect(self._save_preset)
        r1.addWidget(self.preset_name); r1.addWidget(bs); lay.addLayout(r1)
        r2 = QHBoxLayout()
        self.preset_combo = QComboBox()
        self.preset_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        bl = QPushButton("Load into UI"); bla = QPushButton("Load & Apply"); bdel = QPushButton("Delete")
        bl.clicked.connect(self._load_preset_ui); bla.clicked.connect(self._load_apply_preset)
        bdel.clicked.connect(self._delete_preset)
        r2.addWidget(self.preset_combo)
        for b in (bl,bla,bdel): r2.addWidget(b)
        lay.addLayout(r2); lay.addStretch(); self._refresh_presets(); return w

    # ── helpers ───────────────────────────────────────────────────────────────
    def _load_current(self):
        cfg = self.plugin.load_settings()
        self.qss_path_edit.setText(cfg.get("qss_path",""))
        self.qss_editor.setPlainText(cfg.get("qss_inline",""))
        self.live_reload_cb.setChecked(bool(cfg.get("live_reload",False)))
        self.icon_path_edit.setText(cfg.get("icon_path",""))
        self.icon_pack_edit.setText(cfg.get("icon_pack_dir",""))
        self.icon_size_sl.setValue(int(cfg.get("icon_size",0)))
        self.bg_path_edit.setText(cfg.get("bg_image_path",""))
        idx = self.bg_mode.findText(cfg.get("bg_mode","stretch"))
        if idx>=0: self.bg_mode.setCurrentIndex(idx)
        self.bg_op_sl.setValue(int(float(cfg.get("bg_opacity",1.0))*100))
        self.opacity_sl.setValue(int(float(cfg.get("opacity",1.0))*100))
        fam = cfg.get("font_family","")
        if fam: self.font_combo.setCurrentFont(QFont(fam))
        self.font_sz.setValue(int(cfg.get("font_size",0)))

    def _collect_cfg(self):
        return {
            "qss_path":      self.qss_path_edit.text().strip(),
            "qss_inline":    self.qss_editor.toPlainText(),
            "live_reload":   self.live_reload_cb.isChecked(),
            "icon_path":     self.icon_path_edit.text().strip(),
            "icon_pack_dir": self.icon_pack_edit.text().strip(),
            "icon_size":     self.icon_size_sl.value(),
            "bg_image_path": self.bg_path_edit.text().strip(),
            "bg_mode":       self.bg_mode.currentText(),
            "bg_opacity":    self.bg_op_sl.value()/100.0,
            "opacity":       self.opacity_sl.value()/100.0,
            "font_family":   self.font_combo.currentFont().family(),
            "font_size":     self.font_sz.value(),
        }

    def _browse_qss(self):
        p,_ = QFileDialog.getOpenFileName(self,"Select QSS","","QSS (*.qss);;All (*)")
        if p: self.qss_path_edit.setText(p)

    def _load_file_into_editor(self):
        p = self.qss_path_edit.text().strip()
        if p and os.path.isfile(p):
            with open(p,"r",encoding="utf-8") as fh:
                self.qss_editor.setPlainText(fh.read())

    def _save_to_file(self):
        p,_ = QFileDialog.getSaveFileName(self,"Save QSS","","QSS (*.qss)")
        if p:
            with open(p,"w",encoding="utf-8") as fh:
                fh.write(self.qss_editor.toPlainText())
            self.qss_path_edit.setText(p)

    def _browse_icon(self):
        p,_ = QFileDialog.getOpenFileName(self,"Select icon","","Images (*.png *.svg *.ico *.jpg);;All (*)")
        if p: self.icon_path_edit.setText(p)

    def _browse_pack(self):
        d = QFileDialog.getExistingDirectory(self,"Select icon pack folder")
        if d: self.icon_pack_edit.setText(d)

    def _browse_bg(self):
        p,_ = QFileDialog.getOpenFileName(self,"Select background","","Images (*.png *.jpg *.bmp *.webp);;All (*)")
        if p: self.bg_path_edit.setText(p)

    def _upd_icon_prev(self, path):
        if path and os.path.isfile(path): self.icon_prev.setPixmap(QIcon(path).pixmap(32,32))
        else: self.icon_prev.clear()

    def _upd_bg_prev(self, path):
        if path and os.path.isfile(path):
            px = QPixmap(path)
            if not px.isNull():
                self.bg_prev.setPixmap(px.scaled(72,46,Qt.KeepAspectRatio,Qt.SmoothTransformation))
                return
        self.bg_prev.clear()

    def _validate(self):
        t = self.qss_editor.toPlainText()
        errs = []
        if t.count("{") != t.count("}"): errs.append(f"⚠ Unmatched braces: {t.count('{')} vs {t.count('}')}")
        if "/*" in t and t.count("/*") != t.count("*/"): errs.append("⚠ Unclosed comment")
        if errs:
            self._val_lbl.setText("  ".join(errs)); self._val_lbl.setStyleSheet("color:#e17055;")
        else:
            self._val_lbl.setText("✓ No issues"); self._val_lbl.setStyleSheet("color:#00b894;")

    def _format(self):
        t = self.qss_editor.toPlainText()
        out=[]; ind=0
        for ch in t:
            if ch=="{": out.append(" {\n"); ind=4
            elif ch=="}": ind=0; out.append("\n}\n\n")
            elif ch==";": out.append(";\n"+" "*ind)
            else: out.append(ch)
        self.qss_editor.setPlainText("".join(out).strip())

    def _refresh_presets(self):
        self.preset_combo.clear()
        self.preset_combo.addItems(self.plugin.list_presets())

    def _save_preset(self):
        name = self.preset_name.text().strip()
        if not name: QMessageBox.warning(self,"UI Themes+","Enter a preset name."); return
        self.plugin.save_preset(name, self._collect_cfg())
        self._refresh_presets(); self.preset_name.clear()
        self.iface.messageBar().pushSuccess("UI Themes+",f'Preset "{name}" saved.')

    def _fill_ui_from_cfg(self, cfg):
        self.qss_path_edit.setText(cfg.get("qss_path",""))
        self.qss_editor.setPlainText(cfg.get("qss_inline",""))
        self.live_reload_cb.setChecked(bool(cfg.get("live_reload",False)))
        self.icon_path_edit.setText(cfg.get("icon_path",""))
        self.icon_pack_edit.setText(cfg.get("icon_pack_dir",""))
        self.icon_size_sl.setValue(int(cfg.get("icon_size",0) or 0))
        self.bg_path_edit.setText(cfg.get("bg_image_path",""))
        idx = self.bg_mode.findText(cfg.get("bg_mode","stretch"))
        if idx>=0: self.bg_mode.setCurrentIndex(idx)
        try: self.bg_op_sl.setValue(int(float(cfg.get("bg_opacity",1.0))*100))
        except: pass
        try: self.opacity_sl.setValue(int(float(cfg.get("opacity",1.0))*100))
        except: pass
        fam = cfg.get("font_family","")
        if fam: self.font_combo.setCurrentFont(QFont(fam))
        try: self.font_sz.setValue(int(cfg.get("font_size",0) or 0))
        except: pass

    def _load_preset_ui(self):
        name = self.preset_combo.currentText()
        if name: self._fill_ui_from_cfg(self.plugin.load_preset(name))

    def _load_apply_preset(self):
        self._load_preset_ui()
        self.plugin.apply_all(self._collect_cfg())
        title = self.title_edit.text().strip()
        if title: self.iface.mainWindow().setWindowTitle(title)
        self.iface.messageBar().pushSuccess("UI Themes+",
            f'Preset "{self.preset_combo.currentText()}" applied.')

    def _delete_preset(self):
        name = self.preset_combo.currentText()
        if name == "QGIS Default":
            QMessageBox.information(self,"UI Themes+","'QGIS Default' cannot be deleted."); return
        if QMessageBox.question(self,"UI Themes+",f'Delete "{name}"?',
                                QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
            self.plugin.delete_preset(name); self._refresh_presets()

    def _on_apply(self):
        cfg = self._collect_cfg()
        title = self.title_edit.text().strip()
        if title: self.iface.mainWindow().setWindowTitle(title)
        self.plugin.apply_all(cfg)
        self.iface.messageBar().pushSuccess("UI Themes+","Applied.")

    def _on_reset(self):
        if QMessageBox.question(self,"UI Themes+",
                "Reset ALL UI Themes+ customisations?\n"
                "QGIS will restore the theme active before this plugin was first used.",
                QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
            self.plugin.apply_all({"reset":True})
            self._load_current()
