# Changelog

## 0.2.0 — 2026-03-18

- Sync Data: auto-sync span values to Data YAML on save (`syncOnSave` setting)
- Add right-click context menu: "Kata: Sync Data" and "Kata: Lint Current File"
- Hover: support nested schema (e.g. categories.items.status)
- Support indexed anchors (p-categories-0-items-0-status)
- Change D011 rule from badge consistency to duplicate anchor ID check
- Suppress D001 info when inline Schema Reference section exists
- Remove kata-badge styles
- Remove Cmd+Shift+F keybinding (conflicted with VSCode global search)

## 0.1.0 — 2026-03-15

Initial release.

- Auto lint on file save and open
- Editor diagnostics (errors and warnings via Diagnostics API)
- Syntax highlighting for `.kata.md` files (`{{ }}`, `{% %}`, `{#schema ... #}`)
- Settings: Python path, auto-lint toggle, info severity level
