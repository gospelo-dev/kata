# KATA Markdown™ — gospelo-kata
# Copyright (c) 2025 gospelo. All rights reserved.
# Licensed under the MIT License. See LICENSE.md for details.

"""Extract structured JSON data from rendered .kata.md documents.

Parses data-kata annotations to reconstruct the original JSON data
that was used to generate the document. This enables the reverse flow:

    .kata.md (user edits) → extract → JSON → validate / export

Uses the Specification section (anchor IDs) to resolve the correct
property paths, avoiding ambiguity in dash-separated path parsing.
"""

from __future__ import annotations

import html as _html
import json
import re
from pathlib import Path
from typing import Any

# Match: <span data-kata="p-xxx-yyy" ...>value</span>
# Allows additional attributes (e.g., data-kata-enum, data-kata-type)
# between data-kata and >, captured in the optional attrs group.
_DATA_KATA_PATTERN = re.compile(
    r'<span\s+data-kata="p-([a-z0-9]+(?:-[a-z0-9-]*)*)"'
    r'([^>]*)>([^<]*)</span>'
)
_DATA_KATA_TYPE_ATTR = re.compile(r'\bdata-kata-type="([a-z]+)"')

# Match: #### <a id="p-xxx-yyy"></a>xxx-yyy  (in Specification)
_SCHEMA_REF_PATTERN = re.compile(
    r'####\s+<a\s+id="p-([a-z0-9-]+)"></a>\s*(\S+)'
)

# Match: - **type**: array
_SCHEMA_TYPE_PATTERN = re.compile(
    r'-\s+\*\*type\*\*:\s+(\w+)'
)

# Match: <!-- kata: {...} -->
_KATA_METADATA_PATTERN = re.compile(
    r'<!--\s*kata:\s*(\{.*?\})\s*-->'
)


