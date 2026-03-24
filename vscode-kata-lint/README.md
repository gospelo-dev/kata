# KATA Markdown™ Language Support

[![VS Code](https://img.shields.io/badge/VS_Code-1.85%2B-007ACC.svg?logo=visualstudiocode&logoColor=white)](https://code.visualstudio.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/gospelo-dev/kata/blob/main/LICENSE.md)
[![KATA Markdown](https://img.shields.io/badge/Format-KATA_Markdown-00bcd4.svg)](https://github.com/gospelo-dev/kata)
[![Linter](https://img.shields.io/badge/Category-Linter-4caf50.svg)](#features)
[![Marketplace](https://img.shields.io/badge/VS_Marketplace-gospelo.kata--lint-007ACC.svg?logo=visualstudiocode)](https://marketplace.visualstudio.com/items?itemName=gospelo.kata-lint)

A VS Code extension for [gospelo-kata](https://github.com/gospelo-dev/kata). Provides real-time lint, LiveMorph bidirectional sync, hover information, and preview for KATA Markdown™ (`.kata.md`).

[Japanese / 日本語](https://github.com/gospelo-dev/kata/blob/main/vscode-kata-lint/README.ja.md)

---

## Features

### Lint

- **Auto Lint** — Runs `gospelo-kata lint` automatically on file save and open
- **Inline Diagnostics** — Inline squiggles at error locations + Problems panel listing
- **Template & Document Mode** — Validates both templates and rendered documents

### LiveMorph (Bidirectional Sync)

![LiveMorph Concept](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/images/livemorph-concept.jpg?raw=true)

- **Context Menu** — Right-click for Sync to HTML / Sync to Data / Sync OFF / Lint File
- **Status Bar** — Shows current sync mode, click to switch via QuickPick
- **Auto-sync on Save** — `syncOnSave` setting for automatic Data → HTML or HTML → Data sync

### Hover Information

- Hover over `data-kata` attributes to see schema path, type info, and allowed enum values

### Preview CSS

- KATA Markdown™ dedicated preview styles (`kata-card` table layout, status colors)

---

## Requirements

- [VS Code](https://code.visualstudio.com/) 1.85+
- Python 3.11+
- [gospelo-kata](https://github.com/gospelo-dev/kata) CLI

```bash
pip install gospelo-kata
```

---

## Extension Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `kataLint.pythonPath` | `"python"` | Path to the Python interpreter |
| `kataLint.lintOnSave` | `true` | Run lint on file save |
| `kataLint.lintOnOpen` | `true` | Run lint on file open |
| `kataLint.syncOnSave` | `"off"` | Sync mode on save (`"off"` / `"toHtml"` / `"toData"`) |
| `kataLint.severity.info` | `"Information"` | Severity level for info messages |
| `kataLint.exclude` | `[]` | Exclude patterns (glob) |

---

## Lint Rules

See [Lint Rules Reference](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/lint-rules.md) for the full list.

### Security

| Code | Description |
|------|-------------|
| P002 | Prompt injection detection — role override, instruction override, command execution, credential access |
| D016 | HTML injection detection inside `data-kata` spans (XSS prevention) |
| D017 | Structure integrity hash verification — detects post-render tampering of Prompt, Schema, or template body |

---

## Related Documentation

- [VS Code Integration Guide](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/vscode.md)
- [LiveMorph Guide](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/livemorph.md)
- [Template Packages](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/katar.md)

---

## License

MIT — See [LICENSE.md](https://github.com/gospelo-dev/kata/blob/main/LICENSE.md)
