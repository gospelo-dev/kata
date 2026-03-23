---
name: gospelo-kata-pack
description: Manage KATA ARchive™ (.katar) template packages (unpack, edit, repack, test)
---

# /kata-pack — KATA ARchive™ Template Package Management

Manage `.katar` template packages: unpack, edit, repack, and verify.

## Prerequisites

```bash
pip install gospelo-kata
```

---

## Workflow

### 1. List available templates

```bash
gospelo-kata templates
```

### 2. Unpack a template for editing

`.katar` files are ZIP archives. Extract to a temporary directory:

```bash
python -c "
import zipfile
with zipfile.ZipFile('gospelo_kata/templates/{name}.katar', 'r') as zf:
    zf.extractall('/tmp/{name}_rebuild')
"
```

Extracted structure:

```
/tmp/{name}_rebuild/{name}/
  manifest.json          # Package metadata and integrity hash
  {name}_tpl.kata.md     # Template source
```

### 3. Edit the template

Edit `{name}_tpl.kata.md`. The template uses unified block format:

- `**Prompt**` + `` ```yaml `` — AI prompt
- `**Schema**` + `` ```yaml `` — Schema definition (YAML shorthand)
- `**Data**` + `` ```yaml `` — Sample data
- Template body — Jinja2-compatible syntax

### 4. Repack

```bash
gospelo-kata pack /tmp/{name}_rebuild/{name} -o gospelo_kata/templates/{name}.katar
```

This regenerates the integrity hash in `manifest.json`.

**Important**: The `outputs/` directory must be removed before packing — `pack` only allows template, manifest, and image files.

### 5. Verify

```bash
gospelo-kata prepare {name} -o /tmp/test_data.yml
# Edit /tmp/test_data.yml with test values

gospelo-kata build {name} /tmp/test_data.yml -o /tmp/test_outputs/
gospelo-kata lint /tmp/test_outputs/{name}.kata.md
```

If lint errors exist, fix the template and repeat from Step 4.

---

## Command Reference

| Command | Description |
|---------|-------------|
| `templates` | List available templates |
| `pack {dir}` | Pack a directory into `.katar` |
| `pack-init {dir}` | Create a new template scaffold |
| `prepare {name}` | Show template info + generate skeleton data |
| `export {name}` | Export template parts (prompt, schema, data, body, or all) |
| `build {name} {data}` | Build rendered document |
| `lint {file}` | Verify the output |

---

## Notes

- Always use `gospelo-kata pack` to repack — manual ZIP creation will fail the integrity check
- The `build` command may prompt for trust confirmation on first use or when the prompt changes
- After repacking, the prompt hash changes, so the next `build` will show the trust prompt again
