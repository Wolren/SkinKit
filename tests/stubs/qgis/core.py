"""Stub qgis.core for headless testing."""


class QgsMessageLog:
    """Stub for QgsMessageLog."""

    _messages = []

    @classmethod
    def logMessage(cls, msg, tag="", level=0):
        cls._messages.append((msg, tag, level))


class QgsSettings:
    """Stub for QgsSettings — in-memory dict."""

    def __init__(self):
        self._store = {}

    def value(self, key, default=None, type=None):
        val = self._store.get(key, default)
        if type is not None and val is not None:
            try:
                return type(val)
            except (ValueError, TypeError):
                return default
        return val

    def setValue(self, key, val):
        self._store[key] = val

    def remove(self, key):
        keys = [k for k in self._store if k == key or k.startswith(f"{key}/")]
        for k in keys:
            self._store.pop(k, None)

    def beginGroup(self, prefix):
        self._group_prefix = prefix

    def endGroup(self):
        self._group_prefix = None

    def childGroups(self):
        prefix = self._group_prefix or ""
        groups = set()
        for k in self._store:
            if k.startswith(prefix):
                rest = k[len(prefix) :].strip("/")
                if "/" in rest:
                    groups.add(rest.split("/")[0])
        return list(groups)
