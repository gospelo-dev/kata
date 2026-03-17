import * as vscode from "vscode";
import { execFile } from "child_process";

const DIAGNOSTIC_SOURCE = "kata-lint";

interface LintMessage {
  file: string;
  line: number;
  column: number;
  severity: string;
  code: string;
  message: string;
}

function parseLintOutput(output: string): LintMessage[] {
  // Format: file:line:col: level [code] message
  const pattern =
    /^(.+):(\d+):(\d+):\s+(error|warning|info)\s+\[(.+?)\]\s+(.+)$/;
  const messages: LintMessage[] = [];

  for (const line of output.split("\n")) {
    const match = pattern.exec(line.trim());
    if (match) {
      messages.push({
        file: match[1],
        line: parseInt(match[2], 10),
        column: parseInt(match[3], 10),
        severity: match[4],
        code: match[5],
        message: match[6],
      });
    }
  }
  return messages;
}

function toSeverity(
  level: string,
  config: vscode.WorkspaceConfiguration
): vscode.DiagnosticSeverity {
  switch (level) {
    case "error":
      return vscode.DiagnosticSeverity.Error;
    case "warning":
      return vscode.DiagnosticSeverity.Warning;
    case "info": {
      const mapped = config.get<string>("severity.info", "Information");
      switch (mapped) {
        case "Error":
          return vscode.DiagnosticSeverity.Error;
        case "Warning":
          return vscode.DiagnosticSeverity.Warning;
        case "Hint":
          return vscode.DiagnosticSeverity.Hint;
        default:
          return vscode.DiagnosticSeverity.Information;
      }
    }
    default:
      return vscode.DiagnosticSeverity.Information;
  }
}

function lintDocument(
  document: vscode.TextDocument,
  diagnosticCollection: vscode.DiagnosticCollection
): void {
  const config = vscode.workspace.getConfiguration("kataLint");
  const pythonPath = config.get<string>("pythonPath", "python");
  const filePath = document.uri.fsPath;

  execFile(
    pythonPath,
    ["-m", "gospelo_kata.cli", "lint", "--format", "vscode", filePath],
    { cwd: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath, timeout: 10000 },
    (error, stdout, stderr) => {
      // gospelo-kata returns exit code 1 when there are errors, which is normal
      if (error && !stdout && error.code !== 1) {
        // Real execution error (python not found, module not installed, etc.)
        const msg = stderr || error.message;
        if (msg.includes("No module named")) {
          vscode.window.showWarningMessage(
            "kata-lint: gospelo-kata is not installed. Run: pip install gospelo-kata"
          );
        }
        diagnosticCollection.delete(document.uri);
        return;
      }

      const messages = parseLintOutput(stdout);
      const diagnostics: vscode.Diagnostic[] = messages.map((m) => {
        // Convert 1-based line/col to 0-based
        const line = Math.max(0, m.line - 1);
        const col = Math.max(0, m.column - 1);

        // Highlight the whole line for better visibility
        const lineText = document.lineAt(line).text;
        const range = new vscode.Range(line, col, line, lineText.length);

        const diag = new vscode.Diagnostic(
          range,
          m.message,
          toSeverity(m.severity, config)
        );
        diag.source = DIAGNOSTIC_SOURCE;
        diag.code = m.code;
        return diag;
      });

      diagnosticCollection.set(document.uri, diagnostics);
    }
  );
}

function isExcluded(filePath: string): boolean {
  const config = vscode.workspace.getConfiguration("kataLint");
  const excludePatterns = config.get<string[]>("exclude", []);
  for (const pattern of excludePatterns) {
    if (new vscode.RelativePattern(
      vscode.workspace.workspaceFolders?.[0] ?? "",
      pattern
    ).pattern) {
      // Use minimatch-style check via picomatch built into VS Code
      const regex = globToRegex(pattern);
      if (regex.test(filePath)) {
        return true;
      }
    }
  }
  return false;
}

