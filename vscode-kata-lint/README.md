# KATA Markdown™ Language Support

[![VS Code](https://img.shields.io/badge/VS_Code-1.85%2B-007ACC.svg?logo=visualstudiocode&logoColor=white)](https://code.visualstudio.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/gospelo-dev/kata/blob/main/LICENSE.md)
[![KATA Markdown](https://img.shields.io/badge/Format-KATA_Markdown-00bcd4.svg)](https://github.com/gospelo-dev/kata)
[![Linter](https://img.shields.io/badge/Category-Linter-4caf50.svg)](#features)

[gospelo-kata](https://github.com/gospelo-dev/kata) の VSCode 拡張機能です。KATA Markdown テンプレート (`.kata.md`) のリアルタイム lint、シンタックスハイライト、ホバー情報、プレビューを提供します。

[Japanese / 日本語](README.ja.md)

---

## Features

### Lint

- **Auto Lint** — `gospelo-kata lint` をファイル保存・オープン時に自動実行
- **Inline Diagnostics** — エラー箇所にインライン波線 + Problems パネルに表示
- **Template & Document Mode** — テンプレート (`_tpl.kata.md`) とレンダリング済みドキュメント (`.kata.md`) の両方を検証

### Syntax Highlighting

- `{{ variable }}` — 変数補間
- `{% for %}` / `{% if %}` — 制御構文
- `{#schema ... #}` / `{#prompt ... #}` / `{#data ... #}` — Kata ブロック

### Hover Information

- `data-kata` 属性にホバーするとスキーマパスとバインディング情報を表示

### Preview CSS

- KATA Markdown 専用のプレビュースタイルを提供
- `kata-card` テーブルレイアウト、`kata-badge` ステータスバッジの表示

---

## Requirements

- [VS Code](https://code.visualstudio.com/) 1.85+
- Python 3.11+
- [gospelo-kata](https://github.com/gospelo-dev/kata) CLI

```bash
pip install gospelo-kata
```

---

## Lint Rules

### Template Mode (`.kata.md`)

| Code | Level | Description |
|------|-------|-------------|
| S000 | info | No schema defined |
| S001 | error | Invalid JSON in schema block |
| S002 | error | Schema is not a JSON object |
| S003 | warning | Schema missing `type` field |
| S004 | error | Schema file not found |
| T001 | error | Unclosed `{% for %}` / `{% if %}` |
| T002 | error | `{% elif %}` without matching `{% if %}` |
| T003 | error | `{% else %}` without matching `{% if %}` / `{% for %}` |
| T004 | error | `{% endif %}` without matching `{% if %}` |
| T005 | error | `{% endfor %}` without matching `{% for %}` |
| T006 | warning | Unknown block tag |
| F001 | error | Unknown filter name |
| V001 | warning | Variable not found in schema properties |
| V002 | info | Unused schema properties |

### Document Mode (`.md`)

| Code | Level | Description |
|------|-------|-------------|
| D001 | error | Schema not found |
| D002 | error | Required section (`## Heading`) missing |
| D003 | warning | Table column count mismatch |
| D004 | warning | Empty section |
| D005 | warning | Annotation link target not in schema |
| D006 | info | Schema properties with no links |

---

## Extension Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `kataLint.pythonPath` | `"python"` | Path to the Python interpreter |
| `kataLint.lintOnSave` | `true` | Run lint on file save |
| `kataLint.lintOnOpen` | `true` | Run lint on file open |
| `kataLint.severity.info` | `"Information"` | Severity level for info messages |

---

## VSCode Setup

gospelo-kata CLI でタスク設定を自動生成できます:

```bash
gospelo-kata init-vscode --output .vscode/
```

詳細は [VSCode 連携ガイド](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/vscode-integration.md) を参照してください。

---

## License

MIT — See [LICENSE.md](https://github.com/gospelo-dev/kata/blob/main/LICENSE.md)
