# Template Package — KATA ARchive™ (.katar)

How to create, package, and distribute custom templates.

---

## Overview

KATA ARchive™ (`.katar`) is the template package format for gospelo-kata. It is a standard ZIP archive that bundles all files needed for a template into a single file.

Place it directly in `./templates/` without extracting — all commands (`assemble`, `show-schema`, `show-prompt`, etc.) work with it as-is.

**Design principle: 1 package = 1 template = 1 schema**

Each package contains a single template (`_tpl.kata.md`) so that AI can read one schema and generate data. To combine data from multiple templates into a single deliverable (e.g., Excel), use the `generate` command options (e.g., `--prereq`).

![KATA ARchive™ Security Architecture](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/images/katar-security-architecture.jpg?raw=true)

---

## Template Structure

Required files in a template directory:

```
my_template/
├── manifest.json             # Manifest (required)
├── my_template_tpl.kata.md   # Template body (required)
└── images/                   # Image files (optional)
```

### Additional Files

Besides `manifest.json` and `_tpl.kata.md`, a template directory may include **image files**.

Allowed image formats: `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`, `.ico`, `.bmp`

Example uses:

- **Logos / icons** — image assets embedded in documents
- **Diagrams / screenshots** — supplementary materials for the template

> **Security:** Only template and image files are allowed in packages.

---

## manifest.json

A file that defines template metadata. Required when packaging with the `pack` command.

```json
{
  "name": "my_template",
  "version": "1.0.0",
  "description": "Task list with status tracking",
  "author": "your-name",
  "url": "https://github.com/your-org/your-repo",
  "license": "MIT",
  "template": "my_template_tpl.kata.md",
  "requires": []
}
```

### Fields

| Field | Required | Description |
|-------|:--------:|-------------|
| `name` | Yes | Template name (identifier used in commands) |
| `version` | Yes | Semantic versioning |
| `template` | Yes | Template body filename |
| `description` | No | Template description |
| `author` | No | Author name |
| `url` | No | Repository or documentation URL |
| `license` | No | License type (MIT, Apache-2.0, etc.) |
| `requires` | No | Array of dependent template names |

### `requires` — Inter-template Dependencies

When combining data from multiple templates into a single deliverable (e.g., Excel), list the dependent template names in `requires`.

```json
{
  "name": "test_spec",
  "requires": ["test_prereq"]
}
```

Dependency information is displayed when running `show-schema` or `show-prompt`, so AI can generate data for all required templates:

```
$ gospelo-kata show-schema test_spec
...
Requires: test_prereq
  → gospelo-kata show-schema test_prereq
```

### Creating a New Template with `pack-init`

```bash
gospelo-kata pack-init ./my_template/
```

The following structure is auto-generated:

```
my_template/
├── manifest.json             # Manifest (auto-generated)
├── my_template_tpl.kata.md   # Template body (empty scaffold)
├── images/                   # Image file directory (optional)
└── outputs/                  # Rendering output directory
```

When run against an existing directory, it auto-detects `_tpl.kata.md` files and generates a `manifest.json` scaffold.

---

## Template Body (`_tpl.kata.md`)

A file containing `**Prompt**`, `**Schema**`, `**Data**` blocks and a Jinja2-compatible template. The filename is specified in the `template` field of `manifest.json`.

````markdown
**Prompt**

```yaml
This template generates a task list.
Describe each task in the items array.
status must be either draft or done.
```

# {{ title }}

> Version: {{ version }}

| ID | Task | Status |
|----|------|:------:|
{% for item in items %}| {{ item.id }} | {{ item.name }} | {{ item.status }} |
{% endfor %}

<details>
<summary>Schema Reference</summary>

**Schema**

```yaml
title: string!
version: string
items[]!:
  id: string!
  name: string!
  status: enum(draft, done)
```

**Data**

```yaml
```

</details>
````

**Key points:**

- `**Prompt**` + `` ```yaml `` — instructions AI references when generating data
- `**Schema**` + `` ```yaml `` — schema definition for AI to understand data structure
- `**Data**` + `` ```yaml `` — insertion point for `assemble` command data (recommended even if empty)
- Template body — written in Jinja2-compatible syntax

---

## Packaging

Create `.katar` archives only with the `gospelo-kata pack` command. Do not manually create or rename ZIP files.

### Steps

```bash
# 1. Generate template scaffold
gospelo-kata pack-init ./my_template/

# 2. Edit the template body
#    Write **Prompt**, **Schema**, and template in my_template/my_template_tpl.kata.md

# 3. Edit manifest.json
#    Fill in author, url, license, etc.

# 4. Package
gospelo-kata pack ./my_template/
```

This generates `my_template.katar`.

To specify the output path:

```bash
gospelo-kata pack ./my_template/ -o ./dist/my_template.katar
```

### Validation

The `pack` command validates the following:

- `manifest.json` exists
- `name`, `version`, `template` fields are present
- The file specified by `template` exists

---

## Installation

### Install with `init --from-package`

```bash
gospelo-kata init --from-package my_template.katar
```

The file is copied to `./templates/my_template.katar` (not extracted).

### Manual Placement

You can also copy `.katar` files directly to `./templates/`:

```bash
cp my_template.katar ./templates/
```

---

## Usage

After installation, use it just like built-in templates:

```bash
# Verify in template list (version is also displayed)
gospelo-kata templates

# Check schema
gospelo-kata show-schema my_template --format yaml

# Check AI prompt
gospelo-kata show-prompt my_template

