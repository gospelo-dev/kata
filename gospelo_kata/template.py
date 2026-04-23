# KATA Markdown™ — gospelo-kata
# Copyright (c) 2025 gospelo. All rights reserved.
# Licensed under the MIT License. See LICENSE.md for details.

"""Jinja2 3.1.6 compatible template engine (subset) with schema annotation.

Supports a subset of Jinja2 syntax:
- Variable interpolation: {{ var }}, {{ obj.key }}, {{ obj["key"] }}
- For loops: {% for item in list %}...{% endfor %}
- Conditionals: {% if cond %}...{% elif cond %}...{% else %}...{% endif %}
- Filters: {{ var | filter }}, {{ var | filter(arg) }}
- Comments: {# comment #}
- Schema annotation: {#schema ... #} block for embedded JSON Schema

Built-in filters (Jinja2 3.1.6 compatible):
- default(value, default_value="", boolean=False)
- join(value, separator="")
- upper(value), lower(value), title(value), capitalize(value)
- trim(value), striptags(value)
- length(value), count (alias)
- first(value), last(value)
- replace(value, old, new)
- int(value, default=0), float(value, default=0.0)
- abs(value), round(value, precision=0)
- list(value), sort(value), reverse(value), unique(value)
- map(value, attribute=None)
- select(value, test=None), reject(value, test=None)
- batch(value, count, fill=None), slice(value, count, fill=None)
- indent(value, width=4, first=False)
- truncate(value, length=255, end="...")
- wordcount(value)
- center(value, width=80)
- format(value, *args, **kwargs)
- e / escape (HTML escape)
- safe (mark as safe / no-op in non-HTML context)
- items (dict items)
- dictsort(value, case_sensitive=False, by="key")
- tojson(value, indent=None)
"""

from __future__ import annotations

import html
import json
import math
import re
from typing import Any, Callable


# ---------------------------------------------------------------------------
# Schema extraction
# ---------------------------------------------------------------------------

_SCHEMA_INLINE_PATTERN = re.compile(
    r"\{#\s*schema\s*\n(.*?)\n\s*#\}", re.DOTALL
)
# Prompt block: {#prompt ... #} — read by AI assistants, stripped at render time
_PROMPT_PATTERN = re.compile(
    r"\{#\s*prompt\s*\n(.*?)\n\s*#\}", re.DOTALL
)
# Prompt block (code-block form): **Prompt**\n```yaml\n...\n```
_PROMPT_CODEBLOCK_PATTERN = re.compile(
    r"\*\*Prompt\*\*\s*\n\s*```yaml\n(.*?)```", re.DOTALL
)
# Data block: {#data ... #} — embedded YAML data, stripped at render time
_DATA_PATTERN = re.compile(
    r"\{#\s*data\s*\n(.*?)\n\s*#\}", re.DOTALL
)
# Bold-heading code block form: **Data**\n```yaml\n...\n```
_DATA_BOLD_CODEBLOCK_PATTERN = re.compile(
    r"\*\*Data\*\*\s*\n\s*```(?:yaml|json)\n(.*?)\n```", re.DOTALL
)
_SCHEMA_REF_PATTERN = re.compile(
    r"\{#\s*schema\s*:\s*(.+?)\s*#\}"
)
# Markdown link form: [kata-schema](path/to/schema.json)
_SCHEMA_LINK_PATTERN = re.compile(
    r"\[kata-schema\]\((.+?)\)"
)
# YAML/JSON code block form: ```yaml:schema ... ``` or ```json:schema ... ```
_SCHEMA_CODEBLOCK_PATTERN = re.compile(
    r"```(?:yaml|json):schema\s*\n(.*?)\n```", re.DOTALL
)
# Bold-heading code block form: **Schema**\n```yaml\n...\n```
_SCHEMA_BOLD_CODEBLOCK_PATTERN = re.compile(
    r"\*\*Schema\*\*\s*\n\s*```(?:yaml|json)\n(.*?)\n```", re.DOTALL
)
# Matches <details>...<summary>...</summary>...{#schema...#}...</details>
_DETAILS_WRAPPER_PATTERN = re.compile(
    r"<details>\s*\n\s*<summary>.*?</summary>\s*\n(.*?)</details>",
    re.DOTALL,
)


def _strip_details_wrapper(text: str, schema_start: int, schema_end: int) -> str:
    """Remove the schema block from the text.

    If the schema block is inside a <details> wrapper and the wrapper contains
    no other {# ... #} blocks, remove the entire wrapper.  Otherwise remove
    only the schema block itself so that sibling blocks like {#data} survive.
    """
    for m in _DETAILS_WRAPPER_PATTERN.finditer(text):
        if m.start() <= schema_start and schema_end <= m.end():
            # Check if the <details> wrapper contains other blocks
            # ({# ... #} inline blocks or **Bold** + ```yaml code blocks)
            inner = text[m.start():schema_start] + text[schema_end:m.end()]
            if re.search(r"\{#\s*\w+", inner) or re.search(r"\*\*(?:Data|Prompt)\*\*", inner):
                # Other blocks present — only remove the schema block
                return text[:schema_start] + text[schema_end:]
            # Schema is the only block — remove entire wrapper
            return text[:m.start()] + text[m.end():]
    # No wrapper — just remove the schema block itself
    return text[:schema_start] + text[schema_end:]


def _parse_schema_content(content: str) -> Any:
    """Parse schema content as JSON or YAML (auto-detected).

    Auto-detection: if content starts with '{' or '[', parse as JSON;
    otherwise YAML.  For YAML, shorthand type annotations (e.g. ``string!``,
    ``enum(a,b,c)``, ``object[]!``) are expanded to JSON Schema after parsing.

    Args:
        content: Raw schema content string.

    Returns:
        Parsed value (caller should check if it's a dict).

    Raises:
        ValueError: If parsing fails.
    """
    stripped = content.strip()
    if stripped.startswith(("{", "[")):
        # JSON — return as-is (no shorthand expansion)
        try:
            return json.loads(stripped)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in schema: {e}") from e
    else:
        # YAML
        try:
            import yaml
        except ImportError:
            raise ValueError(
                "PyYAML is required for YAML schema support. "
                "Install it with: pip install PyYAML"
            )
        try:
            result = yaml.safe_load(stripped)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in schema: {e}") from e
        # Apply shorthand expansion if the result looks like it uses them
        if isinstance(result, dict) and _has_shorthand(result):
            result = _expand_shorthand_schema(result)
        return result


# ---------------------------------------------------------------------------
# Shorthand type annotation expansion
# ---------------------------------------------------------------------------

_TYPE_ALIASES: dict[str, str] = {
    "int": "integer",
    "float": "number",
    "bool": "boolean",
    "str": "string",
}

_SHORTHAND_PATTERN = re.compile(
    r"^"
    r"(?P<type>string|integer|number|boolean|object|any"
    r"|int|float|bool|str)"                                # base type + aliases
    r"(?P<array>\[\])?"                                    # array suffix
    r"(?P<required>!)?"                                    # required marker
    r"(?:\((?P<constraint>[^)]*)\))?"                      # constraint (min..max)
    r"$"
)

_ENUM_PATTERN = re.compile(
    r"^enum\((?P<values>[^)]+)\)"
    r"(?P<array>\[\])?"
    r"(?P<required>!)?"
    r"$"
)


def _has_shorthand(data: Any) -> bool:
    """Check if a parsed YAML dict contains shorthand type strings."""
    if isinstance(data, dict):
        for v in data.values():
            if isinstance(v, str) and _is_shorthand(v):
                return True
            if isinstance(v, dict) and _has_shorthand(v):
                return True
    return False


def _is_shorthand(value: str) -> bool:
    """Check if a string value looks like a shorthand type annotation."""
    return bool(_SHORTHAND_PATTERN.match(value) or _ENUM_PATTERN.match(value))


_UNION_PATTERN = re.compile(
    r"^(?P<types>[a-zA-Z\[\]|]+)"
    r"(?P<required>!)?"
    r"$"
)


def _expand_type_string(type_str: str) -> tuple[dict[str, Any], bool]:
    """Expand a shorthand type string to a JSON Schema fragment.

    Args:
        type_str: Shorthand like "string!", "enum(a,b,c)", "object[]!(1..)",
                  "integer|integer[]!"

    Returns:
        Tuple of (schema_fragment, is_required).
    """
    # Try enum pattern first
    em = _ENUM_PATTERN.match(type_str)
    if em:
        values = [v.strip() for v in em.group("values").split(",")]
        schema: dict[str, Any] = {"type": "string", "enum": values}
        is_required = em.group("required") is not None
        if em.group("array"):
            schema = {"type": "array", "items": schema}
        return schema, is_required

    # Try standard type pattern
    tm = _SHORTHAND_PATTERN.match(type_str)
    if tm:
        base_type = _TYPE_ALIASES.get(tm.group("type"), tm.group("type"))
        if base_type == "any":
            schema = {}
        else:
            schema = {"type": base_type}
        is_required = tm.group("required") is not None

        # Parse constraint (min..max)
        constraint = tm.group("constraint")
        if constraint:
            _apply_constraint(schema, constraint, base_type, tm.group("array"))

        if tm.group("array"):
            schema = {"type": "array", "items": schema}
        return schema, is_required

    # Try union type pattern (e.g., "integer|integer[]!", "string|string[]")
    um = _UNION_PATTERN.match(type_str)
    if um and "|" in um.group("types"):
        parts = um.group("types").split("|")
        is_required = um.group("required") is not None
        one_of = []
        for part in parts:
            part = part.strip()
            if part.endswith("[]"):
                base = part[:-2]
                base = _TYPE_ALIASES.get(base, base)
                one_of.append({"type": "array", "items": {"type": base}})
            else:
                base = _TYPE_ALIASES.get(part, part)
                one_of.append({"type": base})
        schema = {"oneOf": one_of}
        return schema, is_required

    # Unknown type — raise immediately instead of silent fallback
    raise ValueError(f"Unknown schema type: '{type_str}'")


def _apply_constraint(
    schema: dict[str, Any], constraint: str, base_type: str, is_array: bool | None
) -> None:
    """Apply a constraint expression like '1..100' or '1..' to a schema."""
    parts = constraint.split("..")
    if len(parts) == 2:
        min_val, max_val = parts[0].strip(), parts[1].strip()
        if is_array:
            if min_val:
                schema["minItems"] = int(min_val)
            if max_val:
                schema["maxItems"] = int(max_val)
        elif base_type == "string":
            if min_val:
                schema["minLength"] = int(min_val)
            if max_val:
                schema["maxLength"] = int(max_val)
        else:
            if min_val:
                schema["minimum"] = int(min_val)
            if max_val:
                schema["maximum"] = int(max_val)


def _expand_shorthand_schema(data: dict[str, Any]) -> dict[str, Any]:
    """Expand a YAML dict with shorthand type annotations to full JSON Schema.

    Input (shorthand YAML):
        version: string!
        status: enum(draft, pending, approve)
        categories:
          id: string!
          items:
            name: string!

    Output (JSON Schema):
        {
          "type": "object",
          "required": ["version"],
          "properties": {
            "version": {"type": "string"},
            "status": {"type": "string", "enum": ["draft", "pending", "approve"]},
            "categories": {
              "type": "object",
              "required": ["id"],
              "properties": {
                "id": {"type": "string"},
                "items": {
                  "type": "object",
                  "properties": {
                    "name": {"type": "string"}
                  }
                }
              }
            }
          }
        }
    """
    # If it already looks like a standard JSON Schema (has both "type" and "properties"),
    # return as-is — no shorthand expansion needed
    if "type" in data and "properties" in data:
        return data
    if "type" in data and isinstance(data["type"], str) and \
       data["type"] in ("object", "array", "string", "integer", "number", "boolean"):
        return data

    return _expand_object(data)


