# KATA Markdown™ — gospelo-kata
# Copyright (c) 2025 gospelo. All rights reserved.
# Licensed under the MIT License. See LICENSE.md for details.

"""Tests for gospelo_kata.linter."""

from __future__ import annotations

import json
import os
import tempfile

import pytest

from gospelo_kata.linter import lint, lint_file


# ---------------------------------------------------------------------------
# Schema checks
# ---------------------------------------------------------------------------

class TestSchemaChecks:
    def test_no_schema_info(self):
        result = lint("# Hello {{ name }}")
        assert result.ok
        codes = [m.code for m in result.messages]
        assert "S000" in codes  # info: no schema

    def test_valid_inline_schema(self):
        source = '{#schema\n{"type": "object", "properties": {"x": {"type": "string"}}}\n#}\n{{ x }}'
        result = lint(source)
        assert result.ok
        assert "S001" not in [m.code for m in result.messages]

    def test_invalid_json_schema(self):
        source = '{#schema\n{invalid json}\n#}\n{{ x }}'
        result = lint(source)
        assert not result.ok
        assert "S001" in [m.code for m in result.messages]

    def test_schema_not_object(self):
        source = '{#schema\n[1, 2, 3]\n#}\n{{ x }}'
        result = lint(source)
        assert not result.ok
        assert "S002" in [m.code for m in result.messages]

    def test_schema_missing_type(self):
        source = '{#schema\n{"properties": {"x": {"type": "string"}}}\n#}\n{{ x }}'
        result = lint(source)
        codes = [m.code for m in result.messages]
        assert "S003" in codes  # warning

    def test_schema_file_not_found(self):
        source = "{#schema: nonexistent.json #}\n{{ x }}"
        result = lint(source, file_path="/tmp/test.kata.md")
        assert not result.ok
        assert "S004" in [m.code for m in result.messages]

    def test_schema_file_reference_valid(self):
        schema = {"type": "object", "properties": {"x": {"type": "string"}}}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, dir="/tmp"
        ) as f:
            json.dump(schema, f)
            schema_path = f.name

        try:
            source = f"{{#schema: {os.path.basename(schema_path)} #}}\n{{{{ x }}}}"
            result = lint(source, file_path=os.path.join("/tmp", "test.kata.md"))
            assert result.ok
        finally:
            os.unlink(schema_path)


# ---------------------------------------------------------------------------
# Block nesting checks
# ---------------------------------------------------------------------------

class TestBlockNesting:
    def test_valid_for(self):
        source = "{% for x in items %}{{ x }}{% endfor %}"
        result = lint(source)
        nesting_errors = [m for m in result.messages if m.code.startswith("T")]
        assert len(nesting_errors) == 0

    def test_valid_if(self):
        source = "{% if x %}yes{% elif y %}maybe{% else %}no{% endif %}"
        result = lint(source)
        nesting_errors = [m for m in result.messages if m.code.startswith("T")]
        assert len(nesting_errors) == 0

    def test_unclosed_for(self):
        source = "{% for x in items %}{{ x }}"
        result = lint(source)
        assert "T001" in [m.code for m in result.messages]

    def test_unclosed_if(self):
        source = "{% if x %}yes"
        result = lint(source)
        assert "T001" in [m.code for m in result.messages]

    def test_endfor_without_for(self):
        source = "{{ x }}{% endfor %}"
        result = lint(source)
        assert "T005" in [m.code for m in result.messages]

    def test_endif_without_if(self):
        source = "{{ x }}{% endif %}"
        result = lint(source)
        assert "T004" in [m.code for m in result.messages]

    def test_elif_without_if(self):
        source = "{% elif x %}yes{% endif %}"
        result = lint(source)
        assert "T002" in [m.code for m in result.messages]

    def test_else_without_block(self):
        source = "{% else %}no{% endif %}"
        result = lint(source)
        assert "T003" in [m.code for m in result.messages]

    def test_nested_mismatch(self):
        # for opened, if opened, endfor closes for, but if still open
        source = "{% for x in items %}{% if x %}{{ x }}{% endfor %}"
        result = lint(source)
        error_codes = [m.code for m in result.messages]
        assert any(code in ("T001", "T004", "T005") for code in error_codes)

    def test_valid_nested(self):
        source = "{% for x in items %}{% if x %}{{ x }}{% endif %}{% endfor %}"
        result = lint(source)
        nesting_errors = [m for m in result.messages if m.code.startswith("T")]
        assert len(nesting_errors) == 0

    def test_unknown_tag_warning(self):
        source = "{% foobar %}"
        result = lint(source)
        assert "T006" in [m.code for m in result.messages]


