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
<span data-kata="p-items-0-qty" data-kata-type="integer">42</span>
<span data-kata="p-items-0-status" data-kata-type="enum" data-kata-enum="done">done</span>
<span data-kata="p-items-0-done" data-kata-type="boolean">true</span>
```

- `p-` prefix: property path
- Array indices are embedded in the anchor: `p-items-0-qty` → `items[0].qty`.
  This makes cross-referencing the same element from multiple places in the
  template safe — the extractor dispatches each value onto the correct
  `arr[i]` slot instead of inflating the source array
- `-` delimited: nested properties (`categories.items.status`)
- `data-kata-type`: original JSON Schema type, emitted for anything other
  than `string` (omitted for strings to keep markup small). Recognized
  values: `integer`, `number`, `boolean`, `enum`, `array`. Used by the
  extractor to coerce textContent back to the original type on sync
- `data-kata-enum`: allowed values (shown in VS Code hover)
- `data-kata-each`: array loop marker

`sync to-data` extracts values from these spans and reconstructs the
original data structure, using `data-kata-type` (when present) and the
Specification section's schema shorthand to restore types.

### Hidden annotations

Fields that the template wants to preserve across round-trips but does
not want to display can be wrapped in a hidden span:

```html
<span data-kata="p-characters-0-id" hidden>alice</span>
```

This is the idiom used by the `storyboard` template for
`characters[].id` — the id is not shown to readers but is required by
the schema and must survive `sync to-data`.

---

## Preserving Un-annotated Fields on sync

`sync to-data` applies the extracted values as a **patch on top of the
existing Data block**, not as a replacement. Fields that the template
renders without a `data-kata` span (image `src` attributes, arbitrary
HTML not tied to a schema property, etc.) are preserved from the old
Data block so a single save never silently drops information.

Concretely:

- **Top-level scalars**: the extracted value wins; anything not in the
  extract is kept from the old Data
- **Arrays**: the extracted length is authoritative (so user-initiated
  deletes flow through). Each surviving element is merged with the
  same-index element in the old Data so un-annotated fields on that
  element survive
- **Nested dicts**: recursed into with the same rules

Without this merge, fields such as a storyboard cut's `image` path would
disappear on the first `sync to-data` because only the values wrapped in
`<span data-kata="…">` are visible to the extractor.

---

## Important Notes

- **Don't enable both directions at once**: `toHtml` and `toData` are mutually exclusive. Always pick one mode at a time
- **Don't break span structure**: Deleting `data-kata` attributes or span tags will prevent sync to-data from extracting data
- **Enum values**: When editing span text, only use values allowed by the schema's `enum()` definition
- **Types are restored from the schema**: a `data-kata-type="integer"`
  span that contains "42" becomes `42` (int) in the Data block. A plain
  string field containing `", "` is **not** split into an array when the
  Specification section declares it as `string`