_KEY_SUFFIX_PATTERN = re.compile(
    r"^(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)"
    r"(?P<array>\[\])?"
    r"(?P<required>!)?"
    r"$"
)


def _parse_key(raw_key: str) -> tuple[str, bool, bool]:
    """Parse a shorthand key like 'categories[]!' into (name, is_array, is_required)."""
    m = _KEY_SUFFIX_PATTERN.match(raw_key)
    if m:
        return m.group("name"), m.group("array") is not None, m.group("required") is not None
    return raw_key, False, False


def _expand_object(data: dict[str, Any]) -> dict[str, Any]:
    """Expand a dict of shorthand properties to a JSON Schema object."""
    properties: dict[str, Any] = {}
    required: list[str] = []

    for raw_key, value in data.items():
        # Skip JSON Schema meta-keywords that may already be present.
        # Only skip keys whose values are NOT shorthand strings.
        if raw_key in ("type", "required", "properties", "items",
                       "enum", "description", "$schema", "title",
                       "additionalProperties",
                       "minItems", "maxItems", "minLength", "maxLength"):
            if not (isinstance(value, str) and _is_shorthand(value)):
                continue

        key, key_is_array, key_is_required = _parse_key(raw_key)

        if isinstance(value, str):
            schema_fragment, val_is_required = _expand_type_string(value)
            properties[key] = schema_fragment
            if val_is_required or key_is_required:
                required.append(key)
        elif isinstance(value, dict):
            # Nested object with child properties
            expanded = _expand_object(value)
            if key_is_array:
                properties[key] = {"type": "array", "items": expanded}
            else:
                properties[key] = expanded
            if key_is_required:
                required.append(key)
        elif isinstance(value, list):
            # Could be enum or other list
            properties[key] = {"enum": value}
        else:
            properties[key] = {"type": type(value).__name__}

    result: dict[str, Any] = {"type": "object", "properties": properties}
    if required:
        result["required"] = required
    return result


def extract_schema(
    template_text: str,
    template_path: str | None = None,
) -> tuple[dict[str, Any] | None, str]:
    """Extract schema definition from template text.

    Supports these forms:
    1. Inline schema:   {#schema\\n{ ... JSON ... }\\n#}
       or              {#schema\\ntype: object\\n...YAML...\\n#}
    2. File reference:  {#schema: path/to/schema.json #}
    3. Markdown link:   [kata-schema](path/to/schema.json)
    4. Code block:      ```yaml:schema\\n...\\n``` or ```json:schema\\n...\\n```
       Path is resolved relative to the template file location.

    Forms 1 and 4 auto-detect JSON vs YAML by checking if content starts with '{'.
    Both may be wrapped in a <details> tag (recommended for readability).

    Args:
        template_text: Raw template source.
        template_path: Path to the template file (needed for relative schema refs).

    Returns:
        Tuple of (schema_dict_or_None, template_text_without_schema_block).
    """
    from pathlib import Path

    def _parse_and_clean(match: re.Match, content: str) -> tuple[dict[str, Any], str]:
        parsed = _parse_schema_content(content)
        if not isinstance(parsed, dict):
            raise ValueError(f"Schema must be a mapping, got {type(parsed).__name__}")
        cleaned = _strip_details_wrapper(template_text, match.start(), match.end())
        cleaned = cleaned.lstrip("\n")
        return parsed, cleaned

    # Try code block form first: ```yaml:schema ... ``` or ```json:schema ... ```
    match = _SCHEMA_CODEBLOCK_PATTERN.search(template_text)
    if match is not None:
        return _parse_and_clean(match, match.group(1))

    # Try bold-heading code block form: **Schema**\n```yaml\n...\n```
    match = _SCHEMA_BOLD_CODEBLOCK_PATTERN.search(template_text)
    if match is not None:
        return _parse_and_clean(match, match.group(1))

    # Try inline schema: {#schema ... #} (JSON or YAML auto-detected)
    match = _SCHEMA_INLINE_PATTERN.search(template_text)
    if match is not None:
        return _parse_and_clean(match, match.group(1))

    def _load_file_schema(match: re.Match) -> tuple[dict[str, Any], str]:
        ref_path = match.group(1).strip()
        if template_path:
            schema_path = Path(template_path).parent / ref_path
        else:
            schema_path = Path(ref_path)
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        return _parse_and_clean(match, schema_path.read_text(encoding="utf-8"))

    # Try file reference: {#schema: path #}
    match = _SCHEMA_REF_PATTERN.search(template_text)
    if match is not None:
        return _load_file_schema(match)

    # Try Markdown link form: [kata-schema](path)
    match = _SCHEMA_LINK_PATTERN.search(template_text)
    if match is not None:
        return _load_file_schema(match)

    return None, template_text


def extract_data(template_text: str) -> dict[str, Any] | None:
    """Extract embedded data from {#data ... #} block.

    The data block contains YAML (or JSON) that serves as the
    document's data source. This allows a single .kata.md file
    to contain schema, prompt, data, and template together.

    Returns:
        Parsed data dict, or None if no {#data} block is found.
    """
    match = _DATA_PATTERN.search(template_text)
    if match is None:
        match = _DATA_BOLD_CODEBLOCK_PATTERN.search(template_text)
    if match is None:
        return None

    raw = match.group(1).strip()
    if not raw:
        return None

    # Try JSON first
    if raw.startswith("{"):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

    # Try YAML
    try:
        import yaml
        data = yaml.safe_load(raw)
        if isinstance(data, dict):
            return data
    except ImportError:
        pass
    except Exception:
        pass

    return None


# ---------------------------------------------------------------------------
# Tokeniser
# ---------------------------------------------------------------------------

class _TokenType:
    TEXT = "TEXT"
    VAR = "VAR"           # {{ ... }}
    BLOCK = "BLOCK"       # {% ... %}
    COMMENT = "COMMENT"   # {# ... #}  (non-schema)


def _tokenize(template: str) -> list[tuple[str, str]]:
    """Split template into (token_type, content) pairs."""
    tokens: list[tuple[str, str]] = []
    # Pattern matches {# ... #}, {{ ... }}, {% ... %}
    pattern = re.compile(
        r"(\{#.*?#\}|\{\{.*?\}\}|\{%.*?%\})", re.DOTALL
    )
    pos = 0
    for m in pattern.finditer(template):
        start, end = m.span()
        if start > pos:
            tokens.append((_TokenType.TEXT, template[pos:start]))
        raw = m.group(0)
        if raw.startswith("{#"):
            tokens.append((_TokenType.COMMENT, raw[2:-2].strip()))
        elif raw.startswith("{{"):
            tokens.append((_TokenType.VAR, raw[2:-2].strip()))
        elif raw.startswith("{%"):
            tokens.append((_TokenType.BLOCK, raw[2:-2].strip()))
        pos = end
    if pos < len(template):
        tokens.append((_TokenType.TEXT, template[pos:]))
    return tokens


# ---------------------------------------------------------------------------
# AST nodes
# ---------------------------------------------------------------------------

class _TextNode:
    __slots__ = ("text",)
    def __init__(self, text: str):
        self.text = text


class _VarNode:
    __slots__ = ("expr",)
    def __init__(self, expr: str):
        self.expr = expr


class _ForNode:
    __slots__ = ("var_names", "iterable_expr", "body", "else_body")
    def __init__(self, var_names: list[str], iterable_expr: str,
                 body: list, else_body: list | None = None):
        self.var_names = var_names
        self.iterable_expr = iterable_expr
        self.body = body
        self.else_body = else_body


class _IfNode:
    __slots__ = ("branches", "else_body")
    def __init__(self, branches: list[tuple[str, list]], else_body: list | None = None):
        # branches: [(condition_expr, body_nodes), ...]
        self.branches = branches
        self.else_body = else_body


class _SetNode:
    """``{% set name = expr %}`` — assigns a local variable in context.

    Block form (``{% set x %}...{% endset %}``) is intentionally not
    supported; KATA templates don't need captured-body assignments yet.
    Values assigned via ``set`` are NOT added to ``_var_map``, so
    references to them in ``{{ name }}`` are rendered as raw text
    without ``data-kata`` annotation. This is what enables clean
    cross-referencing (e.g. resolving a speaker inside a cuts loop
    without inflating the speaker's source array during extract).
    """
    __slots__ = ("name", "expr")
    def __init__(self, name: str, expr: str):
        self.name = name
        self.expr = expr


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def _parse(tokens: list[tuple[str, str]]) -> list:
    """Parse token list into AST node list."""
    nodes, _ = _parse_nodes(tokens, 0)
    return nodes


def _parse_nodes(
    tokens: list[tuple[str, str]], pos: int, stop_tags: tuple[str, ...] = ()
) -> tuple[list, int]:
    """Parse tokens from pos until a stop tag is encountered.

    Returns (node_list, new_pos).
    """
    nodes: list = []
    while pos < len(tokens):
        ttype, content = tokens[pos]

        if ttype == _TokenType.TEXT:
            nodes.append(_TextNode(content))
            pos += 1

        elif ttype == _TokenType.VAR:
            nodes.append(_VarNode(content))
            pos += 1

        elif ttype == _TokenType.COMMENT:
            pos += 1  # skip comments

        elif ttype == _TokenType.BLOCK:
            tag = content.split()[0] if content.strip() else ""

            if tag in stop_tags:
                return nodes, pos

            if tag == "for":
                node, pos = _parse_for(tokens, pos)
                nodes.append(node)

            elif tag == "if":
                node, pos = _parse_if(tokens, pos)
                nodes.append(node)

            elif tag == "set":
                node, pos = _parse_set(tokens, pos)
                if node is not None:
                    nodes.append(node)

            else:
                # Unknown block tag – treat as text
                nodes.append(_TextNode(""))
                pos += 1
        else:
            pos += 1

    return nodes, pos


def _parse_set(
    tokens: list[tuple[str, str]], pos: int,
) -> tuple[_SetNode | None, int]:
    """Parse ``{% set name = expr %}`` into a ``_SetNode``.

    Only the inline assignment form is supported. A malformed tag
    returns ``None`` so the caller can skip it instead of raising —
    this matches the "unknown block becomes empty text" behaviour
    already used elsewhere in ``_parse_nodes``.
    """
    _, content = tokens[pos]
    m = re.match(r"set\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)", content.strip())
    if not m:
        return None, pos + 1
    name = m.group(1)
    expr = m.group(2).strip()
    return _SetNode(name, expr), pos + 1


