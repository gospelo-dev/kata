# CLI リファレンス

`gospelo-kata` の全コマンド一覧と詳細オプション。

---

## テンプレート操作

### `templates` — テンプレート一覧

```bash
gospelo-kata templates
```

`[schema, prompt]` タグは AI 生成対応テンプレートを示します。

### `init` — テンプレート初期化

```bash
gospelo-kata init --type checklist -o ./docs/
```

| オプション | 必須 | 説明 |
|-----------|------|------|
| `--type` | Yes | テンプレート名 (checklist, test_spec, agenda) |
| `--output`, `-o` | No | 出力先ディレクトリ |

生成物: `templates/`、`outputs/`、`.workflow_status.json`

### `show-prompt` — AI 向け説明の表示

```bash
gospelo-kata show-prompt checklist
```

テンプレートの `**Prompt**` ブロックを表示。テンプレート名またはファイルパスを指定。

### `show-schema` — スキーマの表示

```bash
gospelo-kata show-schema checklist              # JSON (デフォルト)
gospelo-kata show-schema checklist --format yaml # YAML
```

`**Schema**` ブロックから JSON Schema を生成して表示。

### `schemas` — バリデーションスキーマ一覧

```bash
gospelo-kata schemas
```

### `infer-schema` — スキーマ推論

```bash
gospelo-kata infer-schema template.kata.md              # YAML shorthand
gospelo-kata infer-schema template.kata.md --format json # JSON Schema
```

テンプレートの変数・ループ構造からスキーマを自動推論。

---

## データ検証・生成

### `validate` — JSON バリデーション

```bash
gospelo-kata validate data.json                    # スキーマ自動検出
gospelo-kata validate data.json --schema checklist # スキーマ指定
gospelo-kata validate data.json --schema ./schema.json
```

### `generate` — ドキュメント生成

JSON データから Markdown / Excel / HTML を生成。

```bash
gospelo-kata generate data.json                            # Markdown (stdout)
gospelo-kata generate data.json -f markdown -o output.kata.md
gospelo-kata generate data.json -f excel -o output.xlsx
gospelo-kata generate data.json -f excel --prereq prereq.json -o test.xlsx
gospelo-kata generate data.json -f html -o output.html
```

| オプション | デフォルト | 説明 |
|-----------|-----------|------|
| `--format`, `-f` | markdown | 出力形式 (markdown / excel / html) |
| `--output`, `-o` | stdout | 出力ファイルパス |
| `--type` | 自動検出 | ドキュメントタイプ |
| `--prereq` | — | 前提条件 JSON (test_spec Excel 用) |

### `render` — セルフコンテインド .kata.md のレンダリング

`**Schema**` + `**Data**` ブロックを含む `.kata.md` ファイルを解釈し、data-kata アノテーション付きの出力を生成。

```bash
gospelo-kata render source.kata.md -o outputs/result.kata.md
```

出力には以下が自動付与されます:
- `<span data-kata="p-xxx">` — スキーマプロパティ参照
- `<div data-kata-each="collection">` — ループマーカー
- `<details>` Schema + Data セクション

### `edit` — ブラウザエディター

```bash
gospelo-kata edit data.json
gospelo-kata edit data.json --port 8080 --no-browser
```

---

## Lint・フォーマット

### `lint` — Lint 検証

```bash
gospelo-kata lint output.kata.md                    # テンプレートモード
gospelo-kata lint output.kata.md --format vscode    # VSCode Problem Matcher 形式
gospelo-kata lint rendered.kata.md --schema checklist # ドキュメントモード
```

| オプション | デフォルト | 説明 |
|-----------|-----------|------|
| `--format` | human | 出力形式 (human / vscode) |
| `--schema` | 自動検出 | ドキュメントモード時のスキーマ名 |

**モード自動判定:**
- `data-kata` span があり Jinja 構文がない → ドキュメントモード
- スキーマブロック / `{{ }}` / `{% %}` がある → テンプレートモード
- `<!-- kata: {...} -->` メタデータあり → ドキュメントモード

エラーがある場合、終了コード 1 で終了。

エラーコードの詳細は [Lint ルール一覧](lint-rules.md) を参照。

### `fmt` — 自動フォーマット

rendered `.kata.md` の `data-kata` span 内 HTML タグをサニタイズ。

```bash
gospelo-kata fmt outputs/*.kata.md           # 修正して上書き
gospelo-kata fmt outputs/*.kata.md --check   # チェックのみ (CI 向け)
```

`--check` 指定時、修正が必要な場合は終了コード 1 で終了。

### `gen-schema-section` — Schema Reference セクション生成

```bash
gospelo-kata gen-schema-section checklist
gospelo-kata gen-schema-section ./schema.json --section-map '{"date": "u-meeting-info"}'
```

---

## 分析・ワークフロー

### `extract` — データ抽出

rendered `.kata.md` から元の JSON データを復元 (ラウンドトリップ)。

```bash
gospelo-kata extract rendered.kata.md              # stdout
gospelo-kata extract rendered.kata.md -o data.json # ファイル出力
```

`&lt;` 等の HTML エンティティは自動的に `<` に復元されます。

### `coverage` — チェックリストカバレッジ分析

```bash
gospelo-kata coverage --checklist checklist.json --dir tests/
gospelo-kata coverage --checklist checklist.json --dir tests/ -f markdown
gospelo-kata coverage --checklist checklist.json --dir tests/ -f json
```

| オプション | 必須 | 説明 |
|-----------|------|------|
| `--checklist` | Yes | チェックリスト JSON ファイル |
| `--dir` | Yes | ドキュメントディレクトリの親 |
| `--format`, `-f` | No | 出力形式 (human / markdown / json) |

### `workflow-status` — ワークフロー進捗管理

```bash
gospelo-kata workflow-status --suite-dir ./docs/                    # 確認
gospelo-kata workflow-status --suite-dir ./docs/ --mark-done lint --note "0 errors"
gospelo-kata workflow-status --suite-dir ./docs/ --retry --retry-reason "lint NG"
gospelo-kata workflow-status --suite-dir ./docs/ --reset
```

| オプション | 説明 |
|-----------|------|
| `--suite-dir` | (必須) `.workflow_status.json` のあるディレクトリ |
| `--init TEMPLATE OUTPUT` | ワークフロー初期化 |
| `--mark-done STEP` | ステップを完了にする |
| `--note TEXT` | `--mark-done` と併用。コメントを記録 |
| `--retry` | validate/generate/lint をリセットし round+1 |
| `--retry-reason TEXT` | `--retry` と併用。理由を記録 |
| `--reset` | 全ステップをリセット |

詳細は [ワークフローガイド](workflow-guide.md) を参照。

---

## VSCode 連携

### `init-vscode` — タスク設定の生成

```bash
gospelo-kata init-vscode --output .vscode
```

詳細は [VSCode 連携](vscode-integration.md) を参照。
