# KATA Markdown™ — gospelo-kata
# Copyright (c) 2025 gospelo. All rights reserved.
# Licensed under the MIT License. See LICENSE.md for details.

"""Tests for gospelo_kata.extract."""

from __future__ import annotations

import json

import pytest

from gospelo_kata.extract import (
    extract_from_text,
    extract_metadata,
    _arrays_from_schema,
    _arrays_from_schema_reference,
    _parse_value,
)


SAMPLE_KATA_MD = """\
# <a id="u-test-name"></a>[<span data-kata="p-test-name">My Test</span>](#p-test-name)

<a id="u-header"></a>> Prefix: [<span data-kata="p-test-id-prefix">T</span>](#p-test-id-prefix) | Version: [<span data-kata="p-version">1.0.0</span>](#p-version)

## <a id="u-test-cases"></a>Test Cases

| ID | Category | Description | Expected Result | Priority | Tags |
|:--:|----------|-------------|-----------------|:--------:|------|
| [<span data-kata="p-test-cases-test-id">T-01</span>](#p-test-cases-test-id) | [<span data-kata="p-test-cases-category">Basic</span>](#p-test-cases-category) | [<span data-kata="p-test-cases-description">Test basic op</span>](#p-test-cases-description) | [<span data-kata="p-test-cases-expected-result">Status 200</span>](#p-test-cases-expected-result) | [<span data-kata="p-test-cases-priority">high</span>](#p-test-cases-priority) | [<span data-kata="p-test-cases-tags">smoke, basic</span>](#p-test-cases-tags) |
| [<span data-kata="p-test-cases-test-id">T-02</span>](#p-test-cases-test-id) | [<span data-kata="p-test-cases-category">Error</span>](#p-test-cases-category) | [<span data-kata="p-test-cases-description">Test error</span>](#p-test-cases-description) | [<span data-kata="p-test-cases-expected-result">Status 400</span>](#p-test-cases-expected-result) | [<span data-kata="p-test-cases-priority">medium</span>](#p-test-cases-priority) | [<span data-kata="p-test-cases-tags">negative</span>](#p-test-cases-tags) |

Total: <span data-kata="p-test-cases">2</span> test cases

---

<details>
<summary>Specification</summary>

#### <a id="p-test-name"></a>test_name
- **type**: string

#### <a id="p-test-id-prefix"></a>test_id_prefix
- **type**: string

#### <a id="p-version"></a>version
- **type**: string

#### <a id="p-test-cases"></a>test_cases
- **type**: array **(required)**

#### <a id="p-test-cases-test-id"></a>test_cases-test_id
- **type**: string **(required)**

#### <a id="p-test-cases-category"></a>test_cases-category
- **type**: string **(required)**

#### <a id="p-test-cases-description"></a>test_cases-description
- **type**: string **(required)**

#### <a id="p-test-cases-expected-result"></a>test_cases-expected_result
- **type**: string **(required)**

#### <a id="p-test-cases-priority"></a>test_cases-priority
- **type**: string

#### <a id="p-test-cases-tags"></a>test_cases-tags
- **type**: array

</details>
"""


class TestExtractFromText:
    def test_top_level_scalars(self):
        data = extract_from_text(SAMPLE_KATA_MD)
        assert data["test_name"] == "My Test"
        assert data["test_id_prefix"] == "T"
        assert data["version"] == "1.0.0"

    def test_array_items(self):
        data = extract_from_text(SAMPLE_KATA_MD)
        assert "test_cases" in data
        assert len(data["test_cases"]) == 2

    def test_first_item_properties(self):
        data = extract_from_text(SAMPLE_KATA_MD)
        item = data["test_cases"][0]
        assert item["test_id"] == "T-01"
        assert item["category"] == "Basic"
        assert item["description"] == "Test basic op"
        assert item["expected_result"] == "Status 200"
        assert item["priority"] == "high"
        assert item["tags"] == ["smoke", "basic"]

    def test_second_item(self):
        data = extract_from_text(SAMPLE_KATA_MD)
        item = data["test_cases"][1]
        assert item["test_id"] == "T-02"
        assert item["category"] == "Error"
        assert item["priority"] == "medium"
        assert item["tags"] == "negative"  # single value, not a list

    def test_no_data_kata(self):
        data = extract_from_text("# Plain markdown\n\nNo data-kata here.")
        assert data == {}


