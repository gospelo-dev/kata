# KATA Markdown™ — gospelo-kata
# Copyright (c) 2025 gospelo. All rights reserved.
# Licensed under the MIT License. See LICENSE.md for details.

"""CLI entry point for gospelo-kata."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


KATATPL_EXT = ".katatpl"


MANIFEST_FILE = "manifest.json"

TRUST_FILE = ".template_trust.json"

# Allowed file extensions in .katatpl (besides manifest.json and _tpl.kata.md)
KATATPL_ALLOWED_EXTENSIONS = frozenset({
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico", ".bmp",
})

# Maximum limits for .katatpl packages
KATATPL_MAX_TOTAL_SIZE = 50 * 1024 * 1024  # 50 MB
KATATPL_MAX_FILE_COUNT = 100
KATATPL_MAX_SINGLE_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _is_allowed_katatpl_file(filename: str) -> bool:
    """Check if a file is allowed in a .katatpl package.

    Allowed: manifest.json, *_tpl.kata.md, and image files.
    """
    basename = filename.rsplit("/", 1)[-1] if "/" in filename else filename
    if basename == MANIFEST_FILE:
        return True
    if basename.endswith("_tpl.kata.md"):
        return True
    ext = "." + basename.rsplit(".", 1)[-1].lower() if "." in basename else ""
    return ext in KATATPL_ALLOWED_EXTENSIONS


def _validate_katatpl_safety(zip_path: Path) -> None:
    """Validate a .katatpl file against size limits and integrity hash."""
    import hashlib
    import zipfile
    with zipfile.ZipFile(zip_path, "r") as zf:
        infos = zf.infolist()
        if len(infos) > KATATPL_MAX_FILE_COUNT:
            raise ValueError(
                f"Too many files in {zip_path.name}: {len(infos)} "
                f"(max {KATATPL_MAX_FILE_COUNT})"
            )
        total_size = 0
        for info in infos:
            if info.file_size > KATATPL_MAX_SINGLE_FILE_SIZE:
                raise ValueError(
                    f"File too large in {zip_path.name}: {info.filename} "
                    f"({info.file_size:,} bytes, max {KATATPL_MAX_SINGLE_FILE_SIZE:,})"
                )
            total_size += info.file_size
        if total_size > KATATPL_MAX_TOTAL_SIZE:
            raise ValueError(
                f"Total uncompressed size too large in {zip_path.name}: "
                f"{total_size:,} bytes (max {KATATPL_MAX_TOTAL_SIZE:,})"
            )

        # Integrity check
        manifest_name = None
        for n in zf.namelist():
            if n.endswith(f"/{MANIFEST_FILE}") or n == MANIFEST_FILE:
                manifest_name = n
                break
        if manifest_name is None:
            raise ValueError(f"No {MANIFEST_FILE} found in {zip_path.name}")

        manifest = json.loads(zf.read(manifest_name).decode("utf-8"))
        expected_hash = manifest.get("_integrity")
        if not expected_hash:
            raise ValueError(
                f"Package {zip_path.name} has no integrity hash. "
                f"Repack with: gospelo-kata pack"
            )

        # Recompute hash over non-manifest files
        prefix = manifest_name.rsplit("/", 1)[0] + "/" if "/" in manifest_name else ""
        h = hashlib.sha256()
        for n in sorted(zf.namelist()):
            if n.endswith("/") or n == manifest_name:
                continue
            rel = n[len(prefix):] if prefix and n.startswith(prefix) else n
            h.update(rel.encode("utf-8"))
            h.update(zf.read(n))

        if h.hexdigest() != expected_hash:
            raise ValueError(
                f"Integrity check failed for {zip_path.name}: "
                f"package contents have been tampered with"
            )


def _prompt_hash(prompt_text: str) -> str:
    """Generate a SHA-256 hash of the prompt text."""
    import hashlib
    return hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()


def _load_trust_store() -> dict:
    """Load the trust store from .template_trust.json."""
    trust_path = Path(TRUST_FILE)
    if trust_path.exists():
        return json.loads(trust_path.read_text(encoding="utf-8"))
    return {}


def _save_trust_store(store: dict) -> None:
    """Save the trust store to .template_trust.json."""
    Path(TRUST_FILE).write_text(
        json.dumps(store, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _check_template_trust(template_name: str, prompt_text: str, *, interactive: bool = True) -> bool:
    """Check if a template's prompt is trusted.

    Returns True if trusted. If interactive and untrusted, shows the prompt
    and asks the user for approval.
    """
    h = _prompt_hash(prompt_text)
    store = _load_trust_store()

    if store.get(template_name) == h:
        return True

    if not interactive:
        return False

    # Show prompt for review
    print("=" * 60, file=sys.stderr)
    print(f"Template '{template_name}' — prompt review required", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(file=sys.stderr)
    print(prompt_text, file=sys.stderr)
    print(file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    if store.get(template_name):
        print("WARNING: prompt content has changed since last approval.", file=sys.stderr)

    try:
        answer = input("Trust this template prompt? [y/N]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print(file=sys.stderr)
        return False

    if answer in ("y", "yes"):
        store[template_name] = h
        _save_trust_store(store)
        print(f"Trusted: {template_name} (hash: {h[:12]}...)", file=sys.stderr)
        return True

    print("Denied. Template will not be used.", file=sys.stderr)
    return False


class TemplateSource:
    """Abstraction over a template stored as a directory or a .katatpl file."""

    def __init__(self, name: str, path: Path, is_zip: bool = False):
        self.name = name
        self.path = path
        self.is_zip = is_zip
        self._manifest: dict | None = None
        self._validated = False

    def read_file(self, filename: str) -> str:
        """Read a text file from the template source."""
        return self.read_bytes(filename).decode("utf-8")

    def _ensure_validated(self) -> None:
        """Run safety validation once on first access."""
        if self.is_zip and not self._validated:
            _validate_katatpl_safety(self.path)
            self._validated = True

    def read_bytes(self, filename: str) -> bytes:
        """Read a file as bytes from the template source."""
        if self.is_zip and not _is_allowed_katatpl_file(filename):
            raise PermissionError(f"disallowed file type in katatpl: {filename}")
        if self.is_zip:
            self._ensure_validated()
            import zipfile
            with zipfile.ZipFile(self.path, "r") as zf:
                for candidate in [f"{self.name}/{filename}", filename]:
                    if candidate in zf.namelist():
                        return zf.read(candidate)
            raise FileNotFoundError(f"{filename} not found in {self.path}")
        return (self.path / filename).read_bytes()

    def file_exists(self, filename: str) -> bool:
        """Check if a file exists in the template source."""
        if self.is_zip:
            import zipfile
            with zipfile.ZipFile(self.path, "r") as zf:
                return any(
                    n in zf.namelist()
                    for n in [f"{self.name}/{filename}", filename]
                )
        return (self.path / filename).exists()

    def list_files(self) -> list[str]:
        """List filenames in the template source."""
        if self.is_zip:
            import zipfile
            with zipfile.ZipFile(self.path, "r") as zf:
                prefix = f"{self.name}/"
                files = []
                for n in zf.namelist():
                    if n.endswith("/"):
                        continue
                    rel = n[len(prefix):] if n.startswith(prefix) else n
                    if _is_allowed_katatpl_file(rel):
                        files.append(rel)
                return files
        return [
            str(f.relative_to(self.path))
            for f in self.path.rglob("*")
            if f.is_file()
        ]

    def extract_to(self, dest_dir: Path, exclude: list[str] | None = None) -> list[str]:
        """Extract all files to a destination directory. Returns list of extracted paths."""
        exclude = exclude or []
        extracted = []
        for filename in self.list_files():
            if filename in exclude:
                continue
            data = self.read_bytes(filename)
            out_path = dest_dir / filename
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(data)
            extracted.append(filename)
        return extracted

    def manifest(self) -> dict:
        """Load and cache manifest.json."""
        if self._manifest is not None:
            return self._manifest
        try:
            self._manifest = json.loads(self.read_file(MANIFEST_FILE))
        except (FileNotFoundError, KeyError):
            self._manifest = {}
        return self._manifest

    def find_tpl_kata_md(self) -> str:
        """Find and return the content of the main _tpl.kata.md file."""
        # Check manifest first
        m = self.manifest()
        if "template" in m:
            try:
                return self.read_file(m["template"])
            except FileNotFoundError:
                print(f"Error: template file '{m['template']}' specified in manifest.json not found in {self.path}", file=sys.stderr)
                sys.exit(1)
        # Fallback: search for *_tpl.kata.md
        for name in self.list_files():
            if name.endswith("_tpl.kata.md"):
                return self.read_file(name)
        print(f"Error: no _tpl.kata.md file found in {self.path}", file=sys.stderr)
        sys.exit(1)

    def description(self) -> str:
        """Return the template description."""
        # Check manifest first
        m = self.manifest()
        if "description" in m:
            return m["description"]
        # Fallback: description.txt
        try:
            return self.read_file("description.txt").strip()
        except (FileNotFoundError, KeyError):
            return ""

    def version(self) -> str:
        """Return the template version from manifest."""
        return self.manifest().get("version", "")

    def author(self) -> str:
        """Return the template author from manifest."""
        return self.manifest().get("author", "")

    def url(self) -> str:
        """Return the template URL from manifest."""
        return self.manifest().get("url", "")

    def license(self) -> str:
        """Return the template license from manifest."""
        return self.manifest().get("license", "")

    def requires(self) -> list[str]:
        """Return the list of required template names from manifest."""
        return self.manifest().get("requires", [])


def _builtin_templates_dir() -> Path:
    """Return the path to the package's built-in templates directory."""
    return Path(__file__).parent / "templates"


