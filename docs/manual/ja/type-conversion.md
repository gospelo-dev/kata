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
