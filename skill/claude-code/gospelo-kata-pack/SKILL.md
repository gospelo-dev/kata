---
name: gospelo-kata-pack
description: Manage .katatpl template packages (unpack, edit, repack, test)
---

# KATA Markdown™ Template Package Management

Manage `.katatpl` template packages: unpack, edit, repack, and verify.

## Prerequisites

The `gospelo-kata` package must be installed.

```bash
pip install gospelo-kata
```

---

## Workflow

### 1. List available templates

```bash
python -m gospelo_kata.cli templates
```

### 2. Unpack a template for editing

`.katatpl` files are ZIP archives. Extract to a temporary directory:

```bash
python -c "
import zipfile
with zipfile.ZipFile('gospelo_kata/templates/{name}.katatpl', 'r') as zf:
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

Edit `{name}_tpl.kata.md`. The template contains:

- `{#schema ... #}` — Schema definition (YAML shorthand)
- `{#prompt ... #}` — AI prompt (usage instructions)
- `{#data ... #}` — Sample data (YAML)
- Template body — Jinja2-compatible syntax

### 4. Repack

```bash
python -m gospelo_kata.cli pack /tmp/{name}_rebuild/{name} -o gospelo_kata/templates/{name}.katatpl
```

This regenerates the integrity hash in `manifest.json`.

**Important**: The `outputs/` directory must be removed before packing — `pack` only allows template, manifest, and image files.

### 5. Verify (assemble → render → lint)

```bash
# Create test data
cat <<'EOF' > /tmp/test_data.yaml
# ... YAML data matching the schema ...
EOF

# Assemble
echo "y" | python -m gospelo_kata.cli assemble --type {name} --data /tmp/test_data.yaml -o /tmp/test_tpl.kata.md

# Render
python -m gospelo_kata.cli render /tmp/test_tpl.kata.md -o /tmp/test_out.kata.md

# Lint (must pass with 0 errors)
python -m gospelo_kata.cli lint /tmp/test_out.kata.md
```

If lint errors exist, fix the template and repeat from Step 4.

---

## Command Reference

| Command | Description |
|---------|-------------|
| `templates` | List available templates |
| `pack {dir}` | Pack a directory into `.katatpl` |
| `pack-init {name}` | Create a new template scaffold |
| `assemble --type {name} --data {file}` | Combine template + data into `_tpl.kata.md` |
| `render {file}` | Render a `_tpl.kata.md` to final output |
| `lint {file}` | Verify the output |
| `show-prompt {name}` | Display the template's `{#prompt}` |
| `show-schema {name}` | Display the template's schema |

---

## Notes

- Always use `gospelo-kata pack` to repack — manual ZIP creation will fail the integrity check
- The `assemble` command may prompt for trust confirmation on first use or when the prompt changes — pipe `echo "y"` for non-interactive use
- After repacking, the prompt hash changes, so the next `assemble` will show the trust prompt again