# ---------------------------------------------------------------------------
# Filter checks
# ---------------------------------------------------------------------------

class TestFilterChecks:
    def test_known_filter(self):
        source = "{{ x | upper }}"
        result = lint(source)
        filter_errors = [m for m in result.messages if m.code == "F001"]
        assert len(filter_errors) == 0

    def test_unknown_filter(self):
        source = "{{ x | nonexistent }}"
        result = lint(source)
        assert "F001" in [m.code for m in result.messages]

    def test_filter_with_args(self):
        source = '{{ x | default("N/A") }}'
        result = lint(source)
        filter_errors = [m for m in result.messages if m.code == "F001"]
        assert len(filter_errors) == 0

    def test_filter_chain(self):
        source = "{{ x | lower | capitalize }}"
        result = lint(source)
        filter_errors = [m for m in result.messages if m.code == "F001"]
        assert len(filter_errors) == 0

    def test_chain_with_unknown(self):
        source = "{{ x | upper | bogus | lower }}"
        result = lint(source)
        assert "F001" in [m.code for m in result.messages]


# ---------------------------------------------------------------------------
# Variable reference checks
# ---------------------------------------------------------------------------

class TestVariableChecks:
    def test_known_variable(self):
        source = '{#schema\n{"type":"object","properties":{"title":{"type":"string"}}}\n#}\n{{ title }}'
        result = lint(source)
        var_warnings = [m for m in result.messages if m.code == "V001"]
        assert len(var_warnings) == 0

    def test_unknown_variable(self):
        source = '{#schema\n{"type":"object","properties":{"title":{"type":"string"}}}\n#}\n{{ unknown }}'
        result = lint(source)
        assert "V001" in [m.code for m in result.messages]

    def test_loop_var_not_flagged(self):
        source = '{#schema\n{"type":"object","properties":{"items":{"type":"array"}}}\n#}\n{% for x in items %}{{ x }}{% endfor %}'
        result = lint(source)
        var_warnings = [m for m in result.messages if m.code == "V001"]
        assert len(var_warnings) == 0

    def test_loop_variable_not_flagged(self):
        source = '{#schema\n{"type":"object","properties":{"items":{"type":"array"}}}\n#}\n{% for x in items %}{{ loop.index }}{% endfor %}'
        result = lint(source)
        var_warnings = [m for m in result.messages if m.code == "V001"]
        assert len(var_warnings) == 0


# ---------------------------------------------------------------------------
# Unused properties
# ---------------------------------------------------------------------------

class TestUnusedProperties:
    def test_all_used(self):
        source = '{#schema\n{"type":"object","properties":{"title":{"type":"string"}}}\n#}\n{{ title }}'
        result = lint(source)
        unused = [m for m in result.messages if m.code == "V002"]
        assert len(unused) == 0

    def test_unused_property(self):
        source = '{#schema\n{"type":"object","properties":{"title":{"type":"string"},"unused":{"type":"string"}}}\n#}\n{{ title }}'
        result = lint(source)
        assert "V002" in [m.code for m in result.messages]

    def test_property_used_in_for(self):
        source = '{#schema\n{"type":"object","properties":{"items":{"type":"array"}}}\n#}\n{% for x in items %}{{ x }}{% endfor %}'
        result = lint(source)
        unused = [m for m in result.messages if m.code == "V002"]
        assert len(unused) == 0

    def test_meta_property_excluded(self):
        """Properties with "x-kata-meta": true should not trigger V002."""
        source = '{#schema\n{"type":"object","properties":{"title":{"type":"string"},"meta":{"type":"object","x-kata-meta":true}}}\n#}\n{{ title }}'
        result = lint(source)
        unused = [m for m in result.messages if m.code == "V002"]
        assert len(unused) == 0


# ---------------------------------------------------------------------------
# Output formats
# ---------------------------------------------------------------------------

