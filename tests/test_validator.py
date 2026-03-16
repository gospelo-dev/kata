"""Tests for gospelo_kata.validator."""

from __future__ import annotations

import json
import os
import tempfile

import pytest

from gospelo_kata.validator import (
    detect_schema,
    get_builtin_schema,
    load_schema,
    validate,
    validate_file,
)


# ---------------------------------------------------------------------------
# Type checking
# ---------------------------------------------------------------------------

class TestTypeValidation:
    def test_string_valid(self):
        schema = {"type": "object", "properties": {"x": {"type": "string"}}}
        result = validate({"x": "hello"}, schema)
        assert result.valid

    def test_string_invalid(self):
        schema = {"type": "object", "properties": {"x": {"type": "string"}}}
        result = validate({"x": 123}, schema)
        assert not result.valid

    def test_integer_valid(self):
        schema = {"type": "object", "properties": {"x": {"type": "integer"}}}
        result = validate({"x": 42}, schema)
        assert result.valid

    def test_number_valid(self):
        schema = {"type": "object", "properties": {"x": {"type": "number"}}}
        result = validate({"x": 3.14}, schema)
        assert result.valid

    def test_boolean_valid(self):
        schema = {"type": "object", "properties": {"x": {"type": "boolean"}}}
        result = validate({"x": True}, schema)
        assert result.valid

    def test_array_valid(self):
        schema = {"type": "object", "properties": {"x": {"type": "array"}}}
        result = validate({"x": [1, 2]}, schema)
        assert result.valid

    def test_object_valid(self):
        schema = {"type": "object", "properties": {"x": {"type": "object"}}}
        result = validate({"x": {"a": 1}}, schema)
        assert result.valid

    def test_null_valid(self):
        schema = {"type": "object", "properties": {"x": {"type": "null"}}}
        result = validate({"x": None}, schema)
        assert result.valid


# ---------------------------------------------------------------------------
# Required fields
# ---------------------------------------------------------------------------

class TestRequired:
    def test_required_present(self):
        schema = {"type": "object", "required": ["name"], "properties": {"name": {"type": "string"}}}
        result = validate({"name": "test"}, schema)
        assert result.valid

    def test_required_missing(self):
        schema = {"type": "object", "required": ["name"], "properties": {"name": {"type": "string"}}}
        result = validate({}, schema)
        assert not result.valid
        assert any("required" in e.message for e in result.errors)

    def test_multiple_required(self):
        schema = {
            "type": "object",
            "required": ["a", "b"],
            "properties": {"a": {"type": "string"}, "b": {"type": "string"}},
        }
        result = validate({"a": "x"}, schema)
        assert not result.valid


# ---------------------------------------------------------------------------
# Array validation
# ---------------------------------------------------------------------------

class TestArrayValidation:
    def test_array_items_valid(self):
        schema = {
            "type": "object",
            "properties": {
                "items": {"type": "array", "items": {"type": "string"}},
            },
        }
        result = validate({"items": ["a", "b"]}, schema)
        assert result.valid

    def test_array_items_invalid(self):
        schema = {
            "type": "object",
            "properties": {
                "items": {"type": "array", "items": {"type": "string"}},
            },
        }
        result = validate({"items": ["a", 123]}, schema)
        assert not result.valid

    def test_min_items(self):
        schema = {
            "type": "object",
            "properties": {
                "items": {"type": "array", "minItems": 2},
            },
        }
        result = validate({"items": [1]}, schema)
        assert not result.valid

    def test_max_items(self):
        schema = {
            "type": "object",
            "properties": {
                "items": {"type": "array", "maxItems": 2},
            },
        }
        result = validate({"items": [1, 2, 3]}, schema)
        assert not result.valid


# ---------------------------------------------------------------------------
# String constraints
# ---------------------------------------------------------------------------

class TestStringConstraints:
    def test_min_length(self):
        schema = {"type": "object", "properties": {"x": {"type": "string", "minLength": 3}}}
        result = validate({"x": "ab"}, schema)
        assert not result.valid

    def test_min_length_ok(self):
        schema = {"type": "object", "properties": {"x": {"type": "string", "minLength": 3}}}
        result = validate({"x": "abc"}, schema)
        assert result.valid


# ---------------------------------------------------------------------------
# Enum validation
# ---------------------------------------------------------------------------