def _parse_for(tokens: list[tuple[str, str]], pos: int) -> tuple[_ForNode, int]:
    """Parse {% for var in expr %}...{% else %}...{% endfor %}."""
    _, content = tokens[pos]
    # Parse "for x in expr" or "for x, y in expr"
    m = re.match(r"for\s+(.+?)\s+in\s+(.+)", content.strip())
    if not m:
        raise SyntaxError(f"Invalid for tag: {content}")

    var_part = m.group(1).strip()
    var_names = [v.strip() for v in var_part.split(",")]
    iterable_expr = m.group(2).strip()
    pos += 1

    body, pos = _parse_nodes(tokens, pos, stop_tags=("endfor", "else"))

    else_body = None
    if pos < len(tokens):
        _, tag_content = tokens[pos]
        if tag_content.strip() == "else":
            pos += 1
            else_body, pos = _parse_nodes(tokens, pos, stop_tags=("endfor",))

    # skip endfor
    if pos < len(tokens):
        pos += 1

    return _ForNode(var_names, iterable_expr, body, else_body), pos


def _parse_if(tokens: list[tuple[str, str]], pos: int) -> tuple[_IfNode, int]:
    """Parse {% if %}...{% elif %}...{% else %}...{% endif %}."""
    _, content = tokens[pos]
    condition = content[2:].strip()  # strip "if"
    pos += 1

    branches: list[tuple[str, list]] = []

    body, pos = _parse_nodes(tokens, pos, stop_tags=("elif", "else", "endif"))
    branches.append((condition, body))

    while pos < len(tokens):
        _, tag_content = tokens[pos]
        tag = tag_content.split()[0]

        if tag == "elif":
            cond = tag_content[4:].strip()
            pos += 1
            body, pos = _parse_nodes(tokens, pos, stop_tags=("elif", "else", "endif"))
            branches.append((cond, body))

        elif tag == "else":
            pos += 1
            else_body, pos = _parse_nodes(tokens, pos, stop_tags=("endif",))
            # skip endif
            if pos < len(tokens):
                pos += 1
            return _IfNode(branches, else_body), pos

        elif tag == "endif":
            pos += 1
            return _IfNode(branches, None), pos

        else:
            break

    return _IfNode(branches, None), pos


# ---------------------------------------------------------------------------
# Expression evaluator
# ---------------------------------------------------------------------------

def _resolve_name(name: str, context: dict[str, Any]) -> Any:
    """Resolve a dotted/bracketed name against context.

    Supports: var, obj.key, obj["key"], obj[0], obj.key.sub
    """
    # Split on . but respect brackets
    parts: list[str] = []
    current = ""
    i = 0
    while i < len(name):
        ch = name[i]
        if ch == ".":
            if current:
                parts.append(current)
                current = ""
        elif ch == "[":
            if current:
                parts.append(current)
                current = ""
            # Find matching ]
            j = name.index("]", i)
            bracket_content = name[i + 1 : j].strip()
            # Remove quotes if present
            if (bracket_content.startswith('"') and bracket_content.endswith('"')) or \
               (bracket_content.startswith("'") and bracket_content.endswith("'")):
                bracket_content = bracket_content[1:-1]
            parts.append(bracket_content)
            i = j + 1
            continue
        else:
            current += ch
        i += 1
    if current:
        parts.append(current)

    obj = context
    for part in parts:
        if isinstance(obj, dict):
            obj = obj.get(part)
        elif isinstance(obj, (list, tuple)):
            try:
                obj = obj[int(part)]
            except (ValueError, IndexError):
                return None
        elif hasattr(obj, part):
            obj = getattr(obj, part)
        else:
            return None
    return obj


def _eval_expr(expr: str, context: dict[str, Any]) -> Any:
    """Evaluate a template expression (variable access with optional filters).

    Supports:
    - Simple names: var, obj.key
    - String/number literals: "hello", 'hello', 42, 3.14
    - Filter chains: var | filter | filter(arg)
    - Comparison: ==, !=, <, >, <=, >=
    - Boolean: and, or, not
    - in operator: x in list
    - Ternary: true_val if cond else false_val
    """
    expr = expr.strip()
    if not expr:
        return ""

    # Handle ternary: value_if_true if condition else value_if_false
    # Must check before filters since | can appear in sub-expressions
    ternary_match = re.match(
        r"(.+?)\s+if\s+(.+?)\s+else\s+(.+)", expr
    )
    if ternary_match:
        true_expr = ternary_match.group(1).strip()
        cond_expr = ternary_match.group(2).strip()
        false_expr = ternary_match.group(3).strip()
        if _eval_expr(cond_expr, context):
            return _eval_expr(true_expr, context)
        return _eval_expr(false_expr, context)

    # Split by pipe for filters, but not inside strings or parens
    parts = _split_filters(expr)
    if len(parts) > 1:
        value = _eval_expr(parts[0], context)
        for filter_expr in parts[1:]:
            value = _apply_filter(filter_expr.strip(), value, context)
        return value

    # Boolean operators: and, or
    # Split on ' and ' / ' or ' respecting precedence (or < and)
    or_parts = _split_bool_op(expr, " or ")
    if len(or_parts) > 1:
        return any(_eval_expr(p, context) for p in or_parts)

    and_parts = _split_bool_op(expr, " and ")
    if len(and_parts) > 1:
        return all(_eval_expr(p, context) for p in and_parts)

    # not
    if expr.startswith("not "):
        return not _eval_expr(expr[4:], context)

    # Comparison operators
    for op in ("==", "!=", "<=", ">=", "<", ">"):
        idx = expr.find(op)
        if idx > 0:
            left = _eval_expr(expr[:idx], context)
            right = _eval_expr(expr[idx + len(op) :], context)
            if op == "==":
                return left == right
            elif op == "!=":
                return left != right
            elif op == "<=":
                return left <= right
            elif op == ">=":
                return left >= right
            elif op == "<":
                return left < right
            elif op == ">":
                return left > right

    # 'in' operator: x in y
    in_match = re.match(r"(.+?)\s+in\s+(.+)", expr)
    if in_match:
        left = _eval_expr(in_match.group(1), context)
        right = _eval_expr(in_match.group(2), context)
        if right is None:
            return False
        return left in right

    # String literal
    if (expr.startswith('"') and expr.endswith('"')) or \
       (expr.startswith("'") and expr.endswith("'")):
        return expr[1:-1]

    # Numeric literal
    try:
        if "." in expr:
            return float(expr)
        return int(expr)
    except ValueError:
        pass

    # Boolean / None literals
    if expr == "true" or expr == "True":
        return True
    if expr == "false" or expr == "False":
        return False
    if expr == "none" or expr == "None":
        return None

    # Variable resolution
    return _resolve_name(expr, context)


def _split_filters(expr: str) -> list[str]:
    """Split expression by | (pipe) for filters, respecting strings and parens."""
    parts: list[str] = []
    current = ""
    depth = 0
    in_str: str | None = None
    i = 0
    while i < len(expr):
        ch = expr[i]
        if in_str:
            current += ch
            if ch == in_str and (i == 0 or expr[i - 1] != "\\"):
                in_str = None
        elif ch in ('"', "'"):
            in_str = ch
            current += ch
        elif ch == "(":
            depth += 1
            current += ch
        elif ch == ")":
            depth -= 1
            current += ch
        elif ch == "|" and depth == 0:
            parts.append(current)
            current = ""
        else:
            current += ch
        i += 1
    if current:
        parts.append(current)
    return parts


def _split_bool_op(expr: str, op: str) -> list[str]:
    """Split expression by boolean operator, respecting strings and parens."""
    parts: list[str] = []
    depth = 0
    in_str: str | None = None
    current = ""
    i = 0
    while i < len(expr):
        ch = expr[i]
        if in_str:
            current += ch
            if ch == in_str and (i == 0 or expr[i - 1] != "\\"):
                in_str = None
            i += 1
            continue
        if ch in ('"', "'"):
            in_str = ch
            current += ch
            i += 1
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if depth == 0 and expr[i:].startswith(op):
            parts.append(current)
            current = ""
            i += len(op)
            continue
        current += ch
        i += 1
    if current:
        parts.append(current)
    return parts if len(parts) > 1 else [expr]


# ---------------------------------------------------------------------------
# Built-in filters (Jinja2 3.1.6 compatible)
# ---------------------------------------------------------------------------

def _parse_filter_call(filter_expr: str) -> tuple[str, list[str], dict[str, str]]:
    """Parse a filter expression like 'name(arg1, key=val)'.

    Returns (name, positional_args, keyword_args) as raw strings.
    """
    m = re.match(r"(\w+)\s*\((.*)\)\s*$", filter_expr, re.DOTALL)
    if m:
        name = m.group(1)
        args_str = m.group(2).strip()
        pos_args: list[str] = []
        kw_args: dict[str, str] = {}
        if args_str:
            for arg in _split_args(args_str):
                arg = arg.strip()
                if "=" in arg and not arg.startswith(("'", '"')):
                    k, v = arg.split("=", 1)
                    kw_args[k.strip()] = v.strip()
                else:
                    pos_args.append(arg)
        return name, pos_args, kw_args
    return filter_expr.strip(), [], {}


def _split_args(args_str: str) -> list[str]:
    """Split comma-separated args respecting strings and parens."""
    parts: list[str] = []
    current = ""
    depth = 0
    in_str: str | None = None
    for ch in args_str:
        if in_str:
            current += ch
            if ch == in_str:
                in_str = None
        elif ch in ('"', "'"):
            in_str = ch
            current += ch
        elif ch == "(":
            depth += 1
            current += ch
        elif ch == ")":
            depth -= 1
            current += ch
        elif ch == "," and depth == 0:
            parts.append(current)
            current = ""
        else:
            current += ch
    if current:
        parts.append(current)
    return parts


def _eval_filter_arg(arg: str, context: dict[str, Any]) -> Any:
    """Evaluate a filter argument (literal or variable)."""
    arg = arg.strip()
    if (arg.startswith('"') and arg.endswith('"')) or \
       (arg.startswith("'") and arg.endswith("'")):
        return arg[1:-1]
    if arg == "true" or arg == "True":
        return True
    if arg == "false" or arg == "False":
        return False
    if arg == "none" or arg == "None":
        return None
    try:
        if "." in arg:
            return float(arg)
        return int(arg)
    except ValueError:
        pass
    return _resolve_name(arg, context)


_BUILTIN_FILTERS: dict[str, Callable[..., Any]] = {}


def _register_filter(name: str, aliases: list[str] | None = None):
    """Decorator to register a built-in filter."""
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        _BUILTIN_FILTERS[name] = fn
        for alias in (aliases or []):
            _BUILTIN_FILTERS[alias] = fn
        return fn
    return decorator


@_register_filter("default", aliases=["d"])
def _filter_default(value: Any, default_value: Any = "", boolean: bool = False) -> Any:
    if boolean:
        return value if value else default_value
    return value if value is not None else default_value


@_register_filter("join")
def _filter_join(value: Any, separator: str = "") -> str:
    if not isinstance(value, (list, tuple)):
        return str(value) if value is not None else ""
    return separator.join(str(v) for v in value)


@_register_filter("upper")
def _filter_upper(value: Any) -> str:
    return str(value).upper()


@_register_filter("lower")
def _filter_lower(value: Any) -> str:
    return str(value).lower()


@_register_filter("title")
def _filter_title(value: Any) -> str:
    return str(value).title()


@_register_filter("capitalize")
def _filter_capitalize(value: Any) -> str:
    return str(value).capitalize()


