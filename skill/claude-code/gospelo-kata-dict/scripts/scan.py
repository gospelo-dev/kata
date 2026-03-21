"""gospelo-kata-dict: Source code scanner for dictionary generation.

Scans a project directory and extracts identifiers (function names, class names,
imports, decorators, constants, etc.) grouped by apparent domain.

Usage:
    python scan.py --dir src/bff/ --output identifiers.yaml
    python scan.py --dir src/bff/ --dir infra/modules/ --lang python,terraform
    python scan.py --dir src/bff/ --top 300
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import TextIO

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

EXCLUDE_DIRS = {
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".git",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    "dist",
    "build",
    ".egg-info",
}

LANG_EXTENSIONS: dict[str, list[str]] = {
    "python": [".py"],
    "typescript": [".ts", ".tsx"],
    "terraform": [".tf"],
    "markdown": [".md"],
    "yaml": [".yaml", ".yml"],
    "json": [".json"],
}

# Domain hint keywords for grouping identifiers
DOMAIN_HINTS: dict[str, list[str]] = {
    "auth": [
        "auth",
        "login",
        "signin",
        "credential",
        "password",
        "cognito",
        "jwt",
        "token",
        "bearer",
        "oauth",
        "saml",
        "mfa",
        "totp",
    ],
    "session": [
        "session",
        "cookie",
        "refresh",
        "expire",
        "ttl",
        "id_token",
        "access_token",
    ],
    "authz": [
        "permission",
        "authorize",
        "role",
        "admin",
        "manager",
        "acl",
        "policy",
        "iam",
        "tenant",
        "group",
    ],
    "injection": [
        "inject",
        "sanitize",
        "escape",
        "parameterize",
        "execute",
        "eval",
        "exec",
        "subprocess",
        "sql",
    ],
    "xss": [
        "xss",
        "innerhtml",
        "dangerously",
        "script",
        "sanitize_html",
        "csp",
    ],
    "encryption": [
        "encrypt",
        "decrypt",
        "kms",
        "hash",
        "secret",
        "key",
        "cipher",
        "aes",
        "hmac",
        "base64",
    ],
    "validation": [
        "validate",
        "validator",
        "schema",
        "field",
        "basemodel",
        "pydantic",
        "regex",
        "pattern",
    ],
    "cors": ["cors", "origin", "cross_origin", "access_control"],
    "network": [
        "vpc",
        "subnet",
        "security_group",
        "nacl",
        "cidr",
        "firewall",
        "endpoint",
    ],
    "storage": ["s3", "bucket", "storage", "upload", "download", "presigned"],
    "email": [
        "ses",
        "email",
        "mail",
        "smtp",
        "bounce",
        "dkim",
        "spf",
        "dmarc",
        "unsubscribe",
    ],
    "logging": [
        "log",
        "audit",
        "monitor",
        "alarm",
        "metric",
        "cloudwatch",
        "trace",
    ],
    "api": [
        "router",
        "endpoint",
        "gateway",
        "route",
        "handler",
        "middleware",
        "request",
        "response",
    ],
    "database": [
        "dynamo",
        "aurora",
        "rds",
        "table",
        "query",
        "scan",
        "index",
        "partition",
    ],
    "container": ["ecr", "docker", "container", "image", "registry", "trivy"],
    "dependency": [
        "requirements",
        "package",
        "pip",
        "npm",
        "pnpm",
        "vulnerability",
        "audit",
    ],
}


# ---------------------------------------------------------------------------
# Identifier types
# ---------------------------------------------------------------------------


class Identifier:
    """A single extracted identifier."""

    __slots__ = ("name", "kind", "file", "line", "lang")

    def __init__(
        self, name: str, kind: str, file: str, line: int, lang: str
    ) -> None:
        self.name = name
        self.kind = kind
        self.file = file
        self.line = line
        self.lang = lang

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "kind": self.kind,
            "file": self.file,
            "line": self.line,
            "lang": self.lang,
        }


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------


def discover_files(
    dirs: list[Path], langs: list[str] | None = None
) -> dict[str, list[Path]]:
    """Find files grouped by language, excluding unwanted directories."""
    exts_to_lang: dict[str, str] = {}
    for lang, exts in LANG_EXTENSIONS.items():
        if langs and lang not in langs:
            continue
        for ext in exts:
            exts_to_lang[ext] = lang

    result: dict[str, list[Path]] = defaultdict(list)

    for base_dir in dirs:
        if not base_dir.is_dir():
            print(f"WARNING: {base_dir} is not a directory, skipping", file=sys.stderr)
            continue
        for path in base_dir.rglob("*"):
            if any(part in EXCLUDE_DIRS for part in path.parts):
                continue
            if path.is_file() and path.suffix in exts_to_lang:
                result[exts_to_lang[path.suffix]].append(path)

    return dict(result)


# ---------------------------------------------------------------------------
# Python extractor (AST-based)
# ---------------------------------------------------------------------------


def extract_python(file_path: Path) -> list[Identifier]:
    """Extract identifiers from a Python file using AST."""
    try:
        source = file_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(file_path))
    except (SyntaxError, UnicodeDecodeError):
        return []

    ids: list[Identifier] = []
    rel = str(file_path)

    for node in ast.walk(tree):
        # Function definitions
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            ids.append(
                Identifier(node.name, "function", rel, node.lineno, "python")
            )
            # Decorators
            for dec in node.decorator_list:
                dec_name = _decorator_name(dec)
                if dec_name:
                    ids.append(
                        Identifier(dec_name, "decorator", rel, dec.lineno, "python")
                    )

        # Class definitions
        elif isinstance(node, ast.ClassDef):
            ids.append(
                Identifier(node.name, "class", rel, node.lineno, "python")
            )
            for dec in node.decorator_list:
                dec_name = _decorator_name(dec)
                if dec_name:
                    ids.append(
                        Identifier(dec_name, "decorator", rel, dec.lineno, "python")
                    )

        # Imports
        elif isinstance(node, ast.Import):
            for alias in node.names:
                ids.append(
                    Identifier(alias.name, "import", rel, node.lineno, "python")
                )

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            ids.append(
                Identifier(module, "import_from", rel, node.lineno, "python")
            )
            for alias in node.names:
                ids.append(
                    Identifier(alias.name, "import_name", rel, node.lineno, "python")
                )

        # Constants (UPPER_CASE assignments)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and re.match(
                    r"^[A-Z][A-Z0-9_]+$", target.id
                ):
                    ids.append(
                        Identifier(
                            target.id, "constant", rel, node.lineno, "python"
                        )
                    )

    # String literal patterns (headers, URLs, ARNs)
    _extract_string_patterns(source, rel, ids)

    return ids


def _decorator_name(node: ast.expr) -> str | None:
    """Extract decorator name as string."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parts = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))
    if isinstance(node, ast.Call):
        return _decorator_name(node.func)
    return None


