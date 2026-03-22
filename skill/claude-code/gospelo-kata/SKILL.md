---
name: gospelo-kata
description: Generate, validate, and edit KATA Markdown™ documents
---

# /kata — KATA Markdown™ Basic Operations

The core skill for working with KATA Markdown™ templates. Covers the standard workflow: prepare → build → lint.

## Prerequisites

```bash
pip install gospelo-kata
```

---

## Workflow

### Step 1: List available templates

```bash
gospelo-kata templates
```

### Step 2: Prepare — understand template and generate skeleton

```bash
gospelo-kata prepare {template_name} -o data.yml
```

This outputs:
- **Prompt** — what the template generates and field semantics
- **Schema** — YAML shorthand type definitions
- **data.yml** — skeleton data file with empty/default values

Read the Prompt and Schema carefully before filling in data.

### Step 3: Fill in data.yml

Edit `data.yml` based on the Prompt and Schema:

- Fill all required fields (marked with `!` in Schema)
- Use only permitted values for `enum()` fields
- Set `status` initial value to `"draft"` unless specified otherwise
- Arrays can have multiple entries — the skeleton shows one as an example

### Step 4: Build — assemble + render in one step

```bash
gospelo-kata build {template_name} data.yml -o outputs/
```

This combines the template with data and renders the final `.kata.md` document.

### Step 5: Lint — validate the output

```bash
gospelo-kata lint outputs/{template_name}.kata.md
```

### Step 6: Fix loop

If lint reports errors:
1. Analyze the error details
2. Fix `data.yml`
3. Re-run `build` and `lint`
4. Repeat until errors reach 0

---

## Command Reference

| Command | Description |
|---------|-------------|
| `templates` | List available templates |
| `prepare {name}` | Show template info + generate skeleton data.yml |
| `build {name} {data}` | Build rendered document (assemble + render) |
| `lint {file}` | Validate templates and rendered documents |
| `extract {file}` | Extract structured data from rendered output |
| `assemble --type {name} --data {file}` | Assemble template + data (without render) |
| `render {file}` | Render a _tpl.kata.md file |
| `show-schema {name}` | Display template schema as JSON Schema |
| `show-prompt {name}` | Display template prompt |
| `validate {file}` | Validate JSON/YAML against schema |
| `fmt {file}` | Auto-format data-kata spans |
| `edit {file}` | Browser-based data editor |

---

## Schema Shorthand

| Notation | Meaning |
|----------|---------|
| `string!` | Required string |
| `string` | Optional string |
| `integer`, `number`, `boolean` | Typed values |
| `int`, `float`, `bool`, `str` | Aliases (→ integer, number, boolean, string) |
| `enum(a, b, c)` | Enumeration |
| `string[]` | String array |
| `items[]!:` | Required array of objects (indent children) |

---

## Notes

- Follow the conventions described in the template's Prompt block
- `data-kata` attributes are automatically added by the template engine
- The Schema Reference section is auto-generated
- Use YAML for data files (not JSON)
