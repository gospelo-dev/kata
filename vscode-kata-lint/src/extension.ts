import * as vscode from "vscode";
import { execFile } from "child_process";

const DIAGNOSTIC_SOURCE = "kata-lint";

const SYNC_MODE_LABELS: Record<string, string> = {
  off: "$(sync-ignored) Sync: OFF",
  toHtml: "$(arrow-right) Sync: to HTML",
  toData: "$(arrow-left) Sync: to Data",
};

let syncStatusBarItem: vscode.StatusBarItem;

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

  const lines = codeMatch[1].split("\n");

  function parseLevel(start: number, baseIndent: number, parentPath: string, parentAnchor: string): number {
    let i = start;
    while (i < lines.length) {
      const line = lines[i];
      const trimmed = line.trimStart();
      if (trimmed === "") { i++; continue; }

      const indent = line.length - trimmed.length;
      if (indent < baseIndent) break;

      // Array object: name[]!:
      const arrMatch = /^(\w+)\[\](!)?:\s*$/.exec(trimmed);
      if (arrMatch) {
        const name = arrMatch[1];
        const propPath = parentPath ? `${parentPath}.${name}` : name;
        const anchorName = parentAnchor
          ? `${parentAnchor}-${name}`.replace(/_/g, "-")
          : name.replace(/_/g, "-");
        const anchor = "p-" + anchorName;
        map.set(anchor, {
          prop: propPath,
          type: "array",
          required: !!arrMatch[2],
        });
        i = parseLevel(i + 1, indent + 2, propPath, anchorName);
        continue;
      }

      // Property: name: type! or name: enum(a, b)!
      const propMatch = /^(\w+):\s*(.+)$/.exec(trimmed);
      if (propMatch) {
        const name = propMatch[1];
        let typeStr = propMatch[2].trim();
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
        const propPath = parentPath ? `${parentPath}.${name}` : name;
        const anchorName = parentAnchor
          ? `${parentAnchor}-${name}`.replace(/_/g, "-")
          : name.replace(/_/g, "-");
        const anchor = "p-" + anchorName;

        map.set(anchor, {
          prop: propPath,
          type: fullType,
          required,
          enumValues,
        });
        i++;
        continue;
      }

      i++;
    }
    return i;
  }

  parseLevel(0, 0, "", "");
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
        // Strip array indices (e.g. p-categories-0-items-0-status → p-categories-items-status)
        const stripIndices = (s: string) =>
          s.replace(/-\d+/g, "");
        // Normalize: try exact match, then swap _ and - after "p-" prefix
        const normalize = (s: string, ch: string, rep: string) =>
          "p-" + s.slice(2).replace(new RegExp(`\\${ch}`, "g"), rep);
        const stripped = stripIndices(anchor);
        const info = schemaMap.get(anchor)
          || schemaMap.get(stripped)
          || schemaMap.get(normalize(stripped, "-", "_"))
          || schemaMap.get(normalize(stripped, "_", "-"));
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

function syncToHtml(
  document: vscode.TextDocument,
  diagnosticCollection: vscode.DiagnosticCollection
): void {
  const config = vscode.workspace.getConfiguration("kataLint");
  const pythonPath = config.get<string>("pythonPath", "python");
  const filePath = document.uri.fsPath;
  const cwd = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

  // Data → template re-execution → body update
  execFile(
    pythonPath,
    ["-m", "gospelo_kata.cli", "sync", "to-html", filePath, "-o", filePath],
    { cwd, timeout: 15000 },
    (error, _stdout, stderr) => {
      if (error && error.code !== 0) {
        vscode.window.showErrorMessage(
          `kata-lint: sync to-html failed — ${stderr || error.message}`
        );
        return;
      }

      vscode.commands
        .executeCommand("workbench.action.files.revert")
        .then(() => {
          vscode.window.showInformationMessage("kata-lint: synced to HTML");
          lintDocument(document, diagnosticCollection);
        });
    }
  );
}

