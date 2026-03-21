# Type Conversion Specification

Type conversion rules between KATA Markdown schema definitions and data.

---

## Background

KATA Markdown uses YAML for both schema and data definitions.
However, there is a naming mismatch between schema shorthand type names (`integer`, `boolean`, etc.) and PyYAML's native type names (`int`, `bool`, etc.), which was causing silent bugs.

### PyYAML Type Coercion

```yaml
count: 42          # → int
ratio: 3.14        # → float
active: true       # → bool
name: hello        # → str
quoted: "42"       # → str (quoted forces string)
```

---

## Canonical Schema Shorthand Types

Canonical type names recognized by KATA shorthand:

| Canonical Name | JSON Schema Conversion | Python Type |
|---------------|----------------------|-------------|
| `string` | `{"type": "string"}` | `str` |
| `integer` | `{"type": "integer"}` | `int` |
| `number` | `{"type": "number"}` | `int`, `float` |
| `boolean` | `{"type": "boolean"}` | `bool` |
| `object` | `{"type": "object"}` | `dict` |
| `any` | `{}` | any |

---

## Type Aliases

Aliases matching PyYAML's native type names are introduced. They are normalized to canonical names at parse time.

| Alias | Normalized To | Purpose |
|-------|--------------|---------|
| `int` | `integer` | Short form matching PyYAML type name |
| `float` | `number` | Short form matching Python type name |
| `bool` | `boolean` | Short form matching PyYAML type name |
| `str` | `string` | Short form matching Python type name |

### Schema Examples

```yaml
# Canonical names (recommended)
count: integer!
ratio: number
active: boolean

# Aliases (equivalent)
count: int!
ratio: float
active: bool
```

Both forms produce the same JSON Schema output.

---

## Error Handling for Unknown Types

If a type name does not match any canonical name, alias, or `enum()` pattern, a **`ValueError` is raised immediately**.

### Before (Fallback Behavior)

```python
# Unknown type → silently treated as string (source of bugs)
"int" → {"type": "string", "description": "int"}
```

### After (Error Behavior)

```python
# Unknown type → immediate error
"unknown_type" → ValueError: Unknown schema type: 'unknown_type'
```

This change ensures schema definition errors are caught immediately.

---

## Data Loading

Data is supported in YAML format only. The validator's data loading is changed from `json.loads` to `yaml.safe_load`.

> **Note:** The Data block parser inside `.kata.md` (`_parse_data_block`) already uses `yaml.safe_load`. Only `validate_file` in `validator.py` was using `json.loads`, which is being corrected.

### Type Checking During Validation

The validator checks whether `yaml.safe_load`'s native types match the JSON Schema types from the schema:

| Schema Type | Accepted Python Types |
|------------|----------------------|
| `string` | `str` |
| `integer` | `int` |
| `number` | `int`, `float` |
| `boolean` | `bool` |
| `array` | `list` |
| `object` | `dict` |

---

## Conversion Flow

```
Schema Definition (**Schema** block in .kata.md)
  │
  ├── "integer" / "int"  ──→ {"type": "integer"}
  ├── "number" / "float" ──→ {"type": "number"}
  ├── "boolean" / "bool" ──→ {"type": "boolean"}
  ├── "string" / "str"   ──→ {"type": "string"}
  └── unknown type name   ──→ ValueError (immediate error)
  │
  ↓ Validation
  │
Data (**Data** block in .kata.md / external .yml file)
  └── yaml.safe_load → native types (int, float, bool, str, list, dict)
  │
  ↓ Type Check
  │
Native type vs JSON Schema type → OK / ValidationError
```

---

## Affected Components

| Component | File | Change |
|-----------|------|--------|
| Shorthand Parser | `template.py` | Add `_TYPE_ALIASES` map, replace fallback with `ValueError` |
| Validator | `validator.py` | Change `validate_file` from `json.loads` to `yaml.safe_load` |
| Documentation | `kata-markdown-format.md` | Add aliases to type notation table |
