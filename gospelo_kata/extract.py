# KATA Markdown™ — gospelo-kata
# Copyright (c) 2025 gospelo. All rights reserved.
# Licensed under the MIT License. See LICENSE.md for details.

"""Extract structured JSON data from rendered .kata.md documents.

Parses data-kata annotations to reconstruct the original JSON data
that was used to generate the document. This enables the reverse flow:

    .kata.md (user edits) → extract → JSON → validate / export

Uses the Schema Reference section (anchor IDs) to resolve the correct
property paths, avoiding ambiguity in dash-separated path parsing.
"""

from __future__ import annotations

import html as _html
import json
import re
from pathlib import Path
from typing import Any

# Match: <span data-kata="p-xxx-yyy">value</span>
_DATA_KATA_PATTERN = re.compile(
    r'<span\s+data-kata="p-([a-z0-9]+(?:-[a-z0-9-]*)*)">([^<]*)</span>'
)

# Match: #### <a id="p-xxx-yyy"></a>xxx-yyy  (in Schema Reference)
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

    Uses the Schema Reference section to determine which paths are
    array properties vs top-level scalars.

    Path resolution:
    - Schema ref ``p-test-cases`` with type=array → ``test_cases`` is an array
    - Schema ref ``p-test-cases-test-id`` → ``test_cases[].test_id``
    - Data-kata ``p-test-name`` with no child refs → top-level ``test_name``

    Returns:
        Reconstructed data dict.
    """
    # 1. Parse schema structure from Schema Reference section or provided schema
    array_paths = _parse_schema_arrays(text, schema)

    # 2. Collect all (anchor_path, value) pairs in document order
    entries: list[tuple[str, str]] = []
    for match in _DATA_KATA_PATTERN.finditer(text):
        anchor = match.group(1)  # e.g., "test-cases-test-id"
        value = _html.unescape(match.group(2))  # restore &lt; &gt; etc.
        entries.append((anchor, value))

    # 3. Build data using schema-informed path resolution
    return _build_data(entries, array_paths)


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
    """Parse the Schema Reference section to find array properties.

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
    # Find Schema Reference section
    schema_start = text.find("<summary>Schema Reference</summary>")
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
# Match:   child_name: type  (indented)
_SHORTHAND_CHILD_PATTERN = re.compile(r"^\s+(\w+):\s+\S+")


def _arrays_from_shorthand_block(schema_text: str) -> dict[str, list[str]]:
    """Parse YAML shorthand in a ```yaml code block to find arrays."""
    # Extract code block content after **Schema**
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

    for line in block.split("\n"):
        arr_match = _SHORTHAND_ARRAY_PATTERN.match(line)
        if arr_match:
            current_array = arr_match.group(1).replace("_", "-")
            result[current_array] = []
            continue

        if current_array is not None:
            child_match = _SHORTHAND_CHILD_PATTERN.match(line)
            if child_match:
                child_name = child_match.group(1).replace("_", "-")
                result[current_array].append(child_name)
            else:
                # No longer indented — end of array children
                current_array = None

    return result


def _build_data(
    entries: list[tuple[str, str]],
    array_paths: dict[str, list[str]],
) -> dict[str, Any]:
    """Build nested dict using schema-informed path resolution."""
    result: dict[str, Any] = {}

    # Track array element construction
    array_items: dict[str, list[dict[str, Any]]] = {}
    array_current: dict[str, dict[str, Any]] = {}
    array_first_key: dict[str, str] = {}  # first child key seen per array

    for anchor, value in entries:
        # Try to match against known array prefixes
        matched_array = _find_array_prefix(anchor, array_paths)

        if matched_array is not None:
            child_anchor = anchor[len(matched_array) + 1:]
            prop_name = child_anchor.replace("-", "_")

            if matched_array not in array_items:
                array_items[matched_array] = []
                array_current[matched_array] = {}
                # Remember the first key to detect row boundaries
                array_first_key[matched_array] = prop_name

            # Detect new row: when we see the first key again
            if (prop_name == array_first_key[matched_array]
                    and array_current[matched_array]):
                array_items[matched_array].append(array_current[matched_array])
                array_current[matched_array] = {}

            array_current[matched_array][prop_name] = _parse_value(value)

        elif anchor in array_paths:
            # Standalone array anchor (e.g., count marker "test-cases") — skip
            continue
        else:
            # Top-level scalar
            prop_name = anchor.replace("-", "_")
            result[prop_name] = value

    # Flush remaining array elements
    for arr_anchor in array_items:
        if array_current.get(arr_anchor):
            array_items[arr_anchor].append(array_current[arr_anchor])

    # Merge arrays into result
    for arr_anchor, items in array_items.items():
        prop_name = arr_anchor.replace("-", "_")
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


def _parse_value(value: str) -> Any:
    """Parse a string value, detecting comma-separated lists for tags.

    Only splits on ", " (comma-space) to avoid false positives with
    values that contain commas in sentences.
    """
    # Heuristic: short comma-separated tokens are likely tags/lists
    # Long text with commas is likely a sentence
    if ", " in value and len(value) < 200:
        parts = [v.strip() for v in value.split(", ")]
        # Only treat as list if all parts are short (tag-like)
        if all(len(p) < 50 for p in parts) and len(parts) >= 2:
            # Check: if any part looks like a sentence fragment, don't split
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