@_register_filter("trim")
def _filter_trim(value: Any) -> str:
    return str(value).strip()


@_register_filter("striptags")
def _filter_striptags(value: Any) -> str:
    return re.sub(r"<[^>]+>", "", str(value))


@_register_filter("length", aliases=["count"])
def _filter_length(value: Any) -> int:
    if value is None:
        return 0
    return len(value)


@_register_filter("first")
def _filter_first(value: Any) -> Any:
    if isinstance(value, (list, tuple)) and value:
        return value[0]
    return None


@_register_filter("last")
def _filter_last(value: Any) -> Any:
    if isinstance(value, (list, tuple)) and value:
        return value[-1]
    return None


@_register_filter("replace")
def _filter_replace(value: Any, old: str = "", new: str = "") -> str:
    return str(value).replace(old, new)


@_register_filter("int")
def _filter_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


@_register_filter("float")
def _filter_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


@_register_filter("abs")
def _filter_abs(value: Any) -> Any:
    return abs(value)


@_register_filter("round")
def _filter_round(value: Any, precision: int = 0, method: str = "common") -> float:
    if method == "ceil":
        factor = 10 ** precision
        return math.ceil(value * factor) / factor
    elif method == "floor":
        factor = 10 ** precision
        return math.floor(value * factor) / factor
    return round(float(value), precision)


@_register_filter("list")
def _filter_list(value: Any) -> list:
    if value is None:
        return []
    return list(value)


@_register_filter("sort")
def _filter_sort(
    value: Any, reverse: bool = False, attribute: str | None = None
) -> list:
    if value is None:
        return []
    items = list(value)
    if attribute:
        key_fn = lambda x: x.get(attribute) if isinstance(x, dict) else getattr(x, attribute, None)
        return sorted(items, key=key_fn, reverse=reverse)
    return sorted(items, reverse=reverse)


@_register_filter("reverse")
def _filter_reverse(value: Any) -> Any:
    if isinstance(value, str):
        return value[::-1]
    return list(reversed(list(value)))


