# Changelog

## 0.2

- Renamed from UI Themes+ to SkinKit
- Complete production-readiness audit and fixes
- Background painter now debounced (80ms timer)
- Live-reload file watcher debounced (200ms timer)
- Preset name validation (rejects / \ : % & < >)
- Type-safe settings read with safe_int/safe_float helpers
- Error handling for file I/O throughout
- Qt6 compatible (no QString, QVariant, or QRegExp)
- GitHub Actions CI + release workflows

## 0.1

- Initial release as UI Themes+