class TestExtractWithExternalSchema:
    def test_schema_based_extraction(self):
        schema = {
            "type": "object",
            "properties": {
                "test_name": {"type": "string"},
                "test_cases": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "test_id": {"type": "string"},
                            "category": {"type": "string"},
                            "description": {"type": "string"},
                            "expected_result": {"type": "string"},
                            "priority": {"type": "string"},
                            "tags": {"type": "array"},
                        },
                    },
                },
            },
        }
        data = extract_from_text(SAMPLE_KATA_MD, schema=schema)
        assert data["test_name"] == "My Test"
        assert len(data["test_cases"]) == 2
        assert data["test_cases"][0]["test_id"] == "T-01"


class TestArraysFromSchemaReference:
    def test_parses_arrays(self):
        arrays = _arrays_from_schema_reference(SAMPLE_KATA_MD)
        assert "test-cases" in arrays
        assert "test-id" in arrays["test-cases"]
        assert "category" in arrays["test-cases"]

    def test_no_schema_reference(self):
        arrays = _arrays_from_schema_reference("# No schema here")
        assert arrays == {}


class TestArraysFromSchema:
    def test_detects_array(self):
        schema = {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                        },
                    },
                },
            },
        }
        arrays = _arrays_from_schema(schema)
        assert "items" in arrays
        assert "id" in arrays["items"]
        assert "name" in arrays["items"]


class TestParseValue:
    def test_plain_string(self):
        assert _parse_value("hello") == "hello"

    def test_comma_list(self):
        assert _parse_value("tag1, tag2, tag3") == ["tag1", "tag2", "tag3"]

    def test_long_sentence_not_split(self):
        val = "This is a long sentence, which contains a comma but should not be split"
        result = _parse_value(val)
        assert isinstance(result, str)

    def test_integer_type_coerced(self):
        assert _parse_value("42", "integer") == 42

    def test_integer_type_invalid_falls_back_to_string(self):
        assert _parse_value("abc", "integer") == "abc"

    def test_number_type_coerced(self):
        assert _parse_value("3.14", "number") == pytest.approx(3.14)

    def test_boolean_true_forms(self):
        assert _parse_value("true", "boolean") is True
        assert _parse_value("True", "boolean") is True
        assert _parse_value("YES", "boolean") is True
        assert _parse_value("1", "boolean") is True

    def test_boolean_false_forms(self):
        assert _parse_value("false", "boolean") is False
        assert _parse_value("No", "boolean") is False
        assert _parse_value("0", "boolean") is False

    def test_array_type_splits_on_comma_space(self):
        assert _parse_value("a, b, c", "array") == ["a", "b", "c"]

    def test_array_type_empty(self):
        assert _parse_value("", "array") == []

    def test_enum_kept_as_string(self):
        assert _parse_value("active", "enum") == "active"

    def test_string_with_type_hint_skips_heuristic(self):
        # A typed "string" anchor must not be split on commas, even
        # though the legacy heuristic would have split this value.
        assert _parse_value("a, b, c", "string") == "a, b, c"


SAMPLE_TYPED_KATA_MD = """\
# <span data-kata="p-title">Typed Test</span>

## Data

| Field | Value |
|-------|-------|
| Count | <span data-kata="p-count" data-kata-type="integer">42</span> |
| Enabled | <span data-kata="p-enabled" data-kata-type="boolean">true</span> |
| Ratio | <span data-kata="p-ratio" data-kata-type="number">3.14</span> |

## Items

- id=<span data-kata="p-items-0-id">a</span>, qty=<span data-kata="p-items-0-qty" data-kata-type="integer">10</span>
- id=<span data-kata="p-items-1-id">b</span>, qty=<span data-kata="p-items-1-qty" data-kata-type="integer">20</span>

<details>
<summary>Specification</summary>

**Schema**

```yaml
title: string!
count: integer
enabled: boolean
ratio: number
items[]:
  id: string
  qty: integer
```

</details>
"""


class TestTypedExtraction:
    def test_integer_round_trip_top_level(self):
        data = extract_from_text(SAMPLE_TYPED_KATA_MD)
        assert data["count"] == 42
        assert isinstance(data["count"], int)

    def test_boolean_round_trip_top_level(self):
        data = extract_from_text(SAMPLE_TYPED_KATA_MD)
        assert data["enabled"] is True

    def test_number_round_trip_top_level(self):
        data = extract_from_text(SAMPLE_TYPED_KATA_MD)
        assert data["ratio"] == pytest.approx(3.14)

    def test_typed_fields_inside_array_elements(self):
        data = extract_from_text(SAMPLE_TYPED_KATA_MD)
        assert data["items"][0]["qty"] == 10
        assert data["items"][1]["qty"] == 20
        assert isinstance(data["items"][0]["qty"], int)


