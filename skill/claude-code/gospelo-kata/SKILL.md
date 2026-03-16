---
name: gospelo-kata
description: KATA Markdown ドキュメントの生成・検証・編集
---

# /gospelo-kata — AI Native ドキュメント生成ツールキット

KATA Markdown™ テンプレートから構造化ドキュメントを生成するツール。
テンプレートに埋め込まれた `{#prompt}` と `{#schema}` をAIが読み取り、自律的にドキュメントを生成できます。

## 前提条件

`gospelo-kata` パッケージがインストール済みであること。

```bash
pip install gospelo-kata
```

---

## AI ドキュメント生成ワークフロー

AIがテンプレートを理解してドキュメントを生成する手順:

### 1. テンプレート選択

```bash
python -m gospelo_kata.cli templates
```

利用可能なテンプレートと、schema/prompt の有無を確認します。

### 2. テンプレートの理解

```bash
# プロンプト（テンプレートの使い方説明）を取得
python -m gospelo_kata.cli show-prompt {template_name}

# スキーマ（JSON Schema）を取得
python -m gospelo_kata.cli show-schema {template_name}
python -m gospelo_kata.cli show-schema {template_name} --format yaml
```

**重要**: 必ず show-prompt と show-schema の両方を読み、テンプレートの仕様を理解してからデータを生成すること。

### 3. JSON データ生成

show-schema で取得したスキーマに従い、ユーザーの要件をもとに JSON データを作成します。

- required フィールドは必ず含める
- enum フィールドは許可値のみ使用
- `status` の初期値は `"draft"`

### 4. バリデーション

```bash
python -m gospelo_kata.cli validate {json_file}
```

### 5. ドキュメント生成

```bash
# Markdown (stdout)
python -m gospelo_kata.cli generate {json_file} --format markdown

# Markdown (ファイル出力)
python -m gospelo_kata.cli generate {json_file} --format markdown --output output.kata.md

# Excel
python -m gospelo_kata.cli generate {json_file} --format excel --output output.xlsx
```

### 6. Lint 検証

```bash
python -m gospelo_kata.cli lint {output.kata.md}
```

### 7. 修正ループ

Lint エラーがある場合:
1. エラー内容を分析
2. JSON データを修正
3. 再度バリデーション・生成・Lint を実行
4. エラーが 0 になるまで繰り返す

---

## コマンド一覧

| コマンド | 説明 |
|---------|------|
| `templates` | テンプレート一覧（schema/prompt 有無表示） |
| `show-prompt {name}` | テンプレートの `{#prompt}` を表示 |
| `show-schema {name}` | テンプレートのスキーマを JSON Schema で表示 |
| `validate {file}` | JSON ファイルをスキーマ検証 |
| `generate {file}` | JSON からドキュメント生成 |
| `lint {file}` | .kata.md ファイルの Lint 検証 |
| `init --type {name}` | テンプレートから雛形を初期化 |
| `edit {file}` | ブラウザエディターで JSON 編集 |
| `infer-schema {file}` | テンプレートからスキーマ推論 |
| `schemas` | 利用可能なスキーマ一覧 |

---

## テンプレート仕様（KATA Markdown v2）

### スキーマブロック

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
#}
```

- `string!` — 必須の文字列
- `enum(a, b)` — 許可値の列挙
- `items[]!` — 必須の配列（子はオブジェクト）
- `string[]` — 文字列の配列

### プロンプトブロック

```markdown
{#prompt
テンプレートの使い方をAI向けに説明するブロック。
レンダリング時は自動的に除去される。
#}
```

### データ属性

```html
<span data-kata="p-categories-items-status">draft</span>
```

`data-kata` 属性でスキーマプロパティへの参照を表現。VSCode 拡張でホバー時に型情報を表示。

---

## 注意事項

- テンプレートの `{#prompt}` に記載された規約に従うこと
- `data-kata` 属性はテンプレートエンジンが自動付与（手動不要）
- Schema Reference セクションも自動生成（手動不要）
- Excel 生成には `openpyxl` が必要
- YAML スキーマには `PyYAML` が必要
