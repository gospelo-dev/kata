# KATA Markdown™ — gospelo-kata
# Copyright (c) 2025 gospelo. All rights reserved.
# Licensed under the MIT License. See LICENSE.md for details.

"""Kata document themes."""

from __future__ import annotations

from pathlib import Path

_THEMES_DIR = Path(__file__).parent


def get_theme_css(name: str = "default") -> str:
    """Load a theme CSS file by name.

    Args:
        name: Theme name (without .css extension).

    Returns:
        CSS content string.

    Raises:
        FileNotFoundError: If theme not found.
    """
    css_path = _THEMES_DIR / f"{name}.css"
    if not css_path.exists():
        available = [p.stem for p in _THEMES_DIR.glob("*.css")]
        raise FileNotFoundError(
            f"Theme '{name}' not found. Available: {', '.join(available)}"
        )
    return css_path.read_text(encoding="utf-8")


def wrap_style(css: str) -> str:
    """Wrap CSS content in a <style> tag."""
    return f"<style>\n{css}</style>\n"
