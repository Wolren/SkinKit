"""Stub qgis.PyQt.QtWidgets for headless testing."""

from .QtCore import QObject, QSize, Qt, _Signal


class QWidget(QObject):
    """Stub QWidget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._palette = None
        self._auto_fill = False
        self._layout = None
        self._window_title = ""
        self._opacity = 1.0
        self._icon = None
        self._icon_size = QSize(0, 0)
        self._visible = False
        self._styles = {}

    def palette(self):
        if self._palette is None:
            from .QtGui import QPalette
            self._palette = QPalette()
        return self._palette

    def setPalette(self, pal):
        self._palette = pal

    def setAutoFillBackground(self, fill):
        self._auto_fill = fill

    def autoFillBackground(self):
        return self._auto_fill

    def setWindowTitle(self, title):
        self._window_title = title

    def windowTitle(self):
        return self._window_title

    def setWindowOpacity(self, op):
        self._opacity = op

    def windowOpacity(self):
        return self._opacity

    def setWindowIcon(self, icon):
        self._icon = icon

    def windowIcon(self):
        return self._icon

    def setIconSize(self, sz):
        self._icon_size = sz

    def iconSize(self):
        return self._icon_size

    def show(self):
        self._visible = True

    def hide(self):
        self._visible = False

    def close(self):
        self._visible = False

    def deleteLater(self):
        pass

    def size(self):
        return QSize(800, 600)

    def setStyleSheet(self, css):
        self._styles[self] = css

    def styleSheet(self):
        return self._styles.get(self, "")

    def setLayout(self, layout):
        self._layout = layout

    def layout(self):
        return self._layout

    def update(self, *args):
        pass

    def raise_(self):
        pass

    def activateWindow(self):
        pass

    def installEventFilter(self, obj):
        pass

    def removeEventFilter(self, obj):
        pass

    def setFixedSize(self, w, h):
        pass

    def setFixedWidth(self, w):
        pass

    def setMinimumWidth(self, w):
        pass

    def setMinimumHeight(self, h):
        pass

    def setCursor(self, cursor):
        pass

    def parent(self):
        return self._parent

    def findChildren(self, cls):
        return []

    def font(self):
        from .QtGui import QFont
        return QFont()

    def setFont(self, font):
        pass

    def fontMetrics(self):
        return _FontMetrics()


class _FontMetrics:
    def height(self):
        return 16

    def horizontalAdvance(self, text):
        return len(text) * 8


class QMainWindow(QWidget):
    """Stub QMainWindow."""

    def __init__(self, parent=None):
        super().__init__(parent)


class QDialog(QWidget):
    """Stub QDialog."""

    Accepted = 1
    Rejected = 0

    def __init__(self, parent=None):
        super().__init__(parent)
        self._result = 0

    def exec_(self):
        return self._result

    def accept(self):
        self._result = self.Accepted

    def reject(self):
        self._result = self.Rejected

    def setModal(self, modal):
        pass


class QVBoxLayout:
    """Stub QVBoxLayout."""

    def __init__(self, parent=None):
        self._parent = parent
        self._items = []
        if parent:
            parent.setLayout(self)

    def addWidget(self, w, stretch=0, alignment=None):
        self._items.append(("widget", w, stretch, alignment))

    def addLayout(self, layout):
        self._items.append(("layout", layout))

    def addStretch(self, stretch=0):
        self._items.append(("stretch", stretch))

    def setContentsMargins(self, *margins):
        pass

    def setSpacing(self, spacing):
        pass


class QHBoxLayout:
    """Stub QHBoxLayout."""

    def __init__(self, parent=None):
        self._parent = parent
        self._items = []
        if parent:
            parent.setLayout(self)

    def addWidget(self, w, stretch=0, alignment=None):
        self._items.append(("widget", w, stretch, alignment))

    def addLayout(self, layout):
        self._items.append(("layout", layout))

    def addStretch(self, stretch=0):
        self._items.append(("stretch", stretch))

    def setContentsMargins(self, *margins):
        pass

    def setSpacing(self, spacing):
        pass


class QFormLayout:
    """Stub QFormLayout."""

    def __init__(self, parent=None):
        self._parent = parent
        self._rows = []
        if parent:
            parent.setLayout(self)

    def addRow(self, label, field):
        self._rows.append((label, field))

    def setContentsMargins(self, *margins):
        pass

    def setSpacing(self, spacing):
        pass


class QLabel(QWidget):
    """Stub QLabel."""

    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._text = text
        self._pixmap = None
        self._word_wrap = False
        self._scaled = False

    def setText(self, text):
        self._text = text

    def text(self):
        return self._text

    def setPixmap(self, px):
        self._pixmap = px

    def pixmap(self):
        return self._pixmap

    def setWordWrap(self, wrap):
        self._word_wrap = wrap

    def setFixedSize(self, w, h):
        pass

    def setFixedWidth(self, w):
        pass

    def setScaledContents(self, scaled):
        self._scaled = scaled

    def clear(self):
        self._pixmap = None
        self._text = ""


class QLineEdit(QWidget):
    """Stub QLineEdit."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._text = ""
        self._placeholder = ""
        self.textChanged = _Signal()
        self.textEdited = _Signal()

    def setText(self, text):
        self._text = text
        self.textChanged.emit(text)

    def text(self):
        return self._text

    def clear(self):
        self.setText("")

    def setPlaceholderText(self, txt):
        self._placeholder = txt

    def placeholderText(self):
        return self._placeholder

    def setReadOnly(self, ro):
        pass


