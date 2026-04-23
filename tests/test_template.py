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
    ENUM_COLOR_SCHEMES,
    Template,
    _collect_enum_map,
    _compute_structure_hash,
    _generate_enum_css,
    _resolve_color_scheme,
    extract_data,
    extract_schema,
    generate_schema_reference,
    merge_extracted_into_data,
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


class TestSetStatement:
    def test_simple_assignment(self):
        t = Template("{% set x = 42 %}{{ x }}")
        assert t.render() == "42"

    def test_string_literal_assignment(self):
        t = Template("{% set greeting = 'hello' %}{{ greeting }}")
        assert t.render() == "hello"

    def test_references_context_var(self):
        t = Template("{% set doubled = x * 2 %}{{ doubled }}")
        # x * 2 is not supported (no arithmetic), so this falls back
        # to a reference to x (which evaluates the whole expression).
        # Instead test with a filter that returns a value.
        t = Template("{% set upper_name = name | upper %}{{ upper_name }}")
        assert t.render(name="alice") == "ALICE"

    def test_overrides_previous_binding(self):
        t = Template("{% set x = 1 %}{% set x = 2 %}{{ x }}")
        assert t.render() == "2"

    def test_inside_for_loop(self):
        # `set` inside a for loop shadows per-iteration; we test that
        # the binding is visible after the assignment in the same
        # iteration.
        t = Template(
            "{% for u in users %}"
            "{% set label = u.name | upper %}"
            "{{ label }}"
            "{% endfor %}"
        )
        result = t.render(users=[{"name": "a"}, {"name": "b"}])
        assert result == "AB"

    def test_select_first_element(self):
        # This is the canonical cross-reference use case: pick an
        # element out of one array to use inside a loop over another.
        t = Template(
            "{% for cut in cuts %}"
            "{% set speaker = characters | selectattr('id', 'equalto', cut.speaker) | first %}"
            "[{{ speaker.name }}] "
            "{% endfor %}"
        )
        result = t.render(
            characters=[
                {"id": "a", "name": "Alice"},
                {"id": "b", "name": "Bob"},
            ],
            cuts=[{"speaker": "a"}, {"speaker": "b"}, {"speaker": "a"}],
        )
        assert result == "[Alice] [Bob] [Alice] "

    def test_no_output_from_set_itself(self):
        t = Template("before{% set x = 'hidden' %}after")
        assert t.render() == "beforeafter"

    def test_malformed_set_is_silently_skipped(self):
        # Malformed set tag should not crash the template. It's
        # treated like any other unknown block — skipped with no output.
        t = Template("before{% set broken %}after")
        assert t.render() == "beforeafter"


