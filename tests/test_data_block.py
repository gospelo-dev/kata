# KATA Markdown™ — gospelo-kata
# Copyright (c) 2025 gospelo. All rights reserved.
# Licensed under the MIT License. See LICENSE.md for details.

"""Tests for {#data} block support in template engine."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from gospelo_kata.template import Template, extract_data, render_kata


TEMPLATE_WITH_DATA = """\
{#schema
title: string!
items[]!:
  name: string!
  status: enum(draft, done)
#}

{#data
title: My Checklist
items:
  - name: Task A
    status: draft
  - name: Task B
    status: done
#}

# {{ title }}

| Name | Status |
|------|--------|
{% for item in items %}| {{ item.name }} | {{ item.status }} |
{% endfor %}
"""

TEMPLATE_NO_DATA = """\
{#schema
title: string!
#}

# {{ title }}
"""


class TestExtractData:
    def test_yaml_data(self):
        data = extract_data(TEMPLATE_WITH_DATA)
        assert data is not None
        assert data["title"] == "My Checklist"
        assert len(data["items"]) == 2
        assert data["items"][0]["name"] == "Task A"
        assert data["items"][1]["status"] == "done"

    def test_json_data(self):
        text = '{#data\n{"title": "Hello", "count": 42}\n#}'
        data = extract_data(text)
        assert data == {"title": "Hello", "count": 42}

    def test_no_data_block(self):
        data = extract_data(TEMPLATE_NO_DATA)
        assert data is None

    def test_empty_data_block(self):
        text = "{#data\n\n#}"
        data = extract_data(text)
        assert data is None


class TestTemplateData:
    def test_data_attribute(self):
        tpl = Template(TEMPLATE_WITH_DATA)
        assert tpl.data is not None
        assert tpl.data["title"] == "My Checklist"

    def test_no_data_attribute(self):
        tpl = Template(TEMPLATE_NO_DATA)
        assert tpl.data is None

    def test_data_stripped_from_template(self):
        tpl = Template(TEMPLATE_WITH_DATA)
        # Data block should not appear in rendered output
        result = tpl.render_dict(tpl.data)
        assert "{#data" not in result
        assert "My Checklist" in result

    def test_schema_still_works(self):
        tpl = Template(TEMPLATE_WITH_DATA)
        assert tpl.schema is not None
        assert "properties" in tpl.schema


class TestRenderSelf:
    def test_renders_with_embedded_data(self):
        tpl = Template(TEMPLATE_WITH_DATA)
        result = tpl.render_self()
        assert "# My Checklist" in result
        assert "Task A" in result
        assert "Task B" in result
        assert "draft" in result
        assert "done" in result

    def test_renders_annotated(self):
        tpl = Template(TEMPLATE_WITH_DATA)
        result = tpl.render_self(annotate=True)
        assert "data-kata" in result
        assert "Schema Reference" in result

    def test_raises_without_data(self):
        tpl = Template(TEMPLATE_NO_DATA)
        with pytest.raises(ValueError, match="No {#data}"):
            tpl.render_self()


class TestRenderKata:
    def test_file_render(self, tmp_path):
        kata_file = tmp_path / "test.kata.md"
        kata_file.write_text(TEMPLATE_WITH_DATA, encoding="utf-8")

        result = render_kata(str(kata_file))
        assert "My Checklist" in result
        assert "Task A" in result

    def test_file_render_no_annotate(self, tmp_path):
        kata_file = tmp_path / "test.kata.md"
        kata_file.write_text(TEMPLATE_WITH_DATA, encoding="utf-8")

        result = render_kata(str(kata_file), annotate=False)
        assert "data-kata" not in result
        assert "# My Checklist" in result

    def test_file_no_data_raises(self, tmp_path):
        kata_file = tmp_path / "test.kata.md"
        kata_file.write_text(TEMPLATE_NO_DATA, encoding="utf-8")

        with pytest.raises(ValueError, match="No {#data}"):
            render_kata(str(kata_file))

    def test_validation_failure(self, tmp_path):
        bad_data = """\
{#schema
title: string!
count: integer!
#}

{#data
title: Hello
#}

# {{ title }} ({{ count }})
"""
        kata_file = tmp_path / "bad.kata.md"
        kata_file.write_text(bad_data, encoding="utf-8")

        with pytest.raises(ValueError, match="error"):
            render_kata(str(kata_file), validate=True)

    def test_skip_validation(self, tmp_path):
        bad_data = """\
{#schema
title: string!
count: integer!
#}

{#data
title: Hello
#}

# {{ title }}
"""
        kata_file = tmp_path / "bad.kata.md"
        kata_file.write_text(bad_data, encoding="utf-8")

        # Should not raise
        result = render_kata(str(kata_file), validate=False)
        assert "Hello" in result
