# Changelog

## 0.5.0 — 2026-03-24

- LiveMorph: bidirectional sync (Data → HTML / HTML → Data) via context menu, status bar, and syncOnSave
- Add context menu commands: Sync to HTML, Sync to Data, Sync OFF
- Add status bar indicator for current sync mode with QuickPick switcher
- Add `kataLint.exclude` setting for glob-based file exclusion
- Add `kataLint.ignoreCodes` setting for suppressing specific lint codes
- Update README with LiveMorph documentation and concept diagram
- Fix documentation links to current pages (vscode.md, katar.md, livemorph.md)

## 0.2.0 — 2026-03-18

- Sync Data: auto-sync span values to Data YAML on save (`syncOnSave` setting)
- Add right-click context menu: "Kata: Sync Data" and "Kata: Lint Current File"
- Hover: support nested schema (e.g. categories.items.status)
- Support indexed anchors (p-categories-0-items-0-status)
- Change D011 rule from badge consistency to duplicate anchor ID check
- Suppress D001 info when inline Specification section exists
- Remove kata-badge styles
- Remove Cmd+Shift+F keybinding (conflicted with VSCode global search)

## 0.1.0 — 2026-03-15

Initial release.

- Auto lint on file save and open
- Editor diagnostics (errors and warnings via Diagnostics API)
- Syntax highlighting for `.kata.md` files (`{{ }}`, `{% %}`, `{#schema ... #}`)
- Settings: Python path, auto-lint toggle, info severity level