class TestSetAnnotationInteraction:
    def test_set_result_is_not_annotated(self):
        """Values bound via ``{% set %}`` must render as raw text.

        If an annotated path were emitted here, the same schema
        index would appear twice in the output (once at the source
        annotation, once at the derived display), inflating arrays
        on extract — exactly the bug this feature was meant to fix.
        """
        from gospelo_kata.template import Template
        tpl_src = (
            "{% for c in characters %}"
            "## {{ c.name }}\n"
            "{% endfor %}"
            "---\n"
            "{% for cut in cuts %}"
            "{% set speaker = characters | selectattr('id', 'equalto', cut.speaker) | first %}"
            "{{ speaker.name }}\n"
            "{% endfor %}"
        )
        data = {
            "characters": [
                {"id": "a", "name": "Alice"},
                {"id": "b", "name": "Bob"},
            ],
            "cuts": [
                {"speaker": "a"},
                {"speaker": "b"},
                {"speaker": "a"},
            ],
        }
        t = Template(tpl_src)
        out = t.render_dict(data)
        # Ensure the source annotations exist
        # (the render_dict path doesn't annotate, but the test proves
        # the for/set/selectattr chain renders correctly). Annotation
        # behavior is covered by the extract cross-reference test.
        # Alice: 1 source (Characters loop) + 2 derived (cuts 1 & 3)
        # Bob:   1 source (Characters loop) + 1 derived (cut 2)
        assert out.count("Alice") == 3
        assert out.count("Bob") == 2

    def test_derived_value_has_no_data_kata_span(self):
        """When the template is rendered with annotations, the values
        derived through ``{% set %}`` must render as plain text, not
        as another ``<span data-kata="p-characters-*">``. This is the
        core mechanism by which cross-referencing avoids inflating
        the source array during extract."""
        from gospelo_kata.template import Template
        schema = {
            "type": "object",
            "properties": {
                "characters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                        },
                    },
                },
                "cuts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"speaker": {"type": "string"}},
                    },
                },
            },
        }
        tpl_src = (
            "{#schema\n" + str(schema).replace("'", '"') + "\n#}\n"
            "{% for c in characters %}## {{ c.name }}\n{% endfor %}"
            "---\n"
            "{% for cut in cuts %}"
            "{% set speaker = characters | selectattr('id', 'equalto', cut.speaker) | first %}"
            "SPK-{{ speaker.name }}\n"
            "{% endfor %}"
        )
        # Write schema as JSON (safe form) — inline schema form
        import json as _json
        schema_json = _json.dumps(schema)
        tpl_src = (
            "{#schema\n" + schema_json + "\n#}\n"
            "{% for c in characters %}## {{ c.name }}\n{% endfor %}"
            "---\n"
            "{% for cut in cuts %}"
            "{% set speaker = characters | selectattr('id', 'equalto', cut.speaker) | first %}"
            "SPK-{{ speaker.name }}\n"
            "{% endfor %}"
        )
        data = {
            "characters": [
                {"id": "a", "name": "Alice"},
                {"id": "b", "name": "Bob"},
            ],
            "cuts": [
                {"speaker": "a"},
                {"speaker": "b"},
                {"speaker": "a"},
            ],
        }
        t = Template(tpl_src)
        out = t.render_annotated(data)
        # Source Characters annotations exist
        assert '<span data-kata="p-characters-0-name">Alice</span>' in out
        assert '<span data-kata="p-characters-1-name">Bob</span>' in out
        # Derived values appear as plain text prefix ("SPK-Alice")
        # — crucially, NO additional p-characters-*-name spans are
        # emitted from inside the cuts loop.
        derived_lines = [line for line in out.split("\n") if line.startswith("SPK-")]
        assert len(derived_lines) == 3
        for line in derived_lines:
            assert "data-kata" not in line


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
        assert '<span data-kata="p-items-0-name">A</span>' in result
        assert '<span data-kata="p-items-1-name">B</span>' in result

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
        assert "Specification" in result
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
        assert "Specification" not in result

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
            assert "Specification" in result
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
        text = "# Hello\n\n---\n\n<details>\n<summary>Specification</summary>\n\n#### title\n- type: string\n\n</details>\n"
        result = strip_annotations(text)
        assert "Specification" not in result
        assert "# Hello" in result

    def test_strip_both(self):
        text = '# <span data-kata="p-title">Hello</span>\n\n---\n\n<details>\n<summary>Specification</summary>\n\n#### <a id="p-title"></a>title\n- **type**: string\n\n</details>\n'
        result = strip_annotations(text)
        assert result.strip() == "# Hello"
        assert "data-kata" not in result
        assert "Specification" not in result

    def test_no_annotations_unchanged(self):
        text = "# Hello\n\nSome content"
        assert strip_annotations(text) == text


# ---------------------------------------------------------------------------
# Unified block format: **Schema** / **Data** / **Prompt** + ```yaml
# ---------------------------------------------------------------------------