class QPushButton(QWidget):
    """Stub QPushButton."""

    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._text = text
        self.clicked = _Signal()

    def setFixedWidth(self, w):
        pass

    def setFixedHeight(self, h):
        pass

    def text(self):
        return self._text

    def setText(self, text):
        self._text = text


class QComboBox(QWidget):
    """Stub QComboBox."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._current = -1
        self.currentIndexChanged = _Signal()
        self.currentTextChanged = _Signal()

    def addItem(self, text):
        self._items.append(text)
        if self._current < 0:
            self._current = 0

    def addItems(self, items):
        for i in items:
            self.addItem(i)

    def currentText(self):
        if 0 <= self._current < len(self._items):
            return self._items[self._current]
        return ""

    def setCurrentIndex(self, idx):
        self._current = idx

    def currentIndex(self):
        return self._current

    def findText(self, text):
        for i, item in enumerate(self._items):
            if item == text:
                return i
        return -1

    def count(self):
        return len(self._items)

    def clear(self):
        self._items = []
        self._current = -1

    def setSizePolicy(self, h, v):
        pass


class QTabWidget(QWidget):
    """Stub QTabWidget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tabs = []

    def addTab(self, w, title):
        self._tabs.append((w, title))

    def setCurrentIndex(self, idx):
        pass

    def currentIndex(self):
        return 0

    def count(self):
        return len(self._tabs)

    def widget(self, idx):
        if 0 <= idx < len(self._tabs):
            return self._tabs[idx][0]
        return None


class QGroupBox(QWidget):
    """Stub QGroupBox."""

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self._title = title

    def title(self):
        return self._title

    def setTitle(self, title):
        self._title = title


class QScrollArea(QWidget):
    """Stub QScrollArea."""

    def __init__(self, parent=None):
        super().__init__(parent)

    def setWidgetResizable(self, resizable):
        pass

    def setWidget(self, w):
        pass

    def widget(self):
        return None


class QFrame(QWidget):
    """Stub QFrame."""

    StyledPanel = 6

    def __init__(self, parent=None):
        super().__init__(parent)
        self._frame_shape = 0

    def setFrameShape(self, shape):
        self._frame_shape = shape

    def frameShape(self):
        return self._frame_shape


class QSlider(QWidget):
    """Stub QSlider."""

    TicksBelow = 2
    TicksAbove = 1

    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(parent)
        self._min = 0
        self._max = 100
        self._val = 0
        self._single_step = 1
        self._tick_interval = 0
        self._tick_pos = 0
        self.valueChanged = _Signal()

    def setRange(self, lo, hi):
        self._min = lo
        self._max = hi

    def setMinimum(self, lo):
        self._min = lo

    def setMaximum(self, hi):
        self._max = hi

    def setSingleStep(self, step):
        self._single_step = step

    def setTickInterval(self, ti):
        self._tick_interval = ti

    def setTickPosition(self, pos):
        self._tick_pos = pos

    def setValue(self, val):
        self._val = max(self._min, min(self._max, val))
        self.valueChanged.emit(self._val)

    def value(self):
        return self._val


class QSpinBox(QWidget):
    """Stub QSpinBox."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._min = 0
        self._max = 99
        self._val = 0
        self._special = ""
        self.valueChanged = _Signal()

    def setRange(self, lo, hi):
        self._min = lo
        self._max = hi

    def setValue(self, val):
        self._val = max(self._min, min(self._max, val))
        self.valueChanged.emit(self._val)

    def value(self):
        return self._val

    def setSpecialValueText(self, txt):
        self._special = txt


class QFontComboBox(QWidget):
    """Stub QFontComboBox."""

    def __init__(self, parent=None):
        super().__init__(parent)

    def setCurrentFont(self, font):
        pass

    def currentFont(self):
        from .QtGui import QFont
        return QFont()


class QCheckBox(QWidget):
    """Stub QCheckBox."""

    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._checked = False
        self._text = text
        self.stateChanged = _Signal()

    def setChecked(self, checked):
        self._checked = checked
        self.stateChanged.emit(2 if checked else 0)

    def isChecked(self):
        return self._checked

    def text(self):
        return self._text


class QPlainTextEdit(QWidget):
    """Stub QPlainTextEdit."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._text = ""
        self._placeholder = ""
        self._read_only = False
        self.textChanged = _Signal()
        self.blockCountChanged = _Signal()
        self.updateRequest = _Signal()
        self.cursorPositionChanged = _Signal()

    def setPlainText(self, text):
        self._text = text
        self.textChanged.emit()

    def toPlainText(self):
        return self._text

    def clear(self):
        self.setPlainText("")

    def setPlaceholderText(self, txt):
        self._placeholder = txt

    def placeholderText(self):
        return self._placeholder

    def setReadOnly(self, ro):
        self._read_only = ro

    def isReadOnly(self):
        return self._read_only

    def setFont(self, font):
        pass

    def font(self):
        from .QtGui import QFont
        return QFont()

    def fontMetrics(self):
        return _FontMetrics()

    def document(self):
        return _TextDocument()

    def setViewportMargins(self, left, top, right, bot):
        pass

    def viewport(self):
        return QWidget()

    def contentsRect(self):
        return _Rect()

    def firstVisibleBlock(self):
        return _TextBlock()

    def blockBoundingGeometry(self, block):
        return _Rect()

    def blockBoundingRect(self, block):
        return _Rect()

    def contentOffset(self):
        return _Point()

    def textCursor(self):
        return _TextCursor()

    def setExtraSelections(self, sels):
        pass

    def setTextCursor(self, cursor):
        pass