# ---------------------------------------------------------------------------
# Terraform extractor (regex-based)
# ---------------------------------------------------------------------------

_TF_RESOURCE = re.compile(
    r'^resource\s+"([^"]+)"\s+"([^"]+)"', re.MULTILINE
)
_TF_DATA = re.compile(r'^data\s+"([^"]+)"\s+"([^"]+)"', re.MULTILINE)
_TF_VARIABLE = re.compile(r'^variable\s+"([^"]+)"', re.MULTILINE)
_TF_MODULE = re.compile(r'^module\s+"([^"]+)"', re.MULTILINE)
_TF_OUTPUT = re.compile(r'^output\s+"([^"]+)"', re.MULTILINE)


def extract_terraform(file_path: Path) -> list[Identifier]:
    """Extract identifiers from a Terraform file."""
    try:
        source = file_path.read_text(encoding="utf-8", errors="replace")
    except UnicodeDecodeError:
        return []

    ids: list[Identifier] = []
    rel = str(file_path)

    for m in _TF_RESOURCE.finditer(source):
        line = source[: m.start()].count("\n") + 1
        ids.append(Identifier(m.group(1), "tf_resource_type", rel, line, "terraform"))
        ids.append(Identifier(m.group(2), "tf_resource_name", rel, line, "terraform"))

    for m in _TF_DATA.finditer(source):
        line = source[: m.start()].count("\n") + 1
        ids.append(Identifier(m.group(1), "tf_data_type", rel, line, "terraform"))
        ids.append(Identifier(m.group(2), "tf_data_name", rel, line, "terraform"))

    for m in _TF_VARIABLE.finditer(source):
        line = source[: m.start()].count("\n") + 1
        ids.append(Identifier(m.group(1), "tf_variable", rel, line, "terraform"))

    for m in _TF_MODULE.finditer(source):
        line = source[: m.start()].count("\n") + 1
        ids.append(Identifier(m.group(1), "tf_module", rel, line, "terraform"))

    for m in _TF_OUTPUT.finditer(source):
        line = source[: m.start()].count("\n") + 1
        ids.append(Identifier(m.group(1), "tf_output", rel, line, "terraform"))

    return ids


# ---------------------------------------------------------------------------
# TypeScript extractor (regex-based)
# ---------------------------------------------------------------------------

