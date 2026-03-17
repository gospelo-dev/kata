# KATA Markdown™ — gospelo-kata
# Copyright (c) 2025 gospelo. All rights reserved.
# Licensed under the MIT License. See LICENSE.md for details.

"""Tests for gospelo_kata.template — Jinja2 3.1.6 compatible template engine."""

from __future__ import annotations

import json
import os
import tempfile

import pytest

from gospelo_kata.template import (
    Template,
    extract_schema,
    generate_schema_reference,
    render_file,
    render_template,
    strip_annotations,
)


# ---------------------------------------------------------------------------
# Variable interpolation
# ---------------------------------------------------------------------------

class TestVariableInterpolation:
    def test_simple_variable(self):
        assert Template("{{ name }}").render(name="World") == "World"

    def test_missing_variable_renders_empty(self):
        assert Template("{{ missing }}").render() == ""

    def test_dot_notation(self):
        t = Template("{{ user.name }}")
        assert t.render(user={"name": "Taro"}) == "Taro"

    def test_nested_dot_notation(self):
        t = Template("{{ a.b.c }}")
        assert t.render(a={"b": {"c": "deep"}}) == "deep"

    def test_bracket_notation(self):
        t = Template('{{ data["key"] }}')
        assert t.render(data={"key": "value"}) == "value"

    def test_array_index(self):
        t = Template("{{ items[0] }}")
        assert t.render(items=["first", "second"]) == "first"

    def test_mixed_text_and_vars(self):
        t = Template("Hello {{ name }}, you are {{ age }} years old.")
        assert t.render(name="Alice", age=30) == "Hello Alice, you are 30 years old."

    def test_string_literal(self):
        t = Template('{{ "hello" }}')
        assert t.render() == "hello"

    def test_numeric_literal(self):
        t = Template("{{ 42 }}")
        assert t.render() == "42"


# ---------------------------------------------------------------------------
# For loops
# ---------------------------------------------------------------------------

class TestForLoop:
    def test_simple_list(self):
        t = Template("{% for x in items %}{{ x }} {% endfor %}")
        assert t.render(items=["a", "b", "c"]) == "a b c "

    def test_object_list(self):
        t = Template("{% for p in people %}{{ p.name }}{% endfor %}")
        result = t.render(people=[{"name": "A"}, {"name": "B"}])
        assert result == "AB"

    def test_loop_index(self):
        t = Template("{% for x in items %}{{ loop.index }}{% endfor %}")
        assert t.render(items=["a", "b", "c"]) == "123"

    def test_loop_index0(self):
        t = Template("{% for x in items %}{{ loop.index0 }}{% endfor %}")
        assert t.render(items=["a", "b"]) == "01"

    def test_loop_first_last(self):
        t = Template("{% for x in items %}{{ loop.first }}-{{ loop.last }} {% endfor %}")
        assert t.render(items=["a", "b", "c"]) == "True-False False-False False-True "

    def test_loop_length(self):
        t = Template("{% for x in items %}{{ loop.length }}{% endfor %}")
        assert t.render(items=["a", "b"]) == "22"

    def test_loop_revindex(self):
        t = Template("{% for x in items %}{{ loop.revindex }}{% endfor %}")
        assert t.render(items=["a", "b", "c"]) == "321"

    def test_for_else_empty(self):
        t = Template("{% for x in items %}{{ x }}{% else %}empty{% endfor %}")
        assert t.render(items=[]) == "empty"

    def test_for_else_nonempty(self):
        t = Template("{% for x in items %}{{ x }}{% else %}empty{% endfor %}")
        assert t.render(items=["a"]) == "a"

    def test_nested_for(self):
        t = Template(
            "{% for g in groups %}{% for i in g.items %}{{ i }}{% endfor %} {% endfor %}"
        )
        result = t.render(groups=[
            {"items": ["a", "b"]},
            {"items": ["c"]},
        ])
        assert result == "ab c "

    def test_tuple_unpacking(self):
        t = Template("{% for k, v in pairs %}{{ k }}={{ v }} {% endfor %}")
        assert t.render(pairs=[["a", "1"], ["b", "2"]]) == "a=1 b=2 "


# ---------------------------------------------------------------------------
# Conditionals
# ---------------------------------------------------------------------------

