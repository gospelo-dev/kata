# gospelo-kata Quick Start

Get started with KATA Markdown™ document generation in 5 minutes.

---

## Installation

```bash
pip install gospelo-kata
```

Dependencies: **PyYAML** (required), **openpyxl** (Excel output only)

---

## Method A: Generate with template + data.yml (recommended)

Use a built-in template with YAML data. The most practical approach.

### 1. Explore templates

```bash
gospelo-kata templates              # List available templates
gospelo-kata prepare checklist      # View Prompt + Schema
```

### 2. Create data.yml

```bash
gospelo-kata prepare checklist -o data.yml   # Generate skeleton
```

Edit the generated `data.yml` to fill in your data. You can also use AI skills (`/kata-gen`, etc.) to auto-generate it.

### 3. Build + validate

```bash
gospelo-kata build checklist data.yml -o outputs/
gospelo-kata lint outputs/checklist.kata.md
```

`build` combines template assembly and rendering in one step.

### 4. Extract data (round-trip)

```bash
gospelo-kata extract outputs/checklist.kata.md
```

Reconstructs the original data from the rendered output.

---

## Method B: Generate from a self-contained .kata.md

Write template, schema, and data in a single file.

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

---

## Workflow Overview

```
prepare → create data.yml → build → lint → (fix loop)
```

```
Template + data.yml
  | build (assemble + render)
Rendered (.kata.md)  <- data-kata attributes + Schema/Data
  | lint
Validation (0 errors)
  | extract
Data recovery (round-trip)
```

---

## Next Steps

- [CLI Reference](cli-reference.md) — Full command details
- [KATA Markdown™ Format](kata-markdown-format.md) — Template syntax
- [Lint Rules](lint-rules.md) — Error code reference
- [Skill Guide](skill-guide.md) — AI skill usage guide
- [VSCode Integration](vscode-integration.md) — Extension setup