class TestBoldCodeblockSchema:
    """extract_schema supports **Schema** + ```yaml code block form."""

    def test_bold_codeblock_schema_yaml(self):
        source = '**Schema**\n\n```yaml\ntype: object\nproperties:\n  title:\n    type: string\n```\n\n# {{ title }}'
        schema, cleaned = extract_schema(source)
        assert schema is not None
        assert schema["type"] == "object"
        assert "title" in schema["properties"]
        assert "**Schema**" not in cleaned
        assert "# {{ title }}" in cleaned

    def test_bold_codeblock_schema_json(self):
        source = '**Schema**\n\n```json\n{"type": "object", "properties": {"x": {"type": "string"}}}\n```\n\n{{ x }}'
        schema, cleaned = extract_schema(source)
        assert schema is not None
        assert schema["type"] == "object"
        assert "**Schema**" not in cleaned

    def test_bold_codeblock_schema_in_details(self):
        source = (
            '<details>\n<summary>Specification</summary>\n\n'
            '**Schema**\n\n```yaml\ntype: object\nproperties:\n  name:\n    type: string\n```\n\n'
            '</details>\n\n# {{ name }}'
        )
        schema, cleaned = extract_schema(source)
        assert schema is not None
        assert schema["properties"]["name"]["type"] == "string"
        assert "<details>" not in cleaned
        assert "# {{ name }}" in cleaned

    def test_bold_codeblock_schema_in_details_with_data(self):
        """When <details> has both **Schema** and **Data**, only schema is removed."""
        source = (
            '<details>\n<summary>Specification</summary>\n\n'
            '**Schema**\n\n```yaml\ntype: object\nproperties:\n  x:\n    type: string\n```\n\n'
            '**Data**\n\n```yaml\nx: hello\n```\n\n'
            '</details>\n\n# {{ x }}'
        )
        schema, cleaned = extract_schema(source)
        assert schema is not None
        assert "**Data**" in cleaned

    def test_template_parses_bold_codeblock_schema(self):
        source = '**Schema**\n\n```yaml\ntype: object\nproperties:\n  title:\n    type: string\n```\n\n# {{ title }}'
        t = Template(source)
        assert t.schema is not None
        assert t.schema["type"] == "object"
        result = t.render(title="Hello")
        assert "Hello" in result


class TestBoldCodeblockData:
    """extract_data supports **Data** + ```yaml code block form."""

    def test_bold_codeblock_data_yaml(self):
        source = '**Data**\n\n```yaml\ntitle: Hello World\nauthor: Alice\n```\n'
        data = extract_data(source)
        assert data is not None
        assert data["title"] == "Hello World"
        assert data["author"] == "Alice"

    def test_bold_codeblock_data_json(self):
        source = '**Data**\n\n```json\n{"title": "Hello"}\n```\n'
        data = extract_data(source)
        assert data is not None
        assert data["title"] == "Hello"

    def test_fallback_to_bold_codeblock(self):
        """When {#data} is absent, falls back to **Data** + code block."""
        source = 'Some text\n\n**Data**\n\n```yaml\nkey: value\n```\n'
        data = extract_data(source)
        assert data is not None
        assert data["key"] == "value"

    def test_inline_data_takes_priority(self):
        """When both {#data} and **Data** exist, {#data} is used."""
        source = '{#data\ntitle: from inline\n#}\n\n**Data**\n\n```yaml\ntitle: from bold\n```\n'
        data = extract_data(source)
        assert data is not None
        assert data["title"] == "from inline"

    def test_template_strips_bold_data(self):
        source = (
            '{#schema\n{"type":"object","properties":{"x":{"type":"string"}}}\n#}\n'
            '**Data**\n\n```yaml\nx: hello\n```\n\n# {{ x }}'
        )
        t = Template(source)
        assert t.data is not None
        assert t.data["x"] == "hello"
        assert "**Data**" not in t.template_body


