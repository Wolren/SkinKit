# SkinKit

Complete QGIS UI customisation plugin. Successor to QSS Forge / Load-QSS.

## Installation

1. Copy the `SkinKit/` folder to your QGIS plugins directory:
   - Linux/Mac: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
   - Windows: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
2. Restart QGIS (or use Plugin Reloader).
3. Enable **SkinKit** in Plugins → Manage and Install Plugins.

## Usage

Click the SkinKit toolbar icon, or go to Plugins → SkinKit.

| Tab | What you can do |
|---|---|
| Gallery | Click a theme card, then **Apply** |
| Stylesheet | Browse to a `.qss` file, or write QSS inline with syntax highlighting |
| Icon / Window | Set window icon, toolbar icon size, opacity, icon pack folder |
| Background | Set a background image with stretch/tile/center/fit |
| Font | Override application font family and size |
| Presets | Save/load all settings as named presets |

## Built-in themes

| Name | File |
|---|---|
| Light | `builtin_themes/light/light.qss` |
| Dark | `builtin_themes/Dark/darkstyle.qss` |
| Minimalist | `builtin_themes/Minimalist/Minimalist.qss` |
| Dark Forest | `builtin_themes/DarkForest.qss` |
| Orange Forest | `builtin_themes/OrangeForest.qss` |
| Wombat | `builtin_themes/Wombat/stylesheet.qss` |
| Coffee | `builtin_themes/Coffee/coffee.qss` |
| Dark green | `builtin_themes/Dark Green (FreeCAD)/stylesheet.qss` |
| Light green | `builtin_themes/Light Green (FreeCAD)/stylesheet.qss` |

## Icon packs

- Leave blank → QGIS built-in icons (default reference).
- Set a folder path → `url(icons/…)` in QSS rewritten to that path.
- Each preset stores its own icon pack path.

## Safe Reset

On first load, the plugin records your current QGIS UI theme name.
**Reset All** clears stylesheet overrides and writes that theme name back to `QgsSettings`,
so QGIS restores it on the next restart.

## License

GNU General Public License v3.0.