class QTextEdit(QWidget):
    """Stub QTextEdit."""

    class ExtraSelection:
        def __init__(self):
            self.format = None
            self.cursor = None


class _TextDocument:
    def __init__(self):
        self._blocks = []
        self._highlight = None

    def findBlockByNumber(self, n):
        return _TextBlock()

    def blockCount(self):
        return max(1, len(self._blocks))


class _TextBlock:
    def __init__(self):
        self._num = 0

    def blockNumber(self):
        return self._num

    def isValid(self):
        return True

    def isVisible(self):
        return True

    def next(self):
        return _TextBlock()


class _Rect:
    def __init__(self, x=0, y=0, w=800, h=600):
        self._x = x
        self._y = y
        self._w = w
        self._h = h

    def top(self):
        return self._y

    def bottom(self):
        return self._y + self._h

    def left(self):
        return self._x

    def right(self):
        return self._x + self._w

    def width(self):
        return self._w

    def height(self):
        return self._h

    def contains(self, other):
        return True


class _Point:
    def __init__(self, x=0, y=0):
        self._x = x
        self._y = y

    def x(self):
        return self._x

    def y(self):
        return self._y


class _TextCursor:
    def __init__(self):
        pass

    def clearSelection(self):
        pass


class QFileDialog:
    """Stub QFileDialog."""

    @staticmethod
    def getOpenFileName(*args, **kwargs):
        return ("", "")

    @staticmethod
    def getSaveFileName(*args, **kwargs):
        return ("", "")

    @staticmethod
    def getExistingDirectory(*args, **kwargs):
        return ""


class QMessageBox:
    """Stub QMessageBox."""

    Warning = 0
    Information = 1
    Question = 2
    Yes = 3
    No = 4
    YesToAll = 5
    NoToAll = 6

    @classmethod
    def warning(cls, *args, **kwargs):
        pass

    @classmethod
    def information(cls, *args, **kwargs):
        pass

    @classmethod
    def question(cls, *args, **kwargs):
        return cls.Yes


class QDialogButtonBox(QWidget):
    """Stub QDialogButtonBox."""

    ApplyRole = 0
    ResetRole = 1
    AcceptRole = 2
    RejectRole = 3
    Close = 4

    def __init__(self, parent=None):
        super().__init__(parent)
        self._buttons = []
        self.accepted = _Signal()
        self.rejected = _Signal()

    def addButton(self, text, role):
        btn = QPushButton(text)
        self._buttons.append((btn, role))
        return btn

    def button(self, role):
        for btn, r in self._buttons:
            if r == role:
                return btn
        return None


class QSizePolicy:
    """Stub QSizePolicy."""

    Expanding = 1
    Fixed = 0

    def __init__(self, h=Fixed, v=Fixed):
        self.h = h
        self.v = v


class QApplication(QWidget):
    """Stub QApplication."""

    _instance = None

    def __init__(self, argv=None):
        super().__init__()
        self._font = None
        self._stylesheet = ""
        QApplication._instance = self

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = QApplication()
        return cls._instance

    def setStyleSheet(self, css):
        self._stylesheet = css

    def styleSheet(self):
        return self._stylesheet

    def font(self):
        from .QtGui import QFont
        if self._font is None:
            self._font = QFont()
        return self._font

    def setFont(self, font):
        self._font = font

    def setWindowIcon(self, icon):
        self._window_icon = icon


class QAction(QObject):
    """Stub QAction."""

    def __init__(self, icon=None, text="", parent=None):
        super().__init__(parent)
        self._icon = icon
        self._text = text
        self.triggered = _Signal()

    def triggered(self):
        return self._signal

    def setText(self, text):
        self._text = text

    def text(self):
        return self._text
