# テンプレートパッケージ (.katatpl)

カスタムテンプレートの作成・パッケージ化・配布方法。

---

## 概要

`.katatpl` は gospelo-kata のテンプレートパッケージフォーマットです。中身は標準的な ZIP 形式で、テンプレートに必要なファイル一式を1つのファイルにまとめます。

展開せずそのまま `./templates/` に配置するだけで、`assemble`、`show-schema`、`show-prompt` などすべてのコマンドから利用できます。

**設計原則: 1パッケージ = 1テンプレート = 1スキーマ**

AI がスキーマを1つ読めばデータを生成できるよう、パッケージには1つのテンプレート（`_tpl.kata.md`）のみ含めます。複数テンプレートのデータを結合して Excel 等を生成する場合は、`generate` コマンドのオプション（`--prereq` 等）で対応します。

---

## テンプレートの構成

テンプレートディレクトリに必要なファイル:

```
my_template/
├── manifest.json             # マニフェスト (必須)
├── my_template_tpl.kata.md   # テンプレート本体 (必須)
└── images/                   # 画像ファイル (任意)
```

### 追加ファイル

テンプレートディレクトリには `manifest.json` と `_tpl.kata.md` 以外に**画像ファイル**を含めることができます。

許可される画像形式: `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`, `.ico`, `.bmp`

用途の例:

- **ロゴ・アイコン** — ドキュメントに埋め込む画像アセット
- **図表・スクリーンショット** — テンプレートの補足資料

> **セキュリティ:** パッケージに含められるファイルはテンプレートと画像のみに制限されています。

---

## manifest.json

テンプレートのメタデータを定義するファイル。`pack` コマンドでパッケージ化する際に必須です。

```json
{
  "name": "my_template",
  "version": "1.0.0",
  "description": "Task list with status tracking",
  "author": "your-name",
  "url": "https://github.com/your-org/your-repo",
  "license": "MIT",
  "template": "my_template_tpl.kata.md",
  "requires": []
}
```

### フィールド

| フィールド | 必須 | 説明 |
|-----------|:----:|------|
| `name` | Yes | テンプレート名（コマンドで使用する識別子） |
| `version` | Yes | セマンティックバージョニング |
| `template` | Yes | テンプレート本体のファイル名 |
| `description` | No | テンプレートの説明文 |
| `author` | No | 作者名 |
| `url` | No | リポジトリやドキュメントの URL |
| `license` | No | ライセンス形式 (MIT, Apache-2.0 等) |
| `requires` | No | 依存する他テンプレート名の配列 |

### `requires` — テンプレート間の依存関係

複数テンプレートのデータを組み合わせて1つの成果物（Excel 等）を生成する場合、`requires` に依存先のテンプレート名を記述します。

```json
{
  "name": "test_spec",
  "requires": ["test_prereq"]
}
```

`show-schema` や `show-prompt` 実行時に依存情報が表示され、AI は必要なテンプレートすべてのデータを生成できます:

```
$ gospelo-kata show-schema test_spec
...
Requires: test_prereq
  → gospelo-kata show-schema test_prereq
```

### `pack-init` でテンプレートを新規作成

```bash
gospelo-kata pack-init ./my_template/
```

以下の構成が自動生成されます:

```
my_template/
├── manifest.json             # マニフェスト (自動生成)
├── my_template_tpl.kata.md   # テンプレート本体 (空の雛形)
├── images/                   # 画像ファイル配置先 (任意)
└── outputs/                  # レンダリング出力先
```

既存ディレクトリに対して実行した場合は、`_tpl.kata.md` ファイルを自動検出して `manifest.json` の雛形を生成します。

---

## テンプレート本体 (`_tpl.kata.md`)

`{#schema}`、`{#prompt}`、Jinja2 互換テンプレートを含むファイル。ファイル名は `manifest.json` の `template` フィールドで指定します。

```markdown
{#schema
title: string!
version: string
items[]!:
  id: string!
  name: string!
  status: enum(draft, done)
#}

{#prompt
このテンプレートはタスクリストを生成します。
items 配列に各タスクの詳細を記述してください。
status は draft または done を指定してください。
#}

{#data
#}

# {{ title }}

> Version: {{ version }}

| ID | タスク | ステータス |
|----|--------|:----------:|
{% for item in items %}| {{ item.id }} | {{ item.name }} | {{ item.status }} |
{% endfor %}
```

**ポイント:**

- `{#schema}` — AI がデータ構造を理解するためのスキーマ定義
- `{#prompt}` — AI がデータ生成時に参照する説明文
- `{#data ... #}` — `assemble` コマンドがデータを挿入する位置（空でも記述推奨）
- テンプレート本文 — Jinja2 互換構文で記述

---

## パッケージ化

`.katatpl` の作成は `gospelo-kata pack` コマンドのみで行います。手動で ZIP ファイルを作成・リネームしないでください。