class TestConditionals:
    def test_if_true(self):
        t = Template("{% if show %}yes{% endif %}")
        assert t.render(show=True) == "yes"

    def test_if_false(self):
        t = Template("{% if show %}yes{% endif %}")
        assert t.render(show=False) == ""

    def test_if_else(self):
        t = Template("{% if show %}yes{% else %}no{% endif %}")
        assert t.render(show=False) == "no"

    def test_if_elif_else(self):
        t = Template("{% if x == 1 %}one{% elif x == 2 %}two{% else %}other{% endif %}")
        assert t.render(x=1) == "one"
        assert t.render(x=2) == "two"
        assert t.render(x=3) == "other"

    def test_comparison_operators(self):
        t = Template("{% if x > 5 %}big{% endif %}")
        assert t.render(x=10) == "big"
        assert t.render(x=3) == ""

    def test_boolean_and(self):
        t = Template("{% if a and b %}yes{% endif %}")
        assert t.render(a=True, b=True) == "yes"
        assert t.render(a=True, b=False) == ""

    def test_boolean_or(self):
        t = Template("{% if a or b %}yes{% endif %}")
        assert t.render(a=False, b=True) == "yes"
        assert t.render(a=False, b=False) == ""

    def test_not(self):
        t = Template("{% if not hidden %}visible{% endif %}")
        assert t.render(hidden=False) == "visible"

    def test_in_operator(self):
        t = Template("{% if 'a' in items %}found{% endif %}")
        assert t.render(items=["a", "b"]) == "found"
        assert t.render(items=["c"]) == ""

    def test_nested_if_in_for(self):
        t = Template("{% for u in users %}{% if u.active %}{{ u.name }}{% endif %}{% endfor %}")
        result = t.render(users=[
            {"name": "A", "active": True},
            {"name": "B", "active": False},
            {"name": "C", "active": True},
        ])
        assert result == "AC"

    def test_ternary(self):
        t = Template('{{ "yes" if active else "no" }}')
        assert t.render(active=True) == "yes"
        assert t.render(active=False) == "no"


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------

class TestFilters:
    def test_default(self):
        t = Template('{{ x | default("N/A") }}')
        assert t.render() == "N/A"
        assert t.render(x="hello") == "hello"

    def test_default_alias_d(self):
        t = Template('{{ x | d("fallback") }}')
        assert t.render() == "fallback"

    def test_join(self):
        t = Template('{{ items | join(", ") }}')
        assert t.render(items=["a", "b", "c"]) == "a, b, c"

    def test_upper(self):
        assert Template("{{ x | upper }}").render(x="hello") == "HELLO"

    def test_lower(self):
        assert Template("{{ x | lower }}").render(x="HELLO") == "hello"

    def test_title(self):
        assert Template("{{ x | title }}").render(x="hello world") == "Hello World"

    def test_capitalize(self):
        assert Template("{{ x | capitalize }}").render(x="hello") == "Hello"

    def test_trim(self):
        assert Template("{{ x | trim }}").render(x="  hi  ") == "hi"

    def test_length(self):
        assert Template("{{ items | length }}").render(items=[1, 2, 3]) == "3"

    def test_count_alias(self):
        assert Template("{{ items | count }}").render(items=[1, 2]) == "2"

    def test_first(self):
        assert Template("{{ items | first }}").render(items=[10, 20]) == "10"

    def test_last(self):
        assert Template("{{ items | last }}").render(items=[10, 20]) == "20"

    def test_replace(self):
        t = Template('{{ x | replace("world", "earth") }}')
        assert t.render(x="hello world") == "hello earth"

    def test_int_filter(self):
        assert Template("{{ x | int }}").render(x="42") == "42"
        assert Template("{{ x | int }}").render(x="abc") == "0"

    def test_float_filter(self):
        assert Template("{{ x | float }}").render(x="3.14") == "3.14"

    def test_abs_filter(self):
        assert Template("{{ x | abs }}").render(x=-5) == "5"

    def test_round_filter(self):
        assert Template("{{ x | round(2) }}").render(x=3.14159) == "3.14"

    def test_sort(self):
        t = Template("{{ items | sort | join(',') }}")
        assert t.render(items=[3, 1, 2]) == "1,2,3"

    def test_reverse(self):
        t = Template("{{ items | reverse | join(',') }}")
        assert t.render(items=[1, 2, 3]) == "3,2,1"

    def test_unique(self):
        t = Template("{{ items | unique | join(',') }}")
        assert t.render(items=[1, 2, 2, 3]) == "1,2,3"

    def test_map_attribute(self):
        t = Template('{{ users | map(attribute="name") | join(", ") }}')
        assert t.render(users=[{"name": "A"}, {"name": "B"}]) == "A, B"

    def test_escape(self):
        t = Template("{{ x | escape }}")
        assert t.render(x="<b>hi</b>") == "&lt;b&gt;hi&lt;/b&gt;"

    def test_e_alias(self):
        t = Template("{{ x | e }}")
        assert t.render(x="<script>") == "&lt;script&gt;"

    def test_safe(self):
        t = Template("{{ x | safe }}")
        assert t.render(x="<b>hi</b>") == "<b>hi</b>"

    def test_truncate(self):
        t = Template("{{ x | truncate(10) }}")
        result = t.render(x="Hello World, this is a long string")
        assert len(result) <= 13  # 10 + "..."
        assert result.endswith("...")

    def test_wordcount(self):
        assert Template("{{ x | wordcount }}").render(x="one two three") == "3"

    def test_striptags(self):
        t = Template("{{ x | striptags }}")
        assert t.render(x="<p>hello</p>") == "hello"

    def test_tojson(self):
        t = Template("{{ x | tojson }}")
        result = t.render(x={"a": 1})
        assert json.loads(result) == {"a": 1}

    def test_items(self):
        t = Template("{% for k, v in data | items %}{{ k }}={{ v }} {% endfor %}")
        assert t.render(data={"a": "1", "b": "2"}) in ("a=1 b=2 ", "b=2 a=1 ")

    def test_filter_chain(self):
        t = Template("{{ name | lower | capitalize }}")
        assert t.render(name="hELLO WORLD") == "Hello world"

    def test_groupby(self):
        t = Template('{% for g in items | groupby("cat") %}{{ g.grouper }}:{{ g.list | length }} {% endfor %}')
        result = t.render(items=[
            {"cat": "A", "v": 1},
            {"cat": "A", "v": 2},
            {"cat": "B", "v": 3},
        ])
        assert result == "A:2 B:1 "

    def test_batch(self):
        t = Template("{% for b in items | batch(2) %}[{{ b | join(',') }}]{% endfor %}")
        assert t.render(items=[1, 2, 3, 4, 5]) == "[1,2][3,4][5]"

    def test_indent(self):
        t = Template("{{ text | indent(2) }}")
        result = t.render(text="line1\nline2")
        assert result == "line1\n  line2"

    def test_center(self):
        result = Template("{{ x | center(10) }}").render(x="hi")
        assert len(result) == 10
        assert "hi" in result

    def test_filesizeformat(self):
        t = Template("{{ x | filesizeformat }}")
        assert "kB" in t.render(x=1500)

    def test_dictsort(self):
        t = Template("{% for k, v in data | dictsort %}{{ k }}={{ v }} {% endfor %}")
        assert t.render(data={"b": 2, "a": 1}) == "a=1 b=2 "


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

