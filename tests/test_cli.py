# KATA Markdown™ — gospelo-kata
# Copyright (c) 2025 gospelo. All rights reserved.
# Licensed under the MIT License. See LICENSE.md for details.

"""Tests for gospelo_kata.cli."""

from __future__ import annotations

import json
import os
import shutil
import tempfile

import pytest

from gospelo_kata.cli import main


def _run(argv: list[str], expect_exit: int = 0) -> str:
    """Run CLI and capture stdout. Asserts SystemExit code if raised."""
    import io
    import sys

    old_stdout = sys.stdout
    sys.stdout = buf = io.StringIO()
    try:
        main(argv)
        output = buf.getvalue()
    except SystemExit as e:
        output = buf.getvalue()
        assert e.code == expect_exit, f"Expected exit {expect_exit}, got {e.code}\nOutput: {output}"
    finally:
        sys.stdout = old_stdout
    return output


# ---------------------------------------------------------------------------
# templates
# ---------------------------------------------------------------------------

class TestTemplatesCommand:
    def test_list_templates(self):
        output = _run(["templates"])
        assert "agenda" in output
        assert "checklist" in output
        assert "test_spec" in output


# ---------------------------------------------------------------------------
# schemas
# ---------------------------------------------------------------------------

class TestSchemasCommand:
    def test_list_schemas(self):
        output = _run(["schemas"])
        assert "agenda" in output
        assert "checklist" in output
        assert "test_spec" in output
        assert "test_prereq" in output


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------

