# KATA Markdown™ Language Support

[![VS Code](https://img.shields.io/badge/VS_Code-1.85%2B-007ACC.svg?logo=visualstudiocode&logoColor=white)](https://code.visualstudio.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/gospelo-dev/kata/blob/main/LICENSE.md)
[![KATA Markdown](https://img.shields.io/badge/Format-KATA_Markdown-00bcd4.svg)](https://github.com/gospelo-dev/kata)
[![Linter](https://img.shields.io/badge/Category-Linter-4caf50.svg)](#features)
[![Marketplace](https://img.shields.io/badge/VS_Marketplace-gospelo.kata--lint-007ACC.svg?logo=visualstudiocode)](https://marketplace.visualstudio.com/items?itemName=gospelo.kata-lint)

A VSCode extension for [gospelo-kata](https://github.com/gospelo-dev/kata). Provides real-time lint, syntax highlighting, hover information, and preview for KATA Markdown™ templates (`.kata.md`).

[Japanese / 日本語](https://github.com/gospelo-dev/kata/blob/main/vscode-kata-lint/README.ja.md)

---

## Features

### Lint

- **Auto Lint** — Runs `gospelo-kata lint` automatically on file save and open
- **Inline Diagnostics** — Inline squiggles at error locations + Problems panel listing
- **Template & Document Mode** — Validates both templates (`_tpl.kata.md`) and rendered documents (`.kata.md`)

### Syntax Highlighting

- `{{ variable }}` — Variable interpolation
- `{% for %}` / `{% if %}` — Control structures
- `{#schema ... #}` / `{#prompt ... #}` / `{#data ... #}` — KATA blocks

### Hover Information

- Hover over `data-kata` attributes to see schema path and binding information

### Preview CSS

- Provides preview styles dedicated to KATA Markdown™
- `kata-card` table layout, status styling

---

## Requirements

- [VS Code](https://code.visualstudio.com/) 1.85+
- Python 3.11+
- [gospelo-kata](https://github.com/gospelo-dev/kata) CLI

```bash
pip install gospelo-kata
```

---

## Lint Rules

### Template Mode (`.kata.md`)

| Code | Level | Description |
|------|-------|-------------|
| S000 | info | No schema defined |
| S001 | error | Invalid JSON in schema block |
| S002 | error | Schema is not a JSON object |
| S003 | warning | Schema missing `type` field |
| S004 | error | Schema file not found |
| T001 | error | Unclosed `{% for %}` / `{% if %}` |
| T002 | error | `{% elif %}` without matching `{% if %}` |
| T003 | error | `{% else %}` without matching `{% if %}` / `{% for %}` |
| T004 | error | `{% endif %}` without matching `{% if %}` |
| T005 | error | `{% endfor %}` without matching `{% for %}` |
| T006 | warning | Unknown block tag |
| F001 | error | Unknown filter name |
| V001 | warning | Variable not found in schema properties |
| V002 | info | Unused schema properties |

### Document Mode (`.md`)

| Code | Level | Description |
|------|-------|-------------|
| D001 | error | Schema not found |
| D002 | error | Required section (`## Heading`) missing |
| D003 | warning | Table column count mismatch |
| D004 | warning | Empty section |
| D005 | warning | Annotation link target not in schema |
| D006 | info | Schema properties with no links |

---

## Extension Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `kataLint.pythonPath` | `"python"` | Path to the Python interpreter |
| `kataLint.lintOnSave` | `true` | Run lint on file save |
| `kataLint.lintOnOpen` | `true` | Run lint on file open |
| `kataLint.severity.info` | `"Information"` | Severity level for info messages |

---

## VSCode Setup

Auto-generate task configuration with the gospelo-kata CLI:

```bash
gospelo-kata init-vscode --output .vscode/
```

See the [VSCode Integration Guide](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/vscode-integration.md) for details.

---

## License

MIT — See [LICENSE.md](https://github.com/gospelo-dev/kata/blob/main/LICENSE.md)