class TestBoldCodeblockPrompt:
    """Template class supports **Prompt** + ```yaml code block form."""

    def test_prompt_codeblock_extracted(self):
        source = (
            '**Prompt**\n\n```yaml\nrole: You are a report generator\nformat: markdown\n```\n\n'
            '# {{ title }}'
        )
        t = Template(source)
        assert t.prompt is not None
        assert "role:" in t.prompt
        assert "**Prompt**" not in t.template_body

    def test_inline_prompt_still_works(self):
        source = '{#prompt\nrole: You are a helper\n#}\n\n# {{ title }}'
        t = Template(source)
        assert t.prompt is not None
        assert "role:" in t.prompt

    def test_prompt_included_in_schema_reference(self):
        source = (
            '**Prompt**\n\n```yaml\nrole: report generator\n```\n\n'
            '{#schema\n{"type":"object","required":["title"],"properties":{"title":{"type":"string"}}}\n#}\n'
            '# {{ title }}'
        )
        t = Template(source)
        result = t.render_annotated({"title": "Hello"})
        assert "Specification" in result
        assert "report generator" in result


class TestStripDetailsMultiBlock:
    """_strip_details_wrapper preserves sibling blocks when removing schema."""

    def test_details_with_schema_only_removes_all(self):
        source = (
            '<details>\n<summary>Schema</summary>\n\n'
            '{#schema\n{"type":"object"}\n#}\n\n'
            '</details>\n\n# Content'
        )
        schema, cleaned = extract_schema(source)
        assert schema is not None
        assert "<details>" not in cleaned
        assert "# Content" in cleaned

    def test_details_with_schema_and_data_preserves_data(self):
        source = (
            '<details>\n<summary>Specification</summary>\n\n'
            '{#schema\n{"type":"object","properties":{"x":{"type":"string"}}}\n#}\n\n'
            '{#data\nx: hello\n#}\n\n'
            '</details>\n\n# {{ x }}'
        )
        schema, cleaned = extract_schema(source)
        assert schema is not None
        assert "{#data" in cleaned

    def test_details_with_bold_schema_and_bold_data_preserves_data(self):
        source = (
            '<details>\n<summary>Specification</summary>\n\n'
            '**Schema**\n\n```yaml\ntype: object\nproperties:\n  x:\n    type: string\n```\n\n'
            '**Data**\n\n```yaml\nx: hello\n```\n\n'
            '</details>\n\n# {{ x }}'
        )
        schema, cleaned = extract_schema(source)
        assert schema is not None
        assert "**Data**" in cleaned


class TestGenerateSchemaReferenceBlocks:
    """generate_schema_reference includes prompt, template_body, and data."""

    def test_includes_prompt(self):
        schema = {"type": "object", "properties": {"x": {"type": "string"}}}
        ref = generate_schema_reference(schema, prompt="role: assistant")
        assert "**Prompt**" in ref
        assert "role: assistant" in ref

    def test_includes_template_body(self):
        schema = {"type": "object", "properties": {"x": {"type": "string"}}}
        ref = generate_schema_reference(schema, template_body="# {{ x }}")
        assert "```kata:template" in ref
        assert "# {{ x }}" in ref

    def test_includes_data(self):
        schema = {"type": "object", "properties": {"x": {"type": "string"}}}
        ref = generate_schema_reference(schema, data={"x": "hello"})
        assert "<summary>Data</summary>" in ref
        assert "hello" in ref

    def test_no_prompt_when_none(self):
        schema = {"type": "object", "properties": {"x": {"type": "string"}}}
        ref = generate_schema_reference(schema)
        assert "**Prompt**" not in ref

    def test_full_output_structure(self):
        schema = {"type": "object", "properties": {"title": {"type": "string"}}}
        ref = generate_schema_reference(
            schema, prompt="role: test", template_body="# {{ title }}", data={"title": "Hi"},
        )
        assert "**Prompt**" in ref
        assert "```kata:template" in ref
        assert "**Schema**" in ref
        assert "<summary>Data</summary>" in ref


# ---------------------------------------------------------------------------
# Structure integrity hash
# ---------------------------------------------------------------------------