def _local_templates_dir() -> Path:
    """Return the path to the local project's templates directory."""
    return Path("./templates")


def _list_template_sources(base_dir: Path) -> list[TemplateSource]:
    """List all template sources (directories and .katatpl files) in a base directory."""
    sources: list[TemplateSource] = []
    if not base_dir.exists():
        return sources
    for entry in sorted(base_dir.iterdir()):
        if entry.is_dir():
            sources.append(TemplateSource(entry.name, entry, is_zip=False))
        elif entry.name.endswith(KATATPL_EXT):
            name = entry.name[: -len(KATATPL_EXT)]
            sources.append(TemplateSource(name, entry, is_zip=True))
    return sources


def _resolve_template(type_name: str) -> TemplateSource:
    """Resolve a template type name to a TemplateSource.

    Search order: local ./templates/{type} or {type}.katatpl -> built-in package templates.
    """
    for base in (_local_templates_dir(), _builtin_templates_dir()):
        if not base.exists():
            continue
        # Check directory
        d = base / type_name
        if d.is_dir():
            return TemplateSource(type_name, d, is_zip=False)
        # Check .katatpl
        z = base / f"{type_name}{KATATPL_EXT}"
        if z.is_file():
            return TemplateSource(type_name, z, is_zip=True)

    available: list[str] = []
    for base in (_local_templates_dir(), _builtin_templates_dir()):
        available.extend(s.name for s in _list_template_sources(base))
    available = sorted(set(available))
    print(f"Error: template '{type_name}' not found. Available: {available}", file=sys.stderr)
    sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gospelo-kata",
        description="JSON-driven document generation toolkit",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- validate ---
    val_parser = subparsers.add_parser(
        "validate", help="Validate JSON documents against schemas",
    )
    val_parser.add_argument(
        "file", help="JSON file to validate",
    )
    val_parser.add_argument(
        "--schema", help="Schema name or path (auto-detected if omitted)",
    )

    # --- generate ---
    gen_parser = subparsers.add_parser(
        "generate", help="Generate documents from JSON data",
    )
    gen_parser.add_argument(
        "file", help="Input JSON file",
    )
    gen_parser.add_argument(
        "--format", "-f", choices=["markdown", "excel", "html"],
        default="markdown", help="Output format (default: markdown)",
    )
    gen_parser.add_argument(
        "--output", "-o", help="Output file path (default: stdout for markdown)",
    )
    gen_parser.add_argument(
        "--type", help="Document type (auto-detected if omitted)",
    )
    gen_parser.add_argument(
        "--prereq", help="Prerequisites JSON file (for test_spec Excel)",
    )

    # --- edit ---
    edit_parser = subparsers.add_parser(
        "edit", help="Open JSON file in browser-based editor",
    )
    edit_parser.add_argument(
        "file", help="JSON file to edit",
    )
    edit_parser.add_argument(
        "--port", type=int, default=0, help="Port number (default: auto)",
    )
    edit_parser.add_argument(
        "--no-browser", action="store_true", help="Don't open browser automatically",
    )

    # --- templates ---
    tpl_parser = subparsers.add_parser(
        "templates", help="List available document templates",
    )
    tpl_parser.add_argument(
        "--open", action="store_true",
        help="Open the templates directory in the file manager",
    )

    # --- init ---
    init_parser = subparsers.add_parser(
        "init", help="Initialize a document from a template",
    )
    init_parser.add_argument(
        "--type", help="Document type (e.g., checklist, test_spec) or path to .katatpl",
    )
    init_parser.add_argument(
        "--from-package", help="Path to .katatpl package file to install",
    )
    init_parser.add_argument(
        "--output", "-o", help="Output directory or file path",
    )

    # --- render ---
    render_parser = subparsers.add_parser(
        "render", help="Render a self-contained .kata.md file using its {#data} block",
    )
    render_parser.add_argument(
        "file", help=".kata.md file containing {#schema}, {#data}, and template",
    )
    render_parser.add_argument(
        "--output", "-o", help="Output file path (default: stdout)",
    )
    render_parser.add_argument(
        "--no-annotate", action="store_true",
        help="Disable data-kata annotations in output",
    )
    render_parser.add_argument(
        "--no-validate", action="store_true",
        help="Skip schema validation",
    )

    # --- schemas ---
    sch_parser = subparsers.add_parser(
        "schemas", help="List available validation schemas",
    )

    # --- lint ---
    lint_parser = subparsers.add_parser(
        "lint", help="Lint template (.kata.md) or rendered document (.md) files",
    )
    lint_parser.add_argument(
        "files", nargs="+", help="Template or document file(s) to lint",
    )
    lint_parser.add_argument(
        "--format", choices=["human", "vscode"], default="human",
        help="Output format (default: human)",
    )
    lint_parser.add_argument(
        "--schema", help="Schema name for document mode (e.g., agenda, checklist)",
    )

    # --- gen-schema-section ---
    gss_parser = subparsers.add_parser(
        "gen-schema-section",
        help="Generate Schema section (bidirectional links) from a schema file",
    )
    gss_parser.add_argument(
        "schema", help="Schema name (e.g., agenda) or path to schema JSON file",
    )
    gss_parser.add_argument(
        "--section-map", help="JSON mapping of property to u- anchor (e.g., '{\"date\": \"u-meeting-info\"}')",
    )

    # --- infer-schema ---
    infer_parser = subparsers.add_parser(
        "infer-schema",
        help="Infer a YAML schema scaffold from template variables",
    )
    infer_parser.add_argument(
        "file", help="Template file (.kata.md) to analyze",
    )
    infer_parser.add_argument(
        "--format", "-f", choices=["yaml", "json"], default="yaml",
        help="Output format (default: yaml)",
    )

    # --- show-prompt ---
    sp_parser = subparsers.add_parser(
        "show-prompt",
        help="Show the embedded {#prompt} block from a template",
    )
    sp_parser.add_argument(
        "template", help="Template name (e.g., checklist) or path to .kata.md",
    )

    # --- show-schema ---
    ss_parser = subparsers.add_parser(
        "show-schema",
        help="Show the embedded schema from a template as JSON Schema",
    )
    ss_parser.add_argument(
        "template", help="Template name (e.g., checklist) or path to .kata.md",
    )
    ss_parser.add_argument(
        "--format", "-f", choices=["json", "yaml"], default="json",
        help="Output format (default: json)",
    )

    # --- init-vscode ---
    vscode_parser = subparsers.add_parser(
        "init-vscode", help="Generate .vscode/tasks.json for lint-on-save",
    )
    vscode_parser.add_argument(
        "--output", "-o", default=".vscode",
        help="Output directory (default: .vscode)",
    )

    # --- extract ---
    ext_parser = subparsers.add_parser(
        "extract", help="Extract JSON data from a rendered .kata.md document",
    )
    ext_parser.add_argument(
        "file", help="Rendered .kata.md file to extract data from",
    )
    ext_parser.add_argument(
        "--output", "-o", help="Output JSON file (default: stdout)",
    )
    ext_parser.add_argument(
        "--schema", help="Schema name or path for type hints (optional)",
    )

    # --- coverage ---
    cov_parser = subparsers.add_parser(
        "coverage", help="Analyze checklist coverage against document directories",
    )
    cov_parser.add_argument(
        "--checklist", required=True, help="Path to checklist JSON file",
    )
    cov_parser.add_argument(
        "--dir", required=True, help="Parent directory containing subdirectories",
    )
    cov_parser.add_argument(
        "--format", "-f", choices=["human", "markdown", "json"],
        default="human", help="Output format (default: human)",
    )

    # --- workflow-status ---
    wf_parser = subparsers.add_parser(
        "workflow-status", help="Show or update document generation workflow status",
    )
    wf_parser.add_argument(
        "--suite-dir", required=True, help="Directory containing .workflow_status.json",
    )
    wf_parser.add_argument(
        "--mark-done", metavar="STEP",
        help="Mark a step as done (init, validate, generate, lint, review)",
    )
    wf_parser.add_argument(
        "--note", default="", help="Note to attach when marking a step done",
    )
    wf_parser.add_argument(
        "--retry", action="store_true",
        help="Reset validate/generate/lint for retry loop",
    )
    wf_parser.add_argument(
        "--retry-reason", default="", help="Reason for retry (used with --retry)",
    )
    wf_parser.add_argument(
        "--init", nargs=2, metavar=("TEMPLATE", "OUTPUT"),
        help="Initialize workflow status (e.g., --init checklist checklist.kata.md)",
    )
    wf_parser.add_argument(
        "--reset", action="store_true", help="Reset all steps to not done",
    )

    # --- assemble ---
    asm_parser = subparsers.add_parser(
        "assemble",
        help="Assemble a _tpl.kata.md from a built-in template and a data YAML/JSON file",
    )
    asm_parser.add_argument(
        "--type", required=True,
        help="Template type (e.g., checklist, test_spec, agenda)",
    )
    asm_parser.add_argument(
        "--data", required=True,
        help="Data file (YAML or JSON) to embed as {#data} block",
    )
    asm_parser.add_argument(
        "--output", "-o",
        help="Output _tpl.kata.md file path (default: stdout)",
    )

    # --- pack ---
    pack_parser = subparsers.add_parser(
        "pack",
        help="Pack a template directory into a .katatpl package",
    )
    pack_parser.add_argument(
        "template_dir", help="Template directory to pack (e.g., ./templates/checklist)",
    )
    pack_parser.add_argument(
        "--output", "-o",
        help="Output .katatpl file path (default: {name}.katatpl)",
    )

    # --- pack-init ---
    packinit_parser = subparsers.add_parser(
        "pack-init",
        help="Generate a manifest.json scaffold for a template directory",
    )
    packinit_parser.add_argument(
        "template_dir", help="Template directory (e.g., ./my_template)",
    )

    # --- fmt (format) ---
    fmt_parser = subparsers.add_parser(
        "fmt", help="Auto-format rendered .kata.md files (sanitize HTML in data-kata spans)",
    )
    fmt_parser.add_argument(
        "files", nargs="+", help="Rendered .kata.md files to format",
    )
    fmt_parser.add_argument(
        "--check", action="store_true",
        help="Check only — exit 1 if changes needed, do not modify files",
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        _cmd_validate(args)
    elif args.command == "generate":
        _cmd_generate(args)
    elif args.command == "edit":
        _cmd_edit(args)
    elif args.command == "templates":
        _cmd_templates(args)
    elif args.command == "render":
        _cmd_render(args)
    elif args.command == "init":
        _cmd_init(args)
    elif args.command == "schemas":
        _cmd_schemas(args)
    elif args.command == "lint":
        _cmd_lint(args)
    elif args.command == "gen-schema-section":
        _cmd_gen_schema_section(args)
    elif args.command == "infer-schema":
        _cmd_infer_schema(args)
    elif args.command == "show-prompt":
        _cmd_show_prompt(args)
    elif args.command == "show-schema":
        _cmd_show_schema(args)
    elif args.command == "init-vscode":
        _cmd_init_vscode(args)
    elif args.command == "extract":
        _cmd_extract(args)
    elif args.command == "coverage":
        _cmd_coverage(args)
    elif args.command == "workflow-status":
        _cmd_workflow_status(args)
    elif args.command == "assemble":
        _cmd_assemble(args)
    elif args.command == "pack":
        _cmd_pack(args)
    elif args.command == "pack-init":
        _cmd_pack_init(args)
    elif args.command == "fmt":
        _cmd_fmt(args)
    else:
        parser.print_help()
        sys.exit(1)


def _cmd_validate(args: argparse.Namespace) -> None:
    from .validator import validate_file, get_builtin_schema, load_schema, detect_schema

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(file_path.read_text(encoding="utf-8"))

    if args.schema:
        schema_path = Path(args.schema)
        if schema_path.exists():
            schema = load_schema(schema_path)
            schema_name = schema_path.stem
        else:
            schema = get_builtin_schema(args.schema)
            schema_name = args.schema
    else:
        schema_name = detect_schema(data)
        if schema_name is None:
            print(f"Error: cannot auto-detect schema for {file_path}. Use --schema.", file=sys.stderr)
            sys.exit(1)
        schema = get_builtin_schema(schema_name)

    result = validate_file(file_path, schema, schema_name)
    print(result.summary())
    if not result.valid:
        sys.exit(1)


def _cmd_generate(args: argparse.Namespace) -> None:
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(file_path.read_text(encoding="utf-8"))

    if args.format == "markdown":
        from .generator.markdown import generate
        md = generate(data, doc_type=args.type)
        if args.output:
            Path(args.output).write_text(md, encoding="utf-8")
            print(f"Generated: {args.output}")
        else:
            print(md)

    elif args.format == "excel":
        from .generator.excel import generate
        output = args.output or file_path.with_suffix(".xlsx")
        kwargs = {}
        if args.prereq:
            prereq_path = Path(args.prereq)
            if prereq_path.exists():
                kwargs["prereq_data"] = json.loads(prereq_path.read_text(encoding="utf-8"))
        result_path = generate(data, output, doc_type=args.type, **kwargs)
        print(f"Generated: {result_path}")

    elif args.format == "html":
        from .generator.markdown import generate as gen_md
        md = gen_md(data, doc_type=args.type)
        html = _markdown_to_html(md, file_path.stem)
        output = args.output or str(file_path.with_suffix(".html"))
        Path(output).write_text(html, encoding="utf-8")
        print(f"Generated: {output}")


def _markdown_to_html(md: str, title: str) -> str:
    """Simple Markdown to HTML conversion (basic subset)."""
    import re

    lines = md.split("\n")
    html_lines: list[str] = []
    in_table = False

    for line in lines:
        if line.startswith("# "):
            html_lines.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("### "):
            html_lines.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if all(c.replace("-", "").replace(":", "") == "" for c in cells):
                continue  # separator row
            if not in_table:
                html_lines.append("<table><thead><tr>")
                for c in cells:
                    html_lines.append(f"<th>{c}</th>")
                html_lines.append("</tr></thead><tbody>")
                in_table = True
            else:
                html_lines.append("<tr>")
                for c in cells:
                    html_lines.append(f"<td>{c}</td>")
                html_lines.append("</tr>")
        else:
            if in_table:
                html_lines.append("</tbody></table>")
                in_table = False
            if line.startswith("- "):
                content = line[2:]
                content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", content)
                html_lines.append(f"<li>{content}</li>")
            elif line.strip() == "":
                html_lines.append("")
            else:
                html_lines.append(f"<p>{line}</p>")

    if in_table:
        html_lines.append("</tbody></table>")

    body = "\n".join(html_lines)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
body {{ font-family: -apple-system, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; line-height: 1.6; }}
table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background: #f5f5f5; }}
li {{ margin: 4px 0; }}
</style>
</head>
<body>
{body}
</body>
</html>"""


def _cmd_render(args: argparse.Namespace) -> None:
    from .template import render_kata

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    try:
        result = render_kata(
            str(file_path),
            validate=not args.no_validate,
            annotate=not args.no_annotate,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"Rendered: {args.output}")
    else:
        print(result)


def _cmd_edit(args: argparse.Namespace) -> None:
    from .generator.html_editor import serve_editor
    serve_editor(
        args.file,
        port=args.port,
        open_browser=not args.no_browser,
    )


def _cmd_templates(args: argparse.Namespace) -> None:
    from .template import _PROMPT_PATTERN, _SCHEMA_INLINE_PATTERN

    if args.open:
        import platform
        import subprocess

        # Prefer local, fall back to built-in
        target = _local_templates_dir() if _local_templates_dir().exists() else _builtin_templates_dir()
        system = platform.system()
        if system == "Darwin":
            subprocess.run(["open", str(target)])
        elif system == "Windows":
            subprocess.run(["explorer", str(target)])
        else:
            subprocess.run(["xdg-open", str(target)])
        print(f"Opened: {target}")
        return

    def _print_source(src: TemplateSource, label: str) -> None:
        desc = src.description()
        flags = []
        try:
            tpl_content = src.find_tpl_kata_md()
            if _SCHEMA_INLINE_PATTERN.search(tpl_content):
                flags.append("schema")
            if _PROMPT_PATTERN.search(tpl_content):
                flags.append("prompt")
        except SystemExit:
            pass  # no _tpl.kata.md — still list it
        ver = src.version()
        ver_str = f" v{ver}" if ver else ""
        pkg = " (.katatpl)" if src.is_zip else ""
        reqs = src.requires()
        req_str = f" requires: {', '.join(reqs)}" if reqs else ""
        tag = f" [{', '.join(flags)}]" if flags else ""
        print(f"  {src.name:20s} {desc}{ver_str}{tag}  ({label}{pkg}){req_str}")

    print("Available templates:")
    print()
    local_sources = _list_template_sources(_local_templates_dir())
    local_names = set()
    for s in local_sources:
        _print_source(s, "local")
        local_names.add(s.name)

    for s in _list_template_sources(_builtin_templates_dir()):
        if s.name not in local_names:
            _print_source(s, "built-in")

    if not local_sources and not _builtin_templates_dir().exists():
        print("No templates available.")


def _cmd_init(args: argparse.Namespace) -> None:
    import shutil

    output_dir = Path(args.output) if args.output else Path(".")

    if args.from_package:
        # Install .katatpl to local templates directory (no extraction)
        pkg_path = Path(args.from_package)
        if not pkg_path.exists():
            print(f"Error: package not found: {pkg_path}", file=sys.stderr)
            sys.exit(1)
        if not pkg_path.name.endswith(KATATPL_EXT):
            print(f"Error: expected {KATATPL_EXT} file, got: {pkg_path.name}", file=sys.stderr)
            sys.exit(1)

        tpl_dest = output_dir / "templates"
        tpl_dest.mkdir(parents=True, exist_ok=True)
        dst = tpl_dest / pkg_path.name
        if dst.exists():
            print(f"  skip (exists): {dst}")
            return
        shutil.copy2(pkg_path, dst)
        tpl_name = pkg_path.name[: -len(KATATPL_EXT)]
        print(f"  created: {dst}")
        print(f"  Installed template '{tpl_name}' from {pkg_path.name}")
        return

    if not args.type:
        print("Error: --type or --from-package is required.", file=sys.stderr)
        sys.exit(1)

    tpl_source = _resolve_template(args.type)
    tpl_dest = output_dir / "templates"
    outputs_dest = output_dir / "outputs"

    if tpl_source.is_zip:
        # Copy .katatpl as-is
        tpl_dest.mkdir(parents=True, exist_ok=True)
        dst = tpl_dest / tpl_source.path.name
        if dst.exists():
            print(f"  skip (exists): {dst}")
        else:
            shutil.copy2(tpl_source.path, dst)
            print(f"  created: {dst}")
    else:
        schema_prefixes = ("schema",)
        for src in tpl_source.path.iterdir():
            if src.name == "description.txt":
                continue

            is_schema = src.stem.startswith(schema_prefixes) and src.suffix == ".json"
            is_template = src.suffix == ".md" and ".kata." in src.name
            is_sample_data = src.suffix == ".json" and not is_schema

            if is_schema or is_template:
                dest_dir = tpl_dest
            elif is_sample_data:
                continue
            else:
                dest_dir = output_dir

            dst = dest_dir / src.name
            if dst.exists():
                print(f"  skip (exists): {dst}")
                continue
            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                dest_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
            print(f"  created: {dst}")

    outputs_dest.mkdir(parents=True, exist_ok=True)
    print(f"  created: {outputs_dest}/")

    from .workflow import init_status
    init_status(output_dir, template=args.type)
    print(f"  created: {output_dir / '.workflow_status.json'}")


def _cmd_schemas(args: argparse.Namespace) -> None:
    pkg_dir = Path(__file__).parent

    # Central schemas
    schemas_dir = pkg_dir / "schemas"
    seen: set[str] = set()
    entries: list[tuple[str, str, str, str]] = []

    for f in sorted(schemas_dir.glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        title = data.get("title", f.stem)
        desc = data.get("description", "")
        entries.append((f.stem, title, desc, str(f.relative_to(pkg_dir))))
        seen.add(f.stem)

    # Per-template schemas
    templates_dir = pkg_dir / "templates"
    if templates_dir.exists():
        for d in sorted(templates_dir.iterdir()):
            if d.is_dir():
                for sf in sorted(d.glob("schema*.json")):
                    name = d.name if sf.name == "schema.json" else f"{d.name}/{sf.stem}"
                    if name not in seen:
                        data = json.loads(sf.read_text(encoding="utf-8"))
                        title = data.get("title", name)
                        desc = data.get("description", "")
                        entries.append((name, title, desc, str(sf.relative_to(pkg_dir))))
                        seen.add(name)

    print("Available schemas:")
    print()
    for name, title, desc, location in entries:
        print(f"  {name:20s} {title} — {desc}")
        print(f"  {'':20s} ({location})")


def _cmd_lint(args: argparse.Namespace) -> None:
    from .linter import lint_file

    fmt = getattr(args, "format", "human")
    schema_name = getattr(args, "schema", None)
    has_errors = False
    for file_path in args.files:
        result = lint_file(file_path, schema_name=schema_name)
        output = result.summary(fmt=fmt)
        if output:
            print(output)
        if not result.ok:
            has_errors = True
        if fmt == "human" and len(args.files) > 1:
            print()
    if has_errors:
        sys.exit(1)


def _cmd_gen_schema_section(args: argparse.Namespace) -> None:
    from .template import generate_schema_section
    from .validator import get_builtin_schema

    schema_path = Path(args.schema)
    if schema_path.exists():
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    else:
        try:
            schema = get_builtin_schema(args.schema)
        except ValueError:
            print(f"Error: schema not found: {args.schema}", file=sys.stderr)
            sys.exit(1)

    section_map: dict[str, str] | None = None
    if args.section_map:
        section_map = json.loads(args.section_map)

    output = generate_schema_section(schema, section_map=section_map)
    print(output)


def _cmd_infer_schema(args: argparse.Namespace) -> None:
    """Infer a schema scaffold from template variables."""
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    text = file_path.read_text(encoding="utf-8")
    schema = _infer_schema_from_template(text)

    if args.format == "json":
        print(json.dumps(schema, indent=2, ensure_ascii=False))
    else:
        # YAML shorthand output
        _print_yaml_shorthand(schema)


def _infer_schema_from_template(text: str) -> dict:
    """Analyze template variables and loops to infer a schema structure.

    Walks the template to find:
    - {{ var }} → top-level string property
    - {{ var | join(...) }} → array property
    - {% for item in collection %} → array of objects
    - {{ item.prop }} within loop → nested object properties
    """
    import re

    var_pattern = re.compile(r"\{\{(.*?)\}\}", re.DOTALL)
    for_pattern = re.compile(
        r"\{%\s*for\s+(\w+(?:\s*,\s*\w+)*)\s+in\s+(.+?)\s*%\}", re.DOTALL
    )

    # Collect loop contexts: {loop_var: iterable_expr}
    loops: dict[str, str] = {}
    for m in for_pattern.finditer(text):
        var_names = [v.strip() for v in m.group(1).split(",")]
        iterable = m.group(2).strip()
        for v in var_names:
            loops[v] = iterable

    # Collect all variable references
    # Structure: {root: {sub_props: set()}}
    top_level: dict[str, dict] = {}
    array_hints: set[str] = set()  # vars used with | join or similar

    for m in var_pattern.finditer(text):
        expr = m.group(1).strip()
        # Strip filters but check for array hints
        if "| join" in expr or "| length" in expr or "| sort" in expr:
            base = expr.split("|")[0].strip()
            parts = re.split(r"[.\[]", base)
            if parts[0] in loops:
                iterable = loops[parts[0]]
                root = iterable.split(".")[0] if "." in iterable else iterable
                if len(parts) > 1:
                    prop = parts[1].rstrip("]\"'")
                    top_level.setdefault(root, {"_items": {}})["_items"].setdefault(prop, {})["_array"] = True
            elif len(parts) == 1:
                array_hints.add(parts[0])

        # Parse dotted path
        base = expr.split("|")[0].strip()
        parts = re.split(r"[.\[]", base)
        root = parts[0].strip()

        if not root or root in ("loop", "true", "false", "none", "True", "False", "None"):
            continue

        if root in loops:
            # This is a loop variable — map to its iterable
            iterable = loops[root]
            iter_parts = iterable.split(".")
            # Resolve to top-level
            actual_root = iter_parts[0]
            if actual_root in loops:
                # Nested loop — e.g., for item in cat.items where cat is from categories
                parent_iterable = loops[actual_root]
                parent_root = parent_iterable.split(".")[0] if "." in parent_iterable else parent_iterable
                top_level.setdefault(parent_root, {"_items": {}})
                nested = top_level[parent_root]["_items"]
                nested_key = iter_parts[-1] if len(iter_parts) > 1 else iterable
                nested.setdefault(nested_key, {"_items": {}})
                if len(parts) > 1:
                    prop = parts[1].rstrip("]\"'")
                    nested[nested_key]["_items"][prop] = {}
            else:
                top_level.setdefault(actual_root, {"_items": {}})
                if len(parts) > 1:
                    prop = parts[1].rstrip("]\"'")
                    top_level[actual_root]["_items"][prop] = {}
        else:
            if len(parts) == 1:
                top_level.setdefault(root, {})
            else:
                top_level.setdefault(root, {"_items": {}})
                prop = parts[1].rstrip("]\"'")
                top_level[root]["_items"][prop] = {}

    # Build JSON Schema
    properties: dict[str, Any] = {}
    for key, info in top_level.items():
        if "_items" in info and info["_items"]:
            # Object array
            item_props = {}
            for prop_name, prop_info in info["_items"].items():
                if "_items" in prop_info and prop_info["_items"]:
                    # Nested array
                    nested_props = {k: {"type": "string"} for k in prop_info["_items"]}
                    item_props[prop_name] = {
                        "type": "array",
                        "items": {"type": "object", "properties": nested_props},
                    }
                elif prop_info.get("_array"):
                    item_props[prop_name] = {"type": "array", "items": {"type": "string"}}
                else:
                    item_props[prop_name] = {"type": "string"}
            properties[key] = {
                "type": "array",
                "items": {"type": "object", "properties": item_props},
            }
        elif key in array_hints:
            properties[key] = {"type": "array", "items": {"type": "string"}}
        else:
            properties[key] = {"type": "string"}

    return {"type": "object", "properties": properties}


def _print_yaml_shorthand(schema: dict, indent: int = 0) -> None:
    """Print a JSON Schema as YAML shorthand notation."""
    prefix = "  " * indent
    props = schema.get("properties", {})
    required = set(schema.get("required", []))

    for key, prop in props.items():
        req = "!" if key in required else ""
        prop_type = prop.get("type", "string")

        if prop_type == "array":
            items = prop.get("items", {})
            if items.get("type") == "object" and "properties" in items:
                print(f"{prefix}{key}[]:{req}")
                _print_yaml_shorthand(items, indent + 1)
            elif items.get("type"):
                print(f"{prefix}{key}: {items['type']}[]{req}")
            else:
                print(f"{prefix}{key}: string[]{req}")
        elif prop_type == "object" and "properties" in prop:
            print(f"{prefix}{key}:{req}")
            _print_yaml_shorthand(prop, indent + 1)
        else:
            enum = prop.get("enum")
            if enum:
                print(f"{prefix}{key}: enum({', '.join(str(v) for v in enum)}){req}")
            else:
                print(f"{prefix}{key}: {prop_type}{req}")


def _resolve_template_source(name_or_path: str) -> str:
    """Resolve a template name or path to its source text.

    Search order: file path -> local ./templates/{name} or .katatpl -> built-in templates.
    """
    path = Path(name_or_path)
    if path.exists():
        return path.read_text(encoding="utf-8")
    # Try as template name via _resolve_template (handles dirs and .katatpl)
    try:
        src = _resolve_template(name_or_path)
        return src.find_tpl_kata_md()
    except SystemExit:
        pass
    print(f"Error: template '{name_or_path}' not found", file=sys.stderr)
    sys.exit(1)


def _cmd_show_prompt(args: argparse.Namespace) -> None:
    """Show the {#prompt} block from a template."""
    from .template import _PROMPT_PATTERN

    source_text = _resolve_template_source(args.template)
    match = _PROMPT_PATTERN.search(source_text)
    if match:
        prompt_text = match.group(1).strip()
        print(prompt_text)
        # Show trust status
        trusted = _check_template_trust(args.template, prompt_text, interactive=False)
        status = "trusted" if trusted else "NOT trusted"
        print(f"\n[{status}] (hash: {_prompt_hash(prompt_text)[:12]}...)", file=sys.stderr)
    else:
        print("No {#prompt} block found in this template.", file=sys.stderr)
        sys.exit(1)

    # Show requires info
    try:
        ts = _resolve_template(args.template)
        reqs = ts.requires()
        if reqs:
            print(f"\nRequires: {', '.join(reqs)}", file=sys.stderr)
            for req_name in reqs:
                print(f"  → gospelo-kata show-prompt {req_name}", file=sys.stderr)
    except SystemExit:
        pass


def _cmd_show_schema(args: argparse.Namespace) -> None:
    """Show the embedded schema from a template as JSON Schema."""
    from .template import Template

    source = _resolve_template_source(args.template)
    tpl = Template(source)
    if tpl.schema is None:
        print("No schema found in this template.", file=sys.stderr)
        sys.exit(1)

    if args.format == "yaml":
        try:
            import yaml
            print(yaml.dump(tpl.schema, allow_unicode=True, default_flow_style=False, sort_keys=False))
        except ImportError:
            print(json.dumps(tpl.schema, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(tpl.schema, indent=2, ensure_ascii=False))

    # Show requires info
    try:
        ts = _resolve_template(args.template)
        reqs = ts.requires()
        if reqs:
            print(f"\nRequires: {', '.join(reqs)}", file=sys.stderr)
            for req_name in reqs:
                print(f"  → gospelo-kata show-schema {req_name}", file=sys.stderr)
    except SystemExit:
        pass


def _cmd_init_vscode(args: argparse.Namespace) -> None:
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    tasks_path = output_dir / "tasks.json"
    tasks = {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "kata: lint current file",
                "type": "shell",
                "command": "gospelo-kata",
                "args": ["lint", "--format", "vscode", "${file}"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "silent",
                    "focus": False,
                    "panel": "shared",
                    "clear": True,
                },
                "problemMatcher": {
                    "owner": "kata",
                    "fileLocation": ["absolute"],
                    "pattern": {
                        "regexp": "^(.+):(\\d+):(\\d+):\\s+(error|warning|info)\\s+\\[(.+?)\\]\\s+(.+)$",
                        "file": 1,
                        "line": 2,
                        "column": 3,
                        "severity": 4,
                        "code": 5,
                        "message": 6,
                    },
                },
            },
            {
                "label": "kata: lint all templates",
                "type": "process",
                "command": "find",
                "args": [
                    ".",
                    "-name",
                    "*.kata.md",
                    "-exec",
                    "gospelo-kata",
                    "lint",
                    "--format",
                    "vscode",
                    "{}",
                    "+",
                ],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared",
                    "clear": True,
                },
                "problemMatcher": {
                    "owner": "kata",
                    "fileLocation": ["relative", "${workspaceFolder}"],
                    "pattern": {
                        "regexp": "^(.+):(\\d+):(\\d+):\\s+(error|warning|info)\\s+\\[(.+?)\\]\\s+(.+)$",
                        "file": 1,
                        "line": 2,
                        "column": 3,
                        "severity": 4,
                        "code": 5,
                        "message": 6,
                    },
                },
            },
        ],
    }

    tasks_path.write_text(json.dumps(tasks, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Created: {tasks_path}")
    print()
    print("Usage:")
    print("  1. Open VS Code in your project")
    print("  2. Cmd+Shift+P > 'Tasks: Run Task' > 'kata: lint current file'")
    print("  3. Errors appear in the Problems panel")
    print()
    print("Tip: Add a keybinding to run lint on save:")
    print('  { "key": "cmd+s", "command": "workbench.action.tasks.runTask",')
    print('    "args": "kata: lint current file" }')


def _cmd_extract(args: argparse.Namespace) -> None:
    from .extract import extract_from_file

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    schema = None
    if args.schema:
        from .validator import get_builtin_schema, load_schema
        schema_path = Path(args.schema)
        if schema_path.exists():
            schema = load_schema(schema_path)
        else:
            try:
                schema = get_builtin_schema(args.schema)
            except FileNotFoundError:
                print(f"Warning: schema '{args.schema}' not found, using Schema Reference section",
                      file=sys.stderr)

    data = extract_from_file(file_path, schema=schema)
    output = json.dumps(data, indent=2, ensure_ascii=False)

    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
        print(f"Extracted: {args.output}")
    else:
        print(output)


def _cmd_coverage(args: argparse.Namespace) -> None:
    from .coverage import (
        analyze_coverage,
        report_to_dict,
        report_to_markdown,
        uncovered_items,
    )

    checklist = Path(args.checklist)
    if not checklist.exists():
        print(f"Error: file not found: {checklist}", file=sys.stderr)
        sys.exit(1)

    tests_dir = Path(args.dir)
    if not tests_dir.is_dir():
        print(f"Error: directory not found: {tests_dir}", file=sys.stderr)
        sys.exit(1)

    report = analyze_coverage(checklist, tests_dir)

    if args.format == "json":
        print(json.dumps(report_to_dict(report), indent=2, ensure_ascii=False))
    elif args.format == "markdown":
        print(report_to_markdown(report))
    else:
        # human-readable
        print(f"Coverage: {report.covered}/{report.total} ({report.coverage_pct}%)")
        print()
        uncov = uncovered_items(report)
        if uncov:
            print(f"Uncovered items ({len(uncov)}):")
            for item in uncov:
                name = item["name_ja"] or item["name"]
                print(f"  - {item['id']}: {name}")
        else:
            print("All items covered.")


def _cmd_assemble(args: argparse.Namespace) -> None:
    """Assemble a _tpl.kata.md from a template + external data file."""
    from .template import _SCHEMA_INLINE_PATTERN, _PROMPT_PATTERN, _DATA_PATTERN

    tpl = _resolve_template(args.type)
    tpl_source = tpl.find_tpl_kata_md()

    # Check prompt trust
    from .template import _PROMPT_PATTERN as _PP
    prompt_match = _PP.search(tpl_source)
    if prompt_match:
        if not _check_template_trust(args.type, prompt_match.group(1).strip()):
            sys.exit(1)

    # Read external data file
    data_path = Path(args.data)
    if not data_path.exists():
        print(f"Error: data file not found: {data_path}", file=sys.stderr)
        sys.exit(1)

    data_text = data_path.read_text(encoding="utf-8").strip()

    # Replace or insert {#data} block
    if _DATA_PATTERN.search(tpl_source):
        # Replace existing {#data} block
        result = _DATA_PATTERN.sub(f"{{#data\n{data_text}\n#}}", tpl_source)
    else:
        # Insert {#data} after {#schema} or {#prompt}
        prompt_match = _PROMPT_PATTERN.search(tpl_source)
        schema_match = _SCHEMA_INLINE_PATTERN.search(tpl_source)
        if prompt_match:
            insert_pos = prompt_match.end()
        elif schema_match:
            insert_pos = schema_match.end()
        else:
            insert_pos = 0
        result = tpl_source[:insert_pos] + f"\n\n{{#data\n{data_text}\n#}}\n" + tpl_source[insert_pos:]

    if args.output:
        out_path = Path(args.output)
    else:
        # Default: {data dir}/{type}_tpl.kata.md
        out_path = data_path.parent / f"{args.type}_tpl.kata.md"

    out_path.write_text(result, encoding="utf-8")
    print(f"Assembled: {out_path}")


def _cmd_pack(args: argparse.Namespace) -> None:
    """Pack a template directory into a .katatpl package."""
    import zipfile

    src_dir = Path(args.template_dir)
    if not src_dir.is_dir():
        print(f"Error: directory not found: {src_dir}", file=sys.stderr)
        sys.exit(1)

    tpl_name = src_dir.name

    # Validate manifest.json exists
    manifest_path = src_dir / MANIFEST_FILE
    if not manifest_path.exists():
        print(f"Error: {MANIFEST_FILE} not found in {src_dir}", file=sys.stderr)
        print(f"Create one with: gospelo-kata pack-init {src_dir}", file=sys.stderr)
        sys.exit(1)

    # Validate manifest has required fields
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    missing = [f for f in ("name", "version", "template") if f not in manifest]
    if missing:
        print(f"Error: {MANIFEST_FILE} missing required fields: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    # Validate template file exists
    tpl_file = manifest["template"]
    if not (src_dir / tpl_file).exists():
        print(f"Error: template file '{tpl_file}' specified in {MANIFEST_FILE} not found", file=sys.stderr)
        sys.exit(1)

    if args.output:
        out_path = Path(args.output)
    else:
        out_path = Path(f"{tpl_name}{KATATPL_EXT}")

    # Validate all files are allowed types
    rejected = []
    for file in sorted(src_dir.rglob("*")):
        if file.is_file():
            rel = str(file.relative_to(src_dir))
            if not _is_allowed_katatpl_file(rel):
                rejected.append(rel)
    if rejected:
        print("Error: disallowed file types found (only template, manifest, and image files are allowed):", file=sys.stderr)
        for r in rejected:
            print(f"  {r}", file=sys.stderr)
        sys.exit(1)

    exclude_dirs = {"outputs", "__pycache__"}

    # Collect files to pack (excluding manifest.json — will be rewritten with _integrity)
    import hashlib
    pack_files: list[tuple[str, bytes]] = []  # (arcname_relative, content)
    for file in sorted(src_dir.rglob("*")):
        if file.is_file():
            rel = file.relative_to(src_dir)
            if rel.parts[0] in exclude_dirs:
                continue
            if str(rel) == MANIFEST_FILE:
                continue
            pack_files.append((str(rel), file.read_bytes()))

    # Compute integrity hash over all non-manifest files
    h = hashlib.sha256()
    for rel_name, content in pack_files:
        h.update(rel_name.encode("utf-8"))
        h.update(content)
    manifest["_integrity"] = h.hexdigest()

    # Write ZIP with updated manifest
    manifest_bytes = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{tpl_name}/{MANIFEST_FILE}", manifest_bytes)
        for rel_name, content in pack_files:
            zf.writestr(f"{tpl_name}/{rel_name}", content)

    print(f"Packed: {out_path} (integrity: {manifest['_integrity'][:12]}...)")


def _cmd_pack_init(args: argparse.Namespace) -> None:
    """Scaffold a template directory with manifest.json and template file."""
    src_dir = Path(args.template_dir)
    tpl_name = src_dir.name

    # Create directory if it doesn't exist
    if not src_dir.exists():
        src_dir.mkdir(parents=True)
        print(f"  created: {src_dir}/")

    # manifest.json
    manifest_path = src_dir / MANIFEST_FILE
    if manifest_path.exists():
        print(f"  skip (exists): {manifest_path}")
    else:
        # Auto-detect existing template file
        tpl_file = ""
        for f in src_dir.iterdir():
            if f.name.endswith("_tpl.kata.md"):
                tpl_file = f.name
                break
        if not tpl_file:
            tpl_file = f"{tpl_name}_tpl.kata.md"

        manifest = {
            "name": tpl_name,
            "version": "1.0.0",
            "description": "",
            "author": "",
            "url": "",
            "license": "",
            "template": tpl_file,
        }

        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"  created: {manifest_path}")

    # Template file
    tpl_file_name = f"{tpl_name}_tpl.kata.md"
    tpl_path = src_dir / tpl_file_name
    if tpl_path.exists():
        print(f"  skip (exists): {tpl_path}")
    else:
        tpl_path.write_text(
            """\
{#schema
#}

{#prompt
#}

{#data
#}

""",
            encoding="utf-8",
        )
        print(f"  created: {tpl_path}")

    # images directory
    images_dir = src_dir / "images"
    if images_dir.exists():
        print(f"  skip (exists): {images_dir}/")
    else:
        images_dir.mkdir()
        print(f"  created: {images_dir}/")

    # outputs directory
    outputs_dir = src_dir / "outputs"
    if outputs_dir.exists():
        print(f"  skip (exists): {outputs_dir}/")
    else:
        outputs_dir.mkdir()
        print(f"  created: {outputs_dir}/")


def _cmd_fmt(args: argparse.Namespace) -> None:
    import html as _html
    import re

    # Matches data-kata spans — permissive capture to find HTML inside
    span_pattern = re.compile(
        r'(<span\s+data-kata="p-[a-z0-9-]+">)(.*?)(</span>)',
    )
    html_tag_pattern = re.compile(r"<[a-zA-Z/][^>]*>")

    def _sanitize_span(m: re.Match) -> str:
        open_tag = m.group(1)
        content = m.group(2)
        close_tag = m.group(3)
        needs_fix = False
        safe = content
        # Escape HTML tags
        if html_tag_pattern.search(safe):
            safe = _html.escape(safe, quote=False)
            needs_fix = True
        # Escape pipe chars that break Markdown tables
        if "|" in safe:
            safe = safe.replace("|", "&#124;")
            needs_fix = True
        if needs_fix:
            return f"{open_tag}{safe}{close_tag}"
        return m.group(0)

    needs_fix = False
    for file_path in args.files:
        path = Path(file_path)
        if not path.exists():
            print(f"Error: file not found: {file_path}", file=sys.stderr)
            sys.exit(1)

        text = path.read_text(encoding="utf-8")
        # Use a more robust approach: process line by line
        new_lines = []
        changed = False
        for line in text.split("\n"):
            new_line = span_pattern.sub(_sanitize_span, line)
            if new_line != line:
                changed = True
            new_lines.append(new_line)

        if changed:
            needs_fix = True
            if args.check:
                print(f"  needs formatting: {file_path}")
            else:
                path.write_text("\n".join(new_lines), encoding="utf-8")
                print(f"  formatted: {file_path}")
        else:
            print(f"  ok: {file_path}")

    if args.check and needs_fix:
        sys.exit(1)


def _cmd_workflow_status(args: argparse.Namespace) -> None:
    from .workflow import (
        init_status,
        load_status,
        mark_step_done,
        reset_for_retry,
        reset_status,
        status_summary,
    )

    suite_dir = Path(args.suite_dir)

    if args.init:
        template, output = args.init
        status = init_status(suite_dir, template=template, output=output)
        print(f"Initialized: {suite_dir / '.workflow_status.json'}")
        print(status_summary(status))
        return

    if args.reset:
        status = reset_status(suite_dir)
        print("All steps reset.")
        print(status_summary(status))
        return

    if args.retry:
        status = reset_for_retry(suite_dir, reason=args.retry_reason)
        print(f"Retry: round {status['round']}")
        print(status_summary(status))
        return

    if args.mark_done:
        try:
            status = mark_step_done(suite_dir, args.mark_done, note=args.note)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        print(status_summary(status))
        return

    # Default: show status
    status = load_status(suite_dir)
    print(status_summary(status))


if __name__ == "__main__":
    main()
