# KATA Markdown™ Format Specification

Reference for `.kata.md` file syntax.

---

## Source File Structure

A source `.kata.md` consists of 4 blocks:

````markdown
**Prompt**

```yaml
(AI instructions)
```

(Jinja2 template body)

<details>
<summary>Specification</summary>

**Schema**

```yaml
(Schema definition in YAML shorthand)
```

**Data**

```yaml
(Data in YAML)
```

</details>
````

The Prompt block is **required** in template files. User confirmation is required on first use.

Recommended layout:
1. `**Prompt**` + `` ```yaml `` at the top
2. Jinja2 template body
3. `**Schema**` and `**Data**` inside a `<details>` block

> **Note:** The legacy `{#schema ... #}` / `{#prompt ... #}` / `{#data ... #}` inline syntax is still accepted for backward compatibility but is deprecated. New templates should use the Bold heading + code block format shown above.

---

## Schema Block

Defines data types using YAML shorthand notation.

````markdown
**Schema**

```yaml
title: string!
version: string
categories[]!:
  id: string!
  name: string!
  items[]!:
    id: string!
    status: enum(draft, pending, approve, reject)
    tags: string[]
```
````

### Type Notation

| Notation | Meaning | JSON Schema Conversion |
|----------|---------|----------------------|
| `string` | Optional string | `{"type": "string"}` |
| `string!` | Required string | `{"type": "string"}` + required |
| `integer` | Integer | `{"type": "integer"}` |
| `number` | Number | `{"type": "number"}` |
| `boolean` | Boolean | `{"type": "boolean"}` |
| `enum(a, b, c)` | Enumeration | `{"type": "string", "enum": ["a","b","c"]}` |
| `string[]` | String array | `{"type": "array", "items": {"type": "string"}}` |
| `items[]!:` | Required object array | `{"type": "array", "items": {"type": "object", ...}}` + required |
| `items[]:` | Optional object array | Same as above (without required) |
| `integer\|integer[]` | Union type | `{"oneOf": [{"type": "integer"}, {"type": "array", "items": {"type": "integer"}}]}` |

#### Union Types

Use `|` to specify multiple acceptable types. The value is valid if it matches any of the listed types.

```yaml
expected_status: integer|integer[]!    # Integer or integer array (required)
```

Expands to JSON Schema `oneOf`.

#### Type Aliases

Short forms matching Python/PyYAML type names are also supported. They are normalized to canonical names at parse time.

| Alias | Normalized To |
|-------|--------------|
| `int` | `integer` |
| `float` | `number` |
| `bool` | `boolean` |
| `str` | `string` |

### Nesting

Use indentation to express object/array nesting:

```yaml
categories[]!:
  id: string!
  items[]!:
    id: string!
    name: string!
```

---

## Data Block

Defines data to pass to the template in YAML format.

````markdown
**Data**

```yaml
title: Security Check
categories:
  - id: CAT-01
    name: Input Validation
    items:
      - id: SEC-01
        name: SQL Injection
        status: draft
        tags:
          - web
          - database
```
````

---

## Prompt Block

Descriptive text for AI to reference when generating data. Automatically removed during rendering.

````markdown
**Prompt**

```yaml
This template generates a security test specification.
Describe each test case in the test_cases array.
priority must be one of high/medium/low.
```
````

---

## Template Body (Jinja2 Subset)

### Variable Interpolation

```markdown
# {{ title }}

> Version: {{ version | default("1.0") }}
```

### Loops

```markdown
{% for item in items %}| {{ item.id }} | {{ item.name }} |
{% endfor %}
```

### Conditionals

```markdown
{% if version %}Version: {{ version }}{% endif %}
{% if priority == "high" %}**Critical**{% elif priority == "medium" %}Warning{% else %}Normal{% endif %}
```

### Variable Assignment — `{% set %}`

Bind a local variable with `{% set name = expr %}`. Useful for resolving
a cross-reference once and reusing it, or for computing a derived value
to keep rendered markup concise.

This is how the built-in `storyboard` template picks each cut's speaker
out of the `characters[]` array. For every cut, it looks up the
character whose `id` matches `cut.speaker`, then renders that
character's avatar next to the dialogue bubble:

```jinja
{% for cut in cuts %}
### {{ cut.id }}

{% set speaker = characters | selectattr("id", "equalto", cut.speaker) | first %}
{% if speaker %}
  <img src="{{ speaker.icon }}" alt="{{ speaker.name }}" width="48" />
  <strong>{{ speaker.name }}</strong>
{% endif %}

{% for line in cut.dialogue %}{{ line }}
{% endfor %}
{% endfor %}
```

Values bound via `{% set %}` are **not annotated** with `data-kata`
spans in the rendered output. `{{ speaker.name }}` in the snippet above
renders as plain text — not as another `<span data-kata="p-characters-0-name">…</span>`.
That is crucial for LiveMorph: `characters[0].name` is already
annotated once when the template renders the Characters section, so
re-emitting it through the set-resolved `speaker` variable would
inflate the `characters` array on `sync to-data`.

Block form (`{% set x %}...{% endset %}`) is not supported; only the
inline assignment shown above.

### Built-in Filters

| Filter | Description | Example |
|--------|-------------|---------|
| `default(v)` | Default value | `{{ x \| default("N/A") }}` |
| `join(sep)` | Join array | `{{ tags \| join(", ") }}` |
| `length` | Element count | `{{ items \| length }}` |
| `upper` / `lower` / `title` | Case conversion | `{{ name \| upper }}` |
| `trim` | Strip whitespace | `{{ text \| trim }}` |
| `first` / `last` | First/last element | `{{ items \| first }}` |
| `replace(old, new)` | Replace | `{{ s \| replace("_", "-") }}` |
| `int` / `float` | Type conversion | `{{ val \| int }}` |
| `sort` / `reverse` / `unique` | Sort etc. | `{{ items \| sort }}` |
| `truncate(len)` | Truncate | `{{ desc \| truncate(100) }}` |
| `e` / `escape` | HTML escape | `{{ html \| e }}` |
| `tojson` | JSON conversion | `{{ data \| tojson }}` |
| `selectattr(attr[, test[, value]])` | Keep elements where the attribute passes the test | `{{ items \| selectattr("active") }}` / `{{ items \| selectattr("id", "equalto", "a") }}` |
| `rejectattr(attr[, test[, value]])` | Inverse of `selectattr` | `{{ items \| rejectattr("disabled") }}` |

Supported `selectattr` / `rejectattr` tests: `equalto` (`eq`, `==`),
`ne` (`!=`), `lt`, `gt`, `le`, `ge`, `in`. Omitting the test keeps
elements whose attribute is truthy.

---

## Rendered Output Format

Structure of output generated by `gospelo-kata build` (or `render`).

### data-kata Attributes

Template variables are wrapped in `<span data-kata="p-{property-path}">`:

```html
<span data-kata="p-title">Security Check</span>
```

Nested property anchor paths are joined with `-`. Array elements carry
their index inside the anchor so the extractor can dispatch each value
to the correct slot without relying on document order:

```html
<span data-kata="p-categories-0-items-0-status">draft</span>
```

### data-kata-type Attribute

When the schema declares a non-string type, the annotator adds a
`data-kata-type` attribute so `extract` / `sync to-data` can coerce the
textContent back to its original type:

| Schema type | Rendered attribute | Round-trip result |
|-------------|--------------------|-------------------|
| `integer` | `data-kata-type="integer"` | `"42"` → `42` |
| `number` | `data-kata-type="number"` | `"3.14"` → `3.14` |
| `boolean` | `data-kata-type="boolean"` | `"true"` → `True` |
| `enum(...)` | `data-kata-type="enum"` + `data-kata-enum="..."` | Kept as string |
| `string[]` | `data-kata-type="array"` | Comma-separated → list |
| `string` | (omitted — default) | Kept verbatim |

Plain `string` fields are safe to contain `", "` in natural language
(a sentence, a narration line, a cut's `audio` cue). The extractor
consults the Specification section's schema shorthand and suppresses
its legacy comma-splitting heuristic for any field declared as
`string`, so sync does not turn `"Soft piano, strings in the background"`
into a two-element array.

### data-kata-each Loop Markers

A `<div data-kata-each="collection_name">` is inserted at the start of array loops:

```html
<div data-kata-each="test_cases"></div>
| <span data-kata="p-test-cases-test-id">TC-01</span> | ...
```

### HTML Sanitization

HTML tags in data values are automatically escaped:

- Source data: `<script>alert(1)</script>`
- Output: `&lt;script&gt;alert(1)&lt;/script&gt;`
- On extract: Restored to `<script>alert(1)</script>`

### Specification Section

A `<details>` block is appended at the end of the output. It contains the Prompt, template body, Schema, and Data — everything needed to reconstruct or re-render the document from a single file:

````html
---

<details>
<summary>Specification</summary>

**Prompt**

```yaml
This template generates a security test specification.
priority must be one of high/medium/low.
```

```kata:template
# {{ title }}

{% for item in items %}
- {{ item.name }}
{% endfor %}
```

**Schema**

```yaml
title: string!
items[]!:
  id: string!
  name: string!
```

**Data**

```yaml
title: Security Check
items:
- id: SEC-01
  name: SQL Injection
```

</details>
````

This structure enables reconstruction from a single `.kata.md` file:
- `data-kata` spans -> Variable bindings
- `data-kata-each` divs -> Loop structure
- Prompt -> AI instructions
- Template body -> Jinja2 source
- Schema -> Type definitions
- Data -> Original data

---

## Round-Trip

```
Source (.kata.md)
  +-- **Prompt** + **Schema** + **Data** + Jinja template
  | render
Output (.kata.md)
  +-- data-kata spans + data-kata-each divs
  +-- <details> Prompt + Template + Schema + Data
  | extract
JSON data (equivalent to original)
```

`extract` uses `data-kata` span values and the Specification array structure to reconstruct JSON. HTML entities (`&lt;` etc.) are automatically restored to their original characters (`<`).
