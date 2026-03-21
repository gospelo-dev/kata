# Lint Rules

All rule codes detected by `gospelo-kata lint` and their remedies.

---

## Template Mode (Source .kata.md)

Template syntax validation. Applied to files containing schema blocks, `{{ }}`, or `{% %}` (code block contents are excluded from detection).

### S — Schema Validation

| Code | Level | Description |
|------|-------|-------------|
| S000 | info | No schema defined (neither inline nor file reference) |
| S001 | error | Schema syntax error (JSON/YAML parse failure) |
| S002 | error | Schema is not a mapping (object) |
| S003 | warning | Schema has no `type` field |
| S004 | error | Schema file not found |

**Remedy**: Check the YAML syntax of the `**Schema**` + `` ```yaml `` block.

### T — Template Block Structure

| Code | Level | Description |
|------|-------|-------------|
| T001 | error | Unclosed `{% for %}` or `{% if %}` |
| T002 | error | `{% elif %}` without matching `{% if %}` |
| T003 | error | `{% else %}` without matching `{% if %}` / `{% for %}` |
| T004 | error | `{% endif %}` without matching `{% if %}` |
| T005 | error | `{% endfor %}` without matching `{% for %}` |
| T006 | warning | Unknown block tag (not standard Jinja2) |

**Remedy**: Verify `{% for %}...{% endfor %}` and `{% if %}...{% endif %}` pairing.

### P — Prompt Block

| Code | Level | Description |
|------|-------|-------------|
| P001 | warning | No prompt block found |
| P002 | warning | Suspicious prompt content detected |

**P001 Remedy**: Add a `**Prompt**` + `` ```yaml `` block to the template. This provides AI guidance for data generation. User confirmation is required on first use.

**P002 Remedy**: The prompt contains patterns commonly associated with prompt injection (e.g., role override, instruction override, command execution, credential access). Review the prompt content and remove any suspicious instructions. Prompts should only describe **what data to generate** and **what each field means** — see [Prompt Design Guide](prompt-design-guide.md).

### F — Filter Validation

| Code | Level | Description |
|------|-------|-------------|
| F001 | error | Unknown filter name |

**Remedy**: See the built-in filter list in [KATA Markdown™ Format](kata-markdown-format.md).

### V — Variable References

| Code | Level | Description |
|------|-------|-------------|
| V001 | warning | Template variable not found in schema properties |
| V002 | info | Schema property unused in template |

**Remedy**: V001 — Add the property to the schema, or fix the variable name typo. V002 — Informational only.

---

## Document Mode (Rendered .kata.md / .md)

Structural validation of rendered documents. Auto-applied to files with `data-kata` spans.

### D — Document Structure

| Code | Level | Description |
|------|-------|-------------|
| D001 | info | External schema not found (using inline anchors) |
| D002 | error | Required section (`## heading`) is missing |
| D003 | warning | Table column count mismatch |
| D004 | warning | Empty section (heading only, no content) |
| D005 | warning | `data-kata` anchor not found in schema properties |
| D006 | info | Schema property not referenced by any annotation |
| D007 | warning | Enum value not in allowed values list |
| D008 | warning | String shorter than minLength |
| D009 | warning | String exceeds maxLength |
| D010 | warning | Array element count outside minItems/maxItems range |
| D011 | warning | Duplicate `data-kata` anchor ID |
| D012 | error/warning | kata-card structure issue (unclosed, missing kata-left/kata-right) |
| D014 | warning | Missing `<details>` or `<style>` section |
| D015 | warning | Enum value in table lacks data-kata annotation |
| D016 | error | HTML tag found inside data-kata span |
| D017 | warning | Structure integrity hash mismatch |

### D016 Details

`data-kata` span values must be **plain text**. If HTML tags are present:
- `extract` regex (`[^<]*`) fails to match, causing data loss
- XSS risk when rendered in browsers

**Remedy**:
```bash
# Auto-fix
gospelo-kata fmt problematic.kata.md

# Re-generate with render (auto-sanitizes)
gospelo-kata render source.kata.md -o output.kata.md
```

`render` automatically sanitizes with `html.escape()` on new output.

### D017 Details

The structure integrity hash protects the template structure (Prompt, template body, Schema) inside the `<details>` Schema Reference section against accidental or malicious modification. Data changes are excluded from the hash.

- **warning**: Hash mismatch — Prompt, template body, or Schema has been modified since rendering
- Documents without an integrity hash (older files) do not trigger this rule

**Remedy**:
```bash
# Re-render from source to regenerate the hash
gospelo-kata render source.kata.md -o output.kata.md
```

---

## File System

| Code | Level | Description |
|------|-------|-------------|
| E001 | error | File not found |

---

## Disabling Rules

To disable specific rules, add the following comment to the document:

```html
<!-- kata-lint-disable D014 D006 -->
```

Multiple codes can be specified, separated by spaces.
