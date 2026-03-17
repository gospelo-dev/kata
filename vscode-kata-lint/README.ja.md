# KATA Markdown™ Language Support

[![VS Code](https://img.shields.io/badge/VS_Code-1.85%2B-007ACC.svg?logo=visualstudiocode&logoColor=white)](https://code.visualstudio.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/gospelo-dev/kata/blob/main/LICENSE.md)
[![KATA Markdown](https://img.shields.io/badge/Format-KATA_Markdown-00bcd4.svg)](https://github.com/gospelo-dev/kata)
[![Linter](https://img.shields.io/badge/Category-Linter-4caf50.svg)](#機能)
[![Marketplace](https://img.shields.io/badge/VS_Marketplace-gospelo.kata--lint-007ACC.svg?logo=visualstudiocode)](https://marketplace.visualstudio.com/items?itemName=gospelo.kata-lint)

[gospelo-kata](https://github.com/gospelo-dev/kata) の VSCode 拡張機能です。KATA Markdown™ テンプレート (`.kata.md`) のリアルタイム lint、シンタックスハイライト、ホバー情報、プレビューを提供します。

[English](https://github.com/gospelo-dev/kata/blob/main/vscode-kata-lint/README.md)

---

## 機能

### Lint

- **自動 Lint** — `gospelo-kata lint` をファイル保存・オープン時に自動実行
- **エディタ内表示** — エラー箇所にインライン波線 + Problems パネルに一覧表示
- **テンプレート & ドキュメントモード** — テンプレート (`_tpl.kata.md`) とレンダリング済みドキュメント (`.kata.md`) の両方を検証

### シンタックスハイライト

- `{{ variable }}` — 変数補間
- `{% for %}` / `{% if %}` — 制御構文
- `{#schema ... #}` / `{#prompt ... #}` / `{#data ... #}` — Kata ブロック

### ホバー情報

- `data-kata` 属性にホバーするとスキーマパスとバインディング情報を表示

### プレビュー CSS

- KATA Markdown™ 専用のプレビュースタイルを提供
- `kata-card` テーブルレイアウト、ステータススタイリング

---

## 必要要件

- [VS Code](https://code.visualstudio.com/) 1.85+
- Python 3.11+
- [gospelo-kata](https://github.com/gospelo-dev/kata) CLI

```bash
pip install gospelo-kata
```

---

## Lint チェック項目

### テンプレートモード (`.kata.md`)

| Code | Level | 説明 |
|------|-------|------|
| S000 | info | スキーマ未定義 |
| S001 | error | スキーマブロック内の JSON が不正 |
| S002 | error | スキーマが JSON オブジェクトでない |
| S003 | warning | スキーマに `type` フィールドがない |
| S004 | error | 参照先のスキーマファイルが見つからない |
| T001 | error | `{% for %}` / `{% if %}` が閉じられていない |
| T002 | error | `{% elif %}` に対応する `{% if %}` がない |
| T003 | error | `{% else %}` に対応する `{% if %}` / `{% for %}` がない |
| T004 | error | `{% endif %}` に対応する `{% if %}` がない |
| T005 | error | `{% endfor %}` に対応する `{% for %}` がない |
| T006 | warning | 不明なブロックタグ |
| F001 | error | 不明なフィルター名 |
| V001 | warning | スキーマプロパティに存在しない変数参照 |
| V002 | info | テンプレートで使用されていないスキーマプロパティ |

### ドキュメントモード (`.md`)

| Code | Level | 説明 |
|------|-------|------|
| D001 | error | 指定されたスキーマが見つからない |
| D002 | error | 必須セクション (`## Heading`) が欠落 |
| D003 | warning | テーブルのカラム数が不一致 |
| D004 | warning | 空のセクション |
| D005 | warning | アノテーションリンクのリンク先がスキーマに存在しない |
| D006 | info | スキーマプロパティにリンクがない |

---

## 拡張機能の設定

| Setting | Default | 説明 |
|---------|---------|------|
| `kataLint.pythonPath` | `"python"` | Python インタープリタのパス |
| `kataLint.lintOnSave` | `true` | 保存時の自動 Lint |
| `kataLint.lintOnOpen` | `true` | オープン時の自動 Lint |
| `kataLint.severity.info` | `"Information"` | info レベルの表示方法 |

---

## VSCode セットアップ

gospelo-kata CLI でタスク設定を自動生成できます:

```bash
gospelo-kata init-vscode --output .vscode/
```

詳細は [VSCode 連携ガイド](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/vscode-integration.md) を参照してください。

---

## ライセンス

MIT — [LICENSE.md](https://github.com/gospelo-dev/kata/blob/main/LICENSE.md) を参照