function syncToData(
  document: vscode.TextDocument,
  diagnosticCollection: vscode.DiagnosticCollection
): void {
  const config = vscode.workspace.getConfiguration("kataLint");
  const pythonPath = config.get<string>("pythonPath", "python");
  const filePath = document.uri.fsPath;
  const cwd = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

  // Span extraction → Data block update → re-render
  execFile(
    pythonPath,
    ["-m", "gospelo_kata.cli", "sync", "to-data", filePath, "-o", filePath],
    { cwd, timeout: 15000 },
    (error, _stdout, stderr) => {
      if (error && error.code !== 0) {
        vscode.window.showErrorMessage(
          `kata-lint: sync to-data failed — ${stderr || error.message}`
        );
        return;
      }

      vscode.commands
        .executeCommand("workbench.action.files.revert")
        .then(() => {
          vscode.window.showInformationMessage("kata-lint: synced to Data");
          lintDocument(document, diagnosticCollection);
        });
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

      // Run sync to-html to re-render, then read the output
      execFile(
        pythonPath,
        ["-m", "gospelo_kata.cli", "sync", "to-html", filePath, "-o", filePath],
        { cwd: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath, timeout: 15000 },
        (error, _stdout, _stderr) => {
          if (error && error.code !== 0) {
            resolve([]);
            return;
          }
          // sync writes in-place, so re-read the file and replace the entire document
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
      const syncDirection = cfg.get<string>("syncOnSave", "off");

      if (syncDirection === "toHtml" || syncDirection === "toData") {
        const syncFn = syncDirection === "toHtml" ? syncToHtml : syncToData;
        syncFn(document, diagnosticCollection);
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

  // Sync to HTML command (Data → HTML) + set mode
  context.subscriptions.push(
    vscode.commands.registerCommand("kataLint.syncToHtml", async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor || !isTargetDocument(editor.document)) {
        return;
      }
      const cfg = vscode.workspace.getConfiguration("kataLint");
      await cfg.update("syncOnSave", "toHtml", vscode.ConfigurationTarget.Workspace);
      updateSyncStatusBar();
      syncToHtml(editor.document, diagnosticCollection);
    })
  );

  // Sync to Data command (Span → Data) + set mode
  context.subscriptions.push(
    vscode.commands.registerCommand("kataLint.syncToData", async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor || !isTargetDocument(editor.document)) {
        return;
      }
      const cfg = vscode.workspace.getConfiguration("kataLint");
      await cfg.update("syncOnSave", "toData", vscode.ConfigurationTarget.Workspace);
      updateSyncStatusBar();
      syncToData(editor.document, diagnosticCollection);
    })
  );

  // Sync OFF command — disable auto-sync
  context.subscriptions.push(
    vscode.commands.registerCommand("kataLint.syncOff", async () => {
      const cfg = vscode.workspace.getConfiguration("kataLint");
      await cfg.update("syncOnSave", "off", vscode.ConfigurationTarget.Workspace);
      updateSyncStatusBar();
      vscode.window.showInformationMessage("kata-lint: sync OFF");
    })
  );

  // Sync mode picker command
  context.subscriptions.push(
    vscode.commands.registerCommand("kataLint.setSyncMode", async () => {
      const items: vscode.QuickPickItem[] = [
        { label: "$(sync-ignored) OFF", description: "Manual sync only", detail: "off" },
        { label: "$(arrow-right) Sync to HTML", description: "Data → HTML on save", detail: "toHtml" },
        { label: "$(arrow-left) Sync to Data", description: "Span → Data on save", detail: "toData" },
      ];
      const picked = await vscode.window.showQuickPick(items, {
        placeHolder: "Select sync mode for .kata.md files",
      });
      if (picked) {
        const cfg = vscode.workspace.getConfiguration("kataLint");
        await cfg.update("syncOnSave", picked.detail, vscode.ConfigurationTarget.Workspace);
        updateSyncStatusBar();
      }
    })
  );

  // Status bar item
  syncStatusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  syncStatusBarItem.command = "kataLint.setSyncMode";
  syncStatusBarItem.tooltip = "Click to change Kata sync mode";
  context.subscriptions.push(syncStatusBarItem);
  updateSyncStatusBar();

  // Update status bar when config changes
  context.subscriptions.push(
    vscode.workspace.onDidChangeConfiguration((e) => {
      if (e.affectsConfiguration("kataLint.syncOnSave")) {
        updateSyncStatusBar();
      }
    })
  );

  // Show/hide status bar based on active editor
  context.subscriptions.push(
    vscode.window.onDidChangeActiveTextEditor((editor) => {
      if (editor && isTargetDocument(editor.document)) {
        syncStatusBarItem.show();
      } else {
        syncStatusBarItem.hide();
      }
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

  // Show status bar if active editor is .kata.md
  if (vscode.window.activeTextEditor && isTargetDocument(vscode.window.activeTextEditor.document)) {
    syncStatusBarItem.show();
  }
}

function updateSyncStatusBar(): void {
  const cfg = vscode.workspace.getConfiguration("kataLint");
  const mode = cfg.get<string>("syncOnSave", "off");
  syncStatusBarItem.text = SYNC_MODE_LABELS[mode] || SYNC_MODE_LABELS.off;
}

export function deactivate(): void {
  // nothing to clean up
}