def extract_from_file(
    file_path: str | Path,
    schema: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Extract JSON data from a .kata.md file.

    Args:
        file_path: Path to the .kata.md file.
        schema: Optional JSON Schema for type hints. If None, the Schema
                Reference section in the document is used.

    Returns:
        Reconstructed JSON data dict.
    """
    path = Path(file_path)
    text = path.read_text(encoding="utf-8")
    return extract_from_text(text, schema=schema)


def extract_from_text(
    text: str,
    schema: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Extract JSON data from .kata.md text content.

    Uses the Specification section to determine which paths are
    array properties vs top-level scalars.

    Path resolution:
    - Schema ref ``p-test-cases`` with type=array → ``test_cases`` is an array
    - Schema ref ``p-test-cases-test-id`` → ``test_cases[].test_id``
    - Data-kata ``p-test-name`` with no child refs → top-level ``test_name``

    Returns:
        Reconstructed data dict.
    """
    # 1. Parse schema structure from Specification section or provided schema
    array_paths = _parse_schema_arrays(text, schema)
    # 1b. Look up per-array child types. These let the extractor suppress
    #     the legacy comma-list heuristic for fields that the schema
    #     declares as plain strings (e.g. a cut's ``audio`` containing a
    #     natural-language ", " should not be split into an array).
    if schema is not None:
        child_types = _child_types_from_schema(schema)
    else:
        child_types = _child_types_from_schema_reference(text)

    # 2. Collect all (anchor_path, type, value) triples in document order.
    #    The type attribute (data-kata-type="integer" etc.) lets the extractor
    #    recover the original data type — without it every <span> value is a
    #    string, which breaks round-trips for integer/boolean/number fields.
    entries: list[tuple[str, str | None, str]] = []
    for match in _DATA_KATA_PATTERN.finditer(text):
        anchor = match.group(1)  # e.g., "test-cases-test-id"
        attrs = match.group(2)
        value = _html.unescape(match.group(3))  # restore &lt; &gt; etc.
        type_match = _DATA_KATA_TYPE_ATTR.search(attrs) if attrs else None
        kata_type = type_match.group(1) if type_match else None
        entries.append((anchor, kata_type, value))

    # 3. Build data using schema-informed path resolution
    return _build_data(entries, array_paths, child_types)


def _parse_schema_arrays(
    text: str,
    schema: dict[str, Any] | None = None,
) -> dict[str, list[str]]:
    """Identify array properties and their child property names.

    Returns:
        Dict mapping array anchor prefix to list of child property anchors.
        e.g., {"test-cases": ["test-id", "category", "description", ...]}
    """
    if schema is not None:
        return _arrays_from_schema(schema)

    return _arrays_from_schema_reference(text)


def _arrays_from_schema(schema: dict[str, Any]) -> dict[str, list[str]]:
    """Extract array structure from JSON Schema."""
    result: dict[str, list[str]] = {}
    props = schema.get("properties", {})

    for key, prop in props.items():
        if prop.get("type") == "array":
            items = prop.get("items", {})
            if items.get("type") == "object":
                child_props = list(items.get("properties", {}).keys())
                # Convert to anchor-style: test_id → test-id
                anchor_key = key.replace("_", "-")
                anchor_children = [p.replace("_", "-") for p in child_props]
                result[anchor_key] = anchor_children

    return result


def _arrays_from_schema_reference(text: str) -> dict[str, list[str]]:
    """Parse the Specification section to find array properties.

    Supports two formats:
    1. Legacy anchor headings:
        #### <a id="p-test-cases"></a>test_cases
        - **type**: array **(required)**
    2. YAML shorthand code block:
        ```yaml
        test_cases[]!:
          test_id: string!
        ```
    """
    # Find Specification section
    schema_start = text.find("<summary>Specification</summary>")
    if schema_start == -1:
        schema_start = text.find("<summary>Schema</summary>")
    if schema_start == -1:
        return {}

    schema_text = text[schema_start:]

    # Try YAML shorthand code block first
    result = _arrays_from_shorthand_block(schema_text)
    if result:
        return result

    # Fallback: legacy anchor heading format
    property_defs: list[tuple[str, str]] = []  # (anchor_path, type)
    current_anchor: str | None = None

    for line in schema_text.split("\n"):
        ref_match = _SCHEMA_REF_PATTERN.search(line)
        if ref_match:
            current_anchor = ref_match.group(1)
            continue

        if current_anchor:
            type_match = _SCHEMA_TYPE_PATTERN.search(line)
            if type_match:
                property_defs.append((current_anchor, type_match.group(1)))
                current_anchor = None

    # Find arrays and their children
    array_anchors: set[str] = set()
    for anchor, ptype in property_defs:
        if ptype == "array":
            array_anchors.add(anchor)

    # Group child properties under their array parent
    result = {a: [] for a in array_anchors}
    for anchor, _ptype in property_defs:
        if anchor in array_anchors:
            continue
        for arr_anchor in array_anchors:
            if anchor.startswith(arr_anchor + "-"):
                child = anchor[len(arr_anchor) + 1:]
                result[arr_anchor].append(child)
                break

    return result


# Match: name[]: or name[]!:
_SHORTHAND_ARRAY_PATTERN = re.compile(r"^(\w+)\[\]!?:\s*$")
# Match:   child_name: type  (indented) — captures name and leading type token
_SHORTHAND_CHILD_PATTERN = re.compile(r"^\s+(\w+):\s+(\S+)")


def _leading_spaces(line: str) -> int:
    """Count leading spaces in a line (tabs counted as 1 space)."""
    i = 0
    for ch in line:
        if ch == " ":
            i += 1
        else:
            break
    return i


def _arrays_from_shorthand_block(schema_text: str) -> dict[str, list[str]]:
    """Parse YAML shorthand in a ```yaml code block to find arrays.

    The parser tracks the indent level established by the first child
    of each ``<name>[]:`` block. Only children at that level count —
    any deeper indent (e.g. a nested ``lines[]:`` with its own object
    fields) is skipped so those inner keys don't get mistakenly
    attributed to the outer array, and so that the outer array's
    sibling children after the nested block are still captured.
    """
    code_match = re.search(
        r"\*\*Schema\*\*\s*\n\s*```yaml\n(.*?)```",
        schema_text,
        re.DOTALL,
    )
    if not code_match:
        return {}

    block = code_match.group(1)
    result: dict[str, list[str]] = {}
    current_array: str | None = None
    child_indent: int | None = None

    for line in block.split("\n"):
        if not line.strip():
            continue
        indent = _leading_spaces(line)
        arr_match = _SHORTHAND_ARRAY_PATTERN.match(line)
        if arr_match and indent == 0:
            current_array = arr_match.group(1).replace("_", "-")
            result[current_array] = []
            child_indent = None
            continue

        if current_array is not None:
            if indent == 0:
                # Back to top level — end of the current array block
                current_array = None
                child_indent = None
                continue
            if child_indent is None:
                child_indent = indent
            if indent != child_indent:
                # Deeper (nested object field) or shallower — skip
                continue
            child_match = _SHORTHAND_CHILD_PATTERN.match(line)
            if child_match:
                child_name = child_match.group(1).replace("_", "-")
                result[current_array].append(child_name)

    return result


def _child_types_from_shorthand_block(schema_text: str) -> dict[str, dict[str, str]]:
    """Parse shorthand YAML and return child-type mapping per array.

    Returns e.g.::

        {"cuts": {"scene": "string", "duration-sec": "integer", "audio": "string"}}

    The types are the leading token of each child line (before any ``!``
    modifiers or ``[]`` suffix). Unknown or unparseable lines are skipped —
    they simply don't contribute a type hint, which falls back to legacy
    heuristic behavior in ``_parse_value``.

    The parser handles nested array children (e.g. ``cuts[].lines[]``) by
    tracking the indent level of each outer array's direct children and
    skipping deeper lines.
    """
    code_match = re.search(
        r"\*\*Schema\*\*\s*\n\s*```yaml\n(.*?)```",
        schema_text,
        re.DOTALL,
    )
    if not code_match:
        return {}
    block = code_match.group(1)
    result: dict[str, dict[str, str]] = {}
    current_array: str | None = None
    child_indent: int | None = None
    for line in block.split("\n"):
        if not line.strip():
            continue
        indent = _leading_spaces(line)
        arr_match = _SHORTHAND_ARRAY_PATTERN.match(line)
        if arr_match and indent == 0:
            current_array = arr_match.group(1).replace("_", "-")
            result[current_array] = {}
            child_indent = None
            continue
        if current_array is not None:
            if indent == 0:
                current_array = None
                child_indent = None
                continue
            if child_indent is None:
                child_indent = indent
            if indent != child_indent:
                continue
            child_match = _SHORTHAND_CHILD_PATTERN.match(line)
            if child_match:
                child_name = child_match.group(1).replace("_", "-")
                raw_type = child_match.group(2)
                base = raw_type.rstrip("!")
                if base.endswith("[]"):
                    result[current_array][child_name] = "array"
                else:
                    result[current_array][child_name] = base
    return result


def _child_types_from_schema(schema: dict[str, Any]) -> dict[str, dict[str, str]]:
    """Extract child-type mapping per array from an explicit JSON Schema.

    Mirrors :func:`_child_types_from_shorthand_block` but reads a proper
    JSON Schema dict. Only first-level arrays-of-objects contribute.
    """
    result: dict[str, dict[str, str]] = {}
    props = schema.get("properties", {})
    for key, prop in props.items():
        if prop.get("type") != "array":
            continue
        items = prop.get("items", {})
        if items.get("type") != "object":
            continue
        anchor_key = key.replace("_", "-")
        children: dict[str, str] = {}
        for child_key, child_schema in items.get("properties", {}).items():
            child_anchor = child_key.replace("_", "-")
            ctype = child_schema.get("type")
            if isinstance(ctype, str):
                children[child_anchor] = ctype
        if children:
            result[anchor_key] = children
    return result


def _child_types_from_schema_reference(text: str) -> dict[str, dict[str, str]]:
    """Look up child-type mapping per array from the Specification section.

    Shorthand YAML is tried first (modern format). No legacy anchor-heading
    fallback is provided because the heading format does not carry per-child
    nested type info in a form we can reliably associate with array parents.
    """
    schema_start = text.find("<summary>Specification</summary>")
    if schema_start == -1:
        schema_start = text.find("<summary>Schema</summary>")
    if schema_start == -1:
        return {}
    return _child_types_from_shorthand_block(text[schema_start:])


_INDEXED_CHILD_PATTERN = re.compile(r"^(\d+)-(.+)$")


def _build_data(
    entries: list[tuple[str, str | None, str]],
    array_paths: dict[str, list[str]],
    child_types: dict[str, dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Build nested dict using schema-informed path resolution.

    Supports two anchor formats for array elements:

    1. Indexed (modern): ``p-{arr}-{i}-{prop}`` where ``{i}`` is the numeric
       position of the element in the source data. The extractor uses the
       index to dispatch the value to ``arr[i][prop]`` directly, which makes
       the reconstruction robust against repeated annotations of the same
       element (e.g. cross-referencing ``characters`` inside a ``cuts``
       loop in a storyboard template).

    2. Non-indexed (legacy): ``p-{arr}-{prop}`` without a numeric segment.
       The extractor falls back to a "first-key boundary" heuristic: a new
       element begins every time the first child key seen for this array
       reappears.

    Detection is per-entry: the indexed regex is applied first; if it
    matches, we use indexed dispatch. If the prefix has no leading digit
    segment, we keep the legacy behavior.

    ``child_types`` maps each array anchor to a dict of child-anchor →
    JSON Schema type string. When ``kata_type`` is missing from the span
    (the annotator skips ``data-kata-type="string"`` because string is the
    default), the schema-declared type is consulted. This prevents the
    legacy comma-list heuristic from splitting natural-language fields
    like ``cuts[i].audio = "Room tone, no BGM"`` into ``["Room tone", "no BGM"]``.
    """
    if child_types is None:
        child_types = {}
    result: dict[str, Any] = {}

    # Indexed arrays: arr_anchor -> {index: {prop: value}}
    indexed: dict[str, dict[int, dict[str, Any]]] = {}
    # Legacy (non-indexed) arrays
    legacy_items: dict[str, list[dict[str, Any]]] = {}
    legacy_current: dict[str, dict[str, Any]] = {}
    legacy_first_key: dict[str, str] = {}

    def _effective_type(
        kata_type: str | None,
        matched_array: str | None,
        child_anchor: str,
    ) -> str | None:
        """Choose between the span's own type hint and the schema's."""
        if kata_type is not None:
            return kata_type
        if matched_array is not None:
            return child_types.get(matched_array, {}).get(child_anchor)
        return None

    for anchor, kata_type, value in entries:
        matched_array = _find_array_prefix(anchor, array_paths)

        if matched_array is not None:
            child_anchor = anchor[len(matched_array) + 1:]
            idx_match = _INDEXED_CHILD_PATTERN.match(child_anchor)

            if idx_match:
                index = int(idx_match.group(1))
                prop_name = idx_match.group(2).replace("-", "_")
                # Strip index before looking up the schema (types are keyed
                # by bare child anchor, not anchor-with-index).
                schema_child = idx_match.group(2)
                effective = _effective_type(
                    kata_type, matched_array, schema_child,
                )
                bucket = indexed.setdefault(matched_array, {})
                element = bucket.setdefault(index, {})
                element[prop_name] = _parse_value(value, effective)
            else:
                # Legacy path — no numeric index segment
                prop_name = child_anchor.replace("-", "_")
                effective = _effective_type(
                    kata_type, matched_array, child_anchor,
                )
                if matched_array not in legacy_items:
                    legacy_items[matched_array] = []
                    legacy_current[matched_array] = {}
                    legacy_first_key[matched_array] = prop_name

                if (prop_name == legacy_first_key[matched_array]
                        and legacy_current[matched_array]):
                    legacy_items[matched_array].append(
                        legacy_current[matched_array]
                    )
                    legacy_current[matched_array] = {}

                legacy_current[matched_array][prop_name] = _parse_value(
                    value, effective,
                )

        elif anchor in array_paths:
            # Standalone array anchor (e.g., count marker "test-cases") — skip
            continue
        else:
            # Top-level scalar.
            # Only coerce via _parse_value when a type hint is present —
            # the legacy comma-list heuristic was historically scoped to
            # array child values, not top-level strings, so running it
            # unconditionally here splits sentences like
            # "Meeting Room / Online (Teams, Zoom, etc.)".
            prop_name = anchor.replace("-", "_")
            if kata_type is not None:
                result[prop_name] = _parse_value(value, kata_type)
            else:
                result[prop_name] = value

    # Flush legacy pending rows
    for arr_anchor in legacy_items:
        if legacy_current.get(arr_anchor):
            legacy_items[arr_anchor].append(legacy_current[arr_anchor])

    # Merge indexed arrays (ordered by index) into result
    for arr_anchor, bucket in indexed.items():
        ordered = [bucket[i] for i in sorted(bucket)]
        prop_name = arr_anchor.replace("-", "_")
        result[prop_name] = ordered

    # Merge legacy arrays into result
    for arr_anchor, items in legacy_items.items():
        prop_name = arr_anchor.replace("-", "_")
        if prop_name not in result:
            result[prop_name] = items

    return result


def _find_array_prefix(
    anchor: str,
    array_paths: dict[str, list[str]],
) -> str | None:
    """Find the longest matching array prefix for an anchor path."""
    best: str | None = None
    for arr_anchor in array_paths:
        if anchor.startswith(arr_anchor + "-"):
            if best is None or len(arr_anchor) > len(best):
                best = arr_anchor
    return best


def _parse_value(value: str, kata_type: str | None = None) -> Any:
    """Parse a string value back to its original type.

    When the ``data-kata-type`` attribute is present on the source span,
    we coerce the textContent back to that type — otherwise the extractor
    can only hand back strings, which breaks round-tripping of numeric
    and boolean fields.

    Args:
        value: Raw textContent captured from the span.
        kata_type: Optional type hint from ``data-kata-type`` attribute.
            Recognized values: ``integer``, ``number``, ``boolean``,
            ``array``, ``enum``, ``string``. Unknown or missing falls
            back to the legacy string-with-list-heuristic behavior.
    """
    if kata_type == "integer":
        try:
            return int(value)
        except ValueError:
            return value
    if kata_type == "number":
        try:
            return float(value)
        except ValueError:
            return value
    if kata_type == "boolean":
        low = value.strip().lower()
        if low in ("true", "yes", "1"):
            return True
        if low in ("false", "no", "0"):
            return False
        return value
    if kata_type == "array":
        if not value.strip():
            return []
        return [v.strip() for v in value.split(", ")]
    # Explicitly-typed string / enum: return verbatim. These types can legitimately
    # contain ", " in natural language (e.g. a cut's ``audio`` field, a character's
    # ``role`` sentence), so do NOT split on commas even though the legacy heuristic
    # used to do so.
    if kata_type in ("string", "enum"):
        return value
    # Missing type hint (neither a data-kata-type attribute nor a schema lookup
    # produced one): fall back to the legacy comma-list heuristic. This covers
    # templates that pre-date schema-aware extraction and documents whose
    # Specification section can't be parsed for child types.
    if kata_type is None:
        if ", " in value and len(value) < 200:
            parts = [v.strip() for v in value.split(", ")]
            if all(len(p) < 50 for p in parts) and len(parts) >= 2:
                if not any(" " in p and len(p) > 30 for p in parts):
                    return parts
    return value


def extract_metadata(text: str) -> dict[str, Any] | None:
    """Extract kata metadata from a rendered document.

    Looks for ``<!-- kata: {"schema": "...", ...} -->`` comment.

    Returns:
        Metadata dict or None if not found.
    """
    match = _KATA_METADATA_PATTERN.search(text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None
    return None
