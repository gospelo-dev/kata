# VSCode Integration Guide

Setup and usage of the kata-lint VSCode extension.

---

## Installing the Extension

### Install from VSIX

```bash
# Build
cd vscode-kata-lint
npm install && npm run compile
npx vsce package

# Install
code --install-extension kata-lint-0.1.0.vsix
```

### Prerequisites

- `gospelo-kata` CLI installed and available on PATH
- Python 3.11+

---

## Features

### 1. Real-time Lint

Automatically runs lint on `.kata.md` files when saved or opened, displaying errors in the Problems panel.

**Settings** (`settings.json`):

```json
{
  "kataLint.lintOnSave": true,
  "kataLint.lintOnOpen": true,
  "kataLint.pythonPath": "python",
  "kataLint.severity.info": "Information",
  "kataLint.exclude": []
}
```

| Setting | Default | Description |
|---------|---------|-------------|
| `kataLint.lintOnSave` | `true` | Auto-lint on save |
| `kataLint.lintOnOpen` | `true` | Auto-lint when file is opened |
| `kataLint.pythonPath` | `"python"` | Path to Python |
| `kataLint.severity.info` | `"Information"` | Display level for info (Error/Warning/Information/Hint) |
| `kataLint.exclude` | `[]` | Exclusion patterns (glob) |

### 2. Hover Information

Hovering over `data-kata` attributes shows schema property type information in a popup.

**Displayed information**:
- Property name
- Type (`string`, `enum`, `array`, etc.)
- required / optional
- Allowed enum values
- minLength / maxLength

**Supported format**: Reads information from the YAML shorthand code block in the Schema Reference section.

```html
<!-- Hover here to see: -->
<span data-kata="p-test-cases-priority">high</span>
```

Popup:
```
**test_cases.priority**
- type: `enum` *(required)*
- enum: `high` | `medium` | `low`
```

### 3. Preview CSS

Kata-specific styles (`kata-card`, `kata-badge`, etc.) are applied when previewing `.kata.md` files in Markdown preview.

---

## Task Configuration (tasks.json)

Generate a lint-on-save task with the `init-vscode` command:

```bash
gospelo-kata init-vscode --output .vscode
```

Generated `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "kata: lint current file",
      "type": "shell",
      "command": "gospelo-kata",
      "args": ["lint", "--format", "vscode", "${file}"],
      "problemMatcher": {
        "owner": "kata-lint",
        "fileLocation": "absolute",
        "pattern": {
          "regexp": "^(.+):(\\d+):(\\d+):\\s+(error|warning|info)\\s+\\[(.+?)\\]\\s+(.+)$",
          "file": 1,
          "line": 2,
          "column": 3,
          "severity": 4,
          "code": 5,
          "message": 6
        }
      },
      "group": "test",
      "presentation": { "reveal": "silent" }
    }
  ]
}
```

**Usage**:
1. `Cmd+Shift+P` -> `Tasks: Run Task` -> `kata: lint current file`
2. Errors appear in the Problems panel

---

## Troubleshooting

### gospelo-kata not found

```
kata-lint: gospelo-kata is not installed. Run: pip install gospelo-kata
```

**Remedy**: Set `kataLint.pythonPath` to the correct Python path:

```json
{
  "kataLint.pythonPath": "/path/to/venv/bin/python"
}
```

### Hover does not show type information

**Cause**: Verify that the Schema Reference section is in YAML shorthand format inside `<details>`.

**Required structure**:
```html
<details>
<summary>Schema Reference</summary>

**Schema**

```yaml
property_name: type!
```

</details>
```

The legacy format (`#### <a id="p-xxx">`) is also supported, but YAML shorthand takes precedence.

### Lint results not updating

`Cmd+Shift+P` -> `Developer: Reload Window` to reload.
