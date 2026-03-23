# CLI リファレンス

`gospelo-kata` の全コマンド一覧と詳細オプション。

```bash
gospelo-kata -V    # バージョン表示
gospelo-kata -h    # ヘルプ表示
```

---

## テンプレート操作

### `templates` — テンプレート一覧

```bash
gospelo-kata templates
```

`[schema, prompt]` タグは AI 生成対応テンプレートを示します。

### `prepare` — テンプレート情報表示 + スケルトン data.yml 生成

```bash
gospelo-kata prepare checklist                # 情報表示のみ
gospelo-kata prepare checklist -o data.yml    # 空の data.yml も生成
```

テンプレートの Prompt・Schema を表示し、スキーマからスケルトン `data.yml` を生成します。

| オプション | 必須 | 説明 |
|-----------|------|------|
| `template` | Yes | テンプレート名 (checklist, test_spec, api_test 等) |
| `--output`, `-o` | No | data.yml の出力先パス |

### `build` — テンプレート + データ → 最終出力

`assemble` + `render` をワンステップで実行します。

```bash
gospelo-kata build checklist data.yml -o outputs/
gospelo-kata build api_test data.yml -o outputs/ --no-annotate
```

| オプション | 必須 | 説明 |
|-----------|------|------|
| `template` | Yes | テンプレート名 |
| `data` | Yes | data.yml ファイルパス |
| `--output`, `-o` | No | 出力ディレクトリ |
| `--no-annotate` | No | data-kata アノテーションを付与しない |

初回実行時、テンプレートの Prompt 内容を確認する信頼確認が表示されます。

### `init` — テンプレート初期化 (レガシー)

```bash
gospelo-kata init --type checklist -o ./docs/
```

| オプション | 必須 | 説明 |
|-----------|------|------|
| `--type` | Yes | テンプレート名 (checklist, test_spec, agenda) |
| `--output`, `-o` | No | 出力先ディレクトリ |

生成物: `templates/`、`outputs/`、`.workflow_status.json`

> **注意:** 新しいワークフローでは `prepare` + `build` の使用を推奨します。

### `export` — テンプレートパートの抽出

正規表現ベースの高速抽出（AST/JSON Schema パース不要）。

```bash
gospelo-kata export checklist --part prompt,schema   # AI 推奨パターン
gospelo-kata export checklist --part schema           # 単一パート
gospelo-kata export checklist                         # 全パート
gospelo-kata export checklist --format json            # JSON 出力
gospelo-kata export checklist -o output.md             # ファイル保存
```

| オプション | デフォルト | 説明 |
|-----------|-----------|------|
| `template` | — | テンプレート名またはファイルパス (必須) |
| `--part` | `all` | `prompt`, `schema`, `data`, `body`, `all`, またはカンマ区切り |
| `--format` | `md` | 出力形式: `md`, `yaml`, `json` |
| `--output`, `-o` | stdout | 出力ファイルパス |

出力はパート数で変化: 単一パートは生テキスト、複数パートはセクション見出し付き、`all` はテンプレート名・説明を含みます。

### `import-data` — データのスキーマ検証

YAML データファイルを KATA 短縮記法スキーマで検証します。build 前のゲートとして使用。

```bash
gospelo-kata import-data checklist data.yml         # 検証 + データ出力
gospelo-kata import-data checklist data.yml -q      # 検証のみ (build ゲート)
gospelo-kata import-data checklist data.yml --format json  # JSON 出力
```

| オプション | デフォルト | 説明 |
|-----------|-----------|------|
| `template` | — | テンプレート名またはファイルパス (必須) |
| `data` | — | YAML データファイルパス (必須) |
| `--format` | `yaml` | 出力形式: `yaml`, `json` |
| `--quiet`, `-q` | false | データ出力を抑制、検証結果のみ |

必須フィールド、enum 値、型、配列構造、ネストされたオブジェクトを検証します。ユニオン型（例: `integer|integer[]!`）にも対応。検証エラー時は終了コード 1 で終了。

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

### `generate` — ドキュメント生成 (JSON ベース)

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

> **注意:** テンプレート + data.yml のワークフローでは `build` コマンドが `assemble` + `render` を自動実行するため、`render` を直接使う必要はありません。

### `assemble` — テンプレート + データの結合

組み込みテンプレートと YAML/JSON データを結合し、`_tpl.kata.md` を生成。

```bash
gospelo-kata assemble --type checklist --data data.yml
```

> **注意:** `build` コマンドが `assemble` + `render` を自動実行するため、通常は `build` を使用してください。

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

---

## パッケージ管理

### `pack` — テンプレートのパッケージ化

```bash
gospelo-kata pack ./my_template/ -o my_template.katar
```

### `pack-init` — テンプレートの雛形作成

```bash
gospelo-kata pack-init ./my_template/
```

詳細は [テンプレートパッケージ](template-package.md) を参照。

---

## VSCode 連携

### `init-vscode` — タスク設定の生成

```bash
gospelo-kata init-vscode --output .vscode
```

詳細は [VSCode 連携](vscode-integration.md) を参照。
