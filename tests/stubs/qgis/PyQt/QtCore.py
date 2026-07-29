"""Stub qgis.PyQt.QtCore for headless testing.

Provides minimal stubs sufficient to import and test SkinKit modules.
"""


class QEvent:
    Resize = 14

    def __init__(self, type_):
        self._type = type_

    def type(self):
        return self._type


class QObject:
    """Stub base class."""

    def __init__(self, parent=None):
        self._parent = parent

    def parent(self):
        return self._parent

    def eventFilter(self, obj, event):
        return False

    def installEventFilter(self, obj):
        pass

    def removeEventFilter(self, obj):
        pass


class QTimer(QObject):
    """Stub QTimer."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._single_shot = False
        self._interval = 0
        self._active = False
        self.timeout = _Signal()

    def setSingleShot(self, single):
        self._single_shot = single

    def isSingleShot(self):
        return self._single_shot

    def setInterval(self, ms):
        self._interval = ms

    def interval(self):
        return self._interval

    def start(self, ms=0):
        if ms:
            self._interval = ms
        self._active = True

    def stop(self):
        self._active = False

    def isActive(self):
        return self._active


class QFileSystemWatcher(QObject):
    """Stub QFileSystemWatcher."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._paths = []
        self.fileChanged = _Signal()
        self.directoryChanged = _Signal()

    def addPath(self, path):
        if path not in self._paths:
            self._paths.append(path)

    def removePath(self, path):
        if path in self._paths:
            self._paths.remove(path)

    def files(self):
        return list(self._paths)

    def directories(self):
        return []


class QSize:
    """Stub QSize."""

    def __init__(self, w=0, h=0):
        self._w = w
        self._h = h

    def width(self):
        return self._w

    def height(self):
        return self._h

    def __eq__(self, other):
        if isinstance(other, QSize):
            return self._w == other._w and self._h == other._h
        return False


class Qt:
    IgnoreAspectRatio = 0
    KeepAspectRatio = 1
    SmoothTransformation = 1
    FastTransformation = 0
    AlignRight = 2
    AlignLeft = 1
    AlignCenter = 4
    AlignTop = 8
    AlignBottom = 16
    PointingHandCursor = 13
    Horizontal = 1
    TicksBelow = 2
    TicksAbove = 1


class QRegularExpression:
    """Stub QRegularExpression."""

    def __init__(self, pattern):
        self._pattern = pattern

    def match(self, text, offset=0):
        import re
        m = re.search(self._pattern, text[offset:])
        if m:
            return _QRegularExpressionMatch(m, offset)
        return _QRegularExpressionMatch(None, offset)

    def globalMatch(self, text):
        return _QRegularExpressionMatchIterator(self._pattern, text)


class _QRegularExpressionMatch:
    def __init__(self, match_obj, offset=0):
        self._match = match_obj
        self._offset = offset

    def hasMatch(self):
        return self._match is not None

    def capturedStart(self, n=0):
        if self._match:
            return self._match.start(n) + self._offset
        return -1

    def capturedLength(self, n=0):
        if self._match:
            return self._match.end(n) - self._match.start(n)
        return 0

    def captured(self, n=0):
        if self._match:
            return self._match.group(n)
        return ""


class _QRegularExpressionMatchIterator:
    def __init__(self, pattern, text):
        import re
        self._matches = list(re.finditer(pattern, text))
        self._idx = 0

    def hasNext(self):
        return self._idx < len(self._matches)

    def next(self):
        if self._idx < len(self._matches):
            m = self._matches[self._idx]
            self._idx += 1
            return _QRegularExpressionMatch(m)
        return _QRegularExpressionMatch(None)


class _Signal:
    """Minimal stub signal that can be connected/disconnected/emitted."""

    def __init__(self):
        self._slots = []

    def connect(self, slot):
        if slot not in self._slots:
            self._slots.append(slot)

    def disconnect(self, slot=None):
        if slot is None:
            self._slots.clear()
        elif slot in self._slots:
            self._slots.remove(slot)

    def emit(self, *args, **kwargs):
        for slot in self._slots:
            slot(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        self.emit(*args, **kwargs)