### 手順

```bash
# 1. テンプレートの雛形を生成
gospelo-kata pack-init ./my_template/

# 2. テンプレート本体を編集
#    my_template/my_template_tpl.kata.md に {#schema}, {#prompt}, テンプレートを記述

# 3. manifest.json を編集
#    author, url, license 等を記入

# 4. パッケージ化
gospelo-kata pack ./my_template/
```

`my_template.katatpl` が生成されます。

出力先を指定する場合:

```bash
gospelo-kata pack ./my_template/ -o ./dist/my_template.katatpl
```

### バリデーション

`pack` コマンドは以下を検証します:

- `manifest.json` が存在すること
- `name`, `version`, `template` フィールドがあること
- `template` で指定されたファイルが存在すること

---

## インストール

### `init --from-package` でインストール

```bash
gospelo-kata init --from-package my_template.katatpl
```

`./templates/my_template.katatpl` にコピーされます（展開されません）。

### 手動配置

`.katatpl` ファイルを直接 `./templates/` にコピーしても動作します:

```bash
cp my_template.katatpl ./templates/
```

---

## 使い方

インストール後は組み込みテンプレートと同じように利用できます:

```bash
# テンプレート一覧で確認（バージョンも表示されます）
gospelo-kata templates

# スキーマ確認
gospelo-kata show-schema my_template --format yaml

# AI プロンプト確認
gospelo-kata show-prompt my_template

# データ作成 → アセンブル → レンダリング
gospelo-kata assemble --type my_template --data data.yml
gospelo-kata render my_template_tpl.kata.md -o outputs/my_template.kata.md
gospelo-kata lint outputs/my_template.kata.md
```

---

## テンプレートの検索順序

コマンド実行時のテンプレート検索順序:

1. **ローカル** `./templates/{name}/` (ディレクトリ)
2. **ローカル** `./templates/{name}.katatpl` (パッケージ)
3. **ビルトイン** `gospelo_kata/templates/{name}/` (ディレクトリ)
4. **ビルトイン** `gospelo_kata/templates/{name}.katatpl` (パッケージ)

ローカルに同名のテンプレートがあれば、ビルトインより優先されます。

---

## テンプレート作成のベストプラクティス

### スキーマ設計

- 必須フィールドには `!` を付ける (`string!`, `items[]!:`)
- enum で選択肢を制限する (`enum(draft, pending, approve, reject)`)
- `name_ja` フィールドを用意して多言語対応に備える

### プロンプト設計

- テンプレートの目的を簡潔に説明する
- 各フィールドの意味と制約を記述する
- AI が迷わないよう具体例を含める

### テスト

パッケージ化の前にテンプレートが正しく動作するか確認:

```bash
# テストデータでアセンブル
gospelo-kata assemble --type my_template --data test_data.yml

# レンダリング + lint
gospelo-kata render my_template_tpl.kata.md -o outputs/test.kata.md
gospelo-kata lint outputs/test.kata.md

# ラウンドトリップ確認
gospelo-kata extract outputs/test.kata.md
```

---

## 配布

`.katatpl` ファイルは以下の方法で配布できます:

- **Git リポジトリ** — プロジェクトの `templates/` に含める
- **ファイル共有** — Slack、メール等で直接送付
- **社内パッケージレジストリ** — Artifactory 等に保管

`.katatpl` は単一ファイルなので、どの方法でも簡単に配布できます。

---

## セキュリティ

安全対策として、テンプレートは**ユーザーが明示的に許可したもの**のみ AI ワークフロー（`assemble` コマンド等）で使用できます。

### テンプレートの信頼管理

- 初めて使用するテンプレートは、`{#prompt}` の内容が表示され、ユーザーの確認が求められます
- 許可すると `.template_trust.json` に記録され、以降は確認なしで利用できます
- テンプレートの `{#prompt}` が変更された場合、再度確認が必要になります

```bash
# プロンプト内容と信頼状態を確認
gospelo-kata show-prompt my_template

# assemble 時に未許可テンプレートは確認を求められる
gospelo-kata assemble --type my_template --data data.yml
```

### パッケージのファイル制限

パッケージに含められるファイルは以下のみに制限されています:

- `manifest.json`
- `*_tpl.kata.md` (テンプレート本体)
- 画像ファイル (`.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`, `.ico`, `.bmp`)

上記以外のファイルは `pack` コマンドで拒否され、読み込み時もアクセスできません。

### パッケージのサイズ制限

悪意あるパッケージからの保護として、以下のサイズ制限が適用されます:

| 制限項目 | 上限値 |
|---------|--------|
| ファイル数 | 100 ファイル |
| 単一ファイルサイズ | 10 MB |
| 合計展開サイズ | 50 MB |

制限を超えるパッケージはエラーとなり、読み込まれません。
