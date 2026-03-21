# KATA Markdown™ — gospelo-kata
# Copyright (c) 2025 gospelo. All rights reserved.
# Licensed under the MIT License. See LICENSE.md for details.

"""JSON Schema based document validation.

Validates JSON documents against built-in or custom schemas.
Uses only the Python standard library (no jsonschema dependency).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ValidationError:
    """A single validation error."""

    path: str
    message: str
    value: Any = None


@dataclass
class ValidationResult:
    """Result of a validation run."""

    valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    schema_name: str = ""
    file_path: str = ""

    def summary(self) -> str:
        if self.valid:
            return f"OK: {self.file_path or 'input'} is valid ({self.schema_name})"
        lines = [f"FAIL: {self.file_path or 'input'} has {len(self.errors)} error(s) ({self.schema_name})"]
        for err in self.errors:
            lines.append(f"  - {err.path}: {err.message}")
        return "\n".join(lines)


def _check_type(value: Any, expected: str | list[str]) -> bool:
    """Check if value matches expected JSON Schema type(s)."""
    type_map = {
        "string": str,
        "number": (int, float),
        "integer": int,
        "boolean": bool,
        "array": list,
        "object": dict,
        "null": type(None),
    }
    if isinstance(expected, list):
        return any(_check_type(value, t) for t in expected)
    return isinstance(value, type_map.get(expected, object))


def _validate_node(
    data: Any,
    schema: dict[str, Any],
    path: str,
    errors: list[ValidationError],
) -> None:
    """Recursively validate a data node against a schema node."""
    # type check
    if "type" in schema:
        if not _check_type(data, schema["type"]):
            errors.append(ValidationError(
                path=path,
                message=f"expected type '{schema['type']}', got '{type(data).__name__}'",
                value=data,
            ))
            return

    # enum
    if "enum" in schema:
        if data not in schema["enum"]:
            errors.append(ValidationError(
                path=path,
                message=f"value must be one of {schema['enum']}",
                value=data,
            ))

    # object properties
    if schema.get("type") == "object" and isinstance(data, dict):
        # required
        for key in schema.get("required", []):
            if key not in data:
                errors.append(ValidationError(
                    path=f"{path}.{key}",
                    message="required field is missing",
                ))

        # properties
        props = schema.get("properties", {})
        for key, prop_schema in props.items():
            if key in data:
                _validate_node(data[key], prop_schema, f"{path}.{key}", errors)

        # additionalProperties
        if schema.get("additionalProperties") is False:
            allowed = set(props.keys())
            for key in data:
                if key not in allowed:
                    errors.append(ValidationError(
                        path=f"{path}.{key}",
                        message="unexpected additional property",
                    ))

    # array items
    if schema.get("type") == "array" and isinstance(data, list):
        items_schema = schema.get("items")
        if items_schema:
            for i, item in enumerate(data):
                _validate_node(item, items_schema, f"{path}[{i}]", errors)

        # minItems / maxItems
        if "minItems" in schema and len(data) < schema["minItems"]:
            errors.append(ValidationError(
                path=path,
                message=f"array must have at least {schema['minItems']} items, got {len(data)}",
            ))
        if "maxItems" in schema and len(data) > schema["maxItems"]:
            errors.append(ValidationError(
                path=path,
                message=f"array must have at most {schema['maxItems']} items, got {len(data)}",
            ))

    # string constraints
    if schema.get("type") == "string" and isinstance(data, str):
        if "minLength" in schema and len(data) < schema["minLength"]:
            errors.append(ValidationError(
                path=path,
                message=f"string must be at least {schema['minLength']} characters",
                value=data,
            ))


def validate(data: Any, schema: dict[str, Any], schema_name: str = "") -> ValidationResult:
    """Validate data against a JSON schema.

    Args:
        data: The data to validate.
        schema: JSON Schema dict.
        schema_name: Optional name for error reporting.

    Returns:
        ValidationResult with errors (if any).
    """
    errors: list[ValidationError] = []
    _validate_node(data, schema, "$", errors)
    return ValidationResult(valid=len(errors) == 0, errors=errors, schema_name=schema_name)


def validate_file(file_path: str | Path, schema: dict[str, Any], schema_name: str = "") -> ValidationResult:
    """Validate a JSON file against a schema.

    Args:
        file_path: Path to the JSON file.
        schema: JSON Schema dict.
        schema_name: Optional name for error reporting.

    Returns:
        ValidationResult with file_path set.
    """
    path = Path(file_path)
    if not path.exists():
        return ValidationResult(
            valid=False,
            errors=[ValidationError(path="$", message=f"file not found: {path}")],
            schema_name=schema_name,
            file_path=str(path),
        )

    try:
        import yaml
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except ImportError:
        return ValidationResult(
            valid=False,
            errors=[ValidationError(path="$", message="PyYAML is required: pip install PyYAML")],
            schema_name=schema_name,
            file_path=str(path),
        )
    except yaml.YAMLError as e:
        return ValidationResult(
            valid=False,
            errors=[ValidationError(path="$", message=f"invalid YAML: {e}")],
            schema_name=schema_name,
            file_path=str(path),
        )

    result = validate(data, schema, schema_name)
    result.file_path = str(path)
    return result


def load_schema(schema_path: str | Path) -> dict[str, Any]:
    """Load a JSON Schema from file."""
    path = Path(schema_path)
    return json.loads(path.read_text(encoding="utf-8"))


def get_builtin_schema(name: str) -> dict[str, Any]:
    """Load a built-in schema by name.

    Searches in order:
    1. schemas/ directory (e.g., schemas/checklist.json)
    2. templates/<name>/schema.json (co-located per-template schema)

    Args:
        name: Schema name (e.g., 'checklist', 'test_spec', 'test_prereq').

    Returns:
        Schema dict.

    Raises:
        FileNotFoundError: If schema not found.
    """
    pkg_dir = Path(__file__).parent

    # 1. Central schemas directory
    schema_path = pkg_dir / "schemas" / f"{name}.json"
    if schema_path.exists():
        return load_schema(schema_path)

    # 2. Per-template schema (templates/<name>/schema.json)
    template_schema = pkg_dir / "templates" / name / "schema.json"
    if template_schema.exists():
        return load_schema(template_schema)

    available = [p.stem for p in (pkg_dir / "schemas").glob("*.json")]
    # Also list template dirs that have schema.json
    templates_dir = pkg_dir / "templates"
    if templates_dir.exists():
        for d in templates_dir.iterdir():
            if d.is_dir() and (d / "schema.json").exists() and d.name not in available:
                available.append(d.name)

    raise FileNotFoundError(
        f"Schema '{name}' not found. Available: {sorted(available)}"
    )


def detect_schema(data: dict[str, Any]) -> str | None:
    """Auto-detect document type from data structure.

    Returns:
        Schema name or None if unrecognized.
    """
    if "categories" in data and "templates" in data:
        return "checklist"
    if "test_name" in data and "summary" in data and "risk_map" in data:
        return "test_prereq"
    if isinstance(data.get("test_cases"), list):
        return "test_spec"
    if "attendees" in data and "agenda" in data:
        return "agenda"
    return None
