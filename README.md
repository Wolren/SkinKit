[![CI](https://github.com/Wolren/SkinKit/actions/workflows/ci.yml/badge.svg)](https://github.com/Wolren/SkinKit/actions/workflows/ci.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/Wolren/SkinKit/badge)](https://securityscorecards.dev/viewer/?uri=github.com/Wolren/SkinKit)
[![Socket](https://img.shields.io/badge/Socket-Supply%20Chain%20Security-333?logo=socketdotdev)](https://socket.dev)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![QGIS 3.22+](https://img.shields.io/badge/QGIS-3.22+-green)](https://qgis.org)
[![Qt](https://img.shields.io/badge/Qt-5.x_|_6.x-green)](https://www.qt.io/)

# SkinKit

**Complete QGIS UI customisation plugin.** Successor to QSS Forge / Load-QSS.

---

## Features

| Feature | Details |
|---|---|
| **Theme Gallery** | One-click cards: Light, Dark, Minimalist, Dark Forest, Orange Forest, Wombat, Coffee, Dark green, Light green |
| **Stylesheet Editor** | Syntax-highlighted QSS editor with colour swatches, line numbers, brace/comment validation, auto-indent, save-to-file |
| **Live Reload** | `QFileSystemWatcher` auto-applies when you save the file externally (debounced 200 ms) |
| **Icon Pack per Preset** | Each preset stores its own icons/ folder; blank = QGIS default icons as reference baseline |
| **Background Image** | PNG/JPG on the main window: stretch, tile, center, fit modes (resize debounced 80 ms) |
| **Window Icon** | Override QGIS titlebar/taskbar icon per preset |
| **Toolbar Icon Size** | Slider 0-128 px via `QMainWindow.setIconSize()` |
| **Window Opacity** | Slider 10-100 % |
| **Font Override** | Family + point size |
| **Named Presets** | All settings stored together; QGIS Default always present |
| **Safe Reset** | Restores the QGIS built-in theme active *before* SkinKit was first used |
| **Persist on startup** | All settings stored in `QgsSettings`, re-applied in `initGui()` |

## Quick start

1. Install the plugin: copy `SkinKit/` to your QGIS plugins folder.
2. Enable **SkinKit** in Plugins → Manage and Install Plugins.
3. Click the SkinKit toolbar icon or go to Plugins → SkinKit.
4. Pick a theme from the Gallery tab, then click **Apply**.

## Installation

| OS | Path |
|---|---|
| Linux / macOS | `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/` |
| Windows | `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\` |

Or download `SkinKit-<version>.zip` from [Releases](https://github.com/Wolren/SkinKit/releases) and unzip into that folder.

## Development

```bash
# Lint
ruff check SkinKit/

# Build release zip
python package.py           # creates SkinKit-<version>.zip
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for full development guide.

## License

GNU General Public License v3.0 -- see [LICENSE](LICENSE).
