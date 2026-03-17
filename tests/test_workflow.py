# KATA Markdown™ — gospelo-kata
# Copyright (c) 2025 gospelo. All rights reserved.
# Licensed under the MIT License. See LICENSE.md for details.

"""Tests for gospelo_kata.workflow."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from gospelo_kata.workflow import (
    STEP_KEYS,
    WORKFLOW_FILENAME,
    get_pending_steps,
    init_status,
    is_step_done,
    load_status,
    mark_step_done,
    reset_for_retry,
    reset_status,
    status_summary,
)


@pytest.fixture
def suite_dir(tmp_path):
    """Create a temporary suite directory."""
    return tmp_path / "test_suite"


class TestInitStatus:
    def test_creates_file(self, suite_dir):
        status = init_status(suite_dir, template="checklist", output="checklist.kata.md")
        assert (suite_dir / WORKFLOW_FILENAME).exists()
        assert status["template"] == "checklist"
        assert status["output"] == "checklist.kata.md"
        assert status["round"] == 0
        assert status["history"] == []
        assert all(not status["steps"][k]["done"] for k in STEP_KEYS)

    def test_generated_metadata(self, suite_dir):
        status = init_status(suite_dir, template="checklist")
        gen = status["_generated"]
        assert gen["generator"] == "gospelo_kata"
        assert gen["format_version"] == 1


class TestLoadStatus:
    def test_default_when_missing(self, suite_dir):
        suite_dir.mkdir(parents=True)
        status = load_status(suite_dir)
        assert status["round"] == 0
        assert all(not status["steps"][k]["done"] for k in STEP_KEYS)

    def test_load_existing(self, suite_dir):
        init_status(suite_dir, template="test_spec", output="test_spec.kata.md")
        status = load_status(suite_dir)
        assert status["template"] == "test_spec"


class TestMarkStepDone:
    def test_mark_init(self, suite_dir):
        init_status(suite_dir, template="checklist")
        status = mark_step_done(suite_dir, "init")
        assert status["steps"]["init"]["done"] is True
        assert "at" in status["steps"]["init"]

    def test_mark_with_note(self, suite_dir):
        init_status(suite_dir, template="checklist")
        status = mark_step_done(suite_dir, "lint", note="0 errors")
        assert status["steps"]["lint"]["note"] == "0 errors"

    def test_invalid_step_raises(self, suite_dir):
        init_status(suite_dir, template="checklist")
        with pytest.raises(ValueError, match="Unknown step key"):
            mark_step_done(suite_dir, "nonexistent_step")

    def test_persists_to_disk(self, suite_dir):
        init_status(suite_dir, template="checklist")
        mark_step_done(suite_dir, "validate")
        # Re-load from disk
        status = load_status(suite_dir)
        assert status["steps"]["validate"]["done"] is True


class TestResetForRetry:
    def test_increments_round(self, suite_dir):
        init_status(suite_dir, template="checklist")
        mark_step_done(suite_dir, "init")
        mark_step_done(suite_dir, "validate")
        mark_step_done(suite_dir, "generate")
        mark_step_done(suite_dir, "lint", note="3 errors")

        status = reset_for_retry(suite_dir, reason="lint: 3 errors")
        assert status["round"] == 1
        assert not status["steps"]["validate"]["done"]
        assert not status["steps"]["generate"]["done"]
        assert not status["steps"]["lint"]["done"]
        # init should still be done
        assert status["steps"]["init"]["done"]

    def test_records_history(self, suite_dir):
        init_status(suite_dir, template="checklist")
        mark_step_done(suite_dir, "validate")
        mark_step_done(suite_dir, "generate")
        mark_step_done(suite_dir, "lint")

        reset_for_retry(suite_dir, reason="lint NG")
        status = load_status(suite_dir)

        assert len(status["history"]) == 1
        assert status["history"][0]["round"] == 0
        assert status["history"][0]["reason"] == "lint NG"
        assert "validate" in status["history"][0]["steps_reset"]

    def test_multiple_rounds(self, suite_dir):
        init_status(suite_dir, template="checklist")
        mark_step_done(suite_dir, "validate")
        mark_step_done(suite_dir, "generate")
        mark_step_done(suite_dir, "lint")
        reset_for_retry(suite_dir, reason="round 0 NG")

        mark_step_done(suite_dir, "validate")
        mark_step_done(suite_dir, "generate")
        mark_step_done(suite_dir, "lint")
        status = reset_for_retry(suite_dir, reason="round 1 NG")

        assert status["round"] == 2
        assert len(status["history"]) == 2


class TestResetStatus:
    def test_resets_all(self, suite_dir):
        init_status(suite_dir, template="checklist")
        for key in STEP_KEYS:
            mark_step_done(suite_dir, key)

        status = reset_status(suite_dir)
        assert status["round"] == 0
        assert status["history"] == []
        assert all(not status["steps"][k]["done"] for k in STEP_KEYS)


class TestGetPendingSteps:
    def test_all_pending_initially(self, suite_dir):
        init_status(suite_dir, template="checklist")
        status = load_status(suite_dir)
        assert get_pending_steps(status) == STEP_KEYS

    def test_partial_done(self, suite_dir):
        init_status(suite_dir, template="checklist")
        mark_step_done(suite_dir, "init")
        mark_step_done(suite_dir, "validate")
        status = load_status(suite_dir)
        pending = get_pending_steps(status)
        assert "init" not in pending
        assert "validate" not in pending
        assert "generate" in pending


class TestStatusSummary:
    def test_summary_format(self, suite_dir):
        init_status(suite_dir, template="checklist", output="checklist.kata.md")
        mark_step_done(suite_dir, "init")
        status = load_status(suite_dir)

        summary = status_summary(status)
        assert "Template: checklist" in summary
        assert "Output:   checklist.kata.md" in summary
        assert "Round:    0" in summary
        assert "1/5" in summary
        assert "[OK] init" in summary
        assert "[--] validate" in summary
