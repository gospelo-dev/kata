# KATA Markdown™ — gospelo-kata
# Copyright (c) 2025 gospelo. All rights reserved.
# Licensed under the MIT License. See LICENSE.md for details.

"""Browser-based HTML editor for JSON documents.

Launches a local HTTP server with a single-page editor that:
- Renders JSON data as an editable HTML form
- Provides live Markdown preview
- Saves changes back to the JSON file
"""

from __future__ import annotations

import http.server
import json
import socketserver
import threading
import webbrowser
from pathlib import Path
from typing import Any

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>kata editor — {title}</title>
<style>
:root {{
  --bg: #1e1e2e;
  --surface: #313244;
  --text: #cdd6f4;
  --subtext: #a6adc8;
  --accent: #89b4fa;
  --green: #a6e3a1;
  --red: #f38ba8;
  --border: #45475a;
  --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: var(--font); background: var(--bg); color: var(--text); }}
header {{
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 24px; background: var(--surface); border-bottom: 1px solid var(--border);
}}
header h1 {{ font-size: 16px; font-weight: 600; }}
header .actions {{ display: flex; gap: 8px; }}
button {{
  padding: 6px 16px; border: 1px solid var(--border); border-radius: 6px;
  background: var(--surface); color: var(--text); cursor: pointer; font-size: 13px;
}}
button:hover {{ border-color: var(--accent); }}
button.primary {{ background: var(--accent); color: var(--bg); border-color: var(--accent); }}
button.primary:hover {{ opacity: 0.9; }}
.container {{ display: flex; height: calc(100vh - 49px); }}
.panel {{ flex: 1; overflow-y: auto; padding: 16px; }}
.panel + .panel {{ border-left: 1px solid var(--border); }}
.panel h2 {{ font-size: 14px; color: var(--subtext); margin-bottom: 12px; }}
.field {{ margin-bottom: 12px; }}
.field label {{ display: block; font-size: 12px; color: var(--subtext); margin-bottom: 4px; }}
.field input, .field textarea, .field select {{
  width: 100%; padding: 8px; border: 1px solid var(--border); border-radius: 4px;
  background: var(--bg); color: var(--text); font-family: var(--font); font-size: 13px;
}}
.field textarea {{ min-height: 80px; resize: vertical; }}
.field input:focus, .field textarea:focus {{
  outline: none; border-color: var(--accent);
}}
.array-item {{
  background: var(--surface); border: 1px solid var(--border); border-radius: 6px;
  padding: 12px; margin-bottom: 8px; position: relative;
}}
.array-item .remove {{
  position: absolute; top: 8px; right: 8px; background: none; border: none;
  color: var(--red); cursor: pointer; font-size: 16px; padding: 2px 6px;
}}
.add-btn {{
  display: block; width: 100%; padding: 8px; border: 1px dashed var(--border);
  border-radius: 4px; background: none; color: var(--subtext); cursor: pointer;
  margin-bottom: 12px;
}}
.add-btn:hover {{ border-color: var(--accent); color: var(--accent); }}
#preview {{ white-space: pre-wrap; font-size: 13px; line-height: 1.6; }}
#preview table {{ border-collapse: collapse; margin: 8px 0; }}
#preview th, #preview td {{ border: 1px solid var(--border); padding: 4px 8px; text-align: left; }}
#preview th {{ background: var(--surface); }}
.status {{ padding: 4px 12px; font-size: 12px; border-radius: 4px; }}
.status.saved {{ color: var(--green); }}
.status.modified {{ color: var(--red); }}
.status.error {{ color: var(--red); font-weight: bold; }}
</style>
</head>
<body>
<header>
  <h1>kata editor</h1>
  <div class="actions">
    <span id="status" class="status saved">saved</span>
    <button onclick="resetData()">Reset</button>
    <button class="primary" onclick="saveData()">Save</button>
  </div>
</header>
<div class="container">
  <div class="panel" id="editor-panel">
    <h2>Editor</h2>
    <div id="editor"></div>
  </div>
  <div class="panel" id="preview-panel">
    <h2>Preview (JSON)</h2>
    <pre id="preview"></pre>
  </div>
</div>
<script>
let originalData = {json_data};
let currentData = JSON.parse(JSON.stringify(originalData));

function renderEditor() {{
  const editor = document.getElementById("editor");
  editor.innerHTML = renderObject(currentData, "");
  updatePreview();
}}

function renderObject(obj, path) {{
  let html = "";
  for (const [key, value] of Object.entries(obj)) {{
    const fieldPath = path ? path + "." + key : key;
    if (Array.isArray(value)) {{
      html += renderArray(value, key, fieldPath);
    }} else if (typeof value === "object" && value !== null) {{
      html += '<div class="field"><label>' + key + '</label>';
      html += '<div style="padding-left:12px;border-left:2px solid var(--border);margin-left:4px">';
      html += renderObject(value, fieldPath);
      html += '</div></div>';
    }} else {{
      html += renderField(key, value, fieldPath);
    }}
  }}
  return html;
}}

function renderField(key, value, path) {{
  const id = "f_" + path.replace(/[^a-zA-Z0-9]/g, "_");
  if (typeof value === "string" && value.length > 60) {{
    return '<div class="field"><label>' + key + '</label>' +
      '<textarea id="' + id + '" onchange="updateValue(\\'' + path + '\\', this.value)">' +
      escapeHtml(value) + '</textarea></div>';
  }}
  const inputType = typeof value === "number" ? "number" : "text";
  const val = typeof value === "boolean" ? value : escapeHtml(String(value));
  return '<div class="field"><label>' + key + '</label>' +
    '<input type="' + inputType + '" id="' + id + '" value="' + val + '" ' +
    'onchange="updateValue(\\'' + path + '\\', this.value, \\'' + typeof value + '\\')">' +
    '</div>';
}}