function globToRegex(glob: string): RegExp {
  const escaped = glob
    .replace(/[.+^${}()|[\]\\]/g, "\\$&")
    .replace(/\*\*/g, "{{GLOBSTAR}}")
    .replace(/\*/g, "[^/]*")
    .replace(/\?/g, "[^/]")
    .replace(/\{\{GLOBSTAR\}\}/g, ".*");
  return new RegExp(escaped + "$");
}

function isTargetDocument(document: vscode.TextDocument): boolean {
  if (!document.fileName.endsWith(".kata.md")) {
    return false;
  }
  return !isExcluded(document.uri.fsPath);
}

// ---------------------------------------------------------------------------
// Hover provider — shows schema type info for data-kata attributes
// ---------------------------------------------------------------------------

interface SchemaInfo {
  prop: string;
  type?: string;
  required?: boolean;
  enumValues?: string[];
  minLength?: number;
  maxLength?: number;
}

function parseSchemaReference(text: string): Map<string, SchemaInfo> {
  // Try YAML shorthand code block first (new format)
  const shorthandMap = parseSchemaShorthandBlock(text);
  if (shorthandMap.size > 0) return shorthandMap;

  // Fallback: legacy anchor heading format
  const map = new Map<string, SchemaInfo>();
  const blockPattern =
    /#### <a id="(p-[a-z0-9_-]+)"><\/a>([^\n]*)\n\n?((?:- \*\*[^\n]+\n?)*)/g;
  let m: RegExpExecArray | null;
  while ((m = blockPattern.exec(text)) !== null) {
    const anchor = m[1];
    const body = m[3];
    const info: SchemaInfo = { prop: m[2].trim() };

    const typeMatch = /\*\*type\*\*:\s*(\w+)/.exec(body);
    if (typeMatch) info.type = typeMatch[1];

    info.required = body.includes("**(required)**");

    const enumMatch = /\*\*enum\*\*:\s*\[([^\]]*)\]/.exec(body);
    if (enumMatch) {
      info.enumValues = enumMatch[1]
        .split(",")
        .map((v) => v.trim().replace(/^'|'$/g, ""));
    }

    const minLenMatch = /\*\*minLength\*\*:\s*(\d+)/.exec(body);
    if (minLenMatch) info.minLength = parseInt(minLenMatch[1], 10);

    const maxLenMatch = /\*\*maxLength\*\*:\s*(\d+)/.exec(body);
    if (maxLenMatch) info.maxLength = parseInt(maxLenMatch[1], 10);

    map.set(anchor, info);
  }
  return map;
}

function parseSchemaShorthandBlock(text: string): Map<string, SchemaInfo> {
  const map = new Map<string, SchemaInfo>();

  // Find ```yaml block after **Schema**
  const codeMatch =
    /\*\*Schema\*\*\s*\n\s*```yaml\n([\s\S]*?)```/.exec(text);
  if (!codeMatch) return map;

  const block = codeMatch[1];
  let currentArray: string | null = null;

  for (const line of block.split("\n")) {
    if (line.trim() === "") continue;

    // Array object: name[]!:
    const arrMatch = /^(\w+)\[\](!)?:\s*$/.exec(line);
    if (arrMatch) {
      const name = arrMatch[1];
      const anchor = "p-" + name.replace(/_/g, "-");
      map.set(anchor, {
        prop: name,
        type: "array",
        required: !!arrMatch[2],
      });
      currentArray = name;
      continue;
    }

    // Property: name: type! or name: enum(a, b)!
    const propMatch = /^(\s*)(\w+):\s*(.+)$/.exec(line);
    if (propMatch) {
      const indent = propMatch[1];
      const name = propMatch[2];
      let typeStr = propMatch[3].trim();
      const required = typeStr.endsWith("!");
      if (required) typeStr = typeStr.slice(0, -1);

      const isArrayType = typeStr.endsWith("[]");
      if (isArrayType) typeStr = typeStr.slice(0, -2);

      let enumValues: string[] | undefined;
      const enumMatch = /^enum\((.+)\)$/.exec(typeStr);
      if (enumMatch) {
        enumValues = enumMatch[1].split(",").map((v) => v.trim());
        typeStr = "enum";
      }

      const fullType = isArrayType ? `${typeStr}[]` : typeStr;
      const isChild = indent.length > 0 && currentArray !== null;
      const propPath = isChild ? `${currentArray}.${name}` : name;
      const anchorName = isChild
        ? `${currentArray}-${name}`.replace(/_/g, "-")
        : name.replace(/_/g, "-");
      const anchor = "p-" + anchorName;

      map.set(anchor, {
        prop: propPath,
        type: fullType,
        required,
        enumValues,
      });

      if (!isChild) {
        currentArray = null;
      }
      continue;
    }

    // Non-indented non-matching line ends array context
    if (!/^\s/.test(line)) {
      currentArray = null;
    }
  }

  return map;
}

