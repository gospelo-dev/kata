"""Workflow status management for document generation pipeline.

Each document directory has a .workflow_status.json that tracks
completion of each generation step: init → validate → generate → lint → review.

Based on agentic-tester's workflow_status.py, simplified for
document generation only.
"""

from __future__ import annotations

import fcntl
import json
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKFLOW_FILENAME = ".workflow_status.json"
LOCK_SUFFIX = ".lock"
FORMAT_VERSION = 1

STEP_KEYS = [
    "init",
    "validate",
    "generate",
    "lint",
    "review",
]

# lint NG or review NG → reset these steps
RETRY_RESET_KEYS = [
    "validate",
    "generate",
    "lint",
]


def load_status(suite_dir: str | Path) -> dict[str, Any]:
    """Load workflow status from a directory.

    Returns a dict with 'template', 'output', 'steps', 'round', 'history'.
    If the file does not exist, returns a default status.
    """
    path = Path(suite_dir) / WORKFLOW_FILENAME
    if not path.exists():
        return _default_status()

    with open(path, encoding="utf-8") as f:
        status = json.load(f)

    # Ensure required fields
    if "round" not in status:
        status["round"] = 0
    if "history" not in status:
        status["history"] = []
    if "steps" not in status:
        status["steps"] = {key: {"done": False} for key in STEP_KEYS}

    return status


def is_step_done(status: dict[str, Any], step_key: str) -> bool:
    """Check if a step is marked as done."""
    step = status.get("steps", {}).get(step_key, {})
    return step.get("done", False)


def mark_step_done(
    suite_dir: str | Path,
    step_key: str,
    note: str = "",
) -> dict[str, Any]:
    """Mark a step as done and save the updated status.

    Uses file locking to prevent concurrent write corruption.

    Args:
        suite_dir: Directory containing .workflow_status.json.
        step_key: Step to mark as done (init, validate, generate, lint, review).
        note: Optional comment (e.g., lint error count, review feedback).

    Returns:
        The updated status dict.
    """
    if step_key not in STEP_KEYS:
        msg = f"Unknown step key: {step_key}. Valid keys: {STEP_KEYS}"
        raise ValueError(msg)

    with _lock_status(suite_dir):
        status = load_status(suite_dir)
        step_data: dict[str, Any] = {
            "done": True,
            "at": _now_iso(),
        }
        if note:
            step_data["note"] = note

        status["steps"][step_key] = step_data
        _save_status_unlocked(suite_dir, status)
    return status


def reset_for_retry(
    suite_dir: str | Path,
    reason: str = "",
) -> dict[str, Any]:
    """Reset validate/generate/lint steps for retry loop.

    Increments the round counter, records the reset in history,
    and sets RETRY_RESET_KEYS back to done=false.

    Args:
        suite_dir: Directory containing .workflow_status.json.
        reason: Why the retry is needed (e.g., "lint: 3 errors").

    Returns:
        The updated status dict.
    """
    with _lock_status(suite_dir):
        status = load_status(suite_dir)
        now = _now_iso()

        # Record previous state in history
        prev_steps: dict[str, Any] = {}
        for key in RETRY_RESET_KEYS:
            step = status.get("steps", {}).get(key, {})
            if step.get("done"):
                prev_steps[key] = step.copy()

        current_round = status.get("round", 0)
        status["history"].append({
            "round": current_round,
            "steps_reset": list(prev_steps.keys()),
            "reason": reason or "retry after lint/review failure",
            "at": now,
        })

        # Increment round
        status["round"] = current_round + 1

        # Reset steps
        for key in RETRY_RESET_KEYS:
            status["steps"][key] = {"done": False}

        _save_status_unlocked(suite_dir, status)
    return status


def reset_status(suite_dir: str | Path) -> dict[str, Any]:
    """Reset all steps to not done.

    Uses file locking to prevent concurrent write corruption.
    """
    with _lock_status(suite_dir):
        status = load_status(suite_dir)
        for key in STEP_KEYS:
            status["steps"][key] = {"done": False}
        status["round"] = 0
        status["history"] = []
        _save_status_unlocked(suite_dir, status)
    return status


def get_pending_steps(status: dict[str, Any]) -> list[str]:
    """Return list of step keys that are not yet done."""
    return [key for key in STEP_KEYS if not is_step_done(status, key)]


def init_status(
    suite_dir: str | Path,
    template: str,
    output: str = "",
) -> dict[str, Any]:
    """Initialize a new .workflow_status.json in a directory.

    Args:
        suite_dir: Directory to create the status file in.
        template: Template name (e.g., "checklist").
        output: Output filename (e.g., "checklist.kata.md").

    Returns:
        The created status dict.
    """
    status = _default_status(template=template, output=output)
    Path(suite_dir).mkdir(parents=True, exist_ok=True)
    _save_status(suite_dir, status)
    return status


def status_summary(status: dict[str, Any]) -> str:
    """Return a human-readable summary of workflow status."""
    lines: list[str] = []

    template = status.get("template", "")
    output = status.get("output", "")
    if template:
        lines.append(f"Template: {template}")
    if output:
        lines.append(f"Output:   {output}")

    current_round = status.get("round", 0)
    lines.append(f"Round:    {current_round}")

    done_count = sum(1 for k in STEP_KEYS if is_step_done(status, k))
    lines.append(f"Progress: {done_count}/{len(STEP_KEYS)}")
    lines.append("")

    for key in STEP_KEYS:
        step = status.get("steps", {}).get(key, {})
        mark = "OK" if step.get("done") else "--"
        note = step.get("note", "")
        at = step.get("at", "")
        detail = f" ({at})" if at else ""
        if note:
            detail += f" {note}"
        lines.append(f"  [{mark}] {key}{detail}")

    return "\n".join(lines)


# --- Internal helpers ---


@contextmanager
def _lock_status(suite_dir: str | Path):
    """Acquire an exclusive file lock for .workflow_status.json."""
    lock_path = Path(suite_dir) / (WORKFLOW_FILENAME + LOCK_SUFFIX)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_fd = open(lock_path, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()


def _save_status_unlocked(suite_dir: str | Path, status: dict[str, Any]) -> None:
    """Save workflow status without acquiring a lock (caller must hold lock)."""
    path = Path(suite_dir) / WORKFLOW_FILENAME
    with open(path, "w", encoding="utf-8") as f:
        json.dump(status, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _save_status(suite_dir: str | Path, status: dict[str, Any]) -> None:
    """Save workflow status with file lock."""
    with _lock_status(suite_dir):
        _save_status_unlocked(suite_dir, status)


def _now_iso() -> str:
    """Return current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def _default_status(
    template: str = "",
    output: str = "",
) -> dict[str, Any]:
    """Create a default status with all steps not done."""
    return {
        "template": template,
        "output": output,
        "steps": {key: {"done": False} for key in STEP_KEYS},
        "round": 0,
        "history": [],
        "_generated": {
            "generator": "gospelo_kata",
            "version": "0.2.0",
            "format_version": FORMAT_VERSION,
            "timestamp": _now_iso(),
        },
    }