function renderArray(arr, key, path) {{
  let html = '<div class="field"><label>' + key + ' (' + arr.length + ')</label>';
  for (let i = 0; i < arr.length; i++) {{
    const itemPath = path + "[" + i + "]";
    html += '<div class="array-item">';
    html += '<button class="remove" onclick="removeArrayItem(\\'' + path + '\\',' + i + ')">x</button>';
    if (typeof arr[i] === "object" && arr[i] !== null) {{
      html += renderObject(arr[i], itemPath);
    }} else {{
      html += renderField(i, arr[i], itemPath);
    }}
    html += '</div>';
  }}
  html += '<button class="add-btn" onclick="addArrayItem(\\'' + path + '\\')">+ Add item</button>';
  html += '</div>';
  return html;
}}

function getByPath(obj, path) {{
  const parts = path.replace(/\\[(\d+)\\]/g, ".$1").split(".");
  let curr = obj;
  for (const p of parts) {{
    if (curr === undefined) return undefined;
    curr = curr[p];
  }}
  return curr;
}}

function setByPath(obj, path, value) {{
  const parts = path.replace(/\\[(\d+)\\]/g, ".$1").split(".");
  let curr = obj;
  for (let i = 0; i < parts.length - 1; i++) {{
    curr = curr[parts[i]];
  }}
  const last = parts[parts.length - 1];
  curr[last] = value;
}}

function updateValue(path, value, origType) {{
  if (origType === "number") value = Number(value);
  else if (origType === "boolean") value = value === "true";
  setByPath(currentData, path, value);
  document.getElementById("status").textContent = "modified";
  document.getElementById("status").className = "status modified";
  updatePreview();
}}

function removeArrayItem(path, index) {{
  const arr = getByPath(currentData, path);
  arr.splice(index, 1);
  renderEditor();
  document.getElementById("status").textContent = "modified";
  document.getElementById("status").className = "status modified";
}}

function addArrayItem(path) {{
  const arr = getByPath(currentData, path);
  if (arr.length > 0 && typeof arr[0] === "object") {{
    const template = {{}};
    for (const key of Object.keys(arr[0])) {{
      template[key] = "";
    }}
    arr.push(template);
  }} else {{
    arr.push("");
  }}
  renderEditor();
  document.getElementById("status").textContent = "modified";
  document.getElementById("status").className = "status modified";
}}

function resetData() {{
  currentData = JSON.parse(JSON.stringify(originalData));
  renderEditor();
  document.getElementById("status").textContent = "saved";
  document.getElementById("status").className = "status saved";
}}

async function saveData() {{
  try {{
    const resp = await fetch("/save", {{
      method: "POST",
      headers: {{ "Content-Type": "application/json" }},
      body: JSON.stringify(currentData, null, 2),
    }});
    if (resp.ok) {{
      originalData = JSON.parse(JSON.stringify(currentData));
      document.getElementById("status").textContent = "saved";
      document.getElementById("status").className = "status saved";
    }} else {{
      document.getElementById("status").textContent = "save failed";
      document.getElementById("status").className = "status error";
    }}
  }} catch (e) {{
    document.getElementById("status").textContent = "save error";
    document.getElementById("status").className = "status error";
  }}
}}

function updatePreview() {{
  document.getElementById("preview").textContent = JSON.stringify(currentData, null, 2);
}}

function escapeHtml(s) {{
  return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}}

renderEditor();
</script>
</body>
</html>
"""


def _build_html(data: dict[str, Any], title: str) -> str:
    """Build the editor HTML page."""
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    return _HTML_TEMPLATE.format(
        title=title,
        json_data=json_str,
    )


class _EditorHandler(http.server.BaseHTTPRequestHandler):
    """HTTP handler for the editor."""

    html_content: str = ""
    file_path: Path | None = None
    data: dict[str, Any] = {}

    def do_GET(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(self.html_content.encode("utf-8"))

    def do_POST(self) -> None:
        if self.path == "/save" and self.file_path:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            try:
                new_data = json.loads(body)
                self.file_path.write_text(
                    json.dumps(new_data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                self.__class__.data = new_data
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
            except (json.JSONDecodeError, OSError) as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        # Suppress request logs
        pass


def serve_editor(
    file_path: str | Path,
    port: int = 0,
    open_browser: bool = True,
) -> None:
    """Launch the HTML editor for a JSON file.

    Args:
        file_path: Path to the JSON file to edit.
        port: Port number (0 = auto-assign).
        open_browser: Whether to open the browser automatically.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    title = path.stem

    html = _build_html(data, title)

    handler = type("Handler", (_EditorHandler,), {
        "html_content": html,
        "file_path": path,
        "data": data,
    })

    with socketserver.TCPServer(("127.0.0.1", port), handler) as server:
        actual_port = server.server_address[1]
        url = f"http://127.0.0.1:{actual_port}"
        print(f"kata editor: {url} (editing {path})")
        print("Press Ctrl+C to stop.")

        if open_browser:
            webbrowser.open(url)

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nEditor stopped.")