class TestStructureIntegrity:
    """Tests for _compute_structure_hash and integrity embedding."""

    _SCHEMA = {
        "type": "object",
        "properties": {"title": {"type": "string"}},
        "required": ["title"],
    }

    def test_hash_present_in_output(self):
        ref = generate_schema_reference(
            self._SCHEMA, data={"title": "x"}, prompt="p", template_body="# {{ title }}"
        )
        assert "<!-- kata-structure-integrity: sha256:" in ref

    def test_hash_deterministic(self):
        ref1 = generate_schema_reference(
            self._SCHEMA, data={"title": "x"}, prompt="p", template_body="# {{ title }}"
        )
        ref2 = generate_schema_reference(
            self._SCHEMA, data={"title": "x"}, prompt="p", template_body="# {{ title }}"
        )
        import re
        h1 = re.search(r"sha256:([0-9a-f]{64})", ref1).group(1)
        h2 = re.search(r"sha256:([0-9a-f]{64})", ref2).group(1)
        assert h1 == h2

    def test_data_change_does_not_affect_hash(self):
        ref1 = generate_schema_reference(
            self._SCHEMA, data={"title": "aaa"}, prompt="p", template_body="t"
        )
        ref2 = generate_schema_reference(
            self._SCHEMA, data={"title": "zzz"}, prompt="p", template_body="t"
        )
        import re
        h1 = re.search(r"sha256:([0-9a-f]{64})", ref1).group(1)
        h2 = re.search(r"sha256:([0-9a-f]{64})", ref2).group(1)
        assert h1 == h2

    def test_prompt_change_affects_hash(self):
        ref1 = generate_schema_reference(
            self._SCHEMA, data={"title": "x"}, prompt="original", template_body="t"
        )
        ref2 = generate_schema_reference(
            self._SCHEMA, data={"title": "x"}, prompt="changed", template_body="t"
        )
        import re
        h1 = re.search(r"sha256:([0-9a-f]{64})", ref1).group(1)
        h2 = re.search(r"sha256:([0-9a-f]{64})", ref2).group(1)
        assert h1 != h2

    def test_schema_change_affects_hash(self):
        schema2 = {
            "type": "object",
            "properties": {"title": {"type": "integer"}},
            "required": ["title"],
        }
        ref1 = generate_schema_reference(
            self._SCHEMA, data={"title": "x"}, prompt="p", template_body="t"
        )
        ref2 = generate_schema_reference(
            schema2, data={"title": "x"}, prompt="p", template_body="t"
        )
        import re
        h1 = re.search(r"sha256:([0-9a-f]{64})", ref1).group(1)
        h2 = re.search(r"sha256:([0-9a-f]{64})", ref2).group(1)
        assert h1 != h2

    def test_template_body_change_affects_hash(self):
        ref1 = generate_schema_reference(
            self._SCHEMA, data={"title": "x"}, prompt="p", template_body="# {{ title }}"
        )
        ref2 = generate_schema_reference(
            self._SCHEMA, data={"title": "x"}, prompt="p", template_body="## {{ title }}"
        )
        import re
        h1 = re.search(r"sha256:([0-9a-f]{64})", ref1).group(1)
        h2 = re.search(r"sha256:([0-9a-f]{64})", ref2).group(1)
        assert h1 != h2


# ---------------------------------------------------------------------------
# Enum styling (rich UI)
# ---------------------------------------------------------------------------

class TestCollectEnumMap:
    def test_flat_enum(self):
        schema = {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["todo", "done"]},
                "title": {"type": "string"},
            },
        }
        result = _collect_enum_map(schema)
        assert result == {"status": ["todo", "done"]}

    def test_nested_array_enum(self):
        schema = {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "enum": ["todo", "done"]},
                            "task": {"type": "string"},
                        },
                    },
                },
            },
        }
        result = _collect_enum_map(schema)
        assert result == {"items-status": ["todo", "done"]}

    def test_no_enum(self):
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
        }
        assert _collect_enum_map(schema) == {}

    def test_none_schema(self):
        assert _collect_enum_map(None) == {}


