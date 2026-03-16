---
name: gospelo-kata
description: KATA Markdown ドキュメントの生成・検証・編集
---

# gospelo-kata — AI Native ドキュメント生成ツールキット

KATA Markdown™ テンプレートから構造化ドキュメント (Markdown / Excel) を生成するツール。
テンプレートに埋め込まれた `{#prompt}` (AI向け説明) と `{#schema}` (型定義) を読み取り、自律的にドキュメントを生成できます。

## 前提条件

`gospelo-kata` パッケージがインストール済みであること。

```bash
pip install gospelo-kata
```

---

## AI ドキュメント生成ワークフロー

### Step 1: テンプレート選択

```bash
gospelo-kata templates
```

出力例:
```
Available templates:
  agenda               Meeting agenda with decisions and action items [schema]
  checklist            Structured checklist with categories... [schema, prompt]
  test_spec            Test specification with prerequisites...
```

`[schema, prompt]` タグのあるテンプレートが AI 生成に対応しています。

### Step 2: テンプレートの仕様を取得

```bash
# テンプレートの使い方説明を取得
gospelo-kata show-prompt {template_name}

# データ構造 (JSON Schema) を取得
gospelo-kata show-schema {template_name}
gospelo-kata show-schema {template_name} --format yaml
```

**重要**: 必ず show-prompt と show-schema の両方を読み、テンプレートの仕様を理解してからデータを生成してください。

### Step 3: `_tpl.kata.md` ファイルを作成

テンプレートの `{#schema}` と `{#prompt}` に従い、`{#data}` ブロックにYAMLデータを埋め込んだ `_tpl.kata.md` ファイルを作成します。

```markdown
{#schema
version: string!
description: string!
items[]!:
  id: string!
  name: string!
#}

{#data
version: "1.0"
description: My Document
items:
  - id: "1"
    name: Item One
#}

# {{ description }}

{% for item in items %}
- {{ item.id }}. {{ item.name }}
{% endfor %}
```

ルール:
- `!` 付きフィールドは必須
- `enum()` フィールドは許可値のみ使用する
- `status` の初期値は `"draft"` とする
- 日本語コンテンツでは `name_ja` フィールドを必ず設定する

### Step 4: レンダリング

```bash
# Markdown 出力
gospelo-kata render my_template_tpl.kata.md -o outputs/my_template.kata.md

# Lint 検証
gospelo-kata lint outputs/my_template.kata.md
```

### Step 5: Excel 生成 (オプション)

```bash
gospelo-kata generate data.json --format excel --output output.xlsx
```

### Step 6: 修正ループ

Lint エラーがある場合:
1. エラー内容を確認
2. `_tpl.kata.md` の `{#data}` またはテンプレートを修正
3. Step 4 を再実行
4. エラーが 0 になるまで繰り返す

---

## コマンドリファレンス

| コマンド | 説明 |
|---------|------|
| `templates` | テンプレート一覧（schema/prompt 有無表示） |
| `show-prompt {name}` | テンプレートの `{#prompt}` を表示 |
| `show-schema {name}` | テンプレートのスキーマを JSON Schema で表示 |
| `render {file}` | `_tpl.kata.md` をレンダリングして `.kata.md` を生成 |
| `lint {file}` | .kata.md ファイルの Lint 検証 |
| `extract {file}` | レンダリング済み `.kata.md` からデータを抽出 |
| `init --type {name}` | テンプレートから雛形を初期化 |
| `validate {file}` | JSON ファイルをスキーマ検証 |
| `generate {file}` | JSON からドキュメント生成 |
| `edit {file}` | ブラウザエディターで JSON 編集 |
| `infer-schema {file}` | テンプレートからスキーマ推論 |
| `schemas` | 利用可能なスキーマ一覧 |

全コマンドは `gospelo-kata {command}` で実行します。

---

## テンプレート仕様 (KATA Markdown v2)

### ファイル命名規則

- `*_tpl.kata.md` — テンプレートソース（`{#schema}` + `{#data}` + Jinja テンプレート）
- `*.kata.md` — レンダリング済み出力（`data-kata` 属性付き）

### スキーマブロック `{#schema ... #}`

YAML shorthand でデータ型を定義:

```markdown
{#schema
version: string!
description: string!
categories[]!:
  id: string!
  name: string!
  items[]!:
    id: string!
    status: enum(draft, pending, approve, reject)
    tags: string[]
    auto: enum(full, semi, partial, manual)
    enabled: boolean
#}
```

- `string!` — 必須文字列
- `string` — オプション文字列
- `integer` — 整数
- `number` — 数値
- `boolean` — 真偽値
- `enum(a, b)` — 許可値の列挙
- `items[]!` — 必須オブジェクト配列
- `string[]` — 文字列配列

### プロンプトブロック `{#prompt ... #}`

AI 向けのテンプレート説明。レンダリング時は自動除去されます。

### データブロック `{#data ... #}`

YAML 形式でデータを埋め込み。レンダリング時にテンプレートへ注入されます。

### データ属性 `data-kata`

```html
<span data-kata="p-categories-items-status">draft</span>
```

スキーマプロパティへの参照を表現。テンプレートエンジンが自動付与するため手動記述は不要です。

---

## ワークフロー例

### チェックリストの作成

```bash
# 1. テンプレートから初期化
gospelo-kata init --type checklist --output ./guides/

# 2. _tpl.kata.md の {#data} ブロックを編集

# 3. レンダリング
gospelo-kata render guides/templates/checklist_tpl.kata.md -o guides/outputs/checklist.kata.md

# 4. Lint 検証
gospelo-kata lint guides/outputs/checklist.kata.md
```

---

## 注意事項

- `data-kata` 属性と Schema Reference セクションはテンプレートエンジンが自動生成（手動不要）
- テンプレートの `{#prompt}` に記載された規約に従うこと
- Excel 生成には `openpyxl` が必要
- YAML スキーマには `PyYAML` が必要
