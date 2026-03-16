"""Markdown document generator.

Converts structured data to Markdown using KATA Markdown™ templates.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def generate_checklist_md(data: dict[str, Any]) -> str:
    """Generate a checklist Markdown from data.

    Uses the checklist_tpl.kata.md template via the built-in template engine.
    Renders with annotate=True so that values are auto-linked to the
    Schema Reference section appended at the bottom.

    Args:
        data: Parsed checklist data.

    Returns:
        Markdown string.
    """
    from ..template import render_file

    template_path = Path(__file__).parent.parent / "templates" / "checklist" / "checklist_tpl.kata.md"
    return render_file(str(template_path), data, validate=True, annotate=True)


def generate_test_spec_md(data: dict[str, Any]) -> str:
    """Generate a test specification Markdown from data.

    Args:
        data: Parsed test spec data.

    Returns:
        Markdown string.
    """
    lines: list[str] = []
    test_name = data.get("test_name", "Test Specification")
    lines.append(f"# {test_name}")
    lines.append("")

    test_cases = data.get("test_cases", [])
    if not test_cases:
        lines.append("No test cases defined.")
        return "\n".join(lines)

    # Group by category
    categories: dict[str, list[dict]] = {}
    for case in test_cases:
        cat = case.get("category", "Uncategorized")
        categories.setdefault(cat, []).append(case)

    for cat_name, cases in categories.items():
        lines.append(f"## {cat_name}")
        lines.append("")
        lines.append("| ID | Description | Expected Result | Priority |")
        lines.append("|:--:|-------------|-----------------|:--------:|")

        for case in cases:
            test_id = case["test_id"]
            desc = case["description"]
            expected = case["expected_result"]
            priority = case.get("priority", "-")
            lines.append(f"| {test_id} | {desc} | {expected} | {priority} |")

        lines.append("")

    lines.append(f"Total: {len(test_cases)} test cases")
    lines.append("")

    return "\n".join(lines)


def generate_prereq_md(data: dict[str, Any]) -> str:
    """Generate a prerequisites Markdown from data.

    Args:
        data: Parsed test prereq data.

    Returns:
        Markdown string.
    """
    lines: list[str] = []
    test_name = data.get("test_name", "Test Prerequisites")
    lines.append(f"# {test_name}")
    lines.append("")

    # Summary
    summary = data.get("summary", {})
    if summary:
        lines.append("## Summary")
        lines.append("")
        lines.append("| Key | Value |")
        lines.append("|-----|-------|")
        for key in ["project", "target", "db", "client", "test_environment"]:
            if key in summary:
                lines.append(f"| {key} | {summary[key]} |")
        lines.append("")

        steps = summary.get("steps", [])
        if steps:
            lines.append("### Steps")
            lines.append("")
            for step in steps:
                lines.append(f"- {step}")
            lines.append("")

    # Background
    background = data.get("background", [])
    if background:
        lines.append("## Background")
        lines.append("")
        for item in background:
            lines.append(f"- **{item['key']}**: {item['value']}")
        lines.append("")

    # Perspectives
    perspectives = data.get("perspectives", [])
    if perspectives:
        lines.append("## Test Perspectives")
        lines.append("")
        for item in perspectives:
            lines.append(f"- **{item['name']}**: {item['description']}")
        lines.append("")

    # Constraints
    constraints = data.get("constraints", [])
    if constraints:
        lines.append("## Constraints")
        lines.append("")
        for item in constraints:
            lines.append(f"- {item}")
        lines.append("")

    # Environment
    environment = data.get("environment", [])
    if environment:
        lines.append("## Environment")
        lines.append("")
        lines.append("| Key | Value |")
        lines.append("|-----|-------|")
        for item in environment:
            lines.append(f"| {item['key']} | {item['value']} |")
        lines.append("")

    # Test Data
    test_data = data.get("test_data", [])
    if test_data:
        lines.append("## Test Data")
        lines.append("")
        for item in test_data:
            lines.append(f"- **{item['key']}**: {item['value']}")
        lines.append("")

    # References
    references = data.get("references", [])
    if references:
        lines.append("## References")
        lines.append("")
        for item in references:
            lines.append(f"- [{item['name']}]({item['path']})")
        lines.append("")

    return "\n".join(lines)


def generate_agenda_md(data: dict[str, Any]) -> str:
    """Generate meeting agenda Markdown from data.

    Args:
        data: Parsed agenda data.

    Returns:
        Markdown string.
    """
    lines: list[str] = []
    lines.append(f"# {data.get('title', 'Meeting Minutes')}")
    lines.append("")

    # Meeting info
    lines.append("## Meeting Info")
    lines.append("")
    lines.append("| Item | Value |")
    lines.append("|------|-------|")
    for key in ["date", "time", "location"]:
        if data.get(key):
            lines.append(f"| {key.replace('_', ' ').title()} | {data[key]} |")
    lines.append("")

    # Attendees
    attendees = data.get("attendees", [])
    if attendees:
        lines.append("## Attendees")
        lines.append("")
        lines.append("| Name | Role | Department |")
        lines.append("|------|------|------------|")
        for a in attendees:
            name = a.get("name", "")
            role = a.get("role", "")
            dept = a.get("department", "")
            lines.append(f"| {name} | {role} | {dept} |")
        lines.append("")

    absentees = data.get("absentees", [])
    if absentees:
        lines.append("**Absentees:** " + ", ".join(absentees))
        lines.append("")

    # Agenda & Discussion
    agenda = data.get("agenda", [])
    if agenda:
        lines.append("## Agenda")
        lines.append("")
        for item in agenda:
            presenter = f" ({item['presenter']})" if item.get("presenter") else ""
            duration = f" [{item['duration_min']} min]" if item.get("duration_min") else ""
            lines.append(f"### {item['id']}. {item['topic']}{presenter}{duration}")
            lines.append("")
            if item.get("notes"):
                lines.append(f"*{item['notes']}*")
                lines.append("")
            for point in item.get("discussion", []):
                lines.append(f"- {point}")
            lines.append("")

    # Decisions
    decisions = data.get("decisions", [])
    if decisions:
        lines.append("## Decisions")
        lines.append("")
        lines.append("| ID | Decision | Decided By | Agenda |")
        lines.append("|----|----------|------------|--------|")
        for d in decisions:
            lines.append(
                f"| {d['id']} | {d['description']} "
                f"| {d.get('decided_by', '')} | {d.get('related_agenda', '')} |"
            )
        lines.append("")

    # Action Items
    action_items = data.get("action_items", [])
    if action_items:
        lines.append("## Action Items")
        lines.append("")
        lines.append("| ID | Action | Assignee | Due Date | Status |")
        lines.append("|----|--------|----------|----------|--------|")
        for a in action_items:
            lines.append(
                f"| {a['id']} | {a['description']} "
                f"| {a['assignee']} | {a.get('due_date', '')} | {a.get('status', 'open')} |"
            )
        lines.append("")

    # Next Meeting
    next_meeting = data.get("next_meeting")
    if next_meeting:
        lines.append("## Next Meeting")
        lines.append("")
        parts = []
        if next_meeting.get("date"):
            parts.append(next_meeting["date"])
        if next_meeting.get("time"):
            parts.append(next_meeting["time"])
        if next_meeting.get("location"):
            parts.append(next_meeting["location"])
        if parts:
            lines.append(" / ".join(parts))
            lines.append("")

    # Remarks
    if data.get("remarks"):
        lines.append("## Remarks")
        lines.append("")
        lines.append(data["remarks"])
        lines.append("")

    return "\n".join(lines)


def _kata_metadata_comment(doc_type: str) -> str:
    """Generate a kata metadata HTML comment line."""
    from datetime import date
    meta = {"schema": doc_type, "generated": date.today().isoformat()}
    return f"<!-- kata: {json.dumps(meta, ensure_ascii=False)} -->"


def parse_kata_metadata(text: str) -> dict[str, Any] | None:
    """Extract kata metadata from an HTML comment in Markdown text.

    Looks for: <!-- kata: {"schema": "...", ...} -->

    Returns:
        Parsed metadata dict, or None if not found.
    """
    import re
    m = re.search(r"<!--\s*kata:\s*(\{.*?\})\s*-->", text)
    if m is None:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def generate(
    data: dict[str, Any],
    doc_type: str | None = None,
    *,
    theme: str = "default",
    inline_css: bool = True,
) -> str:
    """Auto-detect document type and generate Markdown.

    Args:
        data: Parsed JSON data.
        doc_type: Explicit document type. Auto-detected if None.
        theme: Theme name for CSS styling. Default: "default".
        inline_css: If True, embed CSS in <style> tag. If False, omit CSS.

    Returns:
        Markdown string with kata metadata comment.
    """
    if doc_type is None:
        from ..validator import detect_schema
        doc_type = detect_schema(data)

    generators = {
        "checklist": generate_checklist_md,
        "test_spec": generate_test_spec_md,
        "test_prereq": generate_prereq_md,
        "agenda": generate_agenda_md,
    }

    gen_func = generators.get(doc_type or "")
    if gen_func is None:
        return _generate_generic_md(data)

    md = gen_func(data)

    # Replace embedded <style> with theme CSS if applicable
    if inline_css and theme:
        md = _apply_theme(md, theme)
    elif not inline_css:
        md = _strip_style_block(md)

    # Prepend kata metadata comment
    if doc_type:
        meta = {"schema": doc_type, "generated": __import__("datetime").date.today().isoformat()}
        if theme and not inline_css:
            meta["theme"] = theme
        md = f"<!-- kata: {json.dumps(meta, ensure_ascii=False)} -->\n" + md

    return md


def _apply_theme(md: str, theme: str) -> str:
    """Replace embedded <style> block with theme CSS."""
    from ..themes import get_theme_css, wrap_style

    try:
        css = get_theme_css(theme)
    except FileNotFoundError:
        return md  # Keep existing style if theme not found

    style_tag = wrap_style(css)

    # Replace existing <style>...</style> block
    import re
    style_pattern = re.compile(r"<style>.*?</style>\s*", re.DOTALL)
    if style_pattern.search(md):
        return style_pattern.sub(style_tag, md)
    else:
        return md + "\n" + style_tag


def _strip_style_block(md: str) -> str:
    """Remove <style>...</style> block from Markdown."""
    import re
    return re.sub(r"\n*<style>.*?</style>\s*", "", md, flags=re.DOTALL)


def _generate_generic_md(data: dict[str, Any]) -> str:
    """Fallback: generate Markdown from arbitrary JSON structure."""
    lines: list[str] = []
    lines.append("# Document")
    lines.append("")

    for key, value in data.items():
        if isinstance(value, str):
            lines.append(f"## {key}")
            lines.append("")
            lines.append(value)
            lines.append("")
        elif isinstance(value, list):
            lines.append(f"## {key}")
            lines.append("")
            for item in value:
                if isinstance(item, dict):
                    parts = [f"{k}: {v}" for k, v in item.items()]
                    lines.append(f"- {', '.join(parts)}")
                else:
                    lines.append(f"- {item}")
            lines.append("")
        elif isinstance(value, dict):
            lines.append(f"## {key}")
            lines.append("")
            for k, v in value.items():
                lines.append(f"- **{k}**: {v}")
            lines.append("")

    return "\n".join(lines)
