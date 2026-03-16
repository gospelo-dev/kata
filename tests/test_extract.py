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
<summary>Schema Reference</summary>

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
