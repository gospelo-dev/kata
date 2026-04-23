# 型コンバート仕様

KATA Markdown のスキーマ型定義とデータ間の型変換ルール。

---

## 背景

KATA Markdown ではスキーマもデータも YAML で記述します。
しかし、スキーマ shorthand の型名（`integer`, `boolean` 等）と PyYAML がパースするネイティブ型名（`int`, `bool` 等）には差異があり、この不一致がサイレントなバグの原因になっていました。

### PyYAML の型変換

```yaml
count: 42          # → int
ratio: 3.14        # → float
active: true       # → bool
name: hello        # → str
quoted: "42"       # → str（クォートにより文字列）
```

---

## スキーマ shorthand の正規型名

KATA shorthand で認識される正規の型名:

| 正規型名 | JSON Schema 変換 | Python 型 |
|---------|-----------------|----------|
| `string` | `{"type": "string"}` | `str` |
| `integer` | `{"type": "integer"}` | `int` |
| `number` | `{"type": "number"}` | `int`, `float` |
| `boolean` | `{"type": "boolean"}` | `bool` |
| `object` | `{"type": "object"}` | `dict` |
| `any` | `{}` | 任意 |

---

## 型エイリアス

PyYAML のネイティブ型名に合わせたエイリアスを導入します。パース時に正規型名に正規化されます。

| エイリアス | 正規化先 | 用途 |
|-----------|---------|------|
| `int` | `integer` | PyYAML の型名に合わせた短縮形 |
| `float` | `number` | Python の型名に合わせた短縮形 |
| `bool` | `boolean` | PyYAML の型名に合わせた短縮形 |
| `str` | `string` | Python の型名に合わせた短縮形 |

### スキーマ記述例

```yaml
# 正規型名（推奨）
count: integer!
ratio: number
active: boolean

# エイリアス（同等）
count: int!
ratio: float
active: bool
```

両方とも同じ JSON Schema に変換されます。

---

## 未知の型名のエラー処理

正規型名にもエイリアスにも `enum()` にもマッチしない型名が指定された場合、**即座に `ValueError` を送出**します。

### 変更前（フォールバック動作）

```python
# 未知の型 → サイレントに string 扱い（バグの原因）
"int" → {"type": "string", "description": "int"}
```

### 変更後（エラー動作）

```python
# 未知の型 → 即座にエラー
"unknown_type" → ValueError: Unknown schema type: 'unknown_type'
```

この変更により、スキーマ定義の誤りが即座に検出されます。

---

## データの読み込み

データは YAML 形式のみをサポートします。バリデータのデータ読み込みを `json.loads` から `yaml.safe_load` に変更します。

> **注意:** `.kata.md` 内の Data ブロック（`_parse_data_block`）は既に `yaml.safe_load` を使用しています。`validator.py` の `validate_file` のみが `json.loads` を使用しており、これを修正します。

### バリデーション時の型チェック

`yaml.safe_load` が返すネイティブ型がスキーマの JSON Schema 型と一致するかをチェックします:

| スキーマ型 | 許容する Python 型 |
|-----------|------------------|
| `string` | `str` |
| `integer` | `int` |
| `number` | `int`, `float` |
| `boolean` | `bool` |
| `array` | `list` |
| `object` | `dict` |

---

## 変換フロー

```
スキーマ定義 (.kata.md 内 **Schema** ブロック)
  │
  ├── "integer" / "int"  ──→ {"type": "integer"}
  ├── "number" / "float" ──→ {"type": "number"}
  ├── "boolean" / "bool" ──→ {"type": "boolean"}
  ├── "string" / "str"   ──→ {"type": "string"}
  └── 未知の型名          ──→ ValueError (即座にエラー)
  │
  ↓ バリデーション
  │
データ (.kata.md 内 **Data** ブロック / 外部 .yml ファイル)
  └── yaml.safe_load → ネイティブ型 (int, float, bool, str, list, dict)
  │
  ↓ 型チェック
  │
ネイティブ型 vs JSON Schema 型 → OK / ValidationError
```

---

## 影響範囲

| コンポーネント | ファイル | 変更内容 |
|-------------|--------|---------|
| Shorthand パーサー | `template.py` | `_TYPE_ALIASES` マップ追加、フォールバック削除 → `ValueError` |
| バリデータ | `validator.py` | `validate_file` を `json.loads` → `yaml.safe_load` に変更 |
| ドキュメント | `kata-markdown-format.md` | 型記法テーブルにエイリアスを追記 |

---

## Round-Trip の型保持 (data-kata-type)

レンダリング済み `.kata.md` から Data を復元するときにも型変換が走ります。
スキーマで string 以外の型が宣言されたフィールドについては、annotator が
span に `data-kata-type` 属性を付与し、`extract` / `sync to-data` が元の型
に戻せるようにしています。

| スキーマ型 | 出力される span 属性 | extract 時の変換 |
|-----------|----------------------|-----------------|
| `integer` | `data-kata-type="integer"` | `"42"` → `42` |
| `number` | `data-kata-type="number"` | `"3.14"` → `3.14` |
| `boolean` | `data-kata-type="boolean"` | `"true"` / `"yes"` / `"1"` → `True` |
| `enum` | `data-kata-type="enum"` + `data-kata-enum="..."` | そのまま文字列 |
| スカラー配列 | `data-kata-type="array"` | `"a, b, c"` → `["a", "b", "c"]` |
| `string` | *(省略 — デフォルト)* | そのまま文字列 |

### string に type 属性を付けない理由

`string` はデフォルトの型なので、markup を軽く保つために省略します。
ただし extract 側は「本当に string かどうか」を判断する必要があります。
型情報が何もない場合、legacy ヒューリスティックが `", "` を array の
区切りとして解釈してしまい、`audio: "Soft piano, strings in the background"`
のような自然文が 2 要素配列に誤変換されるためです。

これを避けるため、extractor は Specification セクションの YAML shorthand
をパースして、各配列要素の子フィールドの schema 型を引き当てます。
`audio: string` と宣言されていれば、カンマ分割を抑制してそのまま
文字列で返します。

`extract_from_text(schema=...)` のように明示 JSON Schema を渡した場合は、
そちらが優先され、rendered の Specification は参照されません。

### `{% set %}` とクロスリファレンス

`{% set %}` で束縛された変数(例: storyboard テンプレートで各カットの
話者を `characters[]` から引く変数)は、**意図的に `data-kata` span を
付けずに plain text として出力**されます。同じスキーマパスを 2 つの場所で
annotate してしまうと、extractor が「ソース配列の要素数が実際より多い」
と誤認してしまうためです。

詳細は [LiveMorph](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/livemorph.md)
を参照してください。