@_register_filter("unique")
def _filter_unique(value: Any) -> list:
    seen: set = set()
    result: list = []
    for item in (value or []):
        key = item if isinstance(item, (str, int, float, bool)) else id(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


@_register_filter("map")
def _filter_map(value: Any, attribute: str | None = None) -> list:
    if value is None:
        return []
    if attribute:
        return [
            item.get(attribute) if isinstance(item, dict)
            else getattr(item, attribute, None)
            for item in value
        ]
    return list(value)


@_register_filter("select")
def _filter_select(value: Any) -> list:
    return [item for item in (value or []) if item]


@_register_filter("reject")
def _filter_reject(value: Any) -> list:
    return [item for item in (value or []) if not item]


def _attr_lookup(item: Any, attr: str) -> Any:
    """Resolve ``item.attr`` or ``item["attr"]`` uniformly."""
    if isinstance(item, dict):
        return item.get(attr)
    return getattr(item, attr, None)


_SELECTATTR_TESTS = {
    "equalto": lambda a, b: a == b,
    "eq": lambda a, b: a == b,
    "==": lambda a, b: a == b,
    "ne": lambda a, b: a != b,
    "!=": lambda a, b: a != b,
    "lt": lambda a, b: a is not None and a < b,
    "gt": lambda a, b: a is not None and a > b,
    "le": lambda a, b: a is not None and a <= b,
    "ge": lambda a, b: a is not None and a >= b,
    "in": lambda a, b: a in (b or []),
}


@_register_filter("selectattr")
def _filter_selectattr(
    value: Any, attribute: str, test: str | None = None,
    *args: Any,
) -> list:
    """``selectattr(attr[, test[, value]])`` — Jinja2-compatible.

    - ``{{ items | selectattr("active") }}`` — items where attr is truthy
    - ``{{ items | selectattr("id", "equalto", "a") }}`` — items where
      ``item.id == "a"``. Supported tests: ``equalto``/``eq``/``==``,
      ``ne``/``!=``, ``lt``, ``gt``, ``le``, ``ge``, ``in``.
    """
    items = list(value or [])
    if test is None:
        return [i for i in items if _attr_lookup(i, attribute)]
    op = _SELECTATTR_TESTS.get(test)
    if op is None:
        raise ValueError(f"Unknown selectattr test: {test}")
    target = args[0] if args else None
    return [i for i in items if op(_attr_lookup(i, attribute), target)]


@_register_filter("rejectattr")
def _filter_rejectattr(
    value: Any, attribute: str, test: str | None = None,
    *args: Any,
) -> list:
    """Inverse of ``selectattr`` — same arg shape."""
    items = list(value or [])
    if test is None:
        return [i for i in items if not _attr_lookup(i, attribute)]
    op = _SELECTATTR_TESTS.get(test)
    if op is None:
        raise ValueError(f"Unknown rejectattr test: {test}")
    target = args[0] if args else None
    return [i for i in items if not op(_attr_lookup(i, attribute), target)]


@_register_filter("batch")
def _filter_batch(value: Any, count: int = 1, fill: Any = None) -> list:
    items = list(value or [])
    result = []
    for i in range(0, len(items), count):
        batch = items[i : i + count]
        if fill is not None and len(batch) < count:
            batch.extend([fill] * (count - len(batch)))
        result.append(batch)
    return result


@_register_filter("slice")
def _filter_slice(value: Any, count: int = 1, fill: Any = None) -> list:
    items = list(value or [])
    result: list[list] = [[] for _ in range(count)]
    for i, item in enumerate(items):
        result[i % count].append(item)
    if fill is not None:
        longest = max(len(s) for s in result) if result else 0
        for s in result:
            while len(s) < longest:
                s.append(fill)
    return result


@_register_filter("indent")
def _filter_indent(value: Any, width: int = 4, first: bool = False, blank: bool = False) -> str:
    s = str(value)
    indent_str = " " * width
    lines = s.split("\n")
    result = []
    for i, line in enumerate(lines):
        if i == 0 and not first:
            result.append(line)
        elif not blank and line.strip() == "":
            result.append(line)
        else:
            result.append(indent_str + line)
    return "\n".join(result)


@_register_filter("truncate")
def _filter_truncate(value: Any, length: int = 255, killwords: bool = False, end: str = "...") -> str:
    s = str(value)
    if len(s) <= length:
        return s
    if killwords:
        return s[: length - len(end)] + end
    # Find last space before length
    truncated = s[: length - len(end)]
    last_space = truncated.rfind(" ")
    if last_space > 0:
        truncated = truncated[:last_space]
    return truncated + end


@_register_filter("wordcount")
def _filter_wordcount(value: Any) -> int:
    return len(str(value).split())


@_register_filter("center")
def _filter_center(value: Any, width: int = 80) -> str:
    return str(value).center(width)


@_register_filter("format")
def _filter_format(value: Any, *args: Any, **kwargs: Any) -> str:
    return str(value) % args if args else str(value)


@_register_filter("escape", aliases=["e"])
def _filter_escape(value: Any) -> str:
    return html.escape(str(value))


@_register_filter("safe")
def _filter_safe(value: Any) -> Any:
    return value


@_register_filter("items")
def _filter_items(value: Any) -> list:
    if isinstance(value, dict):
        return list(value.items())
    return []


@_register_filter("dictsort")
def _filter_dictsort(
    value: Any, case_sensitive: bool = False, by: str = "key"
) -> list:
    if not isinstance(value, dict):
        return []
    items = list(value.items())
    if by == "value":
        key_fn = lambda x: x[1] if case_sensitive else str(x[1]).lower()
    else:
        key_fn = lambda x: x[0] if case_sensitive else str(x[0]).lower()
    return sorted(items, key=key_fn)


@_register_filter("tojson")
def _filter_tojson(value: Any, indent: int | None = None) -> str:
    return json.dumps(value, ensure_ascii=False, indent=indent)


@_register_filter("xmlattr")
def _filter_xmlattr(value: Any) -> str:
    if not isinstance(value, dict):
        return ""
    parts = []
    for k, v in value.items():
        if v is not None and v is not False:
            parts.append(f'{html.escape(str(k))}="{html.escape(str(v))}"')
    return " ".join(parts)


@_register_filter("filesizeformat")
def _filter_filesizeformat(value: Any, binary: bool = False) -> str:
    n = float(value)
    if binary:
        units = ["Bytes", "KiB", "MiB", "GiB", "TiB"]
        base = 1024
    else:
        units = ["Bytes", "kB", "MB", "GB", "TB"]
        base = 1000
    for unit in units[:-1]:
        if abs(n) < base:
            return f"{n:.1f} {unit}"
        n /= base
    return f"{n:.1f} {units[-1]}"


@_register_filter("pprint")
def _filter_pprint(value: Any) -> str:
    import pprint as pp
    return pp.pformat(value)


@_register_filter("urlize")
def _filter_urlize(value: Any) -> str:
    s = str(value)
    return re.sub(
        r"(https?://[^\s<>\"']+)",
        r'<a href="\1">\1</a>',
        s,
    )


@_register_filter("wordwrap")
def _filter_wordwrap(value: Any, width: int = 79, break_long_words: bool = True, wrapstring: str = "\n") -> str:
    import textwrap
    return wrapstring.join(
        textwrap.wrap(str(value), width=width, break_long_words=break_long_words)
    )


@_register_filter("groupby")
def _filter_groupby(value: Any, attribute: str = "") -> list:
    if not value or not attribute:
        return []
    groups: dict[Any, list] = {}
    order: list = []
    for item in value:
        key = item.get(attribute) if isinstance(item, dict) else getattr(item, attribute, None)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(item)
    return [{"grouper": k, "list": groups[k]} for k in order]


def _apply_filter(
    filter_expr: str, value: Any, context: dict[str, Any]
) -> Any:
    """Apply a single filter to a value."""
    name, raw_args, raw_kwargs = _parse_filter_call(filter_expr)

    fn = _BUILTIN_FILTERS.get(name)
    if fn is None:
        # Check if user registered custom filters
        custom = context.get("__filters__", {})
        fn = custom.get(name)
        if fn is None:
            raise NameError(f"Unknown filter: {name}")

    args = [_eval_filter_arg(a, context) for a in raw_args]
    kwargs = {k: _eval_filter_arg(v, context) for k, v in raw_kwargs.items()}

    return fn(value, *args, **kwargs)


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------

def _render_nodes(
    nodes: list,
    context: dict[str, Any],
    *,
    annotate: bool = False,
    _var_map: dict[str, str] | None = None,
    _enum_map: dict[str, list[str]] | None = None,
    _type_map: dict[str, str] | None = None,
) -> str:
    """Render AST nodes to string.

    Args:
        nodes: AST node list.
        context: Template variable context.
        annotate: If True, wrap rendered values with internal anchor links
            that point to the Specification section at the bottom.
        _var_map: Internal — maps loop variable names to their schema
            property path (e.g. ``{"a": "attendees"}``).
        _enum_map: Maps property paths to their enum values for CSS styling.
        _type_map: Maps property paths to their JSON Schema type string
            (e.g. ``"integer"``, ``"boolean"``, ``"enum"``). Used to emit
            ``data-kata-type`` on annotated spans so the extractor can
            restore the original data type.
    """
    if _var_map is None:
        _var_map = {}
    if _enum_map is None:
        _enum_map = {}
    if _type_map is None:
        _type_map = {}
    parts: list[str] = []
    for node in nodes:
        if isinstance(node, _TextNode):
            parts.append(node.text)

        elif isinstance(node, _VarNode):
            value = _eval_expr(node.expr, context)
            rendered = "" if value is None else str(value)

            if annotate and rendered:
                prop = _expr_to_prop_path(node.expr, _var_map)
                # Skip annotation inside HTML attributes (e.g. class="kata-badge-{{ status }}")
                in_attr = _is_inside_html_attr("".join(parts))
                if prop and not in_attr:
                    anchor = _prop_to_anchor(prop)
                    # Sanitize values for safe embedding in data-kata spans:
                    # - html.escape: < > & → entities (prevent XSS, fix extract)
                    # - pipe escape: | → &#124; (prevent Markdown table breakage)
                    safe_val = html.escape(rendered, quote=False).replace("|", "&#124;")
                    # Strip array index from prop and dash-normalize so the
                    # lookup key matches enum_map / type_map (both of which
                    # store dash-normalized keys, matching _prop_to_anchor).
                    # Without underscore → dash, schema properties like
                    # "duration_sec" never resolve their type hint.
                    base_prop = re.sub(
                        r"-\d+-", "-", re.sub(r"-\d+$", "", prop),
                    ).replace("_", "-")
                    attrs = ""
                    # data-kata-type: emitted so the extractor can coerce
                    # integer/boolean/number values back from textContent.
                    # "string" is omitted because it's the default.
                    kata_type = _type_map.get(base_prop)
                    if kata_type and kata_type != "string":
                        attrs += f' data-kata-type="{kata_type}"'
                    # data-kata-enum: retained for CSS styling (value-based
                    # selectors like [data-kata-enum="done"]). Emitted only
                    # when the rendered value is one of the schema's enum
                    # choices.
                    if base_prop in _enum_map and rendered in _enum_map[base_prop]:
                        attrs += f' data-kata-enum="{html.escape(rendered, quote=True)}"'
                    parts.append(f'<span data-kata="{anchor}"{attrs}>{safe_val}</span>')
                else:
                    parts.append(rendered)
            else:
                parts.append(rendered)

        elif isinstance(node, _ForNode):
            iterable = _eval_expr(node.iterable_expr, context)
            if iterable:
                items = list(iterable)
                # Build child var_map for loop variable → array property
                child_var_map = dict(_var_map)
                arr_prop = _expr_to_prop_path(
                    node.iterable_expr, _var_map, is_iterable=True,
                )
                if arr_prop and len(node.var_names) == 1:
                    child_var_map[node.var_names[0]] = arr_prop

                for i, item in enumerate(items):
                    child_ctx = dict(context)
                    # Build per-iteration var_map with array index
                    iter_var_map = dict(child_var_map)
                    if arr_prop and len(node.var_names) == 1:
                        iter_var_map[node.var_names[0]] = f"{arr_prop}-{i}"
                    if len(node.var_names) == 1:
                        child_ctx[node.var_names[0]] = item
                    else:
                        # Tuple unpacking
                        if isinstance(item, (list, tuple)):
                            for j, vn in enumerate(node.var_names):
                                child_ctx[vn] = item[j] if j < len(item) else None
                        elif isinstance(item, dict) and len(node.var_names) == 2:
                            # dict iteration: key, value
                            keys = list(item.keys()) if isinstance(iterable, dict) else None
                            if keys is None:
                                child_ctx[node.var_names[0]] = item
                            else:
                                child_ctx[node.var_names[0]] = item
                    # loop variable (Jinja2 compatible)
                    child_ctx["loop"] = {
                        "index": i + 1,
                        "index0": i,
                        "first": i == 0,
                        "last": i == len(items) - 1,
                        "length": len(items),
                        "revindex": len(items) - i,
                        "revindex0": len(items) - i - 1,
                    }
                    parts.append(_render_nodes(
                        node.body, child_ctx,
                        annotate=annotate, _var_map=iter_var_map,
                        _enum_map=_enum_map, _type_map=_type_map,
                    ))
            elif node.else_body:
                parts.append(_render_nodes(
                    node.else_body, context,
                    annotate=annotate, _var_map=_var_map,
                    _enum_map=_enum_map, _type_map=_type_map,
                ))

        elif isinstance(node, _IfNode):
            rendered = False
            for condition, body in node.branches:
                if _eval_expr(condition, context):
                    parts.append(_render_nodes(
                        body, context,
                        annotate=annotate, _var_map=_var_map,
                        _enum_map=_enum_map, _type_map=_type_map,
                    ))
                    rendered = True
                    break
            if not rendered and node.else_body:
                parts.append(_render_nodes(
                    node.else_body, context,
                    annotate=annotate, _var_map=_var_map,
                    _enum_map=_enum_map, _type_map=_type_map,
                ))

        elif isinstance(node, _SetNode):
            # Mutate the context in place so the binding survives for
            # subsequent sibling nodes in this block. set-defined names
            # are registered in _var_map with a ``None`` sentinel so
            # that any {{ name.x }} reference resolves to an empty
            # schema path in _expr_to_prop_path — i.e. the rendered
            # value is emitted as raw text, never wrapped in a
            # data-kata span. This is what makes cross-referencing
            # (e.g. resolving a speaker inside a cuts loop) safe for
            # extract: derived displays do not inflate the source array.
            context[node.name] = _eval_expr(node.expr, context)
            _var_map[node.name] = None  # None => "do not annotate"

    return "".join(parts)


# ---------------------------------------------------------------------------
# Annotation helpers
# ---------------------------------------------------------------------------

def _expr_to_prop_path(
    expr: str,
    var_map: dict[str, str | None],
    *,
    is_iterable: bool = False,
) -> str:
    """Derive a schema property path from a template expression.

    Args:
        expr: Template expression (e.g. "title", "a.name", "items | upper").
        var_map: Maps names to either a schema path (``"attendees-0"``)
            or ``None``. A ``None`` entry marks a name as non-annotatable
            (e.g. variables assigned via ``{% set %}``); any reference
            resolves to the empty string so the caller skips annotation.
        is_iterable: If True, the expr is used as a for-loop iterable.

    Returns:
        Property path string (e.g. "title", "attendees-name") or "" to skip.
    """
    expr = expr.strip()

    # Strip filters
    if "|" in expr:
        expr = _split_filters(expr)[0].strip()

    if not expr:
        return ""

    # Skip literals and internal vars
    if expr.startswith(("'", '"')):
        return ""
    if expr in ("loop", "true", "false", "none", "True", "False", "None"):
        return ""
    if expr.startswith("loop."):
        return ""

    parts = expr.split(".")
    root = parts[0]

    # For iterable expressions, just return the root property name
    if is_iterable:
        if root in var_map:
            mapped = var_map[root]
            if mapped is None:
                return ""
            return mapped + "-" + ".".join(parts[1:]) if len(parts) > 1 else mapped
        return root

    # Check if root is a loop variable or a local (set) binding
    if root in var_map:
        arr_prop = var_map[root]
        # ``None`` sentinel means "do not annotate" — used for {% set %}
        if arr_prop is None:
            return ""
        if len(parts) > 1:
            return arr_prop + "-" + "-".join(parts[1:])
        # Bare loop var reference (the element itself) — skip
        return ""

    return "-".join(parts) if len(parts) > 1 else root


def _is_inside_html_attr(text: str) -> bool:
    """Check if the end of *text* is inside an HTML attribute value.

    Detects patterns like ``class="kata-badge-`` where a quote is open
    but not yet closed, meaning the next template variable output would
    land inside an HTML attribute and should NOT be annotated.
    """
    last_lt = text.rfind("<")
    if last_lt == -1:
        return False
    last_gt = text.rfind(">")
    if last_gt > last_lt:
        return False  # Tag is closed
    tag_fragment = text[last_lt:]
    double_count = tag_fragment.count('"')
    single_count = tag_fragment.count("'")
    return (double_count % 2 == 1) or (single_count % 2 == 1)


def _prop_to_anchor(prop: str) -> str:
    """Convert a property path to an HTML anchor ID.

    "title" → "p-title"
    "attendees-name" → "p-attendees-name"
    """
    return "p-" + prop.replace(".", "-").replace("_", "-")


def _collect_enum_map(
    schema: dict[str, Any] | None,
    prefix: str = "",
) -> dict[str, list[str]]:
    """Build a map of property paths to their enum values from a schema.

    Returns e.g. ``{"status": ["todo", "done"], "items-status": ["todo", "done"]}``.
    The keys use the same dash-separated format as ``data-kata`` anchors (without "p-").
    """
    if schema is None:
        return {}
    result: dict[str, list[str]] = {}
    props = schema.get("properties", {})
    for raw_key, prop_schema in props.items():
        # Normalize keys to the dash-separated anchor form (see
        # _prop_to_anchor) so lookups by anchor-derived ``base_prop``
        # hit correctly for schema keys containing underscores.
        key = raw_key.replace("_", "-")
        path = f"{prefix}{key}" if not prefix else f"{prefix}-{key}"
        enum_vals = prop_schema.get("enum")
        if enum_vals:
            result[path] = [str(v) for v in enum_vals]
        # Recurse into nested objects
        if prop_schema.get("type") == "object" and "properties" in prop_schema:
            result.update(_collect_enum_map(prop_schema, path + "-"))
        # Recurse into array items
        items_schema = prop_schema.get("items")
        if items_schema and isinstance(items_schema, dict):
            if "properties" in items_schema:
                result.update(_collect_enum_map(items_schema, path))
            elif items_schema.get("enum"):
                result[path] = [str(v) for v in items_schema["enum"]]


    return result


def _collect_type_map(
    schema: dict[str, Any] | None,
    prefix: str = "",
) -> dict[str, str]:
    """Build a map of property paths to their JSON Schema ``type`` string.

    Lets the annotator emit ``data-kata-type`` so the extractor can
    recover numeric/boolean fields without the round-trip collapsing
    them to strings. Paths use the same dash-separated anchor format
    as ``_collect_enum_map`` (without the ``p-`` prefix).

    Properties with an ``enum`` constraint are mapped to ``"enum"``
    regardless of their underlying JSON Schema type, so the extractor
    (and CSS) can treat them uniformly.
    """
    if schema is None:
        return {}
    result: dict[str, str] = {}
    props = schema.get("properties", {})
    for raw_key, prop_schema in props.items():
        # Anchors and base_prop keys are dash-normalized
        # (see _prop_to_anchor), so the type_map key must be normalized
        # too — otherwise a schema key like "duration_sec" never matches
        # the base_prop "cuts-duration-sec" derived from the anchor.
        key = raw_key.replace("_", "-")
        path = f"{prefix}{key}" if not prefix else f"{prefix}-{key}"
        type_val = prop_schema.get("type")
        if prop_schema.get("enum"):
            result[path] = "enum"
        elif isinstance(type_val, str):
            result[path] = type_val
        # Recurse into nested objects
        if type_val == "object" and "properties" in prop_schema:
            result.update(_collect_type_map(prop_schema, path + "-"))
        # Recurse into array items
        items_schema = prop_schema.get("items")
        if items_schema and isinstance(items_schema, dict):
            if "properties" in items_schema:
                result.update(_collect_type_map(items_schema, path))
            elif items_schema.get("enum"):
                result[path] = "enum"
            else:
                item_type = items_schema.get("type")
                if isinstance(item_type, str):
                    # Scalar-array items: expose the element type so each
                    # rendered span carries it (e.g. integer list -> each
                    # element gets data-kata-type="integer").
                    result[path] = item_type
    return result


# ---------------------------------------------------------------------------
# Enum color schemes
# ---------------------------------------------------------------------------

# Each scheme maps semantic enum values to (background, foreground) colors.
# Schemes are selected via colorScheme in the Style block, or default.

# Color palettes derived from Chart Banana theme system (gospelo-chart-banana).
# Each scheme uses semantic roles: positive → done/approved/yes,
# negative → rejected/no/high, neutral → todo/draft/inactive,
# warning → pending/medium/in-progress.

def _build_scheme(
    positive: tuple[str, str],
    negative: tuple[str, str],
    neutral: tuple[str, str],
    warning: tuple[str, str],
) -> dict[str, tuple[str, str]]:
    """Build an enum color scheme from 4 semantic color pairs (bg, fg)."""
    return {
        # positive — completed / success
        "done": positive, "approved": positive, "approve": positive,
        "pass": positive, "yes": positive, "true": positive,
        "active": positive, "ok": positive, "OK": positive,
        "full": positive,
        # negative — failure / danger / high-severity
        "rejected": negative, "reject": negative, "fail": negative,
        "no": negative, "false": negative, "error": negative,
        "high": negative, "HIGH": negative,
        "critical": negative, "CRITICAL": negative,
        "ng": negative, "NG": negative, "ERROR": negative,
        "cancelled": negative,
        # neutral — action needed / informational
        "todo": neutral, "draft": neutral, "inactive": neutral,
        "closed": neutral, "low": neutral, "LOW": neutral,
        "skip": neutral, "info": neutral, "INFO": neutral,
        "manual": neutral, "partial": neutral,
        # warning — in-progress / medium-severity
        "pending": warning, "medium": warning, "MEDIUM": warning,
        "in_progress": warning, "in-progress": warning,
        "open": warning, "semi": warning,
    }

# 浅葱 Asagi — Clear light blue (Chart Banana: asagi, pure_white)
# done=低彩度(完了感), todo=高彩度(アクション要)
_ENUM_SCHEME_DEFAULT = _build_scheme(
    positive=("#e8ecea", "#6b7d75"),   # desaturated sage — finished, faded
    negative=("#fde0d4", "#a33a12"),   # 紅緋 tint
    neutral=("#b0e4ea", "#0e5f6a"),    # 浅葱 stronger — active, needs attention
    warning=("#fff3d4", "#8a6b00"),    # 山吹 tint
)

# Jelly Mint — Fresh translucent green (Chart Banana: jelly_mint, pure_white)
_ENUM_SCHEME_PASTEL = _build_scheme(
    positive=("#eaefec", "#7a8a80"),   # muted sage — done, settled
    negative=("#f8e0dd", "#9e4a40"),   # dusty rose tint
    neutral=("#a8e6c4", "#1a5c3a"),    # mint stronger — todo, fresh action
    warning=("#fce8d5", "#8a5a30"),    # warm peach tint
)

# Vivid Gradient — Bold purple & cyan (Chart Banana: vivid, pure_white)
_ENUM_SCHEME_VIVID = _build_scheme(
    positive=("#b0b8b6", "#3a3a3a"),   # muted gray-green — done, subdued
    negative=("#D63031", "#ffffff"),   # red solid
    neutral=("#00CEC9", "#ffffff"),    # cyan solid — todo, eye-catching
    warning=("#6C5CE7", "#ffffff"),    # purple solid
)

# 墨 Sumi-ink — Monochrome with vermillion (Chart Banana: sumi, shironeri)
_ENUM_SCHEME_MONOCHROME = _build_scheme(
    positive=("#D0D0D0", "#3a3a3a"),   # light ink wash — done, faded
    negative=("#CB1B45", "#ffffff"),   # 紅 kurenai
    neutral=("#1C1C1C", "#ffffff"),    # 墨 sumi — todo, bold
    warning=("#717171", "#ffffff"),    # medium ink
)

# Blue Aura — Calming blue-gray (Chart Banana: blue_aura, pure_white)
_ENUM_SCHEME_OCEAN = _build_scheme(
    positive=("#e8e9ed", "#6a6c73"),   # cool muted gray — done, settled
    negative=("#f8ddd4", "#9c4a35"),   # terracotta tint
    neutral=("#a8cfe0", "#1a3d55"),    # blue aura stronger — todo, active
    warning=("#e4ecf2", "#3d6580"),    # light blue aura
)

ENUM_COLOR_SCHEMES: dict[str, dict[str, tuple[str, str]]] = {
    "default": _ENUM_SCHEME_DEFAULT,
    "pastel": _ENUM_SCHEME_PASTEL,
    "vivid": _ENUM_SCHEME_VIVID,
    "monochrome": _ENUM_SCHEME_MONOCHROME,
    "ocean": _ENUM_SCHEME_OCEAN,
}


def _resolve_color_scheme(style: dict[str, Any] | None) -> str:
    """Read colorScheme from Style block, falling back to 'default'."""
    if style is None:
        return "default"
    name = style.get("colorScheme", "default")
    if name in ENUM_COLOR_SCHEMES:
        return name
    return "default"


def _resolve_enum_overrides(
    style: dict[str, Any] | None,
    color_scheme: str,
) -> dict[str, tuple[str, str]]:
    """Build enum color overrides from Style block's enumColors.

    enumColors maps field names to dicts of {value: semantic_role}.
    Semantic roles: positive, negative, neutral, warning.

    Returns:
        Dict mapping enum value → (bg, fg) color pair.
    """
    if style is None:
        return {}
    enum_colors = style.get("enumColors")
    if not isinstance(enum_colors, dict):
        return {}
    palette = ENUM_COLOR_SCHEMES.get(color_scheme, _ENUM_SCHEME_DEFAULT)
    # Collect the 4 semantic base colors from palette
    semantic = {
        "positive": palette.get("done", palette.get("pass", ("#e8ecea", "#6b7d75"))),
        "negative": palette.get("fail", palette.get("rejected", ("#fde0d4", "#a33a12"))),
        "neutral": palette.get("todo", palette.get("draft", ("#b0e4ea", "#0e5f6a"))),
        "warning": palette.get("pending", palette.get("medium", ("#fff3d4", "#8a6b00"))),
    }
    overrides: dict[str, tuple[str, str]] = {}
    for _field, mapping in enum_colors.items():
        if isinstance(mapping, dict):
            for value, role in mapping.items():
                if isinstance(role, str) and role in semantic:
                    overrides[str(value)] = semantic[role]
    return overrides


def _generate_enum_css(
    enum_map: dict[str, list[str]],
    color_scheme: str = "default",
    style: dict[str, Any] | None = None,
) -> list[str]:
    """Generate CSS rules for enum-valued data-kata spans."""
    lines: list[str] = []
    # Collect unique enum values across all properties
    seen_values: set[str] = set()
    for values in enum_map.values():
        for v in values:
            if v not in seen_values:
                seen_values.add(v)
    if not seen_values:
        return lines
    # Base style for all enum spans
    lines.append("[data-kata-enum] { display: inline-block; padding: 1px 6px; border-radius: 4px; font-size: 0.9em; }")
    palette = ENUM_COLOR_SCHEMES.get(color_scheme, _ENUM_SCHEME_DEFAULT)
    overrides = _resolve_enum_overrides(style, color_scheme)
    for val in sorted(seen_values):
        safe_val = val.replace('"', '\\"')
        # User overrides take precedence
        colors = overrides.get(val) or palette.get(val.lower())
        if colors:
            bg, fg = colors
            lines.append(f'[data-kata-enum="{safe_val}"] {{ background: {bg}; color: {fg}; }}')
    return lines


# ---------------------------------------------------------------------------
# Specification section generator
# ---------------------------------------------------------------------------

_ANNOTATION_PROP_PATTERN = re.compile(r'<span\s+data-kata="p-[a-z0-9-]+">([^<]*)</span>')
_ANNOTATION_LINK_PATTERN = re.compile(r"\[([^\]]*)\]\(#p-[a-z0-9-]+\)")


_STRUCTURE_INTEGRITY_PATTERN = re.compile(
    r"<!-- kata-structure-integrity: sha256:([0-9a-f]{64}) -->"
)


def _compute_structure_hash(details_text: str) -> str:
    """Compute SHA-256 hash of the structure portion of a <details> section.

    The hash covers Prompt, kata:template, and Schema blocks but excludes
    the Data block entirely.  This allows data to change freely while
    detecting any tampering of the template structure.

    Args:
        details_text: The content between ``<details>`` and ``</details>`` tags.

    Returns:
        Hex-encoded SHA-256 hash string.
    """
    import hashlib
    # Remove the **Data** block (from "**Data**" to end of its code block)
    cleaned = re.sub(
        r"\*\*Data\*\*\s*\n\s*```(?:yaml|json)\n.*?\n```",
        "",
        details_text,
        flags=re.DOTALL,
    )
    # Normalize whitespace for stable hashing
    cleaned = "\n".join(line.rstrip() for line in cleaned.strip().splitlines())
    return hashlib.sha256(cleaned.encode("utf-8")).hexdigest()


def generate_schema_reference(
    schema: dict[str, Any],
    data: dict[str, Any] | None = None,
    prompt: str | None = None,
    template_body: str | None = None,
    style: dict[str, Any] | None = None,
) -> str:
    """Generate a Specification section from a JSON Schema.

    The generated Markdown is wrapped in a ``<details>`` tag and contains
    Prompt, template body, Schema, Style, and Data blocks — everything needed
    to reconstruct or re-render the document from a single file.

    A structure integrity hash is embedded as an HTML comment before
    ``</details>``.  The hash covers Prompt, kata:template, Schema, and
    Style blocks but excludes the Data block, allowing data changes without
    invalidating the hash.

    Args:
        schema: JSON Schema dict.
        data: Optional data dict to include as a Data section.
        prompt: Optional prompt text to include.
        template_body: Optional template source to include.
        style: Optional style dict (colorScheme, enumColors).

    Returns:
        Markdown string for the Specification section.
    """
    lines: list[str] = []
    lines.append("")
    # Inline style to prevent table horizontal overflow in Markdown previews.
    lines.append("<style>")
    lines.append("table { table-layout: fixed; width: 100%; display: table !important; overflow: visible !important; }")
    lines.append("table th, table td { overflow-wrap: break-word; word-break: break-word; vertical-align: top; }")
    lines.append(".markdown-preview { max-width: 100% !important; padding-left: 2em !important; padding-right: 2em !important; }")
    # Add enum styling rules if schema contains enum properties
    enum_map = _collect_enum_map(schema)
    color_scheme = _resolve_color_scheme(style)
    enum_css = _generate_enum_css(enum_map, color_scheme, style=style)
    for rule in enum_css:
        lines.append(rule)
    lines.append("</style>")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("<details>")
    lines.append("<summary>Specification</summary>")
    lines.append("")

    if prompt is not None:
        lines.append("**Prompt**")
        lines.append("")
        lines.append("```yaml")
        lines.append(prompt)
        lines.append("```")
        lines.append("")

    if template_body is not None:
        lines.append("**Template**")
        lines.append("")
        lines.append("```kata:template")
        lines.append(template_body.rstrip("\n"))
        lines.append("```")
        lines.append("")

    lines.append("**Schema**")
    lines.append("")
    lines.append("```yaml")
    _schema_to_shorthand(schema, "", lines)
    lines.append("```")
    lines.append("")

    # Compute structure integrity hash (Specification only)
    details_inner = "\n".join(lines[lines.index("<details>") + 2 :])
    integrity_hash = _compute_structure_hash(details_inner)
    lines.append(f"<!-- kata-structure-integrity: sha256:{integrity_hash} -->")
    lines.append("</details>")
    lines.append("")

    # Style block — separate <details>, user-editable
    if style:
        lines.append(generate_style_section(style))

    if data is not None:
        lines.append(generate_data_section(data))

    return "\n".join(lines)


def generate_data_section(data: dict[str, Any]) -> str:
    """Generate a separate Data section wrapped in ``<details>``."""
    lines: list[str] = []
    lines.append("<details>")
    lines.append("<summary>Data</summary>")
    lines.append("")
    lines.append("```yaml")
    try:
        import yaml
        lines.append(yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False).rstrip())
    except ImportError:
        lines.append(json.dumps(data, indent=2, ensure_ascii=False))
    lines.append("```")
    lines.append("")
    lines.append("</details>")
    return "\n".join(lines)