class TestInitCommand:
    def test_init_agenda(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = _run(["init", "--type", "agenda", "--output", tmpdir])
            # .katar is copied as-is to templates/
            assert os.path.exists(os.path.join(tmpdir, "templates", "agenda.katar"))
            assert os.path.exists(os.path.join(tmpdir, "outputs"))
            assert os.path.exists(os.path.join(tmpdir, ".workflow_status.json"))

    def test_init_checklist(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = _run(["init", "--type", "checklist", "--output", tmpdir])
            assert os.path.exists(os.path.join(tmpdir, "templates", "checklist.katar"))

    def test_init_test_spec(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = _run(["init", "--type", "test_spec", "--output", tmpdir])
            assert os.path.exists(os.path.join(tmpdir, "templates", "test_spec.katar"))

    def test_init_nonexistent_type(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = _run(["init", "--type", "nonexistent", "--output", tmpdir], expect_exit=1)

    def test_init_skip_existing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # First init
            _run(["init", "--type", "agenda", "--output", tmpdir])
            # Second init should skip
            output = _run(["init", "--type", "agenda", "--output", tmpdir])
            assert "skip" in output


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------

class TestValidateCommand:
    def test_validate_valid_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, "agenda.json")
            data = {
                "title": "Test Meeting",
                "date": "2026-03-16",
                "attendees": [{"name": "Alice"}],
                "agenda": [{"id": "1", "topic": "Topic 1", "presenter": "Alice"}],
            }
            with open(json_path, "w") as f:
                json.dump(data, f)
            output = _run(["validate", json_path])
            assert "OK" in output

    def test_validate_with_schema(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, "checklist.json")
            data = {
                "version": "1.0",
                "description": "Test",
                "categories": [{
                    "id": "cat1",
                    "name": "Cat1",
                    "items": [{"id": "1", "name": "Item", "name_ja": "アイテム"}],
                }],
            }
            with open(json_path, "w") as f:
                json.dump(data, f)
            output = _run(["validate", json_path, "--schema", "checklist"])
            assert "OK" in output

    def test_validate_file_not_found(self):
        output = _run(["validate", "/tmp/nonexistent_12345.json"], expect_exit=1)

    def test_validate_auto_detect_fails(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, dir="/tmp"
        ) as f:
            json.dump({"unknown": "data"}, f)
            path = f.name

        try:
            output = _run(["validate", path], expect_exit=1)
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# generate
# ---------------------------------------------------------------------------

class TestGenerateCommand:
    def _write_agenda_json(self, tmpdir: str) -> str:
        json_path = os.path.join(tmpdir, "agenda.json")
        data = {
            "meeting_title": "Meeting Title",
            "date": "2026-03-16",
            "attendees": [{"name": "Alice"}],
            "agenda_items": [{"title": "Topic 1", "points": ["point"]}],
        }
        with open(json_path, "w") as f:
            json.dump(data, f)
        return json_path

    def test_generate_markdown_stdout(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = self._write_agenda_json(tmpdir)
            output = _run(["generate", json_path, "--format", "markdown"])
            assert "Meeting Title" in output

    def test_generate_markdown_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = self._write_agenda_json(tmpdir)
            md_path = os.path.join(tmpdir, "output.md")
            _run(["generate", json_path, "--format", "markdown", "--output", md_path])
            assert os.path.exists(md_path)
            content = open(md_path).read()
            assert "Meeting Title" in content

    def test_generate_html(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, "data.json")
            data = {
                "title": "Test Checklist",
                "items": [{"name": "Item 1", "status": "open"}],
            }
            with open(json_path, "w") as f:
                json.dump(data, f)
            html_path = os.path.join(tmpdir, "output.html")
            _run(["generate", json_path, "--format", "html", "--output", html_path])
            assert os.path.exists(html_path)
            content = open(html_path).read()
            assert "<html" in content

    def test_generate_excel(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            spec_path = os.path.join(tmpdir, "spec.json")
            prereq_path = os.path.join(tmpdir, "prereq.json")
            spec_data = {
                "test_name": "Test",
                "test_cases": [
                    {"test_id": "T-01", "category": "Basic", "description": "Test", "expected_result": "Pass"},
                ],
            }
            prereq_data = {
                "prerequisites": [
                    {"name": "Prereq 1", "description": "A prereq", "status": "ready"},
                ],
            }
            with open(spec_path, "w") as f:
                json.dump(spec_data, f)
            with open(prereq_path, "w") as f:
                json.dump(prereq_data, f)
            xlsx_path = os.path.join(tmpdir, "output.xlsx")
            _run([
                "generate", spec_path,
                "--format", "excel",
                "--prereq", prereq_path,
                "--output", xlsx_path,
            ])
            assert os.path.exists(xlsx_path)
            assert os.path.getsize(xlsx_path) > 0

    def test_generate_file_not_found(self):
        output = _run(
            ["generate", "/tmp/nonexistent_12345.json", "--format", "markdown"],
            expect_exit=1,
        )


# ---------------------------------------------------------------------------
# lint
# ---------------------------------------------------------------------------

class TestLintCommand:
    def test_lint_valid(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".kata.md", delete=False, dir="/tmp"
        ) as f:
            f.write("Hello {{ name }}")
            path = f.name

        try:
            output = _run(["lint", path])
            assert "no issues" in output or "0 error" in output
        finally:
            os.unlink(path)

    def test_lint_errors(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".kata.md", delete=False, dir="/tmp"
        ) as f:
            f.write("{% for x in items %}{{ x | badfilter }}")
            path = f.name

        try:
            output = _run(["lint", path], expect_exit=1)
            assert "error" in output
        finally:
            os.unlink(path)

    def test_lint_vscode_format(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".kata.md", delete=False, dir="/tmp"
        ) as f:
            f.write("{% if x %}hello")
            path = f.name

        try:
            output = _run(["lint", "--format", "vscode", path], expect_exit=1)
            # file:line:col: level [code] message
            assert "[T001]" in output
        finally:
            os.unlink(path)

    def test_lint_multiple_files(self):
        paths = []
        for i in range(2):
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".kata.md", delete=False, dir="/tmp"
            ) as f:
                f.write("Hello {{ name }}")
                paths.append(f.name)

        try:
            output = _run(["lint"] + paths)
        finally:
            for p in paths:
                os.unlink(p)

    def test_lint_file_not_found(self):
        output = _run(
            ["lint", "/tmp/nonexistent_12345.kata.md"],
            expect_exit=1,
        )

    def test_lint_document_mode_with_schema(self):
        """lint --schema forces document mode validation."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, dir="/tmp"
        ) as f:
            f.write("# Meeting\n\n## Attendees\n\n| Name |\n|------|\n| Alice |\n")
            path = f.name

        try:
            output = _run(["lint", "--schema", "agenda", path], expect_exit=1)
            assert "D002" in output or "missing" in output.lower()
        finally:
            os.unlink(path)

    def test_lint_document_mode_auto_detect(self):
        """lint auto-detects document mode from metadata comment."""
        md = '<!-- kata: {"schema": "agenda", "generated": "2026-03-15"} -->\n# Meeting\n\n## Attendees\n\n| Name |\n|------|\n| Alice |\n\n## Agenda\n\n### 1. Topic\n\n- point\n'
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, dir="/tmp"
        ) as f:
            f.write(md)
            path = f.name

        try:
            output = _run(["lint", path])
            # Should succeed (all required sections present)
            assert "error" not in output.lower() or "0 error" in output
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# init-vscode
# ---------------------------------------------------------------------------

class TestInitVscodeCommand:
    def test_creates_tasks_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = _run(["init-vscode", "--output", tmpdir])
            tasks_path = os.path.join(tmpdir, "tasks.json")
            assert os.path.exists(tasks_path)
            data = json.loads(open(tasks_path).read())
            assert data["version"] == "2.0.0"
            assert len(data["tasks"]) == 2

    def test_tasks_have_problem_matcher(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _run(["init-vscode", "--output", tmpdir])
            tasks_path = os.path.join(tmpdir, "tasks.json")
            data = json.loads(open(tasks_path).read())
            for task in data["tasks"]:
                assert "problemMatcher" in task
                assert task["problemMatcher"]["owner"] == "kata"


# ---------------------------------------------------------------------------
# render — _tpl.kata.md rejection
# ---------------------------------------------------------------------------

class TestRenderTplRejection:
    def test_render_rejects_tpl_kata_md(self, tmp_path):
        tpl = tmp_path / "sample_tpl.kata.md"
        tpl.write_text("# Test\n")
        import io, sys
        old_stderr = sys.stderr
        sys.stderr = io.StringIO()
        try:
            _run(["render", str(tpl)], expect_exit=1)
        finally:
            err = sys.stderr.getvalue()
            sys.stderr = old_stderr
        assert "_tpl.kata.md files cannot be rendered directly" in err

    def test_render_rejects_legacy_format(self, tmp_path):
        md = tmp_path / "sample.kata.md"
        md.write_text(
            "**Schema**\n```yaml\ntype: object\nproperties:\n  name:\n    type: string\n```\n\n"
            "**Data**\n```yaml\nname: test\n```\n\n"
            "# Hello {{ name }}\n"
        )
        import io, sys
        old_stderr = sys.stderr
        sys.stderr = io.StringIO()
        try:
            _run(["render", str(md)], expect_exit=1)
        finally:
            err = sys.stderr.getvalue()
            sys.stderr = old_stderr
        assert "legacy format" in err
        assert "gospelo-kata convert" in err

    def test_render_allows_new_format(self, tmp_path):
        md = tmp_path / "sample.kata.md"
        md.write_text(
            "# old\n\n"
            "<details>\n<summary>Specification</summary>\n\n"
            "```kata:template\n# {{ name }}\n```\n\n"
            "**Schema**\n\n```yaml\nname: string!\n```\n\n"
            "</details>\n\n"
            "<details>\n<summary>Data</summary>\n\n"
            "```yaml\nname: test\n```\n\n"
            "</details>\n"
        )
        output = _run(["render", str(md)])
        assert "test" in output


# ---------------------------------------------------------------------------
# sync to-html / to-data
# ---------------------------------------------------------------------------

class TestSyncToHtml:
    def test_sync_to_html_works(self, tmp_path):
        md = tmp_path / "sample.kata.md"
        md.write_text(
            "# old\n\n"
            "<details>\n<summary>Specification</summary>\n\n"
            "```kata:template\n# {{ name }}\n```\n\n"
            "**Schema**\n\n```yaml\nname: string!\n```\n\n"
            "</details>\n\n"
            "<details>\n<summary>Data</summary>\n\n"
            "```yaml\nname: hello\n```\n\n"
            "</details>\n"
        )
        output = _run(["sync", "to-html", str(md)])
        assert "hello" in output


# ---------------------------------------------------------------------------
# export — .kata.md file path support
# ---------------------------------------------------------------------------

class TestExportFromFile:
    def test_export_data_from_kata_md(self, tmp_path):
        md = tmp_path / "my_spec.kata.md"
        md.write_text(
            "# My Spec\n\n"
            "<details>\n<summary>Specification</summary>\n\n"
            "**Prompt**\n\n```yaml\nGenerate a spec.\n```\n\n"
            "**Schema**\n\n```yaml\ntitle: string!\n```\n\n"
            "**Data**\n\n```yaml\ntitle: Hello World\n```\n\n"
            "</details>\n"
        )
        output = _run(["export", str(md), "--part", "data", "--format", "yaml"])
        assert "title: Hello World" in output

    def test_export_schema_from_kata_md(self, tmp_path):
        md = tmp_path / "my_spec.kata.md"
        md.write_text(
            "# My Spec\n\n"
            "<details>\n<summary>Specification</summary>\n\n"
            "**Schema**\n\n```yaml\ntitle: string!\n```\n\n"
            "**Data**\n\n```yaml\ntitle: test\n```\n\n"
            "</details>\n"
        )
        output = _run(["export", str(md), "--part", "schema"])
        assert "title: string!" in output


# ---------------------------------------------------------------------------
# sync — bidirectional sync with separated Data <details>
# ---------------------------------------------------------------------------

class TestSyncBidirectional:
    def _build_separated_kata_md(self, data_yaml: str) -> str:
        return (
            "# old title\n\n"
            "<style>\n"
            "table { table-layout: fixed; width: 100%; }\n"
            "</style>\n\n"
            "---\n\n"
            "<details>\n<summary>Specification</summary>\n\n"
            "```kata:template\n"
            "# {{ title }}\n\n"
            "{% for item in items %}- {{ item.name }}\n"
            "{% endfor %}\n"
            "```\n\n"
            "**Schema**\n\n```yaml\n"
            "title: string!\n"
            "items[]!:\n"
            "  name: string!\n"
            "```\n\n"
            "</details>\n\n"
            "<details>\n<summary>Data</summary>\n\n"
            f"```yaml\n{data_yaml}```\n\n"
            "</details>\n"
        )

    def test_sync_updates_body_from_data(self, tmp_path):
        md = tmp_path / "test.kata.md"
        md.write_text(self._build_separated_kata_md(
            "title: My List\nitems:\n- name: apple\n- name: banana\n"
        ))
        output = _run(["sync", "to-html", str(md), "--no-validate"])
        assert "My List" in output
        assert "apple" in output
        assert "banana" in output

    def test_sync_reflects_data_changes(self, tmp_path):
        md = tmp_path / "test.kata.md"
        md.write_text(self._build_separated_kata_md(
            "title: Updated\nitems:\n- name: cherry\n"
        ))
        output = _run(["sync", "to-html", str(md), "--no-validate"])
        assert "Updated" in output
        assert "cherry" in output
        assert "apple" not in output

    def test_sync_adds_new_items(self, tmp_path):
        md = tmp_path / "test.kata.md"
        md.write_text(self._build_separated_kata_md(
            "title: Test\nitems:\n- name: a\n- name: b\n- name: c\n"
        ))
        output = _run(["sync", "to-html", str(md), "--no-validate"])
        assert ">a<" in output
        assert ">b<" in output
        assert ">c<" in output

    def test_sync_is_idempotent(self, tmp_path):
        md = tmp_path / "test.kata.md"
        md.write_text(self._build_separated_kata_md(
            "title: Stable\nitems:\n- name: x\n"
        ))
        out1 = _run(["sync", "to-html", str(md), "--no-validate"])
        md.write_text(out1)
        out2 = _run(["sync", "to-html", str(md), "--no-validate"])
        assert out1 == out2


class TestConvertCommand:
    _LEGACY_SRC = (
        "{#schema\n"
        "title: string!\n"
        "items[]!:\n"
        "  id: string!\n"
        "  task: string!\n"
        "  status: enum(todo, done)\n"
        "#}\n\n"
        "{#prompt\n"
        "A simple TODO list.\n"
        "#}\n\n"
        "{#data\n"
        "title: My Tasks\n"
        "items:\n"
        '  - id: "1"\n'
        "    task: Buy milk\n"
        "    status: done\n"
        '  - id: "2"\n'
        "    task: Buy bread\n"
        "    status: todo\n"
        "#}\n\n"
        "# {{ title }}\n\n"
        "{% for item in items %}| {{ item.id }} | {{ item.task }} | {{ item.status }} |\n"
        "{% endfor %}"
    )

    def test_convert_legacy_to_new_format(self, tmp_path):
        md = tmp_path / "legacy.kata.md"
        md.write_text(self._LEGACY_SRC)
        output = _run(["convert", str(md)])
        assert "converted:" in output
        content = md.read_text()
        assert "<summary>Data</summary>" in content
        assert "```kata:template" in content
        assert "kata-structure-integrity" in content
        assert 'data-kata="p-title"' in content

    def test_convert_adds_enum_styling(self, tmp_path):
        md = tmp_path / "legacy.kata.md"
        md.write_text(self._LEGACY_SRC)
        _run(["convert", str(md)])
        content = md.read_text()
        assert 'data-kata-enum="done"' in content
        assert 'data-kata-enum="todo"' in content
        assert "[data-kata-enum]" in content

    def test_convert_skip_already_new(self, tmp_path):
        md = tmp_path / "new.kata.md"
        md.write_text(self._LEGACY_SRC)
        _run(["convert", str(md)])
        output = _run(["convert", str(md)])
        assert "skip (already new format)" in output

    def test_convert_check_mode(self, tmp_path):
        md = tmp_path / "legacy.kata.md"
        md.write_text(self._LEGACY_SRC)
        output = _run(["convert", "--check", str(md)], expect_exit=1)
        assert "needs convert:" in output
        # File should not be modified
        assert md.read_text() == self._LEGACY_SRC

    def test_converted_file_is_syncable(self, tmp_path):
        md = tmp_path / "legacy.kata.md"
        md.write_text(self._LEGACY_SRC)
        _run(["convert", str(md)])
        # Sync should work on converted file
        output = _run(["sync", "to-html", str(md), "-o", str(md)])
        assert "Rendered:" in output
        content = md.read_text()
        assert "<summary>Data</summary>" in content
