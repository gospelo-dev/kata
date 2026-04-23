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

### ローカル変数 — `{% set %}`

`{% set name = expr %}` でローカル変数を束縛できます。別配列の要素を
毎回検索する代わりに一度だけ引いておく、派生値を計算しておくなどに便利。

組み込みの `storyboard` テンプレートは、この仕組みで各カットの話者を
`characters[]` から引き当てています。`cut.speaker` と `id` が一致する
登場人物を選び、そのアバターと名前をセリフの横に描画します:

```jinja
{% for cut in cuts %}
### {{ cut.id }}

{% set speaker = characters | selectattr("id", "equalto", cut.speaker) | first %}
{% if speaker %}
  <img src="{{ speaker.icon }}" alt="{{ speaker.name }}" width="48" />
  <strong>{{ speaker.name }}</strong>
{% endif %}

{% for line in cut.dialogue %}{{ line }}
{% endfor %}
{% endfor %}
```

`{% set %}` で束縛した変数は**rendered に `data-kata` span を付けない**
仕様です。上記の `{{ speaker.name }}` は素のテキストとして出力され、
`<span data-kata="p-characters-0-name">…</span>` としては**annotate されません**。
これが LiveMorph 上の重要ポイントで、`characters[0].name` は Characters
セクション側で既に annotate 済みのため、set で引き直した `speaker`
経由でもう 1 度 annotate すると `sync to-data` で `characters` 配列が
膨張してしまいます。set 変数を裸のテキストとして扱うことで、それを防いでいます。

ブロック形式 (`{% set x %}...{% endset %}`) は未対応。inline 代入のみ。

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
| `selectattr(attr[, test[, value]])` | `{{ items \| selectattr("active") }}` / `{{ items \| selectattr("id", "equalto", "a") }}` |
| `rejectattr(attr[, test[, value]])` | `selectattr` の逆 |

`selectattr` / `rejectattr` のテスト引数: `equalto` (`eq`, `==`),
`ne` (`!=`), `lt`, `gt`, `le`, `ge`, `in`。省略時は attr が truthy な
要素のみ残す。

---

## レンダリング出力

`build` (または `render`) が生成する出力:

- `<span data-kata="p-{path}">value</span>` — データバインディング
  (例: `p-categories-0-items-0-status`。配列の index もアンカーに含める)
- `<div data-kata-each="collection">` — ループマーカー
- `<details>` セクションに Prompt + Template + Schema + Data を格納

HTML タグはデータ値内で自動エスケープ。`extract` 時に復元。

### data-kata-type 属性

スキーマで string 以外の型が宣言されている場合、annotator が
`data-kata-type` 属性を付与し、`extract` / `sync to-data` 時に
textContent を元の型に戻せるようにします。

| スキーマ型 | 出力される属性 | ラウンドトリップ結果 |
|------------|----------------|----------------------|
| `integer` | `data-kata-type="integer"` | `"42"` → `42` |
| `number` | `data-kata-type="number"` | `"3.14"` → `3.14` |
| `boolean` | `data-kata-type="boolean"` | `"true"` → `True` |
| `enum(...)` | `data-kata-type="enum"` + `data-kata-enum="..."` | 文字列のまま |
| `string[]` | `data-kata-type="array"` | カンマ区切り → list |
| `string` | (省略 — デフォルト) | そのまま保持 |

string 型フィールドに自然文としての `", "` が含まれていても、
Specification の shorthand で `string` と宣言されていれば extract
時にカンマ分割されません。"Soft piano, strings in the background"
のようなナレーション用文字列も安全に round-trip します。

---

## ラウンドトリップ

```
ソース (.kata.md)  → render →  出力 (.kata.md)  → extract →  JSON データ
```

`extract` は `data-kata` span の値と Specification の構造情報から JSON を復元。