class KataHoverProvider implements vscode.HoverProvider {
  provideHover(
    document: vscode.TextDocument,
    position: vscode.Position
  ): vscode.Hover | null {
    if (!document.fileName.endsWith(".md")) {
      return null;
    }
    const line = document.lineAt(position).text;

    // Find data-kata="p-xxx" at cursor position
    const pattern = /data-kata="(p-[a-z0-9_-]+)"/g;
    let match: RegExpExecArray | null;
    while ((match = pattern.exec(line)) !== null) {
      const start = match.index;
      const end = start + match[0].length;
      if (position.character >= start && position.character <= end) {
        const anchor = match[1];
        const schemaMap = parseSchemaReference(document.getText());
        // Normalize: try exact match, then swap _ and - after "p-" prefix
        const normalize = (s: string, ch: string, rep: string) =>
          "p-" + s.slice(2).replace(new RegExp(`\\${ch}`, "g"), rep);
        const info = schemaMap.get(anchor)
          || schemaMap.get(normalize(anchor, "-", "_"))
          || schemaMap.get(normalize(anchor, "_", "-"));
        if (!info) {
          return new vscode.Hover(
            new vscode.MarkdownString(`\`${anchor}\``)
          );
        }

        const parts: string[] = [`**${info.prop}**`];
        if (info.type) {
          const req = info.required ? " *(required)*" : "";
          parts.push(`- type: \`${info.type}\`${req}`);
        }
        if (info.enumValues) {
          parts.push(
            `- enum: ${info.enumValues.map((v) => `\`${v}\``).join(" | ")}`
          );
        }
        if (info.minLength !== undefined) {
          parts.push(`- minLength: ${info.minLength}`);
        }
        if (info.maxLength !== undefined) {
          parts.push(`- maxLength: ${info.maxLength}`);
        }

        const md = new vscode.MarkdownString(parts.join("\n\n"));
        const range = new vscode.Range(
          position.line,
          start,
          position.line,
          end
        );
        return new vscode.Hover(md, range);
      }
    }
    return null;
  }
}

function formatDocument(
  document: vscode.TextDocument,
  diagnosticCollection: vscode.DiagnosticCollection
): void {
  const config = vscode.workspace.getConfiguration("kataLint");
  const pythonPath = config.get<string>("pythonPath", "python");
  const filePath = document.uri.fsPath;

  execFile(
    pythonPath,
    ["-m", "gospelo_kata.cli", "fmt", filePath],
    { cwd: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath, timeout: 10000 },
    (error, stdout, stderr) => {
      if (error && error.code !== 0) {
        vscode.window.showErrorMessage(
          `kata-lint: format failed — ${stderr || error.message}`
        );
        return;
      }

      // Show result
      if (stdout.includes("formatted:")) {
        vscode.window.showInformationMessage("kata-lint: formatted");
        // Re-lint after format
        lintDocument(document, diagnosticCollection);
      } else {
        vscode.window.showInformationMessage("kata-lint: no changes needed");
      }
    }
  );
}

class KataFormattingProvider implements vscode.DocumentFormattingEditProvider {
  provideDocumentFormattingEdits(
    document: vscode.TextDocument
  ): vscode.ProviderResult<vscode.TextEdit[]> {
    return new Promise((resolve) => {
      const config = vscode.workspace.getConfiguration("kataLint");
      const pythonPath = config.get<string>("pythonPath", "python");
      const filePath = document.uri.fsPath;

      // Run fmt --check first to see if changes are needed, then read the formatted output
      execFile(
        pythonPath,
        ["-m", "gospelo_kata.cli", "fmt", filePath],
        { cwd: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath, timeout: 10000 },
        (error, _stdout, _stderr) => {
          if (error && error.code !== 0) {
            resolve([]);
            return;
          }
          // fmt writes in-place, so re-read the file and replace the entire document
          const fs = require("fs");
          try {
            const formatted = fs.readFileSync(filePath, "utf-8");
            const fullRange = new vscode.Range(
              document.positionAt(0),
              document.positionAt(document.getText().length)
            );
            resolve([vscode.TextEdit.replace(fullRange, formatted)]);
          } catch {
            resolve([]);
          }
        }
      );
    });
  }
}

export function activate(context: vscode.ExtensionContext): void {
  const diagnosticCollection =
    vscode.languages.createDiagnosticCollection(DIAGNOSTIC_SOURCE);
  context.subscriptions.push(diagnosticCollection);

  // Register hover provider for .kata.md files
  context.subscriptions.push(
    vscode.languages.registerHoverProvider(
      { language: "markdown" },
      new KataHoverProvider()
    )
  );

  const config = vscode.workspace.getConfiguration("kataLint");

  // Sync and lint on save
  context.subscriptions.push(
    vscode.workspace.onDidSaveTextDocument((document) => {
      if (!isTargetDocument(document)) return;
      const cfg = vscode.workspace.getConfiguration("kataLint");
      if (cfg.get<boolean>("syncOnSave", true)) {
        const pythonPath = cfg.get<string>("pythonPath", "python");
        const filePath = document.uri.fsPath;
        execFile(
          pythonPath,
          ["-m", "gospelo_kata.cli", "fmt", filePath],
          { cwd: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath, timeout: 10000 },
          (error, _stdout, stderr) => {
            if (error && error.code !== 0) {
              vscode.window.showErrorMessage(
                `kata-lint: sync failed — ${stderr || error.message}`
              );
              lintDocument(document, diagnosticCollection);
              return;
            }
            // Revert the editor to pick up the file changes written by fmt
            vscode.commands.executeCommand("workbench.action.files.revert").then(() => {
              lintDocument(document, diagnosticCollection);
            });
          }
        );
      } else if (cfg.get<boolean>("lintOnSave", true)) {
        lintDocument(document, diagnosticCollection);
      }
    })
  );

  // Lint on open
  context.subscriptions.push(
    vscode.workspace.onDidOpenTextDocument((document) => {
      if (!isTargetDocument(document)) return;
      const cfg = vscode.workspace.getConfiguration("kataLint");
      if (cfg.get<boolean>("lintOnOpen", true)) {
        lintDocument(document, diagnosticCollection);
      }
    })
  );

  // Clear diagnostics when file is closed
  context.subscriptions.push(
    vscode.workspace.onDidCloseTextDocument((document) => {
      diagnosticCollection.delete(document.uri);
    })
  );

  // Manual lint command
  context.subscriptions.push(
    vscode.commands.registerCommand("kataLint.lintFile", () => {
      const editor = vscode.window.activeTextEditor;
      if (editor && isTargetDocument(editor.document)) {
        lintDocument(editor.document, diagnosticCollection);
      }
    })
  );

  // Format command
  context.subscriptions.push(
    vscode.commands.registerCommand("kataLint.formatFile", () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor || !isTargetDocument(editor.document)) {
        return;
      }
      formatDocument(editor.document, diagnosticCollection);
    })
  );

  // Register as document formatting provider for .kata.md files
  context.subscriptions.push(
    vscode.languages.registerDocumentFormattingEditProvider(
      { language: "markdown", pattern: "**/*.kata.md" },
      new KataFormattingProvider()
    )
  );

  // Lint already-open files on activation
  if (config.get<boolean>("lintOnOpen", true)) {
    for (const document of vscode.workspace.textDocuments) {
      if (isTargetDocument(document)) {
        lintDocument(document, diagnosticCollection);
      }
    }
  }
}

export function deactivate(): void {
  // nothing to clean up
}
