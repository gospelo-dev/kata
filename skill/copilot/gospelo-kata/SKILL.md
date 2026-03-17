---
name: gospelo-kata
description: Generate, validate, and edit KATA Markdown™ documents
---

# gospelo-kata — AI Native Document Generation Toolkit

A tool for generating structured documents (Markdown / Excel) from KATA Markdown™ templates.
Reads `{#prompt}` (AI instructions) and `{#schema}` (type definitions) embedded in templates to autonomously generate documents.

## Prerequisites

The `gospelo-kata` package must be installed.

```bash
pip install gospelo-kata
```

---

## AI Document Generation Workflow

### Step 1: Template Selection

```bash
gospelo-kata templates
```

Example output:
```
Available templates:
  agenda               Meeting agenda with decisions and action items [schema]
  checklist            Structured checklist with categories... [schema, prompt]
  test_spec            Test specification with prerequisites...
```

Templates with `[schema, prompt]` tags support AI generation.

### Step 2: Get Template Specification

```bash
# Get template usage instructions
gospelo-kata show-prompt {template_name}

# Get data structure (JSON Schema)
gospelo-kata show-schema {template_name}
gospelo-kata show-schema {template_name} --format yaml
```

**Important**: Always read both show-prompt and show-schema to understand the template specification before generating data.

### Step 3: Create `_tpl.kata.md` File

Following the template's `{#schema}` and `{#prompt}`, create a `_tpl.kata.md` file with YAML data embedded in the `{#data}` block.

```markdown
{#schema
version: string!
description: string!
items[]!:
  id: string!
  name: string!
#}

{#data
version: "1.0"
description: My Document
items:
  - id: "1"
    name: Item One
#}

# {{ description }}

{% for item in items %}
- {{ item.id }}. {{ item.name }}
{% endfor %}
```

Rules:
- Fields marked with `!` are required
- Use only permitted values for `enum()` fields
- Set `status` initial value to `"draft"`
- Always set the `name_ja` field for Japanese content

### Step 4: Rendering

```bash
# Markdown output
gospelo-kata render my_template_tpl.kata.md -o outputs/my_template.kata.md

# Lint verification
gospelo-kata lint outputs/my_template.kata.md
```

### Step 5: Excel Generation (Optional)

```bash
gospelo-kata generate data.json --format excel --output output.xlsx
```

### Step 6: Fix Loop

If lint errors exist:
1. Check error details
2. Fix `{#data}` or the template in `_tpl.kata.md`
3. Re-run Step 4
4. Repeat until errors reach 0

---

## Command Reference

| Command | Description |
|---------|-------------|
| `templates` | List templates (shows schema/prompt availability) |
| `show-prompt {name}` | Display the template's `{#prompt}` |
| `show-schema {name}` | Display the template's schema as JSON Schema |
| `render {file}` | Render `_tpl.kata.md` to generate `.kata.md` |
| `lint {file}` | Lint verify a .kata.md file |
| `extract {file}` | Extract data from a rendered `.kata.md` |
| `init --type {name}` | Initialize a scaffold from a template |
| `validate {file}` | Validate a JSON file against the schema |
| `generate {file}` | Generate a document from JSON |
| `edit {file}` | Edit JSON in the browser editor |
| `infer-schema {file}` | Infer schema from a template |
| `schemas` | List available schemas |

All commands are executed with `gospelo-kata {command}`.

---

## Template Specification (KATA Markdown™ v2)

### File Naming Convention

- `*_tpl.kata.md` — Template source (`{#schema}` + `{#data}` + Jinja template)
- `*.kata.md` — Rendered output (with `data-kata` attributes)

### Schema Block `{#schema ... #}`

Define data types with YAML shorthand:

```markdown
{#schema
version: string!
description: string!
categories[]!:
  id: string!
  name: string!
  items[]!:
    id: string!
    status: enum(draft, pending, approve, reject)
    tags: string[]
    auto: enum(full, semi, partial, manual)
    enabled: boolean
#}
```

- `string!` — Required string
- `string` — Optional string
- `integer` — Integer
- `number` — Number
- `boolean` — Boolean
- `enum(a, b)` — Enumeration of permitted values
- `items[]!` — Required object array
- `string[]` — String array

### Prompt Block `{#prompt ... #}`

Template instructions for AI. Automatically removed during rendering.

### Data Block `{#data ... #}`

Embed data in YAML format. Injected into the template during rendering.

### Data Attribute `data-kata`

```html
<span data-kata="p-categories-0-items-0-status">draft</span>
```

Represents a reference to a schema property. The template engine adds these automatically, so manual input is not needed.

---

## Workflow Example

### Creating a Checklist

```bash
# 1. Initialize from template
gospelo-kata init --type checklist --output ./guides/

# 2. Edit the {#data} block in _tpl.kata.md

# 3. Render
gospelo-kata render guides/templates/checklist_tpl.kata.md -o guides/outputs/checklist.kata.md

# 4. Lint verification
gospelo-kata lint guides/outputs/checklist.kata.md
```

---

## Notes

- `data-kata` attributes and Schema Reference sections are auto-generated by the template engine (no manual input needed)
- Follow the conventions described in the template's `{#prompt}`
- Excel generation requires `openpyxl`
- YAML schema requires `PyYAML`