SAMPLE_CROSS_REFERENCE_KATA_MD = """\
# <span data-kata="p-title">Cross-Reference Test</span>

## Characters

- <span data-kata="p-characters-0-name">Alice</span> (id=alice)
- <span data-kata="p-characters-1-name">Bob</span> (id=bob)

## Cuts

- cut 1 speaker: <span data-kata="p-characters-0-name">Alice</span>
- cut 2 speaker: <span data-kata="p-characters-1-name">Bob</span>
- cut 3 speaker: <span data-kata="p-characters-0-name">Alice</span>

<details>
<summary>Specification</summary>

**Schema**

```yaml
title: string!
characters[]:
  name: string
```

</details>
"""


class TestCrossReferenceExtraction:
    def test_duplicate_annotations_do_not_inflate_array(self):
        # Cross-referencing the same array element from multiple
        # places in the template should not create phantom elements
        # in the extracted output — the indexed anchor format lets
        # the extractor collapse repeats onto the same logical entry.
        data = extract_from_text(SAMPLE_CROSS_REFERENCE_KATA_MD)
        assert len(data["characters"]) == 2
        assert data["characters"][0]["name"] == "Alice"
        assert data["characters"][1]["name"] == "Bob"


SAMPLE_STRING_WITH_COMMAS_KATA_MD = """\
# <span data-kata="p-title">Comma Survival Test</span>

## Cuts

### <span data-kata="p-cuts-0-id">C-001</span>
<p>Scene: <span data-kata="p-cuts-0-scene">Wide establishing shot, crane down, fade in.</span></p>
<p>Audio: <span data-kata="p-cuts-0-audio">Soft piano, strings in the background</span></p>
<p>Tags: <span data-kata="p-cuts-0-tags">smoke, basic</span></p>

<details>
<summary>Specification</summary>

**Schema**

```yaml
title: string!
cuts[]:
  id: string
  scene: string
  audio: string
  tags: string[]
```

</details>
"""


class TestSchemaDrivenStringSplitSuppression:
    """Schema-typed string children must not be split on ', ' even though the
    legacy heuristic would otherwise turn natural prose into arrays."""

    def test_string_typed_audio_is_not_split(self):
        data = extract_from_text(SAMPLE_STRING_WITH_COMMAS_KATA_MD)
        # audio is declared as ``string`` in the schema, so its comma-containing
        # value must survive as a single string (previously became a list).
        assert data["cuts"][0]["audio"] == "Soft piano, strings in the background"

    def test_string_typed_scene_is_not_split(self):
        data = extract_from_text(SAMPLE_STRING_WITH_COMMAS_KATA_MD)
        assert data["cuts"][0]["scene"] == (
            "Wide establishing shot, crane down, fade in."
        )

    def test_string_array_tags_still_split(self):
        # tags: string[] — still legitimately an array of scalars.
        data = extract_from_text(SAMPLE_STRING_WITH_COMMAS_KATA_MD)
        assert data["cuts"][0]["tags"] == ["smoke", "basic"]

    def test_external_schema_takes_precedence(self):
        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "cuts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "scene": {"type": "string"},
                            "audio": {"type": "string"},
                            "tags": {"type": "array"},
                        },
                    },
                },
            },
        }
        data = extract_from_text(
            SAMPLE_STRING_WITH_COMMAS_KATA_MD, schema=schema,
        )
        assert data["cuts"][0]["audio"] == (
            "Soft piano, strings in the background"
        )
        assert data["cuts"][0]["scene"] == (
            "Wide establishing shot, crane down, fade in."
        )


class TestExtractMetadata:
    def test_parses_metadata(self):
        text = '<!-- kata: {"schema": "test_spec", "generated": "2026-03-16"} -->\n# Title'
        meta = extract_metadata(text)
        assert meta == {"schema": "test_spec", "generated": "2026-03-16"}

    def test_no_metadata(self):
        assert extract_metadata("# Just a title") is None

    def test_invalid_json(self):
        text = "<!-- kata: {invalid} -->"
        assert extract_metadata(text) is None
