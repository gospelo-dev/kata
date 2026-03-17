# KATA Markdown™ — gospelo-kata
# Copyright (c) 2025 gospelo. All rights reserved.
# Licensed under the MIT License. See LICENSE.md for details.

"""Coverage analysis for checklist items.

Analyzes which checklist items are covered by existing document directories,
and generates coverage reports (JSON, Markdown).

Based on agentic-tester's coverage.py, generalized to work with any
checklist.json and document directory structure.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ChecklistItem:
    """A single checklist item."""

    id: str
    name: str
    name_ja: str
    template: str = ""
    tags: list[str] = field(default_factory=list)


@dataclass
class CoverageResult:
    """Coverage analysis result for a single checklist item."""

    item: ChecklistItem
    covered: bool
    suite_dir: str = ""
    kata_md_exists: bool = False


@dataclass
class CoverageReport:
    """Full coverage report."""

    total: int
    covered: int
    uncovered: int
    coverage_pct: float
    results: list[CoverageResult] = field(default_factory=list)
    by_template: dict[str, dict[str, int]] = field(default_factory=dict)


def load_checklist(checklist_path: str | Path) -> list[ChecklistItem]:
    """Load checklist items from JSON file.

    Expects a JSON file with top-level "categories" array,
    each containing an "items" array.

    Args:
        checklist_path: Path to checklist JSON file.

    Returns:
        Flat list of all checklist items across categories.
    """
    path = Path(checklist_path)
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    items: list[ChecklistItem] = []
    for category in data.get("categories", []):
        for item_data in category.get("items", []):
            items.append(
                ChecklistItem(
                    id=item_data["id"],
                    name=item_data.get("name", ""),
                    name_ja=item_data.get("name_ja", ""),
                    template=item_data.get("template", ""),
                    tags=item_data.get("tags", []),
                )
            )
    return items


def scan_suites(tests_dir: str | Path) -> dict[str, dict[str, bool]]:
    """Scan directories for existing .kata.md documents.

    Args:
        tests_dir: Parent directory containing subdirectories.

    Returns:
        Dict mapping directory name to presence of key files:
        {"01_sql_injection": {"kata_md": True}, ...}
    """
    tests_path = Path(tests_dir)
    if not tests_path.is_dir():
        return {}

    suites: dict[str, dict[str, bool]] = {}
    for entry in sorted(tests_path.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith((".", "_")):
            continue

        kata_md_exists = any(
            f.name.endswith(".kata.md")
            for f in entry.iterdir()
            if f.is_file()
        )
        outputs_dir = entry / "outputs"
        if not kata_md_exists and outputs_dir.is_dir():
            kata_md_exists = any(
                f.name.endswith(".kata.md")
                for f in outputs_dir.iterdir()
                if f.is_file()
            )

        suites[entry.name] = {
            "kata_md": kata_md_exists,
        }
    return suites


def _match_item_to_suite(item_id: str, suite_dirs: list[str]) -> str | None:
    """Try to match a checklist item ID to a directory.

    Matching rules:
    - Item "1" matches dir starting with "01_"
    - Item "5-1" matches dir starting with "05-1_" or "05_"
    - Item "14" matches dir starting with "14_"
    """
    parts = item_id.split("-", 1)
    base = parts[0]
    sub = parts[1] if len(parts) > 1 else None
    base_padded = base.zfill(2)

    # Exact sub-item match first (e.g., "05-1_specific")
    if sub:
        for suite_dir in suite_dirs:
            if suite_dir.startswith(f"{base_padded}-{sub}_"):
                return suite_dir

    # Fallback to base match (e.g., "05_general")
    for suite_dir in suite_dirs:
        if suite_dir.startswith(f"{base_padded}_"):
            return suite_dir

    return None


def analyze_coverage(
    checklist_path: str | Path,
    tests_dir: str | Path,
    mapping: dict[str, str] | None = None,
) -> CoverageReport:
    """Analyze which checklist items are covered by existing directories.

    Args:
        checklist_path: Path to checklist JSON file.
        tests_dir: Parent directory containing subdirectories.
        mapping: Optional explicit mapping of item_id -> dir_name.

    Returns:
        CoverageReport with per-item and aggregate results.
    """
    items = load_checklist(checklist_path)
    suites = scan_suites(tests_dir)
    suite_dirs = list(suites.keys())
    mapping = mapping or {}

    results: list[CoverageResult] = []
    template_stats: dict[str, dict[str, int]] = {}

    for item in items:
        matched_dir = mapping.get(item.id) or _match_item_to_suite(item.id, suite_dirs)

        covered = False
        kata_md_exists = False

        if matched_dir and matched_dir in suites:
            kata_md_exists = suites[matched_dir]["kata_md"]
            covered = kata_md_exists

        results.append(
            CoverageResult(
                item=item,
                covered=covered,
                suite_dir=matched_dir or "",
                kata_md_exists=kata_md_exists,
            )
        )

        # Template stats
        tmpl = item.template or "(none)"
        if tmpl not in template_stats:
            template_stats[tmpl] = {"total": 0, "covered": 0}
        template_stats[tmpl]["total"] += 1
        if covered:
            template_stats[tmpl]["covered"] += 1

    covered_count = sum(1 for r in results if r.covered)
    total = len(results)

    return CoverageReport(
        total=total,
        covered=covered_count,
        uncovered=total - covered_count,
        coverage_pct=round(covered_count / total * 100, 1) if total > 0 else 0.0,
        results=results,
        by_template=template_stats,
    )


def uncovered_items(report: CoverageReport) -> list[dict[str, Any]]:
    """Extract uncovered items from a CoverageReport."""
    return [
        {
            "id": r.item.id,
            "name": r.item.name,
            "name_ja": r.item.name_ja,
            "template": r.item.template,
            "tags": r.item.tags,
        }
        for r in report.results
        if not r.covered
    ]


def report_to_dict(report: CoverageReport) -> dict[str, Any]:
    """Convert CoverageReport to a JSON-serializable dict."""
    return {
        "summary": {
            "total": report.total,
            "covered": report.covered,
            "uncovered": report.uncovered,
            "coverage_pct": report.coverage_pct,
        },
        "by_template": report.by_template,
        "items": [
            {
                "id": r.item.id,
                "name": r.item.name,
                "name_ja": r.item.name_ja,
                "template": r.item.template,
                "covered": r.covered,
                "suite_dir": r.suite_dir,
                "kata_md_exists": r.kata_md_exists,
            }
            for r in report.results
        ],
    }


def report_to_markdown(report: CoverageReport) -> str:
    """Convert CoverageReport to a Markdown summary."""
    lines: list[str] = []
    lines.append("# Checklist Coverage Report")
    lines.append("")
    lines.append(f"Coverage: **{report.covered}/{report.total}** ({report.coverage_pct}%)")
    lines.append("")

    # Summary by template
    if report.by_template:
        lines.append("## By Template")
        lines.append("")
        lines.append("| Template | Total | Covered | Coverage |")
        lines.append("|----------|-------|---------|----------|")
        for tmpl, stats in sorted(report.by_template.items()):
            pct = round(stats["covered"] / stats["total"] * 100, 1) if stats["total"] > 0 else 0.0
            lines.append(f"| `{tmpl}` | {stats['total']} | {stats['covered']} | {pct}% |")
        lines.append("")

    # Detail table
    lines.append("## Item Details")
    lines.append("")
    lines.append("| No | Item | Covered | Dir | .kata.md |")
    lines.append("|----|------|---------|-----|----------|")
    for r in report.results:
        covered_mark = "OK" if r.covered else "--"
        kata_mark = "Yes" if r.kata_md_exists else "--"
        suite = r.suite_dir or "--"
        name = r.item.name_ja or r.item.name
        lines.append(f"| {r.item.id} | {name} | {covered_mark} | {suite} | {kata_mark} |")
    lines.append("")

    return "\n".join(lines)