class TestEnumValidation:
    def test_enum_valid(self):
        schema = {"type": "object", "properties": {"status": {"type": "string", "enum": ["open", "closed"]}}}
        result = validate({"status": "open"}, schema)
        assert result.valid

    def test_enum_invalid(self):
        schema = {"type": "object", "properties": {"status": {"type": "string", "enum": ["open", "closed"]}}}
        result = validate({"status": "invalid"}, schema)
        assert not result.valid


# ---------------------------------------------------------------------------
# Additional properties
# ---------------------------------------------------------------------------

class TestAdditionalProperties:
    def test_additional_allowed(self):
        schema = {"type": "object", "properties": {"x": {"type": "string"}}}
        result = validate({"x": "a", "extra": "b"}, schema)
        assert result.valid

    def test_additional_forbidden(self):
        schema = {
            "type": "object",
            "properties": {"x": {"type": "string"}},
            "additionalProperties": False,
        }
        result = validate({"x": "a", "extra": "b"}, schema)
        assert not result.valid


# ---------------------------------------------------------------------------
# Nested object validation
# ---------------------------------------------------------------------------

class TestNestedObjects:
    def test_nested_valid(self):
        schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "required": ["name"],
                    "properties": {"name": {"type": "string"}},
                },
            },
        }
        result = validate({"user": {"name": "test"}}, schema)
        assert result.valid

    def test_nested_invalid(self):
        schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "required": ["name"],
                    "properties": {"name": {"type": "string"}},
                },
            },
        }
        result = validate({"user": {}}, schema)
        assert not result.valid


# ---------------------------------------------------------------------------
# detect_schema
# ---------------------------------------------------------------------------

class TestDetectSchema:
    def test_detect_checklist(self):
        assert detect_schema({"categories": [], "templates": {}}) == "checklist"

    def test_detect_test_spec(self):
        assert detect_schema({"test_cases": []}) == "test_spec"

    def test_detect_test_prereq(self):
        data = {"test_name": "x", "summary": {}, "risk_map": {}}
        assert detect_schema(data) == "test_prereq"

    def test_detect_agenda(self):
        data = {"attendees": [], "agenda": []}
        assert detect_schema(data) == "agenda"

    def test_detect_unknown(self):
        assert detect_schema({"foo": "bar"}) is None


# ---------------------------------------------------------------------------
# Built-in schemas
# ---------------------------------------------------------------------------

class TestBuiltinSchemas:
    def test_load_checklist_schema(self):
        schema = get_builtin_schema("checklist")
        assert schema["type"] == "object"

    def test_load_test_spec_schema(self):
        schema = get_builtin_schema("test_spec")
        assert schema["type"] == "object"

    def test_load_test_prereq_schema(self):
        schema = get_builtin_schema("test_prereq")
        assert schema["type"] == "object"

    def test_load_agenda_schema(self):
        schema = get_builtin_schema("agenda")
        assert schema["type"] == "object"

    def test_nonexistent_schema(self):
        with pytest.raises(FileNotFoundError):
            get_builtin_schema("nonexistent")


# ---------------------------------------------------------------------------
# validate_file
# ---------------------------------------------------------------------------

class TestValidateFile:
    def test_file_not_found(self):
        result = validate_file(
            "/tmp/nonexistent_12345.json",
            {"type": "object"},
        )
        assert not result.valid

    def test_invalid_json(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, dir="/tmp"
        ) as f:
            f.write("{invalid}")
            path = f.name

        try:
            result = validate_file(path, {"type": "object"})
            assert not result.valid
        finally:
            os.unlink(path)

    def test_valid_file(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, dir="/tmp"
        ) as f:
            json.dump({"name": "test"}, f)
            path = f.name

        try:
            schema = {"type": "object", "properties": {"name": {"type": "string"}}}
            result = validate_file(path, schema)
            assert result.valid
            assert path in result.file_path
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# load_schema
# ---------------------------------------------------------------------------

class TestLoadSchema:
    def test_load_from_file(self):
        schema_data = {"type": "object", "title": "Test"}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, dir="/tmp"
        ) as f:
            json.dump(schema_data, f)
            path = f.name

        try:
            loaded = load_schema(path)
            assert loaded == schema_data
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# ValidationResult.summary
# ---------------------------------------------------------------------------

class TestValidationResultSummary:
    def test_summary_ok(self):
        result = validate({"x": "hello"}, {"type": "object"})
        assert "OK" in result.summary()

    def test_summary_fail(self):
        result = validate(
            {},
            {"type": "object", "required": ["x"]},
            schema_name="test",
        )
        assert "FAIL" in result.summary()
        assert "test" in result.summary()
