# gospelo-kata — KATA Markdown™ for Human-AI Collaboration

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/gospelo-dev/kata/blob/main/LICENSE.md)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![AI Collaborative](https://img.shields.io/badge/AI-Collaborative-ff6f00.svg?logo=openai&logoColor=white)](#why-gospelo-kata)
[![KATA Markdown](https://img.shields.io/badge/Format-KATA_Markdown-00bcd4.svg)](#kata-markdown-format)

A document format and toolkit designed for **human-AI collaboration**. KATA Markdown™ embeds schema, data, and template in a single file — readable and actionable by both humans and AI without special instructions.

## Why gospelo-kata?

KATA Markdown is designed so that both humans and AI can read, understand, and work with the same document. The format is self-describing: AI can understand the template structure from the embedded schema and prompt without needing external instructions, while humans can read and edit the same file naturally. It acts as a harness for autonomous AI — schema, validation, and trust management guide AI output along safe, structured paths.

When generating documents with AI, you often face these problems:

- **No structure** — AI outputs free-form text that's hard to validate or reuse
- **No round-trip** — once rendered, you can't extract the original data back
- **No validation** — schema violations go unnoticed until review
- **AI needs coaching** — you have to explain the output format every time

gospelo-kata solves this with a **single `.kata.md` file** that contains everything: schema definition, structured data, and a Jinja2-compatible template (built-in engine, no external dependency). The embedded `{#schema}` and `{#prompt}` blocks let AI understand the template on its own — no separate instructions needed. Rendered output preserves data bindings via `data-kata` annotations, enabling round-trip extraction and automated validation.

## Features

- **Human-AI collaborative format** — both humans and AI can read, edit, and generate from the same file
- **Self-describing templates** — embedded `{#schema}` and `{#prompt}` let AI understand the template without external instructions
- **Single-file format** — schema, data, and template in one `.kata.md` file
- **YAML shorthand schemas** — define types concisely (`string!`, `enum(a,b,c)`, `items[]!:`)
- **Round-trip** — extract structured data back from rendered documents
- **Lint** — validate both templates and rendered output (20+ rules)
- **AI-friendly** — `assemble` command lets AI generate only YAML data; the toolkit handles the rest
- **Multi-format output** — Markdown, Excel, and HTML
- **VSCode extension** — real-time lint, hover info, preview CSS
- **Zero external dependencies** for core features (built-in Jinja2 3.1.6-compatible engine; PyYAML required, openpyxl optional for Excel)

## Installation

```bash
pip install gospelo-kata

# With Excel support
pip install gospelo-kata[excel]
```

Requires Python 3.11+.

## Quick Start

### 1. Create a document from scratch

```bash
cat > todo_tpl.kata.md << 'EOF'
{#schema
title: string!
items[]!:
  task: string!
  done: boolean
#}

{#data
title: Sprint Tasks
items:
  - task: Set up CI pipeline
    done: true
  - task: Write API tests
    done: false
  - task: Deploy to staging
    done: false
#}

# {{ title }}

| Task | Done |
|------|:----:|
{% for item in items %}| {{ item.task }} | {{ item.done }} |
{% endfor %}
EOF

gospelo-kata render todo_tpl.kata.md -o outputs/todo.kata.md
gospelo-kata lint outputs/todo.kata.md
```

### 2. Use a built-in template

```bash
# List available templates
gospelo-kata templates

# Initialize a project
gospelo-kata init --type checklist -o ./my-project/
```

### 3. AI workflow (recommended)

AI generates only the YAML data; `assemble` combines it with a built-in template:

```bash
# 1. Check schema
gospelo-kata show-schema checklist --format yaml

# 2. AI creates data.yml following the schema

# 3. Assemble template + data
gospelo-kata assemble --type checklist --data data.yml

# 4. Render and validate
gospelo-kata render checklist_tpl.kata.md -o outputs/checklist.kata.md
gospelo-kata lint outputs/checklist.kata.md
```

### 4. Extract data (round-trip)

```bash
gospelo-kata extract outputs/checklist.kata.md -o extracted.json
```

Reconstructs the original structured data from the rendered document.

## KATA Markdown Format

A `_tpl.kata.md` file has three blocks:

```markdown
{#schema
title: string!
version: string
categories[]!:
id: string!
name: string!
items[]!:
id: string!
status: enum(draft, pending, approve, reject)
tags: string[]
#}

{#data
title: Security Checklist
version: "1.0"
categories:

- id: auth
  name: Authentication
  items: - id: auth-01
  status: draft
  tags: [web, api]
  #}

{#prompt
Generate a security checklist with categories and items.
Each item needs an id, status (draft/pending/approve/reject), and tags.
#}

# {{ title }}

{% for cat in categories %}

## {{ cat.name }}

| ID                          | Status        | Tags              |
| --------------------------- | ------------- | ----------------- | ------------ | ------------- |
| {% for item in cat.items %} | {{ item.id }} | {{ item.status }} | {{ item.tags | join(", ") }} |

{% endfor %}
{% endfor %}
```

### Schema Shorthand

| Notation                   | Meaning                                     |
| -------------------------- | ------------------------------------------- |
| `string`                   | Optional string                             |
| `string!`                  | Required string                             |
| `int`, `number`, `boolean` | Typed values                                |
| `enum(a, b, c)`            | Enumeration                                 |
| `string[]`                 | String array                                |
| `items[]!:`                | Required array of objects (indent children) |

### Rendered Output

`gospelo-kata render` produces annotated Markdown:

- `<span data-kata="p-{path}">value</span>` — data bindings
- `<div data-kata-each="collection">` — loop markers
- `<details>` section with Schema + Data for reconstruction

## Built-in Templates

| Type        | Description                                                                  |
| ----------- | ---------------------------------------------------------------------------- |
| `checklist` | Structured checklist with categories, status tracking, and automation levels |
| `test_spec` | Test case specification with prerequisites and expected results              |
| `agenda`    | Meeting agenda with decisions, action items, and time allocation             |

## CLI Commands

| Command           | Description                                               |
| ----------------- | --------------------------------------------------------- |
| `templates`       | List available templates                                  |
| `init`            | Initialize project from a template                        |
| `render`          | Render a `.kata.md` template to annotated output          |
| `assemble`        | Combine built-in template + data file into `_tpl.kata.md` |
| `lint`            | Validate templates and rendered documents                 |
| `extract`         | Extract structured data from rendered output              |
| `validate`        | Validate JSON/YAML data against a schema                  |
| `generate`        | Generate Markdown/Excel/HTML from JSON data               |
| `show-schema`     | Display template schema                                   |
| `show-prompt`     | Display AI prompt                                         |
| `fmt`             | Auto-format `data-kata` spans                             |
| `coverage`        | Analyze checklist coverage                                |
| `edit`            | Browser-based data editor                                 |
| `workflow-status` | Track pipeline progress                                   |

See the [CLI Reference](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/cli-reference.md) for full details.

## AI Integration

gospelo-kata is designed to work with AI assistants. The `assemble` command minimizes what AI needs to generate — just YAML data following the schema.

**Supported AI tools:**

- **Claude Code** — skill files in `skill/claude-code/`
- **GitHub Copilot Chat** — instructions via `.github/copilot-instructions.md`

The 3-step workflow (`data.yml` → `assemble` → `render` + `lint`) works reliably even with smaller models that have limited context windows.

## VSCode Extension

Install from [VS Marketplace](https://marketplace.visualstudio.com/items?itemName=gospelo.kata-lint). The `kata-lint` extension provides:

- Real-time lint diagnostics in the Problems panel
- Hover information for `data-kata` attributes
- Preview CSS for kata-specific styles

See the [VSCode Integration Guide](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/vscode-integration.md).

## Documentation

- [Quick Start](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/quick-start.md)
- [CLI Reference](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/cli-reference.md)
- [KATA Markdown Format](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/kata-markdown-format.md)
- [Lint Rules](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/lint-rules.md)
- [Workflow Guide](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/workflow-guide.md)
- [VSCode Integration](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/vscode-integration.md)
- [Copilot Setup](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/copilot-setup.md)

## License

MIT — free for commercial use. Documents generated by this software and templates created by users are the intellectual property of their respective creators. When used with AI services, data may be transmitted to AI providers. See [LICENSE.md](https://github.com/gospelo-dev/kata/blob/main/LICENSE.md) for details.
