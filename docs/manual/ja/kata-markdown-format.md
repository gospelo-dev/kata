# KATA Markdown™ フォーマット仕様

`.kata.md` ファイルの記法リファレンス。

---

## ソースファイル構造

ソース `.kata.md` は 3 つのブロックで構成されます:

```markdown
{#schema
(YAML shorthand によるスキーマ定義)
#}

{#data
(YAML によるデータ)
#}

(Jinja2 テンプレート本文)
```

オプションで `{#prompt}` ブロック (AI 向け説明) も記述可能です。

---

## スキーマブロック `{#schema ... #}`

YAML shorthand 記法でデータ型を定義します。

```yaml
{#schema
title: string!
version: string
categories[]!:
  id: string!
  name: string!
  items[]!:
    id: string!
    status: enum(draft, pending, approve, reject)
    tags: string[]
#}
```

### 型記法

| 記法 | 意味 | JSON Schema 変換 |
|------|------|-----------------|
| `string` | 任意文字列 | `{"type": "string"}` |
| `string!` | 必須文字列 | `{"type": "string"}` + required |
| `int` | 整数 | `{"type": "integer"}` |
| `number` | 数値 | `{"type": "number"}` |
| `boolean` | 真偽値 | `{"type": "boolean"}` |
| `enum(a, b, c)` | 列挙型 | `{"type": "string", "enum": ["a","b","c"]}` |
| `string[]` | 文字列配列 | `{"type": "array", "items": {"type": "string"}}` |
| `items[]!:` | 必須オブジェクト配列 | `{"type": "array", "items": {"type": "object", ...}}` + required |
| `items[]:` | 任意オブジェクト配列 | 同上 (required なし) |

### ネスト

インデントでオブジェクト/配列のネストを表現:

```yaml
categories[]!:
  id: string!
  items[]!:
    id: string!
    name: string!
```

---

## データブロック `{#data ... #}`

テンプレートに渡すデータを YAML で定義します。

```yaml
{#data
title: セキュリティチェック
categories:
  - id: CAT-01
    name: 入力検証
    items:
      - id: SEC-01
        name: SQLインジェクション
        status: draft
        tags:
          - web
          - database
#}
```

---

## プロンプトブロック `{#prompt ... #}`

AI がデータ生成時に参照する説明文。レンダリング時に自動除去されます。

```markdown
{#prompt
このテンプレートはセキュリティテスト仕様書を生成します。
test_cases 配列に各テストケースの詳細を記述してください。
priority は high/medium/low のいずれかです。
#}
```

---

## テンプレート本文 (Jinja2 サブセット)

### 変数展開

```markdown
# {{ title }}

> Version: {{ version | default("1.0") }}
```

### ループ

```markdown
{% for item in items %}| {{ item.id }} | {{ item.name }} |
{% endfor %}
```

### 条件分岐

```markdown
{% if version %}Version: {{ version }}{% endif %}
{% if priority == "high" %}**重要**{% elif priority == "medium" %}注意{% else %}通常{% endif %}
```

### 組み込みフィルター

| フィルター | 説明 | 例 |
|-----------|------|-----|
| `default(v)` | デフォルト値 | `{{ x \| default("N/A") }}` |
| `join(sep)` | 配列結合 | `{{ tags \| join(", ") }}` |
| `length` | 要素数 | `{{ items \| length }}` |
| `upper` / `lower` / `title` | 大文字変換 | `{{ name \| upper }}` |
| `trim` | 空白除去 | `{{ text \| trim }}` |
| `first` / `last` | 先頭/末尾 | `{{ items \| first }}` |
| `replace(old, new)` | 置換 | `{{ s \| replace("_", "-") }}` |
| `int` / `float` | 型変換 | `{{ val \| int }}` |
| `sort` / `reverse` / `unique` | ソート等 | `{{ items \| sort }}` |
| `truncate(len)` | 切り詰め | `{{ desc \| truncate(100) }}` |
| `e` / `escape` | HTML エスケープ | `{{ html \| e }}` |
| `tojson` | JSON 化 | `{{ data \| tojson }}` |

---

## レンダリング出力フォーマット

`gospelo-kata render` が生成する出力の構造。

### data-kata 属性

テンプレート変数は `<span data-kata="p-{property-path}">` でラップされます:

```html
<span data-kata="p-title">セキュリティチェック</span>
```

ネストされたプロパティのアンカーパスは `-` で連結:

```html
<span data-kata="p-categories-items-status">draft</span>
```

### data-kata-each ループマーカー

配列のループ開始位置に `<div data-kata-each="collection_name">` が挿入されます:

```html
<div data-kata-each="test_cases"></div>
| <span data-kata="p-test-cases-test-id">TC-01</span> | ...
```

### HTML サニタイズ

データ値に含まれる HTML タグは自動エスケープされます:

- ソースデータ: `<script>alert(1)</script>`
- 出力: `&lt;script&gt;alert(1)&lt;/script&gt;`
- extract 時: `<script>alert(1)</script>` に復元

### Schema Reference セクション

出力末尾に `<details>` で Schema と Data が付与されます:

```html
---

<details>
<summary>Schema Reference</summary>

**Schema**

```yaml
title: string!
items[]!:
  id: string!
  name: string!
```

**Data**

```yaml
title: セキュリティチェック
items:
- id: SEC-01
  name: SQLインジェクション
```

</details>
```

この構造により、単一の `.kata.md` ファイルからテンプレートの再構築が可能です:
- `data-kata` span → 変数バインディング
- `data-kata-each` div → ループ構造
- Schema → 型定義
- Data → 元データ

---

## ラウンドトリップ

```
ソース (.kata.md)
  ├── {#schema} + {#data} + Jinja テンプレート
  ↓ render
出力 (.kata.md)
  ├── data-kata span + data-kata-each div
  ├── <details> Schema + Data
  ↓ extract
JSON データ (元データと同等)
```

`extract` は `data-kata` span の値と Schema Reference の配列構造情報を使って JSON を復元します。HTML エンティティ (`&lt;` 等) は自動的に元の文字 (`<`) に戻されます。