class TestComments:
    def test_comment_removed(self):
        t = Template("Hello{# hidden #} World")
        assert t.render() == "Hello World"

    def test_multiline_comment(self):
        t = Template("A{# this\nis\nmultiline #}B")
        assert t.render() == "AB"


# ---------------------------------------------------------------------------
# Schema extraction
# ---------------------------------------------------------------------------

class TestSchemaExtraction:
    def test_inline_schema(self):
        source = '{#schema\n{"type": "object"}\n#}\nHello'
        schema, cleaned = extract_schema(source)
        assert schema == {"type": "object"}
        assert "Hello" in cleaned
        assert "{#schema" not in cleaned

    def test_no_schema(self):
        source = "Hello {{ name }}"
        schema, cleaned = extract_schema(source)
        assert schema is None
        assert cleaned == source

    def test_file_reference_schema(self):
        schema_data = {"type": "object", "properties": {"x": {"type": "string"}}}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, dir="/tmp"
        ) as f:
            json.dump(schema_data, f)
            schema_path = f.name

        try:
            tpl_dir = os.path.dirname(schema_path)
            tpl_path = os.path.join(tpl_dir, "test.kata.md")
            source = f"{{#schema: {os.path.basename(schema_path)} #}}\nHello"
            schema, cleaned = extract_schema(source, template_path=tpl_path)
            assert schema == schema_data
            assert "Hello" in cleaned
        finally:
            os.unlink(schema_path)

    def test_file_reference_not_found(self):
        source = "{#schema: nonexistent.json #}\nHello"
        with pytest.raises(FileNotFoundError):
            extract_schema(source, template_path="/tmp/fake.kata.md")

    def test_details_wrapper_inline(self):
        source = '<details>\n<summary>Schema</summary>\n\n{#schema\n{"type": "object"}\n#}\n\n</details>\n\n# {{ title }}'
        schema, cleaned = extract_schema(source)
        assert schema == {"type": "object"}
        assert "<details>" not in cleaned
        assert "<summary>" not in cleaned
        assert "# {{ title }}" in cleaned

    def test_details_wrapper_file_ref(self):
        schema_data = {"type": "object", "properties": {"x": {"type": "string"}}}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, dir="/tmp"
        ) as f:
            json.dump(schema_data, f)
            schema_path = f.name

        try:
            source = (
                "<details>\n<summary>Schema</summary>\n\n"
                f"{{#schema: {os.path.basename(schema_path)} #}}\n\n"
                "</details>\n\n{{ x }}"
            )
            tpl_path = os.path.join(os.path.dirname(schema_path), "t.kata.md")
            schema, cleaned = extract_schema(source, template_path=tpl_path)
            assert schema == schema_data
            assert "<details>" not in cleaned
        finally:
            os.unlink(schema_path)

    def test_details_wrapper_render_clean(self):
        source = (
            "<details>\n<summary>Schema</summary>\n\n"
            '{#schema\n{"type":"object","required":["title"],'
            '"properties":{"title":{"type":"string"}}}\n#}\n\n'
            "</details>\n\n# {{ title }}"
        )
        t = Template(source)
        result = t.render(title="Hello")
        assert "<details>" not in result
        assert "# Hello" in result


