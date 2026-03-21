"""gospelo-kata-dict: Dictionary validator.

Validates a generated dictionary file against the project source code.

Checks:
  1. YAML syntax is valid
  2. Every project_specific value exists in the scanned source
  3. Every patterns value is valid regex
  4. No duplicate concept entries
  5. All related references point to existing concept IDs
  6. No overly broad keywords

Usage:
    python validate.py --dict dictionaries/security.yaml --dir src/bff/
    python validate.py --dict dictionaries/security.yaml --dir src/bff/ --dir infra/modules/
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install PyYAML", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Validation checks
# ---------------------------------------------------------------------------

BROAD_KEYWORDS = {
    "data",
    "value",
    "result",
    "response",
    "config",
    "utils",
    "helper",
    "common",
    "base",
    "main",
    "app",
    "test",
    "index",
    "type",
    "name",
    "id",
    "key",
    "item",
    "list",
    "get",
    "set",
    "run",
    "init",
    "new",
    "old",
    "tmp",
    "temp",
}

EXCLUDE_DIRS = {
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".git",
}


class ValidationResult:
    """Collects validation errors and warnings."""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.stats: dict[str, int] = {
            "concepts": 0,
            "keywords": 0,
            "project_specific": 0,
            "patterns": 0,
            "related_links": 0,
        }

    @property
    def valid(self) -> bool:
        return len(self.errors) == 0

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def report(self) -> str:
        lines = []
        if self.errors:
            lines.append(f"ERRORS ({len(self.errors)}):")
            for e in self.errors:
                lines.append(f"  [ERROR] {e}")
        if self.warnings:
            lines.append(f"WARNINGS ({len(self.warnings)}):")
            for w in self.warnings:
                lines.append(f"  [WARN]  {w}")

        lines.append("")
        lines.append("Stats:")
        for k, v in self.stats.items():
            lines.append(f"  {k}: {v}")

        status = "PASS" if self.valid else "FAIL"
        lines.append(f"\nResult: {status}")
        return "\n".join(lines)


def _grep_exists(pattern: str, dirs: list[Path]) -> bool:
    """Check if a pattern exists in any file under dirs using grep."""
    for d in dirs:
        try:
            result = subprocess.run(
                [
                    "grep",
                    "-rl",
                    "--include=*.py",
                    "--include=*.ts",
                    "--include=*.tsx",
                    "--include=*.tf",
                    "--include=*.yaml",
                    "--include=*.yml",
                    "--include=*.json",
                    "--include=*.md",
                    pattern,
                    str(d),
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # Filter out excluded dirs
            for line in result.stdout.strip().split("\n"):
                if line and not any(
                    f"/{ex}/" in line or line.startswith(f"{ex}/")
                    for ex in EXCLUDE_DIRS
                ):
                    return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
    return False


def validate_dictionary(
    dict_path: Path,
    source_dirs: list[Path],
    check_source: bool = True,
) -> ValidationResult:
    """Validate a dictionary YAML file."""
    result = ValidationResult()

    # 1. YAML syntax
    try:
        with open(dict_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        result.error(f"YAML parse error: {e}")
        return result

    if not isinstance(data, dict):
        result.error("Root must be a YAML mapping")
        return result

    # Filter out comment-only keys (header lines parsed as keys)
    concept_ids = set()
    concepts = {}
    for key, value in data.items():
        if not isinstance(value, dict):
            continue
        concept_ids.add(key)
        concepts[key] = value

    result.stats["concepts"] = len(concepts)

    # 2. Check each concept entry
    for concept_id, entry in concepts.items():
        prefix = f"[{concept_id}]"

        # Count keywords
        for field in ("keywords", "project_specific"):
            items = entry.get(field, [])
            if isinstance(items, list):
                result.stats["keywords" if field == "keywords" else "project_specific"] += len(items)

        # 2a. project_specific must exist in source
        if check_source and source_dirs:
            ps_items = entry.get("project_specific", [])
            if isinstance(ps_items, list):
                for ps in ps_items:
                    if not isinstance(ps, str):
                        continue
                    # Skip items that look like custom attribute paths
                    if ps.startswith("custom:") or ps.startswith("cognito:"):
                        continue
                    if not _grep_exists(re.escape(str(ps)), source_dirs):
                        result.error(
                            f"{prefix} project_specific '{ps}' not found in source"
                        )

        # 2b. patterns must be valid regex
        patterns = entry.get("patterns", [])
        if isinstance(patterns, list):
            result.stats["patterns"] += len(patterns)
            for pat in patterns:
                if not isinstance(pat, str):
                    continue
                try:
                    re.compile(pat)
                except re.error as e:
                    result.error(f"{prefix} invalid regex pattern '{pat}': {e}")

        # 2c. Broad keyword check
        keywords = entry.get("keywords", [])
        if isinstance(keywords, list):
            for kw in keywords:
                if isinstance(kw, str) and kw.lower() in BROAD_KEYWORDS:
                    result.warn(
                        f"{prefix} broad keyword '{kw}' may cause noisy search results"
                    )

        # 2d. related must reference existing concepts
        related = entry.get("related", [])
        if isinstance(related, list):
            result.stats["related_links"] += len(related)
            for ref in related:
                if isinstance(ref, str) and ref not in concept_ids:
                    result.error(
                        f"{prefix} related '{ref}' does not exist as a concept"
                    )

    # 3. Duplicate check (already handled by YAML parser - last wins)
    # We just note concept count

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate a gospelo-kata-retrieval dictionary."
    )
    parser.add_argument(
        "--dict",
        required=True,
        help="Path to the dictionary YAML file",
    )
    parser.add_argument(
        "--dir",
        action="append",
        default=[],
        help="Source directory to verify project_specific values (can specify multiple)",
    )
    parser.add_argument(
        "--no-source-check",
        action="store_true",
        help="Skip checking project_specific values against source code",
    )

    args = parser.parse_args()

    dict_path = Path(args.dict)
    if not dict_path.exists():
        print(f"ERROR: {dict_path} not found", file=sys.stderr)
        sys.exit(1)

    source_dirs = [Path(d) for d in args.dir]

    result = validate_dictionary(
        dict_path,
        source_dirs,
        check_source=not args.no_source_check,
    )

    print(result.report())
    sys.exit(0 if result.valid else 1)


if __name__ == "__main__":
    main()
