# CLI Reference

Full list of `gospelo-kata` commands and their options.

```bash
gospelo-kata -V    # Show version
gospelo-kata -h    # Show help
```

---

## Template Operations

### `templates` — List templates

```bash
gospelo-kata templates
```

`[schema, prompt]` tags indicate AI-generation-capable templates.

### `prepare` — Show template info + generate skeleton data.yml

```bash
gospelo-kata prepare checklist                # Show info only
gospelo-kata prepare checklist -o data.yml    # Also generate empty data.yml
```

Displays the template's Prompt and Schema, and generates a skeleton `data.yml` from the schema.

| Option | Required | Description |
|--------|----------|-------------|
| `template` | Yes | Template name (checklist, test_spec, api_test, etc.) |
| `--output`, `-o` | No | Output path for data.yml |

### `build` — Template + data → final output

Runs `assemble` + `render` in one step.

```bash
gospelo-kata build checklist data.yml -o outputs/
gospelo-kata build api_test data.yml -o outputs/ --no-annotate
```

| Option | Required | Description |
|--------|----------|-------------|
| `template` | Yes | Template name |
| `data` | Yes | data.yml file path |
| `--output`, `-o` | No | Output directory |
| `--no-annotate` | No | Skip data-kata annotations |

On first use, a trust confirmation prompt is shown for the template's Prompt content.

### `init` — Initialize template (legacy)

```bash
gospelo-kata init --type checklist -o ./docs/
```

| Option | Required | Description |
|--------|----------|-------------|
| `--type` | Yes | Template name (checklist, test_spec, agenda) |
| `--output`, `-o` | No | Output directory |

Output: `templates/`, `outputs/`, `.workflow_status.json`

> **Note:** For new workflows, use `prepare` + `build` instead.

### `show-prompt` — Display AI instructions

```bash
gospelo-kata show-prompt checklist
```

Displays the `**Prompt**` block from the template. Accepts a template name or file path.

### `show-schema` — Display schema

```bash
gospelo-kata show-schema checklist              # JSON (default)
gospelo-kata show-schema checklist --format yaml # YAML
```

Generates and displays JSON Schema from the `**Schema**` block.

### `schemas` — List validation schemas

```bash
gospelo-kata schemas
```

### `infer-schema` — Infer schema

```bash
gospelo-kata infer-schema template.kata.md              # YAML shorthand
gospelo-kata infer-schema template.kata.md --format json # JSON Schema
```

Auto-infers schema from template variables and loop structures.

---

## Data Validation & Generation

### `validate` — JSON validation

```bash
gospelo-kata validate data.json                    # Auto-detect schema
gospelo-kata validate data.json --schema checklist # Specify schema
gospelo-kata validate data.json --schema ./schema.json
```

### `generate` — Document generation (JSON-based)

Generate Markdown / Excel / HTML from JSON data.

```bash
gospelo-kata generate data.json                            # Markdown (stdout)
gospelo-kata generate data.json -f markdown -o output.kata.md
gospelo-kata generate data.json -f excel -o output.xlsx
gospelo-kata generate data.json -f excel --prereq prereq.json -o test.xlsx
gospelo-kata generate data.json -f html -o output.html
```

| Option | Default | Description |
|--------|---------|-------------|
| `--format`, `-f` | markdown | Output format (markdown / excel / html) |
| `--output`, `-o` | stdout | Output file path |
| `--type` | auto-detect | Document type |
| `--prereq` | — | Prerequisite JSON (for test_spec Excel) |

### `render` — Render self-contained .kata.md

Interprets a `.kata.md` file containing `**Schema**` + `**Data**` blocks and produces data-kata annotated output.

```bash
gospelo-kata render source.kata.md -o outputs/result.kata.md
```

The output automatically includes:
- `<span data-kata="p-xxx">` — Schema property references
- `<div data-kata-each="collection">` — Loop markers
- `<details>` Schema + Data section

> **Note:** When using the template + data.yml workflow, `build` runs `assemble` + `render` automatically, so you don't need to call `render` directly.

