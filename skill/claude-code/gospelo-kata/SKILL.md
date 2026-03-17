---
name: gospelo-kata
description: Generate, validate, and edit KATA Markdown™ documents
---

# /gospelo-kata — AI Native Document Generation Toolkit

A tool for generating structured documents from KATA Markdown™ templates.
AI reads the `{#prompt}` and `{#schema}` embedded in templates to autonomously generate documents.

## Prerequisites

The `gospelo-kata` package must be installed.

```bash
pip install gospelo-kata
```

---

## AI Document Generation Workflow

AI follows these steps to understand templates and generate documents:

### 1. Template Selection

```bash
python -m gospelo_kata.cli templates
```

Check available templates and whether they have schema/prompt.

### 2. Understanding the Template

```bash
# Get the prompt (template usage instructions)
python -m gospelo_kata.cli show-prompt {template_name}

# Get the schema (JSON Schema)
python -m gospelo_kata.cli show-schema {template_name}
python -m gospelo_kata.cli show-schema {template_name} --format yaml
```

**Important**: Always read both show-prompt and show-schema to understand the template specification before generating data.

### 3. Generate JSON Data

Create JSON data based on the schema obtained from show-schema and the user's requirements.

- Always include required fields
- Use only permitted values for enum fields
- Set `status` initial value to `"draft"`

### 4. Validation

```bash
python -m gospelo_kata.cli validate {json_file}
```

### 5. Document Generation

```bash
# Markdown (stdout)
python -m gospelo_kata.cli generate {json_file} --format markdown

# Markdown (file output)
python -m gospelo_kata.cli generate {json_file} --format markdown --output output.kata.md

# Excel
python -m gospelo_kata.cli generate {json_file} --format excel --output output.xlsx
```

### 6. Lint Verification

```bash
python -m gospelo_kata.cli lint {output.kata.md}
```

### 7. Fix Loop

If lint errors exist:
1. Analyze the error details
2. Fix the JSON data
3. Re-run validation, generation, and lint
4. Repeat until errors reach 0

---

## Command Reference

| Command | Description |
|---------|-------------|
| `templates` | List templates (shows schema/prompt availability) |
| `show-prompt {name}` | Display the template's `{#prompt}` |
| `show-schema {name}` | Display the template's schema as JSON Schema |
| `validate {file}` | Validate a JSON file against the schema |
| `generate {file}` | Generate a document from JSON |
| `lint {file}` | Lint verify a .kata.md file |
| `init --type {name}` | Initialize a scaffold from a template |
| `edit {file}` | Edit JSON in the browser editor |
| `infer-schema {file}` | Infer schema from a template |
| `schemas` | List available schemas |

---

## Template Specification (KATA Markdown™ v2)

### Schema Block

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
#}
```

- `string!` — Required string
- `enum(a, b)` — Enumeration of permitted values
- `items[]!` — Required array (children are objects)
- `string[]` — Array of strings

### Prompt Block

```markdown
{#prompt
A block that explains template usage for AI.
Automatically removed during rendering.
#}
```

### Data Attributes

```html
<span data-kata="p-categories-0-items-0-status">draft</span>
```

The `data-kata` attribute represents a reference to a schema property. The VSCode extension displays type information on hover.

---

## Notes

- Follow the conventions described in the template's `{#prompt}`
- `data-kata` attributes are automatically added by the template engine (no manual input needed)
- The Schema Reference section is also auto-generated (no manual input needed)
- Excel generation requires `openpyxl`
- YAML schema requires `PyYAML`