def generate_style_section(style: dict[str, Any]) -> str:
    """Generate a separate Style section wrapped in ``<details>``."""
    lines: list[str] = []
    lines.append("<details>")
    lines.append("<summary>Style</summary>")
    lines.append("")
    lines.append("```yaml")
    try:
        import yaml
        lines.append(yaml.dump(
            style, allow_unicode=True,
            default_flow_style=False, sort_keys=False,
        ).rstrip())
    except ImportError:
        lines.append(json.dumps(style, indent=2, ensure_ascii=False))
    lines.append("```")
    lines.append("")
    lines.append("</details>")
    return "\n".join(lines)


def _emit_hidden_anchors(
    schema: dict[str, Any],
    prefix: str,
    lines: list[str],
) -> None:
    """Emit hidden anchor spans for internal link targets (data-kata → #p-xxx)."""
    props = schema.get("properties", {})
    for key, prop_schema in props.items():
        prop_path = f"{prefix}-{key}" if prefix else key
        anchor = _prop_to_anchor(prop_path)
        lines.append(f'<a id="{anchor}"></a>')

        prop_type = prop_schema.get("type", "any")
        if prop_type == "object":
            _emit_hidden_anchors(prop_schema, prop_path, lines)
        if prop_type == "array":
            items_schema = prop_schema.get("items", {})
            if isinstance(items_schema, dict) and "properties" in items_schema:
                _emit_hidden_anchors(items_schema, prop_path, lines)
    if lines and lines[-1] != "":
        lines.append("")


