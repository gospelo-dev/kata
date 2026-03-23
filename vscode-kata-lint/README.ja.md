# KATA Markdown™ Language Support

[![VS Code](https://img.shields.io/badge/VS_Code-1.85%2B-007ACC.svg?logo=visualstudiocode&logoColor=white)](https://code.visualstudio.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/gospelo-dev/kata/blob/main/LICENSE.md)
[![KATA Markdown](https://img.shields.io/badge/Format-KATA_Markdown-00bcd4.svg)](https://github.com/gospelo-dev/kata)
[![Linter](https://img.shields.io/badge/Category-Linter-4caf50.svg)](#機能)
[![Marketplace](https://img.shields.io/badge/VS_Marketplace-gospelo.kata--lint-007ACC.svg?logo=visualstudiocode)](https://marketplace.visualstudio.com/items?itemName=gospelo.kata-lint)

[gospelo-kata](https://github.com/gospelo-dev/kata) の VSCode 拡張機能です。KATA Markdown™ (`.kata.md`) のリアルタイム lint、LiveMorph 双方向同期、ホバー情報、プレビューを提供します。

[English](https://github.com/gospelo-dev/kata/blob/main/vscode-kata-lint/README.md)

---

## 機能

### Lint

- **自動 Lint** — ファイル保存・オープン時に `gospelo-kata lint` を自動実行
- **エディタ内表示** — エラー箇所にインライン波線 + Problems パネルに一覧表示
- **テンプレート & ドキュメントモード** — テンプレートとレンダリング済みドキュメントの両方を検証

### LiveMorph (双方向同期)

![LiveMorph Concept](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/images/livemorph-concept.jpg?raw=true)

- **コンテキストメニュー** — 右クリックで Sync to HTML / Sync to Data / Sync OFF / Lint File
- **ステータスバー** — 現在の同期モードを常時表示、クリックで QuickPick 切替
- **保存時自動同期** — `syncOnSave` 設定で Data → HTML または HTML → Data を自動実行

### ホバー情報

- `data-kata` 属性にホバーするとスキーマパス・型情報・enum 許可値を表示

### プレビュー CSS

- KATA Markdown™ 専用のプレビュースタイル (`kata-card` テーブルレイアウト、ステータスカラー)

---

## 必要要件

- [VS Code](https://code.visualstudio.com/) 1.85+
- Python 3.11+
- [gospelo-kata](https://github.com/gospelo-dev/kata) CLI

```bash
pip install gospelo-kata
```

---

## 拡張機能の設定

| Setting | Default | 説明 |
|---------|---------|------|
| `kataLint.pythonPath` | `"python"` | Python インタープリタのパス |
| `kataLint.lintOnSave` | `true` | 保存時の自動 Lint |
| `kataLint.lintOnOpen` | `true` | オープン時の自動 Lint |
| `kataLint.syncOnSave` | `"off"` | 保存時の同期モード (`"off"` / `"toHtml"` / `"toData"`) |
| `kataLint.severity.info` | `"Information"` | info レベルの表示方法 |
| `kataLint.exclude` | `[]` | 除外パターン (glob) |

---

## Lint ルール

詳細は [Lint ルール一覧](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/lint-rules.md) を参照。

### セキュリティ

| Code | 説明 |
|------|------|
| P002 | プロンプトインジェクション検出 — ロール上書き、命令上書き、コマンド実行、資格情報アクセス |
| D016 | `data-kata` span 内の HTML インジェクション検出 (XSS 防止) |
| D017 | 構造整合性ハッシュ検証 — レンダリング後の Prompt・Schema・テンプレート本体の改ざんを検出 |

---

## 関連ドキュメント

- [VS Code 連携ガイド](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/vscode.md)
- [LiveMorph ガイド](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/livemorph.md)
- [テンプレートパッケージ](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/katar.md)

---

## ライセンス

MIT — [LICENSE.md](https://github.com/gospelo-dev/kata/blob/main/LICENSE.md) を参照
