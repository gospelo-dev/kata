# VS Code Integration

Setup and usage for the kata-lint VS Code extension.

---

## Installation

```bash
cd vscode-kata-lint
npm install && npm run compile
npx vsce package
code --install-extension kata-lint-*.vsix
```

Prerequisites:
- `gospelo-kata` CLI on PATH
- Python 3.11+

---

## Features

### 1. Real-time Lint

Automatically runs lint on `.kata.md` files when opened or saved. Errors appear in the Problems panel.

### 2. LiveMorph (Bidirectional Sync)

Sync Data block and HTML body bidirectionally. Available via context menu or auto-sync on save.

→ Details in [LiveMorph Guide](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/livemorph.md)

### 3. Hover Information

Hover over `data-kata` attributes to see schema property type info:

- Property name
- Type (`string`, `enum`, `array`, etc.)
- required / optional
- Allowed enum values
- minLength / maxLength

### 4. Preview CSS

KATA-specific styles (`kata-card`, etc.) are applied in Markdown preview.

---

## Context Menu

Right-click on a `.kata.md` file:

| Menu Item | Action |
|-----------|--------|
| **Kata: Sync to HTML** | Sync Data → body + set mode to `toHtml` |
| **Kata: Sync to Data** | Sync body → Data + set mode to `toData` |
| **Kata: Sync OFF** | Disable auto-sync |
| **Kata: Lint File** | Run lint only |

---

## Status Bar

When a `.kata.md` file is open, the current sync mode is shown in the status bar.
Click to switch modes via QuickPick.

| Display | Meaning |
|---------|---------|
| `Sync: OFF` | No auto-sync |
| `→ Sync: to HTML` | Auto Data → body on save |
| `← Sync: to Data` | Auto body → Data on save |

---

## Settings

`settings.json`:

```json
{
  "kataLint.lintOnSave": true,
  "kataLint.lintOnOpen": true,
  "kataLint.syncOnSave": "off",
  "kataLint.pythonPath": "python",
  "kataLint.severity.info": "Information",
  "kataLint.exclude": []
}
```

| Setting | Default | Description |
|---------|---------|-------------|
| `kataLint.lintOnSave` | `true` | Auto-lint on save |
| `kataLint.lintOnOpen` | `true` | Auto-lint on file open |
| `kataLint.syncOnSave` | `"off"` | Sync mode on save (`"off"` / `"toHtml"` / `"toData"`) |
| `kataLint.pythonPath` | `"python"` | Python path |
| `kataLint.severity.info` | `"Information"` | Info level display (Error/Warning/Information/Hint) |
| `kataLint.exclude` | `[]` | Exclude patterns (glob) |

---

## Task Configuration (tasks.json)

Auto-generate a lint task:

```bash
gospelo-kata init-vscode --output .vscode
```

Then: `Cmd+Shift+P` → `Tasks: Run Task` → `kata: lint current file`

---

## Troubleshooting

### gospelo-kata not found

Set `kataLint.pythonPath` to the correct path:

```json
{
  "kataLint.pythonPath": "/path/to/venv/bin/python"
}
```

### No hover type info

Verify the Specification section uses `<details>` with YAML shorthand format.

### Sync not working

1. Check the status bar shows a mode other than `OFF`
2. Verify CLI works: `gospelo-kata -V`
3. `Cmd+Shift+P` → `Developer: Reload Window`