def _schema_to_shorthand(
    schema: dict[str, Any],
    indent: str,
    lines: list[str],
) -> None:
    """Convert JSON Schema to YAML shorthand notation for code block output."""
    props = schema.get("properties", {})
    required = set(schema.get("required", []))

    for key, prop_schema in props.items():
        prop_type = prop_schema.get("type", "any")
        req = "!" if key in required else ""

        if prop_type == "array":
            items_schema = prop_schema.get("items", {})
            if isinstance(items_schema, dict) and "properties" in items_schema:
                lines.append(f"{indent}{key}[]{req}:")
                _schema_to_shorthand(items_schema, indent + "  ", lines)
            elif isinstance(items_schema, dict) and "type" in items_schema:
                lines.append(f"{indent}{key}: {items_schema['type']}[]{req}")
            else:
                lines.append(f"{indent}{key}: string[]{req}")
        elif prop_type == "object" and "properties" in prop_schema:
            lines.append(f"{indent}{key}{req}:")
            _schema_to_shorthand(prop_schema, indent + "  ", lines)
        else:
            enum_vals = prop_schema.get("enum")
            if enum_vals:
                lines.append(f"{indent}{key}: enum({', '.join(str(v) for v in enum_vals)}){req}")
            else:
                lines.append(f"{indent}{key}: {prop_type}{req}")


def _walk_schema_props(
    schema: dict[str, Any],
    prefix: str,
    lines: list[str],
) -> None:
    """Recursively walk schema properties and emit anchor headings.

    Legacy format kept for backward compatibility with extract.py
    which parses Specification sections.
    """
    props = schema.get("properties", {})
    required = set(schema.get("required", []))

    for key, prop_schema in props.items():
        prop_path = f"{prefix}-{key}" if prefix else key
        anchor = _prop_to_anchor(prop_path)
        prop_type = prop_schema.get("type", "any")

        req_mark = " **(required)**" if key in required else ""
        lines.append(f'#### <a id="{anchor}"></a>{prop_path}')
        lines.append(f"- **type**: {prop_type}{req_mark}")

        # Enum
        if "enum" in prop_schema:
            lines.append(f"- **enum**: {prop_schema['enum']}")

        # String constraints
        if "minLength" in prop_schema:
            lines.append(f"- **minLength**: {prop_schema['minLength']}")

        # Description
        if "description" in prop_schema:
            lines.append(f"- {prop_schema['description']}")

        lines.append("")

        # Recurse into object properties
        if prop_type == "object":
            _walk_schema_props(prop_schema, prop_path, lines)

        # Recurse into array items if they have properties
        if prop_type == "array":
            items_schema = prop_schema.get("items", {})
            if isinstance(items_schema, dict) and "properties" in items_schema:
                _walk_schema_props(items_schema, prop_path, lines)


# ---------------------------------------------------------------------------
# Schema section generator (for embedding in templates)
# ---------------------------------------------------------------------------

def generate_schema_section(
    schema: dict[str, Any],
    *,
    section_map: dict[str, str] | None = None,
) -> str:
    """Generate a Schema section with bidirectional links for .kata.md templates.

    Produces Markdown like::

        - [#p-title](#u-title) (string, required)
          Meeting title
          Used as document heading

    Args:
        schema: JSON Schema dict.
        section_map: Optional mapping from top-level property name to
            ``u-`` anchor name (section ID). If not provided, each
            top-level property maps to ``u-{prop_name}``.

    Returns:
        Markdown string for the Schema section body (without <details> wrapper).
    """
    lines: list[str] = []
    _walk_schema_section(schema, "", lines, depth=0, section_map=section_map or {})
    return "\n".join(lines)


def _walk_schema_section(
    schema: dict[str, Any],
    prefix: str,
    lines: list[str],
    *,
    depth: int = 0,
    section_map: dict[str, str] | None = None,
) -> None:
    """Recursively walk schema properties and emit bidirectional link list items."""
    props = schema.get("properties", {})
    required = set(schema.get("required", []))
    indent = "  " * depth

    for key, prop_schema in props.items():
        prop_path = f"{prefix}-{key}" if prefix else key
        anchor = _prop_to_anchor(prop_path)
        prop_type = prop_schema.get("type", "any")

        # Determine u- target
        norm_path = prop_path.replace("_", "-")
        if section_map and prop_path in section_map:
            u_target = section_map[prop_path]
        elif prefix and section_map:
            # Child property: link to parent section
            top_key = prefix.split("-")[0] if "-" in prefix else prefix
            u_target = section_map.get(top_key, f"u-{top_key.replace('_', '-')}")
        elif prefix:
            top_key = prefix.split("-")[0] if "-" in prefix else prefix
            u_target = f"u-{top_key.replace('_', '-')}"
        else:
            u_target = f"u-{norm_path}"

        # Type info
        req_mark = ", required" if key in required else ""
        enum_info = ""
        if "enum" in prop_schema:
            enum_info = ", enum: " + "/".join(str(e) for e in prop_schema["enum"])

        lines.append(f"{indent}- [#{anchor}](#{u_target}) ({prop_type}{req_mark}{enum_info})")

        # Description (may contain \n for multi-line)
        desc = prop_schema.get("description", "")
        if desc:
            for desc_line in desc.split("\n"):
                lines.append(f"{indent}  {desc_line}")

        # Recurse into object properties
        if prop_type == "object" and "properties" in prop_schema:
            _walk_schema_section(prop_schema, prop_path, lines, depth=depth + 1, section_map=section_map)

        # Recurse into array items if they have properties
        if prop_type == "array":
            items_schema = prop_schema.get("items", {})
            if isinstance(items_schema, dict) and "properties" in items_schema:
                _walk_schema_section(items_schema, prop_path, lines, depth=depth + 1, section_map=section_map)

        # Recurse into array items
        elif prop_type == "array" and "items" in prop_schema:
            items_schema = prop_schema["items"]
            if items_schema.get("type") == "object":
                _walk_schema_props(items_schema, prop_path, lines)


def strip_annotations(text: str) -> str:
    """Remove annotation links from rendered Markdown.

    Converts ``[value](#p-title)`` back to plain ``value``.
    Also removes the Specification section at the bottom.

    Args:
        text: Annotated Markdown text.

    Returns:
        Clean Markdown without annotation links or Specification.
    """
    # Remove annotations (data-kata spans and legacy links)
    cleaned = _ANNOTATION_PROP_PATTERN.sub(r"\1", text)
    cleaned = _ANNOTATION_LINK_PATTERN.sub(r"\1", cleaned)

    # Remove Specification section
    # Matches: ---\n\n<details>\n<summary>Specification</summary>\n...\n</details>\n
    ref_pattern = re.compile(
        r"\n---\n\n<details>\s*\n<summary>Specification</summary>\n.*?</details>\n?",
        re.DOTALL,
    )
    cleaned = ref_pattern.sub("", cleaned)

    return cleaned


# Handle dict iteration for {% for k, v in dict.items() %} or {% for k, v in dict | items %}
_orig_for_render = None  # placeholder