_TS_EXPORT_FUNC = re.compile(
    r"export\s+(?:async\s+)?function\s+(\w+)", re.MULTILINE
)
_TS_EXPORT_CLASS = re.compile(r"export\s+class\s+(\w+)", re.MULTILINE)
_TS_EXPORT_INTERFACE = re.compile(r"export\s+interface\s+(\w+)", re.MULTILINE)
_TS_EXPORT_TYPE = re.compile(r"export\s+type\s+(\w+)", re.MULTILINE)
_TS_IMPORT = re.compile(
    r"import\s+.*?\s+from\s+['\"]([^'\"]+)['\"]", re.MULTILINE
)
_TS_COMPONENT = re.compile(
    r"(?:export\s+)?(?:default\s+)?function\s+([A-Z]\w+)\s*\(", re.MULTILINE
)


def extract_typescript(file_path: Path) -> list[Identifier]:
    """Extract identifiers from a TypeScript/TSX file."""
    try:
        source = file_path.read_text(encoding="utf-8", errors="replace")
    except UnicodeDecodeError:
        return []

    ids: list[Identifier] = []
    rel = str(file_path)

    for pat, kind in [
        (_TS_EXPORT_FUNC, "function"),
        (_TS_EXPORT_CLASS, "class"),
        (_TS_EXPORT_INTERFACE, "interface"),
        (_TS_EXPORT_TYPE, "type"),
        (_TS_IMPORT, "import"),
        (_TS_COMPONENT, "component"),
    ]:
        for m in pat.finditer(source):
            line = source[: m.start()].count("\n") + 1
            ids.append(Identifier(m.group(1), kind, rel, line, "typescript"))

    return ids


# ---------------------------------------------------------------------------
# Markdown extractor
# ---------------------------------------------------------------------------

_MD_HEADING = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)


def extract_markdown(file_path: Path) -> list[Identifier]:
    """Extract headings from a Markdown file."""
    try:
        source = file_path.read_text(encoding="utf-8", errors="replace")
    except UnicodeDecodeError:
        return []

    ids: list[Identifier] = []
    rel = str(file_path)

    for m in _MD_HEADING.finditer(source):
        line = source[: m.start()].count("\n") + 1
        level = len(m.group(1))
        ids.append(Identifier(m.group(2).strip(), f"h{level}", rel, line, "markdown"))

    return ids


# ---------------------------------------------------------------------------
# String pattern extractor (cross-language)
# ---------------------------------------------------------------------------

_HEADER_PATTERN = re.compile(
    r"""['"](X-[\w-]+|Authorization|Content-Security-Policy|"""
    r"""Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options)['"]""",
    re.IGNORECASE,
)
_ARN_PATTERN = re.compile(r"arn:aws:[\w:*/-]+")
_AWS_SERVICE_PATTERN = re.compile(
    r"""['"](cognito-idp|dynamodb|s3|ses|sesv2|kms|"""
    r"""secretsmanager|lambda|apigateway|cloudfront|sqs|sns|"""
    r"""sts|iam|ecr|bedrock|bedrock-runtime|rds-data)['"]"""
)


def _extract_string_patterns(
    source: str, file_path: str, ids: list[Identifier]
) -> None:
    """Extract security-relevant string patterns from source."""
    for pat, kind in [
        (_HEADER_PATTERN, "header"),
        (_ARN_PATTERN, "arn"),
        (_AWS_SERVICE_PATTERN, "aws_service"),
    ]:
        seen = set()
        for m in pat.finditer(source):
            val = m.group(1) if m.lastindex else m.group(0)
            if val not in seen:
                seen.add(val)
                line = source[: m.start()].count("\n") + 1
                ids.append(Identifier(val, kind, file_path, line, "pattern"))


# ---------------------------------------------------------------------------
# Domain grouping
# ---------------------------------------------------------------------------


def guess_domain(name: str) -> str:
    """Guess which domain an identifier belongs to."""
    name_lower = name.lower().replace("-", "_")
    scores: dict[str, int] = defaultdict(int)

    for domain, hints in DOMAIN_HINTS.items():
        for hint in hints:
            if hint in name_lower:
                scores[domain] += 1

    if not scores:
        return "other"
    return max(scores, key=lambda d: scores[d])


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

EXTRACTORS = {
    "python": extract_python,
    "typescript": extract_typescript,
    "terraform": extract_terraform,
    "markdown": extract_markdown,
}