### `assemble` — Assemble template with external data

Combines a built-in template with an external YAML/JSON data file to produce a `_tpl.kata.md`.

```bash
gospelo-kata assemble --type checklist --data data.yaml
```

> **Note:** `build` runs `assemble` + `render` automatically, so use `build` instead in most cases.

### `edit` — Browser editor

```bash
gospelo-kata edit data.json
gospelo-kata edit data.json --port 8080 --no-browser
```

---

## Lint & Formatting

### `lint` — Lint validation

```bash
gospelo-kata lint output.kata.md                    # Template mode
gospelo-kata lint output.kata.md --format vscode    # VSCode Problem Matcher format
gospelo-kata lint rendered.kata.md --schema checklist # Document mode
```

| Option | Default | Description |
|--------|---------|-------------|
| `--format` | human | Output format (human / vscode) |
| `--schema` | auto-detect | Schema name for document mode |

**Mode auto-detection:**
- Has `data-kata` spans and no Jinja syntax -> Document mode
- Has schema blocks / `{{ }}` / `{% %}` -> Template mode
- Has `<!-- kata: {...} -->` metadata -> Document mode

Exits with code 1 if errors are found.

See [Lint Rules](lint-rules.md) for error code details.

### `fmt` — Auto-format

Sanitizes HTML tags inside `data-kata` spans in rendered `.kata.md` files.

```bash
gospelo-kata fmt outputs/*.kata.md           # Fix and overwrite
gospelo-kata fmt outputs/*.kata.md --check   # Check only (for CI)
```

`--check` exits with code 1 if fixes are needed.

### `gen-schema-section` — Generate Schema Reference section

```bash
gospelo-kata gen-schema-section checklist
gospelo-kata gen-schema-section ./schema.json --section-map '{"date": "u-meeting-info"}'
```

---

## Analysis & Workflow

### `extract` — Data extraction

Reconstructs original JSON data from rendered `.kata.md` (round-trip).

```bash
gospelo-kata extract rendered.kata.md              # stdout
gospelo-kata extract rendered.kata.md -o data.json # file output
```

HTML entities like `&lt;` are automatically restored to `<`.

### `coverage` — Checklist coverage analysis

```bash
gospelo-kata coverage --checklist checklist.json --dir tests/
gospelo-kata coverage --checklist checklist.json --dir tests/ -f markdown
gospelo-kata coverage --checklist checklist.json --dir tests/ -f json
```

| Option | Required | Description |
|--------|----------|-------------|
| `--checklist` | Yes | Checklist JSON file |
| `--dir` | Yes | Parent of document directories |
| `--format`, `-f` | No | Output format (human / markdown / json) |

### `workflow-status` — Workflow progress management

```bash
gospelo-kata workflow-status --suite-dir ./docs/                    # Check status
gospelo-kata workflow-status --suite-dir ./docs/ --mark-done lint --note "0 errors"
gospelo-kata workflow-status --suite-dir ./docs/ --retry --retry-reason "lint NG"
gospelo-kata workflow-status --suite-dir ./docs/ --reset
```

| Option | Description |
|--------|-------------|
| `--suite-dir` | (Required) Directory containing `.workflow_status.json` |
| `--init TEMPLATE OUTPUT` | Initialize workflow |
| `--mark-done STEP` | Mark a step as complete |
| `--note TEXT` | Used with `--mark-done`. Records a comment |
| `--retry` | Reset validate/generate/lint and increment round |
| `--retry-reason TEXT` | Used with `--retry`. Records the reason |
| `--reset` | Reset all steps |

---

## Package Management

### `pack` — Package a template

```bash
gospelo-kata pack ./my_template/ -o my_template.katar
```

### `pack-init` — Create a template scaffold

```bash
gospelo-kata pack-init ./my_template/
```

See [Template Package](template-package.md) for details.

---

## VSCode Integration

### `init-vscode` — Generate task configuration

```bash
gospelo-kata init-vscode --output .vscode
```

See [VSCode Integration](vscode-integration.md) for details.
