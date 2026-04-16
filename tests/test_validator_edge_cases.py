"""Edge case tests for gospelo_kata/validator.py"""
import pytest
from gospelo_kata.validator import (
    validate,
    detect_schema,
    ValidationResult,
    ValidationError,
)


# ── detect_schema tests ───────────────────────────────────────────────────────

def test_detect_schema_checklist():
    data = {"categories": [], "templates": []}
    assert detect_schema(data) == "checklist"


def test_detect_schema_test_prereq():
    data = {"test_name": "x", "summary": "y", "risk_map": {}}
    assert detect_schema(data) == "test_prereq"


def test_detect_schema_test_spec():
    data = {"test_cases": []}
    assert detect_schema(data) == "test_spec"


def test_detect_schema_agenda():
    data = {"attendees": [], "agenda": []}
    assert detect_schema(data) == "agenda"


def test_detect_schema_unknown_returns_none():
    data = {"unknown_field": "value"}
    assert detect_schema(data) is None


# ── validate enum tests ───────────────────────────────────────────────────────

def test_validate_enum_valid():
    schema = {"type": "string", "enum": ["a", "b", "c"]}
    result = validate("a", schema)
    assert result.valid


def test_validate_enum_invalid():
    schema = {"type": "string", "enum": ["a", "b", "c"]}
    result = validate("z", schema)
    assert not result.valid
    assert any("must be one of" in e.message for e in result.errors)


# ── validate additionalProperties tests ──────────────────────────────────────

def test_validate_additional_properties_rejected():
    schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "additionalProperties": False,
    }
    result = validate({"name": "ok", "extra": "bad"}, schema)
    assert not result.valid
    assert any("unexpected additional property" in e.message for e in result.errors)


def test_validate_additional_properties_allowed():
    schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}},
    }
    result = validate({"name": "ok", "extra": "fine"}, schema)
    assert result.valid


# ── validate array minItems/maxItems tests ────────────────────────────────────

def test_validate_array_min_items_fail():
    schema = {"type": "array", "minItems": 2}
    result = validate([1], schema)
    assert not result.valid
    assert any("at least" in e.message for e in result.errors)


def test_validate_array_max_items_fail():
    schema = {"type": "array", "maxItems": 2}
    result = validate([1, 2, 3], schema)
    assert not result.valid
    assert any("at most" in e.message for e in result.errors)


def test_validate_array_items_valid():
    schema = {"type": "array", "minItems": 1, "maxItems": 3}
    result = validate([1, 2], schema)
    assert result.valid


# ── validate string minLength tests ──────────────────────────────────────────

def test_validate_string_min_length_fail():
    schema = {"type": "string", "minLength": 5}
    result = validate("hi", schema)
    assert not result.valid
    assert any("at least" in e.message for e in result.errors)


def test_validate_string_min_length_pass():
    schema = {"type": "string", "minLength": 3}
    result = validate("hello", schema)
    assert result.valid


# ── ValidationResult.summary tests ───────────────────────────────────────────

def test_validation_result_summary_valid():
    result = ValidationResult(valid=True, schema_name="test", file_path="file.json")
    assert "OK" in result.summary()
    assert "file.json" in result.summary()


def test_validation_result_summary_invalid():
    errors = [ValidationError(path="$.name", message="required field is missing")]
    result = ValidationResult(valid=False, errors=errors, schema_name="test", file_path="file.json")
    summary = result.summary()
    assert "FAIL" in summary
    assert "$.name" in summary


# ── validate required fields ──────────────────────────────────────────────────

def test_validate_missing_required_field():
    schema = {
        "type": "object",
        "required": ["name"],
        "properties": {"name": {"type": "string"}},
    }
    result = validate({}, schema)
    assert not result.valid
    assert any("required field is missing" in e.message for e in result.errors)


# ── validate type mismatch ────────────────────────────────────────────────────

def test_validate_type_mismatch():
    schema = {"type": "string"}
    result = validate(123, schema)
    assert not result.valid
    assert any("expected type" in e.message for e in result.errors)