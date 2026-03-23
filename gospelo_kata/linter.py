# KATA Markdown™ — gospelo-kata
# Copyright (c) 2025 gospelo. All rights reserved.
# Licensed under the MIT License. See LICENSE.md for details.

"""Linter for .kata.md template files.

Checks:
- Schema syntax: {#schema ... #} JSON validity, file reference existence
- Prompt block: {#prompt ... #} presence (required for templates)
- Template syntax: unclosed {% for %} / {% if %} blocks, nesting errors
- Variable references: {{ var }} existence in schema properties
- Filter validity: {{ x | filter }} references a known built-in filter
- Unused properties: schema properties not referenced in template
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class LintMessage:
    """A single lint finding."""

    level: str  # "error" | "warning" | "info"
    line: int
    column: int
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.level.upper()} [{self.code}] line {self.line}:{self.column} — {self.message}"


@dataclass
class LintResult:
    """Aggregated lint results for a file."""

    file_path: str = ""
    messages: list[LintMessage] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for m in self.messages if m.level == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for m in self.messages if m.level == "warning")

    @property
    def ok(self) -> bool:
        return self.error_count == 0

    def summary(self, fmt: str = "human") -> str:
        """Format lint results.

        Args:
            fmt: Output format.
                "human" — readable summary (default)
                "vscode" — file:line:col: level [code] message (VS Code Problem Matcher compatible)
        """
        fp = self.file_path or "input"
        if fmt == "vscode":
            if not self.messages:
                return ""
            lines = []
            for m in self.messages:
                lines.append(f"{fp}:{m.line}:{m.column}: {m.level} [{m.code}] {m.message}")
            return "\n".join(lines)

        # human format
        if not self.messages:
            return f"OK: {fp} — no issues found"
        lines = [f"{fp}: {self.error_count} error(s), {self.warning_count} warning(s)"]
        for m in self.messages:
            lines.append(f"  {m}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Line/column tracking
# ---------------------------------------------------------------------------

def _line_col(text: str, pos: int) -> tuple[int, int]:
    """Convert a character offset to (line, column) — both 1-based."""
    line = text[:pos].count("\n") + 1
    last_nl = text.rfind("\n", 0, pos)
    col = pos - last_nl  # 1-based
    return line, col


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def _check_schema(text: str, file_path: str | None, messages: list[LintMessage]) -> dict[str, Any] | None:
    """Check schema block syntax and return parsed schema if valid.

    Supports JSON and YAML in all schema forms:
    - Inline: {#schema ... #}
    - Code block: ```yaml:schema ... ``` or ```json:schema ... ```
    - File reference: {#schema: path #}
    - Markdown link: [kata-schema](path)
    """
    from .template import (
        _SCHEMA_INLINE_PATTERN, _SCHEMA_REF_PATTERN,
        _SCHEMA_LINK_PATTERN, _SCHEMA_CODEBLOCK_PATTERN,
        _SCHEMA_BOLD_CODEBLOCK_PATTERN,
        _parse_schema_content,
    )

    def _validate_parsed(schema: Any, line: int, col: int) -> dict[str, Any] | None:
        if not isinstance(schema, dict):
            messages.append(LintMessage(
                level="error", line=line, column=col,
                code="S002", message="Schema must be a mapping (object)",
            ))
            return None
        if "type" not in schema:
            messages.append(LintMessage(
                level="warning", line=line, column=col,
                code="S003", message="Schema has no 'type' field",
            ))
        return schema

    def _try_parse_content(content: str, line: int, col: int, source: str = "") -> dict[str, Any] | None:
        try:
            schema = _parse_schema_content(content)
        except ValueError as e:
            messages.append(LintMessage(
                level="error", line=line, column=col,
                code="S001", message=f"Invalid schema{source}: {e}",
            ))
            return None
        return _validate_parsed(schema, line, col)

    def _try_load_file(ref_path_str: str, line: int, col: int) -> dict[str, Any] | None:
        ref_path = ref_path_str.strip()
        if file_path:
            schema_path = Path(file_path).parent / ref_path
        else:
            schema_path = Path(ref_path)
        if not schema_path.exists():
            messages.append(LintMessage(
                level="error", line=line, column=col,
                code="S004", message=f"Schema file not found: {schema_path}",
            ))
            return None
        return _try_parse_content(
            schema_path.read_text(encoding="utf-8"), line, col,
            source=f" in {schema_path}",
        )

    # Code block form: ```yaml:schema ... ``` or ```json:schema ... ```
    match = _SCHEMA_CODEBLOCK_PATTERN.search(text)
    if match:
        line, col = _line_col(text, match.start())
        return _try_parse_content(match.group(1), line, col)

    # Bold-heading code block form: **Schema**\n```yaml\n...\n```
    match = _SCHEMA_BOLD_CODEBLOCK_PATTERN.search(text)
    if match:
        line, col = _line_col(text, match.start())
        return _try_parse_content(match.group(1), line, col)

    # Inline schema: {#schema ... #}
    match = _SCHEMA_INLINE_PATTERN.search(text)
    if match:
        line, col = _line_col(text, match.start())
        return _try_parse_content(match.group(1), line, col)

    # File reference: {#schema: path #}
    match = _SCHEMA_REF_PATTERN.search(text)
    if match:
        line, col = _line_col(text, match.start())
        return _try_load_file(match.group(1), line, col)

    # Markdown link form: [kata-schema](path)
    match = _SCHEMA_LINK_PATTERN.search(text)
    if match:
        line, col = _line_col(text, match.start())
        return _try_load_file(match.group(1), line, col)

    # No schema defined
    messages.append(LintMessage(
        level="info", line=1, column=1,
        code="S000", message="No schema defined (neither inline nor file reference)",
    ))
    return None


def _check_block_nesting(text: str, messages: list[LintMessage]) -> None:
    """Check {% for %} / {% if %} block nesting and closure."""
    block_pattern = re.compile(r"\{%(.*?)%\}", re.DOTALL)
    stack: list[tuple[str, int, int]] = []  # (tag, line, col)

    for m in block_pattern.finditer(text):
        content = m.group(1).strip()
        tag = content.split()[0] if content else ""
        line, col = _line_col(text, m.start())

        if tag in ("for", "if"):
            stack.append((tag, line, col))

        elif tag == "elif":
            if not stack or stack[-1][0] != "if":
                messages.append(LintMessage(
                    level="error", line=line, column=col,
                    code="T002", message="{% elif %} without matching {% if %}",
                ))

        elif tag == "else":
            if not stack or stack[-1][0] not in ("if", "for"):
                messages.append(LintMessage(
                    level="error", line=line, column=col,
                    code="T003", message="{% else %} without matching {% if %} or {% for %}",
                ))

        elif tag == "endif":
            if not stack or stack[-1][0] != "if":
                messages.append(LintMessage(
                    level="error", line=line, column=col,
                    code="T004", message="{% endif %} without matching {% if %}",
                ))
            else:
                stack.pop()

        elif tag == "endfor":
            if not stack or stack[-1][0] != "for":
                messages.append(LintMessage(
                    level="error", line=line, column=col,
                    code="T005", message="{% endfor %} without matching {% for %}",
                ))
            else:
                stack.pop()

        elif tag not in ("", "raw", "endraw", "set", "block", "endblock",
                         "extends", "include", "macro", "endmacro", "call",
                         "endcall", "filter", "endfilter"):
            messages.append(LintMessage(
                level="warning", line=line, column=col,
                code="T006", message=f"Unknown block tag: {{% {tag} %}}",
            ))

    # Unclosed blocks
    for tag, line, col in stack:
        end_tag = "endif" if tag == "if" else "endfor"
        messages.append(LintMessage(
            level="error", line=line, column=col,
            code="T001", message=f"{{% {tag} %}} opened here but never closed (missing {{% {end_tag} %}})",
        ))


def _collect_template_vars(text: str) -> list[tuple[str, int, int]]:
    """Collect all variable names referenced in {{ ... }} expressions.

    Returns list of (root_var_name, line, col).
    """
    var_pattern = re.compile(r"\{\{(.*?)\}\}", re.DOTALL)
    results: list[tuple[str, int, int]] = []

    for m in var_pattern.finditer(text):
        expr = m.group(1).strip()
        line, col = _line_col(text, m.start())
        # Extract root variable name (before ., [, |)
        root = re.split(r"[.\[| ]", expr)[0].strip()
        if root and not _is_literal(root):
            results.append((root, line, col))

    return results


def _collect_for_vars(text: str) -> set[str]:
    """Collect all loop variable names from {% for x in ... %} blocks."""
    for_pattern = re.compile(r"\{%\s*for\s+(.+?)\s+in\s+", re.DOTALL)
    loop_vars: set[str] = set()
    for m in for_pattern.finditer(text):
        var_part = m.group(1).strip()
        for v in var_part.split(","):
            loop_vars.add(v.strip())
    # Always available
    loop_vars.add("loop")
    return loop_vars


def _is_literal(name: str) -> bool:
    """Check if a name is a literal value rather than a variable."""
    if name in ("true", "false", "True", "False", "none", "None", "not"):
        return True
    try:
        float(name)
        return True
    except ValueError:
        pass
    if (name.startswith('"') and name.endswith('"')) or \
       (name.startswith("'") and name.endswith("'")):
        return True
    return False


def _get_schema_properties(schema: dict[str, Any], prefix: str = "") -> set[str]:
    """Recursively collect property names from a JSON Schema."""
    props: set[str] = set()
    for key in schema.get("properties", {}):
        full = f"{prefix}.{key}" if prefix else key
        props.add(key)  # root name
        props.add(full)  # dotted path
        sub_schema = schema["properties"][key]
        if sub_schema.get("type") == "object":
            props.update(_get_schema_properties(sub_schema, full))
        elif sub_schema.get("type") == "array" and "items" in sub_schema:
            items_schema = sub_schema["items"]
            if items_schema.get("type") == "object":
                # Items properties are accessed via loop vars, not directly
                for item_key in items_schema.get("properties", {}):
                    props.add(item_key)
    return props


def _check_var_references(
    text: str,
    schema: dict[str, Any] | None,
    messages: list[LintMessage],
) -> None:
    """Check that {{ var }} references exist in schema properties."""
    if schema is None:
        return

    schema_props = _get_schema_properties(schema)
    template_vars = _collect_template_vars(text)
    for_vars = _collect_for_vars(text)

    for var_name, line, col in template_vars:
        if var_name in for_vars:
            continue
        if var_name not in schema_props:
            messages.append(LintMessage(
                level="warning", line=line, column=col,
                code="V001", message=f"Variable '{{{{ {var_name} }}}}' not found in schema properties",
            ))


def _check_unused_properties(
    text: str,
    schema: dict[str, Any] | None,
    messages: list[LintMessage],
) -> None:
    """Check for schema properties not referenced in the template."""
    if schema is None:
        return

    props = schema.get("properties", {})
    # Exclude properties marked with "x-kata-meta": true
    top_level_props = {k for k, v in props.items() if not v.get("x-kata-meta")}
    if not top_level_props:
        return

    template_vars = {name for name, _, _ in _collect_template_vars(text)}

    # Also check for vars used in {% for x in PROP %} or {% if PROP %}
    block_pattern = re.compile(r"\{%(.*?)%\}", re.DOTALL)
    for m in block_pattern.finditer(text):
        content = m.group(1).strip()
        # Extract variable references from block tags
        words = re.findall(r"[a-zA-Z_]\w*", content)
        template_vars.update(words)

    unused = top_level_props - template_vars
    if unused:
        messages.append(LintMessage(
            level="info", line=1, column=1,
            code="V002", message=f"Unused schema properties: {', '.join(sorted(unused))}",
        ))


# ---------------------------------------------------------------------------
# Prompt injection detection
# ---------------------------------------------------------------------------

_PROMPT_INJECTION_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # Role/identity override
    (re.compile(r"you\s+are\s+(now|a|an)\b", re.IGNORECASE),
     "role override attempt ('you are now/a/an ...')"),
    (re.compile(r"act\s+as\s+(a|an|if)\b", re.IGNORECASE),
     "role override attempt ('act as ...')"),
    (re.compile(r"pretend\s+(to\s+be|you\s+are)\b", re.IGNORECASE),
     "role override attempt ('pretend to be ...')"),
    # Instruction override
    (re.compile(r"ignore\s+(all\s+)?(previous|above|prior|earlier)\s+(instructions?|rules?|prompts?)", re.IGNORECASE),
     "instruction override attempt ('ignore previous instructions')"),
    (re.compile(r"disregard\s+(all\s+)?(previous|above|prior|earlier)", re.IGNORECASE),
     "instruction override attempt ('disregard previous ...')"),
    (re.compile(r"forget\s+(all\s+)?(previous|above|prior|earlier)", re.IGNORECASE),
     "instruction override attempt ('forget previous ...')"),
    (re.compile(r"override\s+(the\s+)?(system|instructions?|rules?)", re.IGNORECASE),
     "instruction override attempt ('override system/instructions')"),
    # System prompt extraction
    (re.compile(r"(show|reveal|print|output|display|repeat)\s+(your\s+)?(system\s+prompt|instructions|rules)", re.IGNORECASE),
     "system prompt extraction attempt"),
    (re.compile(r"what\s+(are|is)\s+your\s+(system\s+)?(prompt|instructions|rules)", re.IGNORECASE),
     "system prompt extraction attempt"),
    # Command execution
    (re.compile(r"(execute|run|eval)\s+(this\s+)?(command|shell|script|code|bash|python)", re.IGNORECASE),
     "command execution attempt"),
    (re.compile(r"(os\.system|subprocess|exec|eval)\s*\(", re.IGNORECASE),
     "code execution pattern"),
    # Special tokens / delimiters
    (re.compile(r"<\|im_start\|>|<\|im_end\|>|<\|endoftext\|>"),
     "chat-ML delimiter injection"),
    (re.compile(r"\[INST\]|\[/INST\]|<<SYS>>|<</SYS>>"),
     "Llama-style delimiter injection"),
    # Data exfiltration
    (re.compile(r"(send|post|upload|transmit|exfiltrate)\s+(to|data|the|all)", re.IGNORECASE),
     "potential data exfiltration instruction"),
    # Credential / secret access
    (re.compile(r"(access|read|show|print|display|reveal)\s+(the\s+|your\s+|my\s+)?(api[_\s]?key|secret|password|credential|token|env)", re.IGNORECASE),
     "credential access attempt"),
]


def detect_prompt_injection(prompt_content: str) -> list[dict]:
    """Scan prompt content for injection patterns.

    Returns a list of dicts with keys: 'pattern', 'description', 'line_offset', 'match'.
    """
    hits: list[dict] = []
    lines = prompt_content.split("\n")
    for line_idx, line in enumerate(lines):
        for pattern, description in _PROMPT_INJECTION_PATTERNS:
            m = pattern.search(line)
            if m:
                hits.append({
                    "pattern": pattern.pattern,
                    "description": description,
                    "line_offset": line_idx,
                    "match": m.group(0),
                })
    return hits


def _check_prompt_block(text: str, messages: list[LintMessage]) -> None:
    """Check that a {#prompt} block is present in the template."""
    from .template import _PROMPT_PATTERN, _PROMPT_CODEBLOCK_PATTERN

    prompt_match = _PROMPT_PATTERN.search(text)
    if not prompt_match:
        prompt_match = _PROMPT_CODEBLOCK_PATTERN.search(text)

    if not prompt_match:
        messages.append(LintMessage(
            level="warning", line=1, column=1,
            code="P001", message="No {#prompt} block found — templates must include a prompt block for AI guidance",
        ))
        return

    # P002: Check for prompt injection patterns
    prompt_content = prompt_match.group(1)
    prompt_start_line, _ = _line_col(text, prompt_match.start(1))
    for hit in detect_prompt_injection(prompt_content):
        line = prompt_start_line + hit["line_offset"]
        messages.append(LintMessage(
            level="warning", line=line, column=1,
            code="P002",
            message=f"Suspicious prompt content detected: {hit['description']}",
        ))


def _check_filters(text: str, messages: list[LintMessage]) -> None:
    """Check that filters referenced in {{ ... | filter }} are known."""
    from .template import _BUILTIN_FILTERS

    var_pattern = re.compile(r"\{\{(.*?)\}\}", re.DOTALL)

    for m in var_pattern.finditer(text):
        expr = m.group(1).strip()
        line, col = _line_col(text, m.start())

        # Split by pipe
        parts = expr.split("|")
        if len(parts) <= 1:
            continue

        for filter_part in parts[1:]:
            filter_part = filter_part.strip()
            # Extract filter name (before parentheses)
            filter_name = re.split(r"[\s(]", filter_part)[0].strip()
            if filter_name and filter_name not in _BUILTIN_FILTERS:
                messages.append(LintMessage(
                    level="error", line=line, column=col,
                    code="F001", message=f"Unknown filter: '{filter_name}'",
                ))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _parse_disable_comments(text: str) -> set[str]:
    """Parse <!-- kata-lint-disable CODE1 CODE2 ... --> comments.

    Returns set of disabled rule codes.
    """
    disabled: set[str] = set()
    for m in re.finditer(r"<!--\s*kata-lint-disable\s+([\w\s,]+)\s*-->", text):
        for code in re.findall(r"[A-Z]\d+", m.group(1)):
            disabled.add(code)
    return disabled


def lint(text: str, file_path: str | None = None) -> LintResult:
    """Lint a .kata.md template string.

    Args:
        text: Template source text.
        file_path: Optional file path (for schema file resolution and reporting).

    Returns:
        LintResult with all findings.
    """
    result = LintResult(file_path=file_path or "")
    messages = result.messages

    # Parse disable comments
    disabled = _parse_disable_comments(text)

    # 1. Schema check
    schema = _check_schema(text, file_path, messages)

    # 2. Block nesting check
    _check_block_nesting(text, messages)

    # 3. Filter check
    _check_filters(text, messages)

    # 4. Prompt block check
    _check_prompt_block(text, messages)

    # 5. Variable reference check (requires schema)
    _check_var_references(text, schema, messages)

    # 6. Unused properties check (requires schema)
    _check_unused_properties(text, schema, messages)

    # Filter out disabled rules
    if disabled:
        result.messages = [m for m in messages if m.code not in disabled]

    # Sort by line number
    result.messages.sort(key=lambda m: (m.line, m.column))

    return result


def lint_file(file_path: str, schema_name: str | None = None) -> LintResult:
    """Lint a template or rendered document file.

    Automatically detects the mode:
    - Template mode (.kata.md or files with {# schema #} / {{ }} / {% %}):
      checks template syntax, filters, variable references.
    - Document mode (rendered .md with <!-- kata: {...} --> metadata):
      checks required sections and structure against the schema.

    Args:
        file_path: Path to the file.
        schema_name: Override schema name (e.g., "agenda"). If provided,
            forces document mode validation.

    Returns:
        LintResult with all findings.
    """
    path = Path(file_path)
    if not path.exists():
        result = LintResult(file_path=file_path)
        result.messages.append(LintMessage(
            level="error", line=1, column=1,
            code="E001", message=f"File not found: {file_path}",
        ))
        return result

    text = path.read_text(encoding="utf-8")

    # Detect mode: template has Jinja2-like syntax, document does not
    # Strip code blocks before checking — template syntax inside ``` blocks
    # (e.g. kata:template in Schema Reference) should not trigger template mode
    text_no_codeblocks = re.sub(r"```[^\n]*\n.*?```", "", text, flags=re.DOTALL)
    has_template_syntax = (
        "{#" in text_no_codeblocks
        or "{{" in text_no_codeblocks
        or "{%" in text_no_codeblocks
    )

    if schema_name:
        # Explicit schema → document mode
        return lint_document(text, schema_name, file_path=str(path))

    # Check for kata metadata comment → document mode
    from .generator.markdown import parse_kata_metadata
    meta = parse_kata_metadata(text)
    if meta and meta.get("schema"):
        return lint_document(text, meta["schema"], file_path=str(path))

    # Rendered output: has data-kata spans but no template syntax → document mode
    has_data_kata = 'data-kata="p-' in text
    if has_data_kata and not has_template_syntax:
        return lint_document(text, "", file_path=str(path))

    if has_template_syntax or file_path.endswith(".kata.md"):
        return lint(text, file_path=str(path))

    return lint(text, file_path=str(path))


# ---------------------------------------------------------------------------
# Document mode lint (rendered Markdown)
# ---------------------------------------------------------------------------

def _get_required_sections(schema: dict[str, Any]) -> list[str]:
    """Derive required Markdown sections (## headings) from schema properties."""
    sections: list[str] = []
    props = schema.get("properties", {})
    required = set(schema.get("required", []))

    for key in required:
        if key in props:
            prop = props[key]
            # Arrays and objects typically become sections
            if prop.get("type") in ("array", "object"):
                # Convert key to section title: snake_case → Title Case
                title = key.replace("_", " ").title()
                sections.append(title)
    return sections


def _extract_headings(text: str) -> list[tuple[str, int, int]]:
    """Extract Markdown headings from text.

    Returns list of (heading_text, level, line_number).
    """
    headings: list[tuple[str, int, int]] = []
    for i, line in enumerate(text.split("\n"), 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            # Count heading level
            level = 0
            for ch in stripped:
                if ch == "#":
                    level += 1
                else:
                    break
            title = stripped[level:].strip()
            headings.append((title, level, i))
    return headings


def lint_document(
    text: str,
    schema_name: str,
    file_path: str | None = None,
) -> LintResult:
    """Lint a rendered Markdown document against a schema.

    Checks:
    - Required sections (## headings) derived from schema required properties
    - Table column count consistency
    - Empty required sections
    - Annotation link targets: ``[value](#p-xxx)`` must have matching anchor
    - Orphan anchors: ``<a id="p-xxx">`` without any linking reference

    Args:
        text: Rendered Markdown text.
        schema_name: Schema name to validate against.
        file_path: Optional file path for reporting.

    Returns:
        LintResult with all findings.
    """
    result = LintResult(file_path=file_path or "")
    messages = result.messages

    # Load schema (optional — inline anchors can substitute)
    schema: dict[str, Any] | None = None
    try:
        from .validator import get_builtin_schema
        schema = get_builtin_schema(schema_name)
    except FileNotFoundError:
        has_schema_ref = "Schema Reference" in text and "**Schema**" in text
        if not has_schema_ref:
            messages.append(LintMessage(
                level="info", line=1, column=1,
                code="D001", message=f"External schema not found: {schema_name} — using inline anchors",
            ))

    # Check required sections (only when external schema available
    # AND the document has no inline anchors — template-generated docs
    # use dynamic headings that don't match static schema property names)
    headings = _extract_headings(text)
    has_inline_anchors = bool(
        re.search(r'<a\s+id="p-', text) or re.search(r'data-kata="p-', text)
    )
    if schema is not None and not has_inline_anchors:
        required_sections = _get_required_sections(schema)
        heading_titles = {h[0].lower() for h in headings}
        for section in required_sections:
            if section.lower() not in heading_titles:
                messages.append(LintMessage(
                    level="error", line=1, column=1,
                    code="D002",
                    message=f"Required section missing: '## {section}'",
                ))

    # Check table consistency
    _check_table_columns(text, messages)

    # Check empty sections
    _check_empty_sections(text, headings, messages)

    # Check annotation links (works with external schema AND/OR inline anchors)
    _check_annotation_links(text, schema, messages)

    # Check for HTML tags inside data-kata span values
    _check_html_in_spans(text, messages)

    # Check structural integrity of kata-card format
    if has_inline_anchors:
        _check_duplicate_anchors(text, messages)
        _check_card_structure(text, messages)
        _check_required_sections_present(text, messages)
        _check_unlinked_values(text, schema, messages)

    # Check structure integrity hash
    _check_structure_integrity(text, messages)

    # Filter out disabled rules
    disabled = _parse_disable_comments(text)
    if disabled:
        result.messages = [m for m in messages if m.code not in disabled]

    # Sort by line
    result.messages.sort(key=lambda m: (m.line, m.column))
    return result


def _mask_pipes_in_spans(line: str) -> str:
    """Replace pipe characters inside backticks and Jinja2 tags with a placeholder."""
    # Mask pipes inside backtick spans
    result = re.sub(r"`[^`]*`", lambda m: m.group().replace("|", "\x00"), line)
    # Mask pipes inside Jinja2 expression/statement tags
    result = re.sub(r"\{\{.*?\}\}", lambda m: m.group().replace("|", "\x00"), result)
    result = re.sub(r"\{%.*?%\}", lambda m: m.group().replace("|", "\x00"), result)
    return result


def _check_table_columns(text: str, messages: list[LintMessage]) -> None:
    """Check that tables have consistent column counts."""
    lines = text.split("\n")
    table_start: int | None = None
    expected_cols: int = 0

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            masked = _mask_pipes_in_spans(stripped)
            cells = [c.strip() for c in masked.split("|")[1:-1]]
            # Skip separator rows
            if all(c.replace("-", "").replace(":", "") == "" for c in cells):
                continue
            if table_start is None:
                table_start = i
                expected_cols = len(cells)
            else:
                if len(cells) != expected_cols:
                    messages.append(LintMessage(
                        level="warning", line=i, column=1,
                        code="D003",
                        message=f"Table column count mismatch: expected {expected_cols}, got {len(cells)} (table started at line {table_start})",
                    ))
        else:
            if table_start is not None:
                table_start = None
                expected_cols = 0


def _check_empty_sections(
    text: str,
    headings: list[tuple[str, int, int]],
    messages: list[LintMessage],
) -> None:
    """Check for sections with no content between headings."""
    lines = text.split("\n")
    for idx, (title, level, line_num) in enumerate(headings):
        # Skip H1 followed by H2 — this is a normal document structure
        if level == 1 and idx + 1 < len(headings) and headings[idx + 1][1] == 2:
            continue

        # Find next heading or end of file
        if idx + 1 < len(headings):
            next_line = headings[idx + 1][2]
        else:
            next_line = len(lines) + 1

        # Check if there's any non-empty content between this heading and the next
        content_lines = lines[line_num : next_line - 1]  # 0-based
        has_content = any(l.strip() for l in content_lines)

        if not has_content:
            messages.append(LintMessage(
                level="warning", line=line_num, column=1,
                code="D004",
                message=f"Empty section: '{title}'",
            ))


def _collect_schema_anchors(schema: dict[str, Any], prefix: str = "") -> set[str]:
    """Collect all valid anchor IDs that a schema would generate."""
    anchors: set[str] = set()
    props = schema.get("properties", {})
    for key, prop_schema in props.items():
        prop_path = f"{prefix}-{key}" if prefix else key
        anchor = "p-" + prop_path.replace("_", "-")
        anchors.add(anchor)

        prop_type = prop_schema.get("type", "")
        if prop_type == "object":
            anchors.update(_collect_schema_anchors(prop_schema, prop_path))
        elif prop_type == "array" and "items" in prop_schema:
            items_schema = prop_schema["items"]
            if items_schema.get("type") == "object":
                anchors.update(_collect_schema_anchors(items_schema, prop_path))
    return anchors


def _collect_schema_enums(schema: dict[str, Any], prefix: str = "") -> dict[str, list[str]]:
    """Collect anchor ID → enum values mapping from a JSON Schema.

    Returns dict like {"p-categories-items-status": ["draft", "pending", "approve", "reject"]}.
    """
    enums: dict[str, list[str]] = {}
    props = schema.get("properties", {})
    for key, prop_schema in props.items():
        prop_path = f"{prefix}-{key}" if prefix else key
        anchor = "p-" + prop_path.replace("_", "-")

        if "enum" in prop_schema:
            enums[anchor] = [str(v) for v in prop_schema["enum"]]

        prop_type = prop_schema.get("type", "")
        if prop_type == "object":
            enums.update(_collect_schema_enums(prop_schema, prop_path))
        elif prop_type == "array" and "items" in prop_schema:
            items_schema = prop_schema["items"]
            if items_schema.get("type") == "object":
                enums.update(_collect_schema_enums(items_schema, prop_path))
    return enums


@dataclass
class PropConstraints:
    """Constraints for a schema property (anchor ID)."""
    enum: list[str] | None = None
    min_length: int | None = None
    max_length: int | None = None
    min_items: int | None = None
    max_items: int | None = None


def _collect_schema_constraints(
    schema: dict[str, Any], prefix: str = ""
) -> dict[str, PropConstraints]:
    """Collect anchor ID → constraints mapping from a JSON Schema."""
    constraints: dict[str, PropConstraints] = {}
    props = schema.get("properties", {})
    for key, prop_schema in props.items():
        prop_path = f"{prefix}-{key}" if prefix else key
        anchor = "p-" + prop_path.replace("_", "-")

        c = PropConstraints()
        if "enum" in prop_schema:
            c.enum = [str(v) for v in prop_schema["enum"]]
        if "minLength" in prop_schema:
            c.min_length = prop_schema["minLength"]
        if "maxLength" in prop_schema:
            c.max_length = prop_schema["maxLength"]
        if "minItems" in prop_schema:
            c.min_items = prop_schema["minItems"]
        if "maxItems" in prop_schema:
            c.max_items = prop_schema["maxItems"]

        if any(v is not None for v in (c.enum, c.min_length, c.max_length, c.min_items, c.max_items)):
            constraints[anchor] = c

        prop_type = prop_schema.get("type", "")
        if prop_type == "object":
            constraints.update(_collect_schema_constraints(prop_schema, prop_path))
        elif prop_type == "array" and "items" in prop_schema:
            items_schema = prop_schema["items"]
            if items_schema.get("type") == "object":
                constraints.update(_collect_schema_constraints(items_schema, prop_path))
    return constraints


def _parse_inline_constraints(
    text: str,
    defined_anchors: set[str],
    constraints: dict[str, PropConstraints],
) -> None:
    """Parse constraint definitions from inline Schema Reference section.

    Looks for patterns like:
        #### <a id="p-categories-items-status"></a>categories-items-status
        - **type**: string **(required)**
        - **enum**: ['draft', 'pending', 'approve', 'reject']
        - **minLength**: 1
        - **maxLength**: 100
        - **minItems**: 1
        - **maxItems**: 10
    """
    lines = text.split("\n")
    current_anchor: str | None = None
    anchor_pattern = re.compile(r'<a\s+id="(p-[a-z0-9-]+)"')
    enum_pattern = re.compile(r"\*\*enum\*\*:\s*\[([^\]]+)\]")
    int_constraint_pattern = re.compile(
        r"\*\*(minLength|maxLength|minItems|maxItems)\*\*:\s*(\d+)"
    )

    for line in lines:
        am = anchor_pattern.search(line)
        if am:
            current_anchor = am.group(1)
            continue

        if current_anchor and current_anchor in defined_anchors:
            c = constraints.setdefault(current_anchor, PropConstraints())

            em = enum_pattern.search(line)
            if em and c.enum is None:
                c.enum = [v.strip().strip("'\"") for v in em.group(1).split(",")]

            im = int_constraint_pattern.search(line)
            if im:
                name, value = im.group(1), int(im.group(2))
                if name == "minLength" and c.min_length is None:
                    c.min_length = value
                elif name == "maxLength" and c.max_length is None:
                    c.max_length = value
                elif name == "minItems" and c.min_items is None:
                    c.min_items = value
                elif name == "maxItems" and c.max_items is None:
                    c.max_items = value


def _parse_shorthand_constraints(
    text: str,
    valid_anchors: set[str],
    constraints: dict[str, PropConstraints],
) -> None:
    """Parse Schema shorthand YAML block for type constraints.

    Handles nested arrays recursively, e.g.:
        categories[]!:
          items[]!:
            status: enum(draft, pending, approve, reject)
    → anchor p-categories-items-status with enum constraint.
    """
    schema_match = re.search(
        r"\*\*Schema\*\*\s*\n\s*```yaml\n([\s\S]*?)```", text
    )
    if not schema_match:
        return

    lines = schema_match.group(1).split("\n")

    def _parse_level(start: int, base_indent: int, parent_anchor: str) -> int:
        i = start
        while i < len(lines):
            line = lines[i]
            stripped = line.lstrip()
            if not stripped:
                i += 1
                continue
            indent = len(line) - len(stripped)
            if indent < base_indent:
                break

            # Array: name[]!:
            arr_match = re.match(r"^([a-z_][a-z0-9_]*)\[\](!)?:\s*$", stripped)
            if arr_match:
                name = arr_match.group(1)
                anchor_part = f"{parent_anchor}-{name}" if parent_anchor else name
                anchor_part = anchor_part.replace("_", "-")
                anchor = f"p-{anchor_part}"
                valid_anchors.add(anchor)
                i = _parse_level(i + 1, indent + 2, anchor_part)
                continue

            # Field: name: type
            field_match = re.match(r"^([a-z_][a-z0-9_]*):\s+(.+)$", stripped)
            if field_match:
                name = field_match.group(1)
                type_str = field_match.group(2).strip()
                required = type_str.endswith("!")
                if required:
                    type_str = type_str[:-1]

                anchor_part = f"{parent_anchor}-{name}" if parent_anchor else name
                anchor_part = anchor_part.replace("_", "-")
                anchor = f"p-{anchor_part}"
                valid_anchors.add(anchor)

                c = constraints.setdefault(anchor, PropConstraints())
                enum_match = re.match(r"^enum\((.+)\)$", type_str)
                if enum_match:
                    c.enum = [v.strip() for v in enum_match.group(1).split(",")]
                i += 1
                continue

            i += 1
        return i

    _parse_level(0, 0, "")


def _check_annotation_links(
    text: str,
    schema: dict[str, Any] | None,
    messages: list[LintMessage],
) -> None:
    """Check that annotation links [value](#p-xxx) reference valid schema properties.

    Valid anchors are derived from two sources:
    1. External JSON Schema (if provided) — via _collect_schema_anchors
    2. Inline anchor definitions in the document — <a id="p-...">
    Both are merged so that documents with a <details>Schema Reference</details>
    section work without requiring an external schema.json.
    """
    # Collect valid anchors from external schema
    valid_anchors: set[str] = set()
    if schema is not None:
        valid_anchors = _collect_schema_anchors(schema)

    # Also collect anchors defined inline in the document (<a id="p-...">)
    anchor_def_pattern = re.compile(r'<a\s+id="(p-[a-z0-9-]+)"')
    lines = text.split("\n")
    defined_anchors: set[str] = set()
    for line in lines:
        for m in anchor_def_pattern.finditer(line):
            defined_anchors.add(m.group(1))

    valid_anchors |= defined_anchors

    # Collect constraints from external schema
    constraint_map: dict[str, PropConstraints] = {}
    if schema is not None:
        constraint_map = _collect_schema_constraints(schema)

    # Also parse inline constraint definitions from Schema Reference section
    _parse_inline_constraints(text, defined_anchors, constraint_map)
    # Parse Schema shorthand block for constraints
    _parse_shorthand_constraints(text, valid_anchors, constraint_map)

    if not valid_anchors:
        return

    # Find all annotation props in the text and validate values
    # Supports both data-kata="p-xxx" and legacy [text](#p-xxx)
    prop_pattern = re.compile(r'<span\s+data-kata="(p-[a-z0-9-]+)">([^<]*)</span>')
    legacy_link_pattern = re.compile(r"\[([^\]]*)\]\(#(p-[a-z0-9-]+)\)")

    def _iter_annotations(line: str):
        for m in prop_pattern.finditer(line):
            yield m.group(1), m.group(2), m.start()
        for m in legacy_link_pattern.finditer(line):
            yield m.group(2), m.group(1), m.start()

    def _strip_indices(anchor: str) -> str:
        """Strip array indices from anchor: p-categories-0-items-0-status → p-categories-items-status"""
        return re.sub(r"-\d+", "", anchor)

    for line_num, line in enumerate(lines, 1):
        for anchor, link_text, start_pos in _iter_annotations(line):
            col = start_pos + 1
            # Match indexed anchors by stripping indices
            base_anchor = _strip_indices(anchor)
            if anchor not in valid_anchors and base_anchor not in valid_anchors:
                messages.append(LintMessage(
                    level="warning", line=line_num, column=col,
                    code="D005",
                    message=f"Annotation link '#{anchor}' does not match any schema property",
                ))
            elif (anchor in constraint_map or base_anchor in constraint_map) and link_text:
                c = constraint_map.get(anchor) or constraint_map.get(base_anchor)
                # D007: enum check
                if c.enum is not None and link_text not in c.enum:
                    messages.append(LintMessage(
                        level="warning", line=line_num, column=col,
                        code="D007",
                        message=f"Value '{link_text}' is not a valid enum value for #{anchor} (allowed: {', '.join(c.enum)})",
                    ))
                # D008: minLength check
                if c.min_length is not None and len(link_text) < c.min_length:
                    messages.append(LintMessage(
                        level="warning", line=line_num, column=col,
                        code="D008",
                        message=f"Value '{link_text}' is too short for #{anchor} (minLength: {c.min_length})",
                    ))
                # D009: maxLength check
                if c.max_length is not None and len(link_text) > c.max_length:
                    messages.append(LintMessage(
                        level="warning", line=line_num, column=col,
                        code="D009",
                        message=f"Value '{link_text}' exceeds maxLength for #{anchor} (maxLength: {c.max_length}, got: {len(link_text)})",
                    ))
                # D010: minItems / maxItems — link_text is comma-separated list
                if c.min_items is not None or c.max_items is not None:
                    items = [v.strip() for v in link_text.split(",") if v.strip()] if link_text else []
                    count = len(items)
                    if c.min_items is not None and count < c.min_items:
                        messages.append(LintMessage(
                            level="warning", line=line_num, column=col,
                            code="D010",
                            message=f"Too few items for #{anchor} (minItems: {c.min_items}, got: {count})",
                        ))
                    if c.max_items is not None and count > c.max_items:
                        messages.append(LintMessage(
                            level="warning", line=line_num, column=col,
                            code="D010",
                            message=f"Too many items for #{anchor} (maxItems: {c.max_items}, got: {count})",
                        ))

    # Check for defined anchors not referenced by any annotation
    referenced_anchors: set[str] = set()
    for line in lines:
        for anchor, _, _ in _iter_annotations(line):
            referenced_anchors.add(anchor)

    # An anchor is "covered" if it is directly referenced OR if any
    # child anchor (longer prefix) is referenced.
    # e.g., p-categories is covered when p-categories-id is referenced.
    covered_anchors: set[str] = set(referenced_anchors)
    for ref in referenced_anchors:
        # Mark all parent prefixes as covered
        parts = ref.split("-")
        for i in range(2, len(parts)):  # start at 2 to skip "p-" prefix minimum
            parent = "-".join(parts[:i])
            covered_anchors.add(parent)

    # Only report orphans for anchors actually defined in the document,
    # not those derived solely from the external schema.
    orphan = (defined_anchors - covered_anchors)
    if orphan:
        messages.append(LintMessage(
            level="info", line=1, column=1,
            code="D006",
            message=f"Schema properties with no annotation links: {', '.join(sorted(orphan))}",
        ))


def _check_duplicate_anchors(text: str, messages: list[LintMessage]) -> None:
    """D011: Check for duplicate data-kata anchor IDs."""
    pattern = re.compile(r'data-kata="(p-[a-z0-9-]+)"')
    seen: dict[str, int] = {}  # anchor → first line number
    for line_num, line in enumerate(text.split("\n"), 1):
        for m in pattern.finditer(line):
            anchor = m.group(1)
            if anchor in seen:
                messages.append(LintMessage(
                    level="warning", line=line_num, column=m.start() + 1,
                    code="D011",
                    message=f"Duplicate anchor '{anchor}' (first seen at line {seen[anchor]})",
                ))
            else:
                seen[anchor] = line_num


# ---------------------------------------------------------------------------
# HTML safety checks for data-kata spans
# ---------------------------------------------------------------------------

_RAW_SPAN_PATTERN = re.compile(
    r'<span\s+data-kata="(p-[a-z0-9-]+)">(.*?)</span>'
)
def _check_structure_integrity(text: str, messages: list[LintMessage]) -> None:
    """D017: Verify structure integrity hash in the Schema Reference section.

    The hash covers Prompt, kata:template, and Schema blocks but excludes
    the Data block — so data changes are allowed without invalidating the
    hash.  A mismatch indicates the template structure has been modified
    after rendering.
    """
    from .template import _STRUCTURE_INTEGRITY_PATTERN, _compute_structure_hash

    # Extract <details> section content
    details_match = re.search(
        r"<details>\s*\n\s*<summary>.*?</summary>\s*\n(.*?)<!-- kata-structure-integrity:",
        text,
        re.DOTALL,
    )
    hash_match = _STRUCTURE_INTEGRITY_PATTERN.search(text)

    if hash_match is None:
        # No hash present — skip (backward compat with older documents)
        return

    if details_match is None:
        return

    stored_hash = hash_match.group(1)
    details_inner = details_match.group(1)
    computed_hash = _compute_structure_hash(details_inner)

    if computed_hash != stored_hash:
        line = text[:hash_match.start()].count("\n") + 1
        messages.append(LintMessage(
            level="warning", line=line, column=1,
            code="D017",
            message=(
                "Structure integrity hash mismatch — "
                "Prompt, template body, or Schema may have been modified after rendering"
            ),
        ))


_HTML_TAG_PATTERN = re.compile(r"<[a-zA-Z/][^>]*>")


def _check_html_in_spans(text: str, messages: list[LintMessage]) -> None:
    """D016: Detect HTML tags inside data-kata span values.

    Values bound via ``data-kata`` must be plain text. Embedded HTML tags
    break the extract round-trip (``[^<]*`` regex) and can pose XSS risk
    when the document is rendered in a browser.
    """
    lines = text.split("\n")
    for line_num, line in enumerate(lines, 1):
        for m in _RAW_SPAN_PATTERN.finditer(line):
            anchor = m.group(1)
            content = m.group(2)
            html_match = _HTML_TAG_PATTERN.search(content)
            if html_match:
                col = m.start() + 1
                tag = html_match.group(0)
                messages.append(LintMessage(
                    level="error", line=line_num, column=col,
                    code="D016",
                    message=(
                        f"HTML tag '{tag}' in data-kata span '{anchor}'"
                        " — value must be plain text"
                        " (use &lt; &gt; or run formatter to sanitize)"
                    ),
                ))


# ---------------------------------------------------------------------------
# Structural integrity checks for hand-edited documents
# ---------------------------------------------------------------------------



def _extract_card_blocks(text: str) -> list[tuple[int, str, str]]:
    """Extract kata-card blocks handling nested tags.

    Returns list of (line_number, tag_name, card_content) tuples.
    Handles nested tables (e.g. kata-props inside kata-card).
    """
    lines = text.split("\n")
    cards: list[tuple[int, str, str]] = []
    card_start_line = 0
    card_tag = ""
    card_lines: list[str] = []
    depth = 0

    for line_num, line in enumerate(lines, 1):
        if depth == 0 and 'class="kata-card"' in line:
            card_tag = "table" if "<table" in line else "div"
            card_start_line = line_num
            card_lines = [line]
            depth = 1
        elif depth > 0:
            card_lines.append(line)
            close_tag = "</table>" if card_tag == "table" else "</div>"
            open_tag = "<table" if card_tag == "table" else "<div"
            depth += line.count(open_tag)
            depth -= line.count(close_tag)
            if depth <= 0:
                cards.append((card_start_line, card_tag, "\n".join(card_lines)))
                depth = 0

    return cards


def _check_card_structure(text: str, messages: list[LintMessage]) -> None:
    """D012: Check kata-card structure integrity.

    Supports both v1 (<table>) and v2 (<div>) card layouts.
    Detects:
        - Unclosed card containers
        - Missing kata-left / kata-right sections
    """
    cards = _extract_card_blocks(text)

    # Check for unclosed cards
    open_count = text.count('class="kata-card"')
    if open_count > len(cards):
        # Find unclosed card positions
        for m in re.finditer(r'class="kata-card"', text):
            pos = m.start()
            card_line, _ = _line_col(text, pos)
            if not any(cl == card_line for cl, _, _ in cards):
                messages.append(LintMessage(
                    level="error", line=card_line, column=1,
                    code="D012",
                    message="kata-card is never closed",
                ))

    # Check each card has kata-left and kata-right
    for card_line, _tag, card_text in cards:
        if 'class="kata-left"' not in card_text:
            messages.append(LintMessage(
                level="warning", line=card_line, column=1,
                code="D012",
                message="Card is missing kata-left section",
            ))
        if 'class="kata-right"' not in card_text:
            messages.append(LintMessage(
                level="warning", line=card_line, column=1,
                code="D012",
                message="Card is missing kata-right section",
            ))


def _check_required_sections_present(text: str, messages: list[LintMessage]) -> None:
    """D014: Check that <details>Schema Reference and <style> sections exist.

    The <style> check is relaxed when the document has a theme metadata field
    (e.g. <!-- kata: {"theme": "default"} -->), indicating CSS is externalized.
    """
    if "<details>" not in text:
        messages.append(LintMessage(
            level="warning", line=1, column=1,
            code="D014",
            message="Missing <details> section (Schema Reference)",
        ))
    if "<style>" not in text:
        # Check for theme metadata — if present, CSS is externalized
        has_theme_meta = bool(re.search(r'<!--\s*kata:.*?"theme":', text))
        if not has_theme_meta:
            messages.append(LintMessage(
                level="warning", line=1, column=1,
                code="D014",
                message="Missing <style> section (use inline CSS or set theme in metadata)",
            ))


def _check_unlinked_values(
    text: str,
    schema: dict[str, Any] | None,
    messages: list[LintMessage],
) -> None:
    """D015: Detect enum-like values in card tables that lost their annotation links.

    When someone hand-edits [approve](#p-categories-items-status) to just "approve",
    the document loses its type link. This checks table cells for bare enum values.
    """
    # Collect all known enum values from schema
    enum_values: set[str] = set()
    if schema is not None:
        for _anchor, constraint in _collect_schema_constraints(schema).items():
            if constraint.enum:
                enum_values.update(constraint.enum)

    if not enum_values:
        return

    lines = text.split("\n")
    annotated_pattern = re.compile(r'data-kata="p-[a-z0-9-]+">[^<]*</span>|\[[^\]]*\]\(#p-[a-z0-9-]+\)')
    in_card = False
    card_depth = 0
    card_is_table = False

    for line_num, line in enumerate(lines, 1):
        if card_depth == 0 and 'class="kata-card"' in line:
            in_card = True
            card_is_table = "<table" in line
            card_depth = 1
        elif in_card:
            close_tag = "</table>" if card_is_table else "</div>"
            open_tag = "<table" if card_is_table else "<div"
            card_depth += line.count(open_tag)
            card_depth -= line.count(close_tag)
            if card_depth <= 0:
                in_card = False

        if not in_card or not line.strip().startswith("|"):
            continue

        # Split table cells
        cells = line.split("|")
        for cell in cells:
            cell_stripped = cell.strip()
            # Skip cells that already have annotations
            if annotated_pattern.search(cell):
                continue
            # Check if cell contains a bare enum value (possibly inside <span>)
            # Strip HTML tags to get the text content
            text_content = re.sub(r"<[^>]+>", "", cell_stripped).strip()
            if text_content in enum_values:
                messages.append(LintMessage(
                    level="warning", line=line_num, column=1,
                    code="D015",
                    message=f"Bare value '{text_content}' in table — should be annotated with data-kata",
                ))
