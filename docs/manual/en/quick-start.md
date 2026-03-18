# gospelo-kata Quick Start

Get started with KATA Markdown™ document generation in 5 minutes.

---

## Installation

```bash
pip install gospelo-kata
```

Dependencies: **PyYAML** (required), **openpyxl** (Excel output only)

---

## Method A: Generate from a self-contained .kata.md

Write template, schema, and data in a single file. The simplest approach.

### 1. Create a source file

````bash
cat > my_checklist.kata.md << 'EOF'
**Prompt**

```yaml
This template generates a task checklist with status tracking.
Describe items in the items array with id, name, and status.
status must be one of todo/done.
```

# {{ title }}

> Version: {{ version }}

| ID | Item | Status |
|:--:|------|:------:|
{% for item in items %}| {{ item.id }} | {{ item.name }} | {{ item.status }} |
{% endfor %}

Total: {{ items | length }} items

<details>
<summary>Schema Reference</summary>

**Schema**

```yaml
title: string!
version: string
items[]!:
  id: string!
  name: string!
  status: enum(todo, done)
```

**Data**

```yaml
title: Security Checklist
version: 1.0
items:
  - id: SEC-01
    name: Input validation
    status: todo
  - id: SEC-02
    name: SQL injection prevention
    status: done
```

</details>
EOF
````

### 2. Render

```bash
gospelo-kata render my_checklist.kata.md -o outputs/my_checklist.kata.md
```

The output `.kata.md` will have `data-kata` attributes and a Schema/Data section appended automatically.

### 3. Lint

```bash
gospelo-kata lint outputs/my_checklist.kata.md
```

### 4. Extract data (round-trip)

```bash
gospelo-kata extract outputs/my_checklist.kata.md
```

Reconstructs the original JSON data from the rendered output.

---

## Method B: Generate with template + JSON

Separate the built-in template from the JSON data.

### 1. Initialize template

```bash
gospelo-kata init --type test_spec -o ./my_project/
```

Creates `templates/`, `outputs/`, and `.workflow_status.json`.

### 2. Create and validate JSON data

```bash
gospelo-kata validate my_data.json --schema test_spec
```

### 3. Generate document

```bash
gospelo-kata generate my_data.json -f markdown -o output.kata.md
```

---

## Workflow Overview

```
Source (.kata.md)
  | render
Rendered (.kata.md)  <- data-kata attributes + Schema/Data
  | lint
Validation (0 errors)
  | extract
JSON data recovery (round-trip)
```

---

## Next Steps

- [CLI Reference](cli-reference.md) — Full command details
- [KATA Markdown™ Format](kata-markdown-format.md) — Template syntax
- [Lint Rules](lint-rules.md) — Error code reference
- [Workflow Guide](workflow-guide.md) — Pipeline management
- [VSCode Integration](vscode-integration.md) — Extension setup