# ---------------------------------------------------------------------------
# Template class
# ---------------------------------------------------------------------------

class TestTemplateClass:
    def test_render_dict(self):
        t = Template("{{ title }}")
        assert t.render_dict({"title": "Hello"}) == "Hello"

    def test_validate_with_schema(self):
        source = '{#schema\n{"type":"object","required":["name"],"properties":{"name":{"type":"string"}}}\n#}\n{{ name }}'
        t = Template(source)
        result = t.validate({"name": "ok"})
        assert result.valid

    def test_validate_fails(self):
        source = '{#schema\n{"type":"object","required":["name"],"properties":{"name":{"type":"string"}}}\n#}\n{{ name }}'
        t = Template(source)
        result = t.validate({})
        assert not result.valid

    def test_validate_no_schema(self):
        t = Template("{{ name }}")
        assert t.validate({"name": "x"}) is None


# ---------------------------------------------------------------------------
# render_template / render_file
# ---------------------------------------------------------------------------

class TestRenderFunctions:
    def test_render_template(self):
        result = render_template("{{ x }} + {{ y }}", {"x": "1", "y": "2"})
        assert result == "1 + 2"

    def test_render_file(self):
        source = '{#schema\n{"type":"object","required":["name"],"properties":{"name":{"type":"string"}}}\n#}\nHello {{ name }}'
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".kata.md", delete=False, dir="/tmp"
        ) as f:
            f.write(source)
            path = f.name

        try:
            result = render_file(path, {"name": "World"})
            assert result.strip() == "Hello World"
        finally:
            os.unlink(path)

    def test_render_file_validation_failure(self):
        source = '{#schema\n{"type":"object","required":["name"],"properties":{"name":{"type":"string"}}}\n#}\n{{ name }}'
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".kata.md", delete=False, dir="/tmp"
        ) as f:
            f.write(source)
            path = f.name

        try:
            with pytest.raises(ValueError):
                render_file(path, {})
        finally:
            os.unlink(path)

    def test_render_file_skip_validation(self):
        source = '{#schema\n{"type":"object","required":["name"],"properties":{"name":{"type":"string"}}}\n#}\n{{ name }}'
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".kata.md", delete=False, dir="/tmp"
        ) as f:
            f.write(source)
            path = f.name

        try:
            result = render_file(path, {}, validate=False)
            assert result.strip() == ""
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# Annotation rendering
# ---------------------------------------------------------------------------