# Create data → assemble → render
gospelo-kata assemble --type my_template --data data.yml
gospelo-kata render my_template_tpl.kata.md -o outputs/my_template.kata.md
gospelo-kata lint outputs/my_template.kata.md
```

---

## Template Search Order

Template search order when running commands:

1. **Local** `./templates/{name}/` (directory)
2. **Local** `./templates/{name}.katar` (package)
3. **Built-in** `gospelo_kata/templates/{name}/` (directory)
4. **Built-in** `gospelo_kata/templates/{name}.katar` (package)

Local templates with the same name take priority over built-in templates.

---

## Best Practices for Template Creation

### Schema Design

- Mark required fields with `!` (`string!`, `items[]!:`)
- Restrict choices with enum (`enum(draft, pending, approve, reject)`)
- Include `name_ja` fields for multilingual support

### Prompt Design

- Explain the template's purpose concisely
- Describe the meaning and constraints of each field
- Include concrete examples so AI doesn't have to guess

### Testing

Verify that the template works correctly before packaging:

```bash
# Assemble with test data
gospelo-kata assemble --type my_template --data test_data.yml

# Render + lint
gospelo-kata render my_template_tpl.kata.md -o outputs/test.kata.md
gospelo-kata lint outputs/test.kata.md

# Round-trip verification
gospelo-kata extract outputs/test.kata.md
```

---

## AI Skill Integration

Use the `/gospelo-kata-pack` skill with Claude Code or GitHub Copilot to let AI unpack, edit, repack, and test templates in one go.

```
/gospelo-kata-pack
```

See `skill/claude-code/gospelo-kata-pack/SKILL.md` for details.

---

## Distribution

`.katar` files can be distributed via:

- **Git repository** — include in the project's `templates/` directory
- **File sharing** — send directly via Slack, email, etc.
- **Internal package registry** — store in Artifactory, etc.

Since `.katar` is a single file, distribution is straightforward regardless of method.

---

## Security

As a safety measure, only templates **explicitly approved by the user** can be used in AI workflows (e.g., the `assemble` command).

### Template Trust Management

- On first use, the `**Prompt**` block contents are displayed and user confirmation is required
- Once approved, the trust is recorded in `.template_trust.json` and no further confirmation is needed
- If the template's `**Prompt**` is modified, re-confirmation is required

```bash
# Check prompt contents and trust status
gospelo-kata show-prompt my_template

# assemble prompts for confirmation on untrusted templates
gospelo-kata assemble --type my_template --data data.yml
```

### Package File Restrictions

Only the following files are allowed in packages:

- `manifest.json`
- `*_tpl.kata.md` (template body)
- Image files (`.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`, `.ico`, `.bmp`)

All other files are rejected by the `pack` command and cannot be accessed at load time.

### Package Size Limits

To protect against malicious packages, the following size limits are enforced:

| Limit | Maximum |
|-------|---------|
| File count | 100 files |
| Single file size | 10 MB |
| Total extracted size | 50 MB |

Packages exceeding these limits will be rejected with an error.

### Package Integrity Verification

`.katar` packages have a built-in **tamper detection** mechanism.

**How it works:**

1. When you create a package with `gospelo-kata pack`, a SHA-256 hash is computed from the contents of all files
2. The hash is stored in the `_integrity` field of `manifest.json`
3. When loading a package, the hash is recomputed from the file contents and compared against `_integrity`
4. If they don't match, the package is considered tampered and loading is rejected

Think of it like a wax seal on an envelope. If the seal is broken, you know someone may have tampered with the contents.

### Rendered Document Structure Integrity

Rendered `.kata.md` files also have tamper detection.

**How it works:**

1. During `gospelo-kata render`, a hash is computed from the Prompt, template body, and Schema inside the `<details>` section (the Data block is excluded)
2. The hash is embedded as an HTML comment: `<!-- kata-structure-integrity: sha256:... -->`
3. During `gospelo-kata lint`, the same computation is performed and compared against the embedded hash
4. If they don't match, a `D017` warning is reported

The Data block is excluded because editing data is normal user behavior. What we want to detect is unintended changes to the template structure (Prompt, Schema, and template body).

### Why Publishing This Process Is Safe

There's a concept in cryptography called **Kerckhoffs's Principle**: "Security should depend on keeping the key secret, not on keeping the algorithm secret."

gospelo-kata's hash verification is based on SHA-256, one of the most widely used algorithms in the world. Even if you know exactly how the hash is computed, it is computationally infeasible to modify file contents while producing the same hash value. Publishing the algorithm does not reduce security.

### Limitations and Complementary Measures

Here's an important caveat:

**Integrity verification detects tampering — it does not prove authorship.**

For example, if an attacker creates a malicious template using `gospelo-kata pack`, the package hash will be computed correctly. Integrity verification alone cannot tell you *who* created the package.

This is where **Trust Management** fills the gap:

- When using an unknown template for the first time, the `**Prompt**` contents are displayed and the user must explicitly approve it
- Templates never auto-execute without user approval
- If a template's `**Prompt**` is modified, re-approval is required

The two-layer approach — integrity verification plus trust management — ensures both "the content hasn't been tampered with" and "the user intentionally approved this."

### Known Concerns

| Concern | Mitigation |
|---------|------------|
| A malicious actor can create a valid `.katar` package | Mitigated by trust management (Prompt approval). User confirmation is required on first use |
| Package authorship cannot be cryptographically proven | Digital signatures are not yet supported. Users must assess the trustworthiness of the distribution source |
| AI may not correctly evaluate Prompt safety | Prompt contents are shown to the user. The final decision is always made by a human |
| Data block could be tampered with after rendering | Data is excluded from the structure hash. Data correctness is validated by schema validation (lint) |
