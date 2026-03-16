"""Tests for gospelo_kata.coverage."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gospelo_kata.coverage import (
    ChecklistItem,
    CoverageReport,
    CoverageResult,
    _match_item_to_suite,
    analyze_coverage,
    load_checklist,
    report_to_dict,
    report_to_markdown,
    scan_suites,
    uncovered_items,
)


@pytest.fixture
def checklist_json(tmp_path):
    """Create a sample checklist JSON file."""
    data = {
        "categories": [
            {
                "id": "cat1",
                "name": "Category 1",
                "items": [
                    {"id": "1", "name": "Item One", "name_ja": "項目1", "template": "checklist", "tags": ["web"]},
                    {"id": "2", "name": "Item Two", "name_ja": "項目2", "template": "checklist", "tags": []},
                    {"id": "5-1", "name": "Item Five Sub One", "name_ja": "項目5-1", "template": "test_spec"},
                ],
            },
            {
                "id": "cat2",
                "name": "Category 2",
                "items": [
                    {"id": "14", "name": "Item Fourteen", "name_ja": "項目14", "template": "checklist"},
                ],
            },
        ],
    }
    path = tmp_path / "checklist.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


@pytest.fixture
def tests_dir(tmp_path):
    """Create sample test suite directories."""
    base = tmp_path / "tests"
    # Covered: has .kata.md
    suite1 = base / "01_item_one"
    suite1.mkdir(parents=True)
    (suite1 / "checklist.kata.md").write_text("# Test")

    # Covered: has .kata.md in outputs/
    suite2 = base / "02_item_two"
    (suite2 / "outputs").mkdir(parents=True)
    (suite2 / "outputs" / "checklist.kata.md").write_text("# Test")

    # Not covered: no .kata.md
    suite14 = base / "14_item_fourteen"
    suite14.mkdir(parents=True)
    (suite14 / "readme.md").write_text("# Readme")

    # Hidden dir should be skipped
    hidden = base / ".hidden"
    hidden.mkdir(parents=True)

    return base


class TestLoadChecklist:
    def test_loads_all_items(self, checklist_json):
        items = load_checklist(checklist_json)
        assert len(items) == 4
        assert items[0].id == "1"
        assert items[0].name_ja == "項目1"
        assert items[0].template == "checklist"
        assert items[0].tags == ["web"]

    def test_optional_fields(self, tmp_path):
        data = {
            "categories": [{
                "id": "c",
                "name": "C",
                "items": [{"id": "1", "name": "X"}],
            }]
        }
        path = tmp_path / "minimal.json"
        path.write_text(json.dumps(data))
        items = load_checklist(path)
        assert items[0].name_ja == ""
        assert items[0].template == ""
        assert items[0].tags == []


class TestScanSuites:
    def test_scans_directories(self, tests_dir):
        suites = scan_suites(tests_dir)
        assert "01_item_one" in suites
        assert suites["01_item_one"]["kata_md"] is True
        assert "14_item_fourteen" in suites
        assert suites["14_item_fourteen"]["kata_md"] is False

    def test_skips_hidden(self, tests_dir):
        suites = scan_suites(tests_dir)
        assert ".hidden" not in suites

    def test_nonexistent_dir(self, tmp_path):
        suites = scan_suites(tmp_path / "nonexistent")
        assert suites == {}


class TestMatchItemToSuite:
    def test_simple_match(self):
        dirs = ["01_sql_injection", "02_xss", "14_auth"]
        assert _match_item_to_suite("1", dirs) == "01_sql_injection"
        assert _match_item_to_suite("2", dirs) == "02_xss"
        assert _match_item_to_suite("14", dirs) == "14_auth"

    def test_sub_item_exact(self):
        dirs = ["05_general", "05-1_specific"]
        assert _match_item_to_suite("5-1", dirs) == "05-1_specific"

    def test_sub_item_fallback_to_base(self):
        dirs = ["05_general"]
        assert _match_item_to_suite("5-1", dirs) == "05_general"

    def test_no_match(self):
        dirs = ["01_sql", "02_xss"]
        assert _match_item_to_suite("99", dirs) is None


class TestAnalyzeCoverage:
    def test_full_analysis(self, checklist_json, tests_dir):
        report = analyze_coverage(checklist_json, tests_dir)
        assert report.total == 4
        assert report.covered == 2  # 01 and 02 have .kata.md
        assert report.uncovered == 2  # 5-1 (no dir) and 14 (no .kata.md)
        assert report.coverage_pct == 50.0

    def test_explicit_mapping(self, checklist_json, tests_dir):
        # Map item 14 to suite 01 (which has .kata.md)
        report = analyze_coverage(checklist_json, tests_dir, mapping={"14": "01_item_one"})
        assert report.covered == 3

    def test_by_template_stats(self, checklist_json, tests_dir):
        report = analyze_coverage(checklist_json, tests_dir)
        assert "checklist" in report.by_template
        assert report.by_template["checklist"]["total"] == 3


class TestUncoveredItems:
    def test_returns_uncovered(self, checklist_json, tests_dir):
        report = analyze_coverage(checklist_json, tests_dir)
        uncov = uncovered_items(report)
        ids = [item["id"] for item in uncov]
        assert "5-1" in ids
        assert "14" in ids
        assert "1" not in ids


class TestReportToDict:
    def test_serializable(self, checklist_json, tests_dir):
        report = analyze_coverage(checklist_json, tests_dir)
        d = report_to_dict(report)
        # Should be JSON-serializable
        json.dumps(d, ensure_ascii=False)
        assert d["summary"]["total"] == 4
        assert len(d["items"]) == 4


class TestReportToMarkdown:
    def test_markdown_output(self, checklist_json, tests_dir):
        report = analyze_coverage(checklist_json, tests_dir)
        md = report_to_markdown(report)
        assert "# Checklist Coverage Report" in md
        assert "2/4" in md
        assert "50.0%" in md
        assert "| No | Item |" in md