class TestAnnotation:
    """Tests for render_annotated, generate_schema_reference, strip_annotations."""

    def _make_template(self, schema: dict, body: str) -> Template:
        schema_json = json.dumps(schema)
        source = f"{{#schema\n{schema_json}\n#}}\n{body}"
        return Template(source)

    def test_simple_var_annotated(self):
        schema = {"type": "object", "properties": {"title": {"type": "string"}}}
        tpl = self._make_template(schema, "# {{ title }}")
        result = tpl.render_annotated({"title": "Hello"})
        assert '<span data-kata="p-title">Hello</span>' in result

    def test_dotted_var_not_in_loop(self):
        schema = {
            "type": "object",
            "properties": {"info": {"type": "object", "properties": {"name": {"type": "string"}}}},
        }
        tpl = self._make_template(schema, "{{ info.name }}")
        result = tpl.render_annotated({"info": {"name": "Alice"}})
        assert '<span data-kata="p-info-name">Alice</span>' in result

    def test_for_loop_child_var_annotated(self):
        schema = {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"name": {"type": "string"}},
                    },
                },
            },
        }
        tpl = self._make_template(schema, "{% for x in items %}{{ x.name }}{% endfor %}")
        result = tpl.render_annotated({"items": [{"name": "A"}, {"name": "B"}]})
        assert '<span data-kata="p-items-name">A</span>' in result
        assert '<span data-kata="p-items-name">B</span>' in result

    def test_filter_does_not_break_annotation(self):
        schema = {"type": "object", "properties": {"title": {"type": "string"}}}
        tpl = self._make_template(schema, "{{ title | upper }}")
        result = tpl.render_annotated({"title": "hello"})
        assert '<span data-kata="p-title">HELLO</span>' in result

    def test_literal_not_annotated(self):
        schema = {"type": "object", "properties": {"x": {"type": "string"}}}
        tpl = self._make_template(schema, '{{ "literal" }}')
        result = tpl.render_annotated({"x": "val"})
        assert "data-kata=" not in result

    def test_loop_var_not_annotated(self):
        schema = {
            "type": "object",
            "properties": {"items": {"type": "array", "items": {"type": "string"}}},
        }
        tpl = self._make_template(schema, "{% for x in items %}{{ loop.index }}{% endfor %}")
        result = tpl.render_annotated({"items": ["a"]})
        assert "data-kata=" not in result

    def test_none_value_not_annotated(self):
        schema = {"type": "object", "properties": {"title": {"type": "string"}}}
        tpl = self._make_template(schema, "{{ title }}")
        result = tpl.render_annotated({"title": None})
        assert "data-kata=" not in result

    def test_schema_reference_section_generated(self):
        schema = {
            "type": "object",
            "required": ["title"],
            "properties": {"title": {"type": "string", "minLength": 1}},
        }
        tpl = self._make_template(schema, "# {{ title }}")
        result = tpl.render_annotated({"title": "Hello"})
        assert "Schema Reference" in result
        assert "title: string!" in result

    def test_schema_reference_nested_array(self):
        schema = {
            "type": "object",
            "properties": {
                "attendees": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name"],
                        "properties": {
                            "name": {"type": "string"},
                            "role": {"type": "string"},
                        },
                    },
                },
            },
        }
        ref = generate_schema_reference(schema)
        assert "attendees[]:" in ref
        assert "name: string!" in ref
        assert "role: string" in ref

    def test_no_schema_falls_back_to_plain(self):
        tpl = Template("# {{ title }}")
        assert tpl.schema is None
        result = tpl.render_annotated({"title": "Hello"})
        # No schema → links still attempted but no reference section
        assert "Schema Reference" not in result

    def test_render_file_annotated(self):
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        schema_json = json.dumps(schema)
        source = f"{{#schema\n{schema_json}\n#}}\nHello {{{{ name }}}}"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".kata.md", delete=False, dir="/tmp"
        ) as f:
            f.write(source)
            path = f.name

        try:
            result = render_file(path, {"name": "World"}, annotate=True)
            assert '<span data-kata="p-name">World</span>' in result
            assert "Schema Reference" in result
        finally:
            os.unlink(path)


class TestStripAnnotations:
    def test_strip_data_kata(self):
        text = '# <span data-kata="p-title">Hello</span>\n\n<span data-kata="p-attendees-name">Alice</span>'
        result = strip_annotations(text)
        assert result == "# Hello\n\nAlice"
        assert "data-kata" not in result

    def test_strip_legacy_links(self):
        text = "# [Hello](#p-title)\n\n[Alice](#p-attendees-name)"
        result = strip_annotations(text)
        assert result == "# Hello\n\nAlice"
        assert "#p-" not in result

    def test_strip_schema_reference_section(self):
        text = "# Hello\n\n---\n\n<details>\n<summary>Schema Reference</summary>\n\n#### title\n- type: string\n\n</details>\n"
        result = strip_annotations(text)
        assert "Schema Reference" not in result
        assert "# Hello" in result

    def test_strip_both(self):
        text = '# <span data-kata="p-title">Hello</span>\n\n---\n\n<details>\n<summary>Schema Reference</summary>\n\n#### <a id="p-title"></a>title\n- **type**: string\n\n</details>\n'
        result = strip_annotations(text)
        assert result.strip() == "# Hello"
        assert "data-kata" not in result
        assert "Schema Reference" not in result

    def test_no_annotations_unchanged(self):
        text = "# Hello\n\nSome content"
        assert strip_annotations(text) == text
