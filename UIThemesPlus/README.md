# UI Themes+

Complete QGIS UI customisation plugin. Successor to QSS Forge / Load-QSS.

## Features

| Feature | Details |
|---|---|
| **Theme Gallery** | One-click cards: QGIS Default, Night Mapping, Blend of Gray, Dark Forest, Therian Wolf, PrideGIS |
| **Stylesheet Editor** | Syntax-highlighted QSS editor with colour swatches, line numbers, brace/comment validation, auto-indent, save-to-file |
| **Live Reload** | QFileSystemWatcher auto-applies when you save the file externally |
| **Icon Pack per Preset** | Each preset stores its own icons/ folder; blank = QGIS default icons as reference baseline |
| **Background Image** | PNG/JPG background on the main window: stretch, tile, center, fit modes |
| **Window Icon** | Override QGIS titlebar/taskbar icon per preset |
| **Toolbar Icon Size** | Slider 0–128 px via QMainWindow.setIconSize() |
| **Window Opacity** | Slider 10–100 % |
| **Font Override** | Family + point size |
| **Named Presets** | All settings stored together; QGIS Default always present |
| **Safe Reset** | Restores the QGIS built-in theme that was active *before* UI Themes+ was first used |
| **Persist on startup** | All settings stored in QgsSettings, re-applied in initGui() |

## Installation

1. Copy `UIThemesPlus/` to your QGIS plugins folder:
   - Linux/Mac: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
   - Windows: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
2. Restart QGIS (or use Plugin Reloader).
3. Enable **UI Themes+** in Plugins → Manage and Install Plugins.

## Built-in theme stubs

`builtin_themes/DarkForest.qss`, `Therian.qss`, `PrideGIS.qss` are stubs.
Replace their content with your full QSS files from this session, **or** just
point the Stylesheet Editor file picker to the external paths.

## Icon packs

- Leave Icon pack folder blank → QGIS built-in icons (default, always the reference).
- Set a folder path → all `url(icons/...)` in your QSS are rewritten to that path automatically.
- Each preset can have a different icon pack.

## Safe Reset

On first load, the plugin records your current QGIS UI theme name.
Reset All → clears stylesheet overrides and writes that theme name back to QgsSettings,
so QGIS restores it on the next restart (e.g. Night Mapping → Night Mapping, not Default).

## License
GPL-3.0