def _log(msg: str) -> None:
    """Print progress message to stderr with timestamp."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", file=sys.stderr, flush=True)


def scan(
    dirs: list[Path],
    langs: list[str] | None = None,
    top_n: int = 200,
) -> dict:
    """Run the full scan pipeline and return structured results."""

    # Phase 1: File discovery
    _log("Phase 1/5: Discovering files...")
    files_by_lang = discover_files(dirs, langs)

    file_stats: dict[str, int] = {}
    total_files = 0
    for lang, files in files_by_lang.items():
        file_stats[lang] = len(files)
        total_files += len(files)
    _log(f"  Found {total_files} files: {file_stats}")

    # Phase 2: Identifier extraction
    _log("Phase 2/5: Extracting identifiers...")
    all_ids: list[Identifier] = []
    for lang, files in files_by_lang.items():
        extractor = EXTRACTORS.get(lang)
        if not extractor:
            _log(f"  [{lang}] No extractor available, skipping {len(files)} files")
            continue
        count_before = len(all_ids)
        for i, f in enumerate(files):
            all_ids.extend(extractor(f))
            # Progress every 50 files or at the end
            if (i + 1) % 50 == 0 or i + 1 == len(files):
                _log(
                    f"  [{lang}] {i + 1}/{len(files)} files processed "
                    f"({len(all_ids) - count_before} identifiers)"
                )
    _log(f"  Total: {len(all_ids)} identifiers extracted")

    # Phase 3: Frequency analysis
    _log("Phase 3/5: Counting frequencies...")
    name_counter: Counter = Counter()
    for ident in all_ids:
        name_counter[ident.name] += 1
    _log(f"  {len(name_counter)} unique identifiers, top-{top_n} selected")

    top_identifiers = name_counter.most_common(top_n)

    # Phase 4: Domain grouping
    _log("Phase 4/5: Grouping by domain...")
    domain_groups: dict[str, list[dict]] = defaultdict(list)
    seen_in_domain: dict[str, set[str]] = defaultdict(set)

    for ident in all_ids:
        domain = guess_domain(ident.name)
        if ident.name not in seen_in_domain[domain]:
            seen_in_domain[domain].add(ident.name)
            domain_groups[domain].append(
                {
                    "name": ident.name,
                    "kind": ident.kind,
                    "file": ident.file,
                    "count": name_counter[ident.name],
                }
            )

    for domain in domain_groups:
        domain_groups[domain].sort(key=lambda x: x["count"], reverse=True)

    domain_summary = {d: len(ids) for d, ids in domain_groups.items()}
    _log(f"  {len(domain_groups)} domains: {domain_summary}")

    # Phase 5: Building result
    _log("Phase 5/5: Building output...")
    kind_counter: Counter = Counter()
    for ident in all_ids:
        kind_counter[ident.kind] += 1

    result = {
        "scan_metadata": {
            "scanned_dirs": [str(d) for d in dirs],
            "languages": langs or list(files_by_lang.keys()),
            "scanned_at": datetime.now(timezone.utc).isoformat(),
            "file_counts": file_stats,
            "total_identifiers": len(all_ids),
            "unique_identifiers": len(name_counter),
            "kind_counts": dict(kind_counter.most_common()),
        },
        "top_identifiers": [
            {"name": name, "count": count} for name, count in top_identifiers
        ],
        "domain_groups": dict(domain_groups),
    }
    _log("Done.")
    return result


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def write_output(data: dict, output: TextIO) -> None:
    """Write scan results as YAML (preferred) or JSON."""
    if HAS_YAML:
        yaml.dump(
            data,
            output,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=120,
        )
    else:
        json.dump(data, output, ensure_ascii=False, indent=2)
        output.write("\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan source code and extract identifiers for dictionary generation."
    )
    parser.add_argument(
        "--dir",
        action="append",
        required=True,
        help="Target directory to scan (can specify multiple)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output file path (default: stdout)",
    )
    parser.add_argument(
        "--lang",
        default=None,
        help="Comma-separated language filter (python,typescript,terraform,markdown)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=200,
        help="Number of top identifiers to include (default: 200)",
    )

    args = parser.parse_args()

    dirs = [Path(d) for d in args.dir]
    langs = args.lang.split(",") if args.lang else None

    result = scan(dirs, langs=langs, top_n=args.top)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            write_output(result, f)
        _log(f"Written to: {out_path}")
    else:
        write_output(result, sys.stdout)

    # Final summary
    meta = result["scan_metadata"]
    _log(
        f"Summary: {meta['file_counts']} -> "
        f"{meta['total_identifiers']} identifiers "
        f"({meta['unique_identifiers']} unique) "
        f"in {len(result['domain_groups'])} domains"
    )


if __name__ == "__main__":
    main()
