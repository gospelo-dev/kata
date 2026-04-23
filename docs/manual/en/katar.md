# Template Package --- KATA ARchive&#8482; (.katar)

Create, package, and distribute custom templates.

---

## Overview

KATA ARchive (.katar) is the template package format for gospelo-kata.
ZIP-based, no extraction needed. Just place in `./templates/` and use immediately.

**Design principle: 1 package = 1 template = 1 schema**

![KATA ARchive Security Architecture](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/images/katar-security-architecture.jpg?raw=true)

---

## Directory Structure

```
my_template/
├── manifest.json             # Metadata (required)
├── my_template_tpl.kata.md   # Template body (required)
└── images/                   # Image assets (optional)
    └── my_template/          # Template-namespaced asset root
        └── ...
```

### Image Asset Path Convention

Bundled image assets are addressed from Data using
`./images/{template-name}/...` — a template-namespaced path rather than
a bare `./images/...`. This lets multiple templates with image assets
live side-by-side in the same workspace without their files colliding.

Example from the `storyboard` template's Data block:

```yaml
characters:
  - id: alice
    icon: ./images/storyboard/characters/alice.png
  - id: bob
    icon: ./images/storyboard/characters/bob.png
cuts:
  - id: C-001
    image: ./images/storyboard/C-001.jpg
```

The `.katar` archive stores these assets under
`storyboard/images/storyboard/...` so the same relative path resolves
both inside the package and in the rendered output's working directory.

---

## Quick Start

```bash
# 1. Generate scaffold
gospelo-kata pack-init ./my_template/

# 2. Edit template body (Prompt + Schema + Jinja2 template)

# 3. Package
gospelo-kata pack ./my_template/ -o my_template.katar

# 4. Install (just copy to templates/)
cp my_template.katar ./templates/

# 5. Use
gospelo-kata prepare my_template -o data.yml
gospelo-kata build my_template data.yml -o outputs/
```

---

## manifest.json

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

| Field | Required | Description |
|-------|:--------:|-------------|
| `name` | Yes | Template name (command identifier) |
| `version` | Yes | Semantic versioning |
| `template` | Yes | Template body filename |
| `description` | No | Template description |
| `author` | No | Author name |
| `url` | No | Repository URL |
| `license` | No | License (MIT, Apache-2.0, etc.) |
| `requires` | No | Array of dependent template names |
| `attributions` | No | Array of third-party asset credits (see below) |

### attributions

Optional. Record third-party asset origins (images, fonts, etc.)
bundled with the template. Each entry documents which files come from
which source and under what license, so `.katar` consumers can comply
with upstream redistribution requirements.

```json
{
  "attributions": [
    {
      "files": ["images/storyboard/characters/alice.png"],
      "source": "Custom-drawn pictogram",
      "license": "MIT",
      "copyright": "Copyright 2026 your-name",
      "notes": "Rendered from a hand-drawn silhouette at 1440×1440 then downsampled to 128×128"
    }
  ]
}
```

Fields inside each entry are advisory — there is no strict schema.
Include `files`, `source`, `license`, `copyright`, `notes` as
appropriate for the origin you want to credit.

---

## Template Body (`_tpl.kata.md`)

````markdown
**Prompt**

```yaml
This template generates a task list.
Describe items in the items array with id, name, and status.
```

# {{ title }}

| ID | Task | Status |
|----|------|:------:|
{% for item in items %}| {{ item.id }} | {{ item.name }} | {{ item.status }} |
{% endfor %}

<details>
<summary>Specification</summary>

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

---

## Search Order

1. `./templates/{name}/` (local directory)
2. `./templates/{name}.katar` (local package)
3. `gospelo_kata/templates/{name}/` (built-in directory)
4. `gospelo_kata/templates/{name}.katar` (built-in package)

Local templates take priority over built-ins.

---

## Security

### Trust Management

- First-time use displays the `**Prompt**` content and requires user approval
- Approval is recorded in `.template_trust.json`
- If the Prompt changes, re-approval is required

### File Restrictions

Allowed files in a package:

- `manifest.json`
- `*_tpl.kata.md` (template body)
- Images (`.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`, `.ico`, `.bmp`)

### Size Limits

| Limit | Maximum |
|-------|---------|
| File count | 100 |
| Single file | 10 MB |
| Total extracted size | 50 MB |

### Integrity Verification

`pack` records a SHA-256 hash of all files in `manifest.json`'s `_integrity` field.
On load, the hash is recomputed and verified. Mismatches are rejected.

Rendered `.kata.md` files also embed a structure integrity hash, verified by lint rule D017.

→ Full security details in [Template Package (detailed)](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/template-package.md)

---

## Distribution

- **Git repository** --- Include in `templates/`
- **File sharing** --- Send via Slack, email, etc.
- **Internal registry** --- Store in Artifactory, etc.
