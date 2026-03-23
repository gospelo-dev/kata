# KATA Markdown™ フォーマット仕様

`.kata.md` ファイルの記法リファレンス。

---

## ソースファイル構造

````markdown
**Prompt**

```yaml
(AI 向け説明)
```

(Jinja2 テンプレート本文)

<details>
<summary>Specification</summary>

**Schema**

```yaml
(YAML shorthand スキーマ)
```

**Data**

```yaml
(YAML データ)
```

</details>
````

推奨レイアウト: Prompt → テンプレート本文 → Schema + Data (`<details>` 内)

---

## スキーマブロック

YAML shorthand 記法でデータ型を定義。

| 記法 | 意味 |
|------|------|
| `string` | 任意文字列 |
| `string!` | 必須文字列 |
| `integer`, `number`, `boolean` | 型付き値 |
| `int`, `float`, `bool`, `str` | エイリアス |
| `enum(a, b, c)` | 列挙型 |
| `string[]` | 文字列配列 |
| `items[]!:` | 必須オブジェクト配列 (子をインデントで記述) |
| `integer\|integer[]!` | union 型 (`oneOf` に展開) |

ネストはインデントで表現:

```yaml
categories[]!:
  id: string!
  items[]!:
    id: string!
    status: enum(draft, pending, approve, reject)
    tags: string[]
```

---

## テンプレート本文 (Jinja2 サブセット)

### 変数・ループ・条件分岐

```markdown
# {{ title }}

{% for item in items %}| {{ item.id }} | {{ item.name }} |
{% endfor %}

{% if version %}Version: {{ version }}{% endif %}
```

### 組み込みフィルター

| フィルター | 例 |
|-----------|-----|
| `default(v)` | `{{ x \| default("N/A") }}` |
| `join(sep)` | `{{ tags \| join(", ") }}` |
| `length` | `{{ items \| length }}` |
| `upper` / `lower` / `title` | `{{ name \| upper }}` |
| `trim` | `{{ text \| trim }}` |
| `first` / `last` | `{{ items \| first }}` |
| `replace(old, new)` | `{{ s \| replace("_", "-") }}` |
| `int` / `float` | `{{ val \| int }}` |
| `sort` / `reverse` / `unique` | `{{ items \| sort }}` |
| `truncate(len)` | `{{ desc \| truncate(100) }}` |
| `e` / `escape` | `{{ html \| e }}` |
| `tojson` | `{{ data \| tojson }}` |

---

## レンダリング出力

`build` (または `render`) が生成する出力:

- `<span data-kata="p-{path}">value</span>` — データバインディング
- `<div data-kata-each="collection">` — ループマーカー
- `<details>` セクションに Prompt + Template + Schema + Data を格納

HTML タグはデータ値内で自動エスケープ。`extract` 時に復元。

---

## ラウンドトリップ

```
ソース (.kata.md)  → render →  出力 (.kata.md)  → extract →  JSON データ
```

`extract` は `data-kata` span の値と Specification の構造情報から JSON を復元。