def _fix_dict_iteration(node: _ForNode, context: dict[str, Any]) -> list:
    """Handle dict iteration, converting to list of tuples."""
    iterable = _eval_expr(node.iterable_expr, context)
    if isinstance(iterable, dict) and len(node.var_names) == 2:
        return list(iterable.items())
    return list(iterable) if iterable else []


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class Template:
    """Jinja2 3.1.6 compatible template (subset).

    Supports variable interpolation, for loops, conditionals, filters,
    and optional embedded JSON Schema via {#schema ... #} annotation.
    """

    def __init__(self, source: str, template_path: str | None = None):
        self.source = source
        self.template_path = template_path
        self.schema, cleaned = extract_schema(source, template_path)
        self.style: dict[str, Any] | None = None
        # Extract prompt block (for AI assistants) and strip from template
        prompt_match = _PROMPT_PATTERN.search(cleaned)
        if not prompt_match:
            prompt_match = _PROMPT_CODEBLOCK_PATTERN.search(cleaned)
        self.prompt = prompt_match.group(1) if prompt_match else None
        cleaned = _PROMPT_PATTERN.sub("", cleaned)
        cleaned = _PROMPT_CODEBLOCK_PATTERN.sub("", cleaned).lstrip("\n")
        # Extract data block (embedded YAML data) and strip from template
        self.data = extract_data(cleaned)
        cleaned = _DATA_PATTERN.sub("", cleaned)
        cleaned = _DATA_BOLD_CODEBLOCK_PATTERN.sub("", cleaned).lstrip("\n")
        # Strip <details> wrapper (used in template files) before tokenizing
        cleaned = re.sub(
            r"<details>\s*<summary>Specification</summary>.*?</details>\s*",
            "", cleaned, flags=re.DOTALL,
        ).rstrip("\n")
        self.template_body = cleaned
        tokens = _tokenize(cleaned)
        self._ast = _parse(tokens)

    def render(self, **kwargs: Any) -> str:
        """Render the template with given variables."""
        body = _render_nodes(self._ast, kwargs)
        if self.schema is not None and "#p-" in body:
            body += generate_schema_reference(
                self.schema,
                prompt=self.prompt,
                template_body=self.template_body,
                style=self.style,
            )
        return body

    def render_dict(self, data: dict[str, Any]) -> str:
        """Render the template with a data dictionary.

        If the rendered output contains internal links (``#p-``) and a schema
        is embedded, a Specification section is automatically appended.
        """
        body = _render_nodes(self._ast, data)
        if self.schema is not None and "#p-" in body:
            body += generate_schema_reference(
                self.schema,
                data=self.data,
                prompt=self.prompt,
                template_body=self.template_body,
                style=self.style,
            )
        return body

    def render_annotated(self, data: dict[str, Any]) -> str:
        """Render with schema annotation links and Specification section.

        Each rendered value is wrapped as ``[value](#p-property)`` linking
        to the corresponding anchor in a Specification section appended
        at the bottom of the document.

        If no schema is embedded, falls back to plain render_dict.
        """
        enum_map = _collect_enum_map(self.schema) if self.schema else {}
        type_map = _collect_type_map(self.schema) if self.schema else {}
        body = _render_nodes(
            self._ast, data, annotate=True,
            _enum_map=enum_map, _type_map=type_map,
        )
        if self.schema is not None:
            body += generate_schema_reference(
                self.schema,
                data=self.data,
                prompt=self.prompt,
                template_body=self.template_body,
                style=self.style,
            )
        return body

    def render_self(self, *, annotate: bool = False) -> str:
        """Render the template using its embedded {#data} block.

        Args:
            annotate: If True, render with schema annotation links.

        Returns:
            Rendered string.

        Raises:
            ValueError: If no {#data} block is embedded.
        """
        if self.data is None:
            raise ValueError("No {#data} block found in template")
        if annotate:
            return self.render_annotated(self.data)
        return self.render_dict(self.data)

    def validate(self, data: dict[str, Any]) -> "ValidationResult | None":
        """Validate data against embedded schema, if present.

        Returns ValidationResult or None if no schema is embedded.
        """
        if self.schema is None:
            return None
        from .validator import validate
        return validate(data, self.schema, schema_name="embedded")


class ValidationResult:
    """Placeholder for type hint — actual class is in validator.py."""
    pass


def render_template(source: str, data: dict[str, Any]) -> str:
    """One-shot: parse and render a template string with data."""
    tpl = Template(source)
    return tpl.render_dict(data)


def render_file(
    template_path: str,
    data: dict[str, Any],
    *,
    validate: bool = True,
    annotate: bool = False,
) -> str:
    """Load a .kata.md template file, optionally validate data, and render.

    Args:
        template_path: Path to the .kata.md template file.
        data: Data dictionary to render with.
        validate: If True and schema is embedded, validate data first.
        annotate: If True, render with schema annotation links and
            append a Specification section at the bottom.

    Returns:
        Rendered string.

    Raises:
        ValueError: If validation fails.
    """
    from pathlib import Path
    path = Path(template_path)
    source = path.read_text(encoding="utf-8")
    tpl = Template(source, template_path=str(path))

    if validate and tpl.schema is not None:
        from .validator import validate as do_validate
        result = do_validate(data, tpl.schema, schema_name=path.name)
        if not result.valid:
            raise ValueError(result.summary())

    if annotate:
        return tpl.render_annotated(data)
    return tpl.render_dict(data)


_KATA_TEMPLATE_RE = re.compile(
    r"```kata:template\n(.*?)```", re.DOTALL
)
_DATA_DETAILS_RE = re.compile(
    r"<details>\s*<summary>Data</summary>\s*```(?:yaml)?\n(.*?)```\s*</details>",
    re.DOTALL,
)


def _is_separated_format(source: str) -> bool:
    """Check if .kata.md uses separated Data <details> format."""
    return bool(_DATA_DETAILS_RE.search(source))


def _extract_data_from_details(source: str) -> dict[str, Any] | None:
    """Extract YAML data from <details>Data</details> section."""
    m = _DATA_DETAILS_RE.search(source)
    if not m:
        return None
    try:
        import yaml
        return yaml.safe_load(m.group(1))
    except Exception:
        return None


def _replace_data_in_source(source: str, new_data: dict[str, Any]) -> str:
    """Replace the Data block in source with new data, preserving structure."""
    import yaml
    new_yaml = yaml.dump(
        new_data, allow_unicode=True, default_flow_style=False, sort_keys=False,
    ).rstrip()
    new_block = (
        "<details>\n<summary>Data</summary>\n\n"
        f"```yaml\n{new_yaml}\n```\n\n</details>"
    )
    return _DATA_DETAILS_RE.sub(new_block, source)


def merge_extracted_into_data(
    old_data: dict[str, Any] | None,
    extracted: dict[str, Any],
) -> dict[str, Any]:
    """Merge LiveMorph-extracted values into the existing Data block.

    LiveMorph (``sync to-data``) gets back only those fields that the
    template actually annotates with ``<span data-kata=...>``. Fields
    that the template renders as raw markup — e.g. ``<img src="..." />``
    attributes or hidden dialogue lines — never come back from extract,
    so replacing the Data block with the raw extract would silently
    destroy information that the user set in the original Data.

    This merges the extract on top of the old Data so that:

    - **Top-level scalars**: extract wins if present; otherwise old is
      kept.
    - **Arrays**: extract dictates the final length and ordering (so
      user-initiated deletes and reorders flow through). Each element
      is merged with the element at the same index in old_data so that
      un-annotated fields on surviving elements survive too.
    - **Nested dicts**: recursed into, same rules apply.
    - If ``old_data`` is ``None`` (e.g. Data block missing or
      unparseable), extract is returned as-is.
    """
    if old_data is None:
        return extracted

    def _merge(old: Any, new: Any) -> Any:
        if isinstance(new, dict) and isinstance(old, dict):
            merged = dict(old)
            for k, v in new.items():
                if k in merged:
                    merged[k] = _merge(merged[k], v)
                else:
                    merged[k] = v
            return merged
        if isinstance(new, list) and isinstance(old, list):
            merged_list = []
            for i, item in enumerate(new):
                if i < len(old):
                    merged_list.append(_merge(old[i], item))
                else:
                    merged_list.append(item)
            # Elements beyond the extract length are dropped — that
            # mirrors a user-initiated delete in the rendered view.
            return merged_list
        # Scalar or type mismatch: extract wins.
        return new

    result = _merge(old_data, extracted)
    if not isinstance(result, dict):
        # Defensive: if the roots aren't both dicts, fall back to
        # extract to avoid returning a non-dict Data block.
        return extracted
    return result


def _extract_kata_template(source: str) -> str | None:
    """Extract template code from ```kata:template block."""
    m = _KATA_TEMPLATE_RE.search(source)
    return m.group(1).rstrip("\n") if m else None


def _extract_style_block(source: str) -> dict[str, Any] | None:
    """Extract Style block from a separate ``<details>Style</details>``."""
    m = re.search(
        r"<details>\s*<summary>Style</summary>\s*```(?:yaml)?\n(.*?)```\s*</details>",
        source, re.DOTALL,
    )
    if not m:
        return None
    try:
        import yaml
        style = yaml.safe_load(m.group(1))
        if isinstance(style, dict):
            return style
    except Exception:
        pass
    return None


def render_kata(
    kata_path: str,
    *,
    validate: bool = True,
    annotate: bool = True,
) -> str:
    """Render a self-contained .kata.md file using its embedded data.

    Supports two formats:
    - **New format**: Data in separate ``<details>Data</details>``,
      template code in ``kata:template`` block. Re-renders from template.
    - **Legacy format**: Data inside ``<details>Specification</details>``.
      Falls back to span-replacement rendering.

    Args:
        kata_path: Path to the .kata.md file.
        validate: If True and schema is embedded, validate data first.
        annotate: If True, render with schema annotation links.

    Returns:
        Rendered string.

    Raises:
        ValueError: If no data block or if validation fails.
    """
    from pathlib import Path as _Path
    path = _Path(kata_path)
    source = path.read_text(encoding="utf-8")

    if _is_separated_format(source):
        # New format: re-render from kata:template + Data <details>
        data = _extract_data_from_details(source)
        if data is None:
            raise ValueError(f"Could not parse Data block in {kata_path}")

        tpl_code = _extract_kata_template(source)
        if tpl_code is None:
            raise ValueError(f"No kata:template block found in {kata_path}")

        # Extract Specification <details> (for schema + prompt)
        schema_ref_match = re.search(
            r"<details>\s*<summary>Specification</summary>(.*?)</details>",
            source, re.DOTALL,
        )
        schema_inner = schema_ref_match.group(1) if schema_ref_match else ""

        # Extract schema from **Schema** block
        schema_yaml_match = re.search(
            r"\*\*Schema\*\*\s*\n\s*```(?:yaml)?\n(.*?)```",
            schema_inner, re.DOTALL,
        )
        schema = None
        if schema_yaml_match:
            schema = _parse_schema_content(schema_yaml_match.group(1))

        # Extract prompt
        prompt_match = re.search(
            r"\*\*Prompt\*\*\s*\n\s*```(?:yaml)?\n(.*?)```",
            schema_inner, re.DOTALL,
        )
        prompt = prompt_match.group(1).rstrip("\n") if prompt_match else None

        # Extract Style block (separate <details>)
        style = _extract_style_block(source)

        if validate and schema is not None:
            from .validator import validate as do_validate
            result = do_validate(data, schema, schema_name=path.name)
            if not result.valid:
                raise ValueError(result.summary())

        # Parse and render template code
        tokens = _tokenize(tpl_code)
        ast = _parse(tokens)

        if annotate:
            enum_map = _collect_enum_map(schema) if schema else {}
            type_map = _collect_type_map(schema) if schema else {}
            body = _render_nodes(
                ast, data, annotate=True,
                _enum_map=enum_map, _type_map=type_map,
            )
            if schema is not None:
                body += generate_schema_reference(
                    schema,
                    prompt=prompt,
                    template_body=tpl_code,
                    data=data,
                    style=style,
                )
        else:
            body = _render_nodes(ast, data)

        return body

    # Legacy format: fall back to Template-based rendering
    tpl = Template(source, template_path=str(path))

    if tpl.data is None:
        raise ValueError(f"No {{#data}} block found in {kata_path}")

    if validate and tpl.schema is not None:
        from .validator import validate as do_validate
        result = do_validate(tpl.data, tpl.schema, schema_name=path.name)
        if not result.valid:
            raise ValueError(result.summary())

    return tpl.render_self(annotate=annotate)