class TestGenerateEnumCss:
    def test_known_enum_values(self):
        css = _generate_enum_css({"status": ["todo", "done"]})
        assert any("data-kata-enum" in line for line in css)
        assert any('"done"' in line for line in css)
        assert any('"todo"' in line for line in css)

    def test_empty_map(self):
        assert _generate_enum_css({}) == []

    def test_unknown_enum_values_no_color(self):
        css = _generate_enum_css({"kind": ["custom_value"]})
        # Base style should exist
        assert any("[data-kata-enum]" in line for line in css)
        # No specific color rule for unknown values
        assert not any("custom_value" in line for line in css)


class TestEnumSpanAnnotation:
    def test_enum_span_has_data_kata_enum_attr(self):
        src = (
            "status: {{ status }}\n"
            "{#schema\n"
            '{"type":"object","properties":{"status":{"type":"string","enum":["todo","done"]}}}\n'
            "#}\n"
        )
        tpl = Template(src)
        result = tpl.render_annotated({"status": "done"})
        assert 'data-kata-enum="done"' in result

    def test_non_enum_span_no_enum_attr(self):
        src = (
            "name: {{ name }}\n"
            "{#schema\n"
            '{"type":"object","properties":{"name":{"type":"string"}}}\n'
            "#}\n"
        )
        tpl = Template(src)
        result = tpl.render_annotated({"name": "Alice"})
        assert "data-kata-enum" not in result

    def test_enum_css_in_schema_reference(self):
        schema = {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["todo", "done"]},
            },
        }
        ref = generate_schema_reference(schema)
        assert 'data-kata-enum="done"' in ref
        assert 'data-kata-enum="todo"' in ref

    def test_array_enum_in_for_loop(self):
        src = (
            "{% for item in items %}{{ item.status }} {% endfor %}\n"
            "{#schema\n"
            '{"type":"object","properties":{"items":{"type":"array","items":'
            '{"type":"object","properties":{"status":{"type":"string","enum":["todo","done"]}}}}}}\n'
            "#}\n"
        )
        tpl = Template(src)
        result = tpl.render_annotated({"items": [{"status": "done"}, {"status": "todo"}]})
        assert 'data-kata-enum="done"' in result
        assert 'data-kata-enum="todo"' in result


class TestEnumColorSchemes:
    def test_all_schemes_exist(self):
        assert "default" in ENUM_COLOR_SCHEMES
        assert "pastel" in ENUM_COLOR_SCHEMES
        assert "vivid" in ENUM_COLOR_SCHEMES
        assert "monochrome" in ENUM_COLOR_SCHEMES
        assert "ocean" in ENUM_COLOR_SCHEMES

    def test_vivid_todo_uses_white_foreground(self):
        css = _generate_enum_css({"status": ["todo"]}, "vivid")
        joined = " ".join(css)
        assert "#ffffff" in joined

    def test_monochrome_no_color_hues(self):
        css = _generate_enum_css({"status": ["done", "todo"]}, "monochrome")
        joined = " ".join(css)
        # monochrome only uses gray-scale hex values (no a-f except in selectors)
        for line in css:
            if "background" in line:
                assert "#d4edda" not in line  # not default green

    def test_resolve_from_style(self):
        style = {"colorScheme": "vivid"}
        assert _resolve_color_scheme(style) == "vivid"

    def test_resolve_fallback_to_default(self):
        assert _resolve_color_scheme(None) == "default"

    def test_resolve_unknown_scheme_falls_back(self):
        style = {"colorScheme": "nonexistent"}
        assert _resolve_color_scheme(style) == "default"

    def test_schema_reference_uses_scheme(self):
        schema = {
            "type": "object",
            "properties": {"status": {"type": "string", "enum": ["todo"]}},
        }
        style = {"colorScheme": "vivid"}
        ref = generate_schema_reference(schema, style=style)
        assert "#00CEC9" in ref  # vivid todo uses cyan


