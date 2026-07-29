"""Stub qgis.PyQt.QtGui for headless testing."""



class QColor:
    """Stub QColor."""

    def __init__(self, *args):
        self._r = 0
        self._g = 0
        self._b = 0
        self._a = 255
        self._valid = True
        if len(args) == 1 and isinstance(args[0], str):
            s = args[0].lstrip("#")
            if len(s) in (3, 6, 8):
                try:
                    if len(s) == 3:
                        s = "".join(c * 2 for c in s)
                    if len(s) == 8:
                        self._a = int(s[6:8], 16)
                        s = s[:6]
                    self._r = int(s[0:2], 16)
                    self._g = int(s[2:4], 16)
                    self._b = int(s[4:6], 16)
                except ValueError:
                    self._valid = False
            else:
                self._valid = False
        elif len(args) >= 3:
            self._r = int(args[0])
            self._g = int(args[1])
            self._b = int(args[2])
            if len(args) >= 4:
                self._a = int(args[3])

    def isValid(self):
        return self._valid

    def red(self):
        return self._r

    def green(self):
        return self._g

    def blue(self):
        return self._b

    def alpha(self):
        return self._a

    def name(self):
        return f"#{self._r:02x}{self._g:02x}{self._b:02x}"

    def lighter(self, factor=150):
        return self

    def __repr__(self):
        return f"QColor({self.name()})"


class QFont:
    """Stub QFont."""

    Bold = 75  # QFont.Weight enum value (Qt5 compat)

    def __init__(self, family="", pointSize=-1):
        self._family = family
        self._pointSize = pointSize
        self._bold = False
        self._italic = False

    def setFamily(self, family):
        self._family = family

    def family(self):
        return self._family

    def setPointSize(self, sz):
        self._pointSize = sz

    def pointSize(self):
        return self._pointSize

    def setBold(self, bold):
        self._bold = bold

    def bold(self):
        return self._bold

    def setItalic(self, italic):
        self._italic = italic

    def italic(self):
        return self._italic


class QIcon:
    """Stub QIcon."""

    def __init__(self, path=""):
        self._path = path

    def pixmap(self, w, h):
        return QPixmap()


class QBrush:
    """Stub QBrush."""

    def __init__(self, *args):
        pass


class QPalette:
    """Stub QPalette."""

    Window = 1

    def __init__(self, other=None):
        self._brushes = {}

    def setBrush(self, role, brush):
        self._brushes[role] = brush

    def brush(self, role):
        return self._brushes.get(role, QBrush())


class QPixmap:
    """Stub QPixmap."""

    def __init__(self, path=None):
        self._path = path
        self._null = path is None

    def isNull(self):
        return self._null

    def scaled(self, *args, **kwargs):
        return self

    def width(self):
        return 100

    def height(self):
        return 100


class QTextCharFormat:
    """Stub QTextCharFormat."""

    def __init__(self):
        self._foreground = None
        self._background = None
        self._font_weight = -1
        self._font_italic = False
        self._properties = {}

    def setForeground(self, color):
        self._foreground = color

    def foreground(self):
        return self._foreground

    def setBackground(self, color):
        self._background = color

    def background(self):
        return self._background

    def setFontWeight(self, weight):
        self._font_weight = weight

    def fontWeight(self):
        return self._font_weight

    def setFontItalic(self, italic):
        self._font_italic = italic

    def fontItalic(self):
        return self._font_italic

    def setProperty(self, key, val):
        self._properties[key] = val


class QTextFormat:
    FullWidthSelection = 768  # commonly used value


class QSyntaxHighlighter:
    """Stub QSyntaxHighlighter — tracks formats set per position."""

    def __init__(self, document=None):
        self._document = document
        self._formats = {}
        self._current_block_state = -1
        self._previous_block_state = -1

    def setFormat(self, start, length, fmt):
        for i in range(start, start + length):
            self._formats[i] = fmt

    def formatAt(self, pos):
        return self._formats.get(pos)

    def document(self):
        return self._document

    def highlightBlock(self, text):
        pass

    def setCurrentBlockState(self, state):
        self._previous_block_state = self._current_block_state
        self._current_block_state = state

    def previousBlockState(self):
        return self._previous_block_state


class QPainter:
    """Stub QPainter."""

    def __init__(self, device=None):
        pass

    def fillRect(self, rect, color):
        pass

    def setPen(self, color):
        pass

    def setFont(self, font):
        pass

    def drawText(self, x, y, w, h, align, text):
        pass
