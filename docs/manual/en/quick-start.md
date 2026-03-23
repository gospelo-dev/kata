# Quick Start

Pick a template, fill in the data, done.

---

## Install

```bash
pip install gospelo-kata
```

---

## Step 1 --- Choose a Template

```bash
gospelo-kata templates                       # List available templates
gospelo-kata prepare agenda -o data.yml      # Generate skeleton YAML
```

`data.yml` contains a scaffold of the fields required by the template.

## Step 2 --- Write Your Data

Edit `data.yml`:

```yaml
title: Weekly Standup
date: "2026-03-24"
attendees:
  - name: Alice
    role: Chair
  - name: Bob
    role: Scribe
agenda:
  - id: A-01
    topic: Review last week's action items
  - id: A-02
    topic: Release plan review
```

> AI skills (`/kata-gen`, `/kata-collect`) can auto-generate this YAML for you.

## Step 3 --- Build

```bash
gospelo-kata build agenda data.yml -o ./
```

`agenda.kata.md` is generated as a self-contained file with template, schema, data, and body all in one.

## Step 4 --- Validate

```bash
gospelo-kata lint agenda.kata.md
# → OK: agenda.kata.md — no issues found
```

---

## Keep Editing with LiveMorph

After the initial build, use **LiveMorph** to update the document as many times as needed.

### Changed the Data? → `sync to-html`

```bash
# After editing the Data block:
gospelo-kata sync to-html agenda.kata.md
```

Data changes flow through the template into the body.

### Edited the Body Directly? → `sync to-data`

```bash
# After editing span values in the body:
gospelo-kata sync to-data agenda.kata.md
```

Body changes are extracted into the Data block and re-rendered.

> With the VS Code extension, LiveMorph runs automatically on save. → [VS Code Integration](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/vscode.md)

---

## Summary

```
prepare  →  data.yml (scaffold)
    ↓
  edit
    ↓
build    →  .kata.md (complete)  →  lint to validate
    ↓
LiveMorph  →  Edit Data → sync to-html (repeat)
           →  Edit body → sync to-data (repeat)
```

- **You only edit the Data block or the body spans**
- No need to touch the template or schema
- `gospelo-kata export agenda.kata.md --part data` extracts just the data

---

## Next Steps

- [LiveMorph Guide](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/livemorph.md) --- Bidirectional sync details
- [Template List](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/templates.md) --- Built-in templates
- [CLI Reference](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/cli-reference.md) --- All commands
- [VS Code Integration](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/vscode.md) --- Extension setup