class TestMergeExtractedIntoData:
    """merge_extracted_into_data protects un-annotated fields.

    LiveMorph (``sync to-data``) only gets back the values that the
    template actually wraps in ``<span data-kata=...>``. Fields like
    image src attributes, hidden dialogue lines, etc. must survive a
    round-trip; otherwise a single save in VSCode silently loses data.
    """

    def test_none_old_data_returns_extract(self):
        assert merge_extracted_into_data(None, {"a": 1}) == {"a": 1}

    def test_top_level_scalar_override(self):
        old = {"title": "Old", "version": "1.0"}
        new = {"title": "New"}
        # version is not in extract, must survive
        assert merge_extracted_into_data(old, new) == {
            "title": "New", "version": "1.0",
        }

    def test_top_level_new_key_added(self):
        # Extract surfaces a key we never had; merge keeps both
        assert merge_extracted_into_data({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}

    def test_nested_dict_merge(self):
        old = {"meta": {"author": "alice", "tags": ["a"]}}
        new = {"meta": {"author": "bob"}}
        assert merge_extracted_into_data(old, new) == {
            "meta": {"author": "bob", "tags": ["a"]}
        }

    def test_array_element_survival_of_unannotated_field(self):
        # Template annotates only ``name``; ``icon`` is rendered raw
        # in an <img src> attribute and never reaches extract.
        old = {
            "characters": [
                {"name": "Alice", "icon": "a.png"},
                {"name": "Bob", "icon": "b.png"},
            ],
        }
        extracted = {
            "characters": [
                {"name": "Alice"},
                {"name": "Bob"},
            ],
        }
        merged = merge_extracted_into_data(old, extracted)
        assert merged["characters"][0]["icon"] == "a.png"
        assert merged["characters"][1]["icon"] == "b.png"
        assert merged["characters"][0]["name"] == "Alice"

    def test_array_element_deleted_by_user(self):
        # User removed the third cut from the rendered view.
        # Extract has only 2 elements — merged result must match.
        old = {"cuts": [{"id": "c1"}, {"id": "c2"}, {"id": "c3"}]}
        extracted = {"cuts": [{"id": "c1"}, {"id": "c2"}]}
        merged = merge_extracted_into_data(old, extracted)
        assert len(merged["cuts"]) == 2
        assert merged["cuts"][1]["id"] == "c2"

    def test_array_element_added_beyond_old(self):
        # Rendered view gained a new row. Extract is longer than old;
        # the extra element is taken as-is (no old counterpart to merge).
        old = {"cuts": [{"id": "c1", "icon": "keep"}]}
        extracted = {
            "cuts": [{"id": "c1"}, {"id": "c2"}],
        }
        merged = merge_extracted_into_data(old, extracted)
        assert len(merged["cuts"]) == 2
        assert merged["cuts"][0] == {"id": "c1", "icon": "keep"}
        assert merged["cuts"][1] == {"id": "c2"}

    def test_extract_value_wins_over_old_scalar(self):
        old = {"a": {"n": 1}}
        new = {"a": {"n": 2}}
        assert merge_extracted_into_data(old, new) == {"a": {"n": 2}}

    def test_type_mismatch_extract_wins(self):
        # If the old value is a scalar but extract says array,
        # extract wins (shape change is user-intent).
        old = {"tags": "a"}
        new = {"tags": ["a", "b"]}
        assert merge_extracted_into_data(old, new) == {"tags": ["a", "b"]}

    def test_deep_nested_unannotated_survives(self):
        old = {
            "cuts": [
                {
                    "id": "c1",
                    "dialogue": ["line a", "line b"],
                    "image": "a.jpg",
                }
            ]
        }
        extracted = {"cuts": [{"id": "c1"}]}
        merged = merge_extracted_into_data(old, extracted)
        assert merged["cuts"][0]["dialogue"] == ["line a", "line b"]
        assert merged["cuts"][0]["image"] == "a.jpg"
