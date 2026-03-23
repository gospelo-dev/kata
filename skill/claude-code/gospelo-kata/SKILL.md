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

### Step 4: Validate data against schema

```bash
gospelo-kata import-data {template_name} data.yml -q
```

Checks required fields, enum values, and types before building. Fix errors in `data.yml` before proceeding.

### Step 5: Build — assemble + render in one step

```bash
gospelo-kata build {template_name} data.yml -o outputs/
```

This combines the template with data and renders the final `.kata.md` document.

### Step 6: Lint — validate the output

```bash
gospelo-kata lint outputs/{template_name}.kata.md
```

### Step 7: Fix loop

If lint reports errors:
1. Analyze the error details
2. Fix `data.yml`
3. Re-run `import-data`, `build`, and `lint`
4. Repeat until errors reach 0

---

## Command Reference

| Command | Description |
|---------|-------------|
| `templates` | List available templates |
| `prepare {name}` | Show template info + generate skeleton data.yml |
| `build {name} {data}` | Build rendered document (assemble + render) |
| `lint {file}` | Validate templates and rendered documents |
| `export {name}` | Export template parts (prompt, schema, data, body, or all) |
| `import-data {name} {data.yml}` | Validate YAML data against template schema and output |
| `extract {file}` | Extract structured data from rendered output |
| `assemble --type {name} --data {file}` | Assemble template + data (without render) |
| `render {file}` | Render a _tpl.kata.md file |
| `validate {file}` | Validate JSON/YAML against schema |
| `fmt {file}` | Auto-format data-kata spans |
| `edit {file}` | Browser-based data editor |

### export — Fast Template Part Extraction

Export individual parts of a template without full parsing. Uses regex-based extraction for speed.

```bash
# Export prompt + schema together (recommended for AI context)
gospelo-kata export {template_name} --part prompt,schema

# Export all parts
gospelo-kata export {template_name}

# Export a single part
gospelo-kata export {template_name} --part schema
gospelo-kata export {template_name} --part data

# JSON format (for programmatic use)
gospelo-kata export {template_name} --format json

# Save to file
gospelo-kata export {template_name} -o catalog.md
```

| Option | Default | Description |
|--------|---------|-------------|
| `--part` | `all` | `prompt`, `schema`, `data`, `body`, `all`, or comma-separated (e.g., `prompt,schema`) |
| `--format` | `md` | `md`, `yaml`, or `json` |
| `--output` / `-o` | stdout | Output file path |

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
- **Context saving**: When you need to inspect data in a `.kata.md` file, do NOT read the entire file. Use `gospelo-kata export {template_name} --part data` or `gospelo-kata extract {file}` instead. This avoids loading the full document (which includes Schema Reference, annotations, etc.) into the conversation context.