class TestOutputFormat:
    def test_human_format_ok(self):
        result = lint("{{ x }}")
        summary = result.summary(fmt="human")
        assert "OK" in summary or "0 error" in summary

    def test_human_format_errors(self):
        result = lint("{% if x %}hello")
        summary = result.summary(fmt="human")
        assert "error" in summary

    def test_vscode_format(self):
        result = lint("{% if x %}hello")
        summary = result.summary(fmt="vscode")
        # file:line:col: level [code] message
        assert ":1:" in summary or ":2:" in summary
        assert "error" in summary
        assert "[T001]" in summary

    def test_vscode_format_no_issues(self):
        result = lint("hello world")
        summary = result.summary(fmt="vscode")
        # no errors/warnings, only info
        # vscode format still shows info
        # but should not contain "error"
        assert "error" not in summary


# ---------------------------------------------------------------------------
# lint_file
# ---------------------------------------------------------------------------

class TestLintFile:
    def test_file_not_found(self):
        result = lint_file("/tmp/nonexistent_file_12345.kata.md")
        assert not result.ok
        assert "E001" in [m.code for m in result.messages]

    def test_valid_file(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".kata.md", delete=False, dir="/tmp"
        ) as f:
            f.write("Hello {{ name }}")
            path = f.name

        try:
            result = lint_file(path)
            assert result.ok
        finally:
            os.unlink(path)

    def test_invalid_file(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".kata.md", delete=False, dir="/tmp"
        ) as f:
            f.write("{% for x in items %}{{ x | badfilter }}")
            path = f.name

        try:
            result = lint_file(path)
            assert not result.ok
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# Document mode lint
# ---------------------------------------------------------------------------

class TestDocumentModeLint:
    def test_lint_document_missing_section(self):
        from gospelo_kata.linter import lint_document
        # agenda schema requires: attendees (array), agenda (array)
        # which maps to "## Attendees" and "## Agenda"
        text = "# Meeting\n\n## Attendees\n\n| Name | Role |\n|------|------|\n| Alice | PM |\n"
        result = lint_document(text, "agenda")
        codes = [m.code for m in result.messages]
        assert "D002" in codes  # missing "## Agenda"

    def test_lint_document_all_sections_present(self):
        from gospelo_kata.linter import lint_document
        text = (
            "# Meeting\n\n"
            "## Attendees\n\n| Name |\n|------|\n| Alice |\n\n"
            "## Agenda\n\n### 1. Topic\n\n- Discussion point\n"
        )
        result = lint_document(text, "agenda")
        codes = [m.code for m in result.messages]
        assert "D002" not in codes

    def test_lint_document_schema_not_found(self):
        from gospelo_kata.linter import lint_document
        result = lint_document("# Hello", "nonexistent_schema_xyz")
        # D001 is info-level (missing schema is non-fatal; inline anchors substitute)
        assert "D001" in [m.code for m in result.messages]

    def test_lint_document_table_column_mismatch(self):
        from gospelo_kata.linter import lint_document
        text = (
            "# Meeting\n\n"
            "## Attendees\n\n"
            "| Name | Role |\n"
            "|------|------|\n"
            "| Alice | PM | Extra |\n\n"
            "## Agenda\n\n### 1. Topic\n"
        )
        result = lint_document(text, "agenda")
        codes = [m.code for m in result.messages]
        assert "D003" in codes

    def test_lint_document_empty_section(self):
        from gospelo_kata.linter import lint_document
        text = (
            "# Meeting\n\n"
            "## Attendees\n"
            "## Agenda\n\n### 1. Topic\n"
        )
        result = lint_document(text, "agenda")
        codes = [m.code for m in result.messages]
        assert "D004" in codes  # empty Attendees section

    def test_lint_file_auto_detects_document_mode(self):
        """lint_file auto-detects document mode from <!-- kata: {...} --> metadata."""
        md = '<!-- kata: {"schema": "agenda", "generated": "2026-03-15"} -->\n# Meeting\n\n## Attendees\n\n| Name |\n|------|\n| Alice |\n\n## Agenda\n\n### 1. Topic\n'
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, dir="/tmp"
        ) as f:
            f.write(md)
            path = f.name

        try:
            result = lint_file(path)
            # Should be in document mode (not template mode)
            # No template errors expected
            template_codes = [m.code for m in result.messages if m.code.startswith(("S", "T", "F", "V"))]
            assert len(template_codes) == 0
        finally:
            os.unlink(path)

    def test_lint_file_schema_name_override(self):
        """lint_file with --schema forces document mode."""
        md = "# Meeting\n\n## Attendees\n\n| Name |\n|------|\n| Alice |\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, dir="/tmp"
        ) as f:
            f.write(md)
            path = f.name

        try:
            result = lint_file(path, schema_name="agenda")
            codes = [m.code for m in result.messages]
            assert "D002" in codes  # missing "## Agenda"
        finally:
            os.unlink(path)

    def test_parse_kata_metadata(self):
        from gospelo_kata.generator.markdown import parse_kata_metadata
        text = '<!-- kata: {"schema": "agenda", "generated": "2026-03-15"} -->\n# Meeting'
        meta = parse_kata_metadata(text)
        assert meta is not None
        assert meta["schema"] == "agenda"
        assert meta["generated"] == "2026-03-15"

    def test_parse_kata_metadata_missing(self):
        from gospelo_kata.generator.markdown import parse_kata_metadata
        meta = parse_kata_metadata("# Just a heading")
        assert meta is None


