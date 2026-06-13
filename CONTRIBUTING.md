# Contributing

## Development setup

1. Clone the repo and symlink or copy `SkinKit/` into your QGIS profile plugins folder.
2. Use QGIS Plugin Reloader (from plugin manager) to reload after edits.
3. Run `python package.py` to build a release zip.

## Code style

- **Linter:** [ruff](https://docs.astral.sh/ruff/) — run `ruff check .` before committing.
- **Target:** Python 3.8+ (QGIS 3.16 minimum).
- **Qt:** Use `qgis.PyQt` compat layer, not raw `PyQt5`/`PyQt6`.
- No `# -*- coding: utf-8 -*-` headers (Python 3 defaults to UTF-8).
- Public methods should have docstrings (Google style).

## Pull requests

- Keep changes focused — one feature/fix per PR.
- Test manually in QGIS before submitting.
- Update `metadata.txt` version and `changelog` field.

## Release process

1. Bump version in `metadata.txt`.
2. Tag: `git tag v0.3 && git push origin v0.3`.
3. CI builds `SkinKit-<version>.zip` and creates a GitHub release.
4. Upload the zip to <https://plugins.qgis.org> manually or via the QGIS plugin upload API.
