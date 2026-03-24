# LiveMorph --- Bidirectional Real-time Sync

LiveMorph synchronizes the Data block and HTML body of a KATA Markdown document bidirectionally.
Edit either side, and the other updates automatically.

---

## Concept

![LiveMorph Concept Diagram](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/images/livemorph-concept.jpg?raw=true)

| Direction | Command | What Happens |
|-----------|---------|-------------|
| **Data → HTML** | `sync to-html` | Edit Data block → re-execute template → update body |
| **HTML → Data** | `sync to-data` | Edit `data-kata` spans in body → extract to Data block → re-render |

---

## CLI Usage

### Sync to HTML (Data → Body)

After editing the Data block's YAML:

```bash
gospelo-kata sync to-html document.kata.md
```

Internally:
1. Reads Specification (template + schema + data) from the `.kata.md`
2. Re-executes the template with the Data block's YAML
3. Overwrites the `.kata.md` with the new body

### Sync to Data (Body → Data)

After directly editing `<span data-kata="...">` values in the body:

```bash
gospelo-kata sync to-data document.kata.md
```

Internally:
1. Extracts all `data-kata` span values from the body
2. Replaces the Data block YAML with the extracted data
3. Re-executes the template with the updated Data (ensures consistency)

---

## VS Code Usage

The VS Code extension (kata-lint) lets you operate LiveMorph directly from the editor.

### Context Menu

Right-click on a `.kata.md` file:

| Menu Item | Action |
|-----------|--------|
| **Kata: Sync to HTML** | Sync Data → body + set mode to `toHtml` |
| **Kata: Sync to Data** | Sync body → Data + set mode to `toData` |
| **Kata: Sync OFF** | Disable auto-sync |
| **Kata: Lint File** | Run lint only |

### Status Bar

The current sync mode is shown in the status bar at the bottom of the editor:

| Display | Mode |
|---------|------|
| `Sync: OFF` | No auto-sync (manual commands only) |
| `→ Sync: to HTML` | Auto-sync Data → body on save |
| `← Sync: to Data` | Auto-sync body → Data on save |

Click the status bar item to switch modes via QuickPick.

### Settings

`settings.json`:

```json
{
  "kataLint.syncOnSave": "off"
}
```

| Value | Behavior |
|-------|----------|
| `"off"` | Do nothing on save (default) |
| `"toHtml"` | Sync Data → body on save |
| `"toData"` | Sync body → Data on save |

> Default is `"off"`. Explicitly select a mode to avoid unintended overwrites.

---

## Workflow Examples

### Example 1: AI Generates Data → Human Reviews

```bash
# 1. AI generates data
gospelo-kata prepare test_spec -o data.yml
# (AI skill /kata-gen auto-generates data.yml)

# 2. Build
gospelo-kata build test_spec data.yml -o ./

# 3. Review & edit body in VS Code
#    → sync to-data (edits flow back to Data)

# 4. Validate
gospelo-kata lint test_spec.kata.md
```

### Example 2: Bulk-update Data in an Existing Document

```bash
# 1. Update Data block YAML via script
# 2. Sync to body
gospelo-kata sync to-html document.kata.md
```

### Example 3: Real-time Editing in VS Code

1. Open a `.kata.md` file in VS Code
2. Click status bar → select `to HTML`
3. Edit the Data block and save → body updates automatically
4. Want to switch direction? → Click status bar → select `to Data`
5. Edit body spans and save → Data updates automatically

---

## How data-kata Attributes Work

LiveMorph uses `data-kata` attributes to map between Data and HTML.

```html
<span data-kata="p-title">Security Checklist</span>
<span data-kata="p-categories-items-status" data-kata-enum="draft|pending|done">draft</span>
```

- `p-` prefix: property path
- `-` delimited: nested properties (`categories.items.status`)
- `data-kata-enum`: allowed values (shown in VS Code hover)
- `data-kata-each`: array loop marker

`sync to-data` extracts values from these spans and reconstructs the original data structure.

---

## Important Notes

- **Don't enable both directions at once**: `toHtml` and `toData` are mutually exclusive. Always pick one mode at a time
- **Don't break span structure**: Deleting `data-kata` attributes or span tags will prevent sync to-data from extracting data
- **Enum values**: When editing span text, only use values allowed by the schema's `enum()` definition