# ---------------------------------------------------------------------------
# Annotation link checks (D005, D006)
# ---------------------------------------------------------------------------

class TestAnnotationLinkChecks:
    def test_valid_annotation_link(self):
        from gospelo_kata.linter import lint_document
        text = (
            '# [Meeting](#p-title)\n\n'
            '## [Attendees](#p-attendees)\n\n| Name |\n|------|\n| Alice |\n\n'
            '## [Agenda](#p-agenda)\n\n### 1. Topic\n\n'
            '---\n\n<details>\n<summary>Schema Reference</summary>\n\n'
            '#### <a id="p-title"></a>title\n- **type**: string\n\n'
            '#### <a id="p-attendees"></a>attendees\n- **type**: array\n\n'
            '#### <a id="p-agenda"></a>agenda\n- **type**: array\n\n'
            '</details>\n'
        )
        result = lint_document(text, "agenda")
        codes = [m.code for m in result.messages]
        assert "D005" not in codes  # all links valid

    def test_invalid_annotation_link(self):
        from gospelo_kata.linter import lint_document
        text = (
            '# [Meeting](#p-nonexistent)\n\n'
            '## Attendees\n\n| Name |\n|------|\n| Alice |\n\n'
            '## Agenda\n\n### 1. Topic\n'
        )
        result = lint_document(text, "agenda")
        codes = [m.code for m in result.messages]
        assert "D005" in codes

    def test_html_tag_in_data_kata_span(self):
        from gospelo_kata.linter import lint_document
        text = (
            '# <span data-kata="p-title">Test</span>\n\n'
            '| Desc |\n|------|\n'
            '| <span data-kata="p-description">inject <script>alert(1)</script> here</span> |\n\n'
            '---\n\n<details>\n<summary>Schema Reference</summary>\n\n'
            '**Schema**\n\n```yaml\ntitle: string\ndescription: string\n```\n\n'
            '</details>\n'
        )
        result = lint_document(text, "test")
        codes = [m.code for m in result.messages]
        assert "D016" in codes
        # Only the span with HTML tag should be flagged
        d016_msgs = [m for m in result.messages if m.code == "D016"]
        assert len(d016_msgs) == 1
        assert "<script>" in d016_msgs[0].message

    def test_no_html_tag_in_data_kata_span(self):
        from gospelo_kata.linter import lint_document
        text = (
            '# <span data-kata="p-title">Clean Title</span>\n\n'
            '| Desc |\n|------|\n'
            '| <span data-kata="p-description">No HTML here</span> |\n\n'
            '---\n\n<details>\n<summary>Schema Reference</summary>\n\n'
            '**Schema**\n\n```yaml\ntitle: string\ndescription: string\n```\n\n'
            '</details>\n'
        )
        result = lint_document(text, "test")
        codes = [m.code for m in result.messages]
        assert "D016" not in codes

    def test_orphan_anchor_info(self):
        from gospelo_kata.linter import lint_document
        text = (
            '# Meeting\n\n'
            '## Attendees\n\n| Name |\n|------|\n| Alice |\n\n'
            '## Agenda\n\n### 1. Topic\n\n'
            '---\n\n<details>\n<summary>Schema Reference</summary>\n\n'
            '#### <a id="p-title"></a>title\n- **type**: string\n\n'
            '#### <a id="p-attendees"></a>attendees\n- **type**: array\n\n'
            '</details>\n'
        )
        result = lint_document(text, "agenda")
        codes = [m.code for m in result.messages]
        # p-title and p-attendees defined but not referenced by any link
        assert "D006" in codes
