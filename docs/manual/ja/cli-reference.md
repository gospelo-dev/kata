# CLI リファレンス

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

### `build` — テンプレート → .kata.md 生成

```bash
gospelo-kata build todo -o ./                          # 初期値で生成
gospelo-kata build checklist data.yml -o outputs/      # 外部データ指定
```

| オプション | 説明 |
|-----------|------|
| `data` | データファイル (省略時はテンプレート内蔵の Data を使用) |
| `--output`, `-o` | 出力ディレクトリ |
| `--no-annotate` | data-kata アノテーションを付与しない |
| `--no-validate` | スキーマ検証をスキップ |

### `prepare` — テンプレート情報 + スケルトン data.yml

```bash
gospelo-kata prepare checklist                # 情報表示のみ
gospelo-kata prepare checklist -o data.yml    # スケルトン data.yml 生成
```

### `export` — テンプレートパートの抽出

```bash
gospelo-kata export checklist --part prompt,schema   # AI 推奨
gospelo-kata export checklist --format json           # JSON 出力
gospelo-kata export checklist -o output.md            # ファイル保存
```

| オプション | デフォルト | 説明 |
|-----------|-----------|------|
| `--part` | `all` | `prompt`, `schema`, `data`, `body`, `all` (カンマ区切り) |
| `--format` | `md` | `md`, `yaml`, `json` |
| `--output`, `-o` | stdout | 出力ファイルパス |

### `import-data` — データのスキーマ検証

```bash
gospelo-kata import-data checklist data.yml -q
```

### `init` — テンプレート初期化

```bash
gospelo-kata init --type checklist -o ./docs/
gospelo-kata init --from-package my_template.katar
```

---

## 同期 (LiveMorph)

### `sync` — 双方向同期

```bash
gospelo-kata sync to-html document.kata.md   # Data → 本文
gospelo-kata sync to-data document.kata.md   # 本文 → Data
```

→ [LiveMorph ガイド](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/livemorph.md)

---

## レンダリング・生成

### `render` — .kata.md のレンダリング

```bash
gospelo-kata render source.kata.md -o outputs/result.kata.md
```

### `assemble` — テンプレート + データの結合

```bash
gospelo-kata assemble --type checklist --data data.yml
```

### `generate` — JSON ベースのドキュメント生成

```bash
gospelo-kata generate data.json -f markdown -o output.kata.md
gospelo-kata generate data.json -f excel -o output.xlsx
gospelo-kata generate data.json -f html -o output.html
```

### `validate` — JSON バリデーション

```bash
gospelo-kata validate data.json --schema checklist
```

---

## Lint・フォーマット

### `lint` — Lint 検証

```bash
gospelo-kata lint output.kata.md
gospelo-kata lint output.kata.md --format vscode    # VSCode Problem Matcher 形式
```

モードは自動判定: `data-kata` span → ドキュメントモード、Jinja 構文 → テンプレートモード。

→ [Lint ルール一覧](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/lint-rules.md)

### `fmt` — 自動フォーマット

```bash
gospelo-kata fmt outputs/*.kata.md           # 修正して上書き
gospelo-kata fmt outputs/*.kata.md --check   # チェックのみ (CI 向け)
```

---

## 分析

### `extract` — データ抽出 (ラウンドトリップ)

```bash
gospelo-kata extract rendered.kata.md -o data.json
```

### `coverage` — チェックリストカバレッジ

```bash
gospelo-kata coverage --checklist checklist.json --dir tests/ -f markdown
```

### `workflow-status` — ワークフロー進捗管理

```bash
gospelo-kata workflow-status --suite-dir ./docs/
gospelo-kata workflow-status --suite-dir ./docs/ --mark-done lint --note "0 errors"
```

---

## パッケージ管理

```bash
gospelo-kata pack-init ./my_template/                    # 雛形作成
gospelo-kata pack ./my_template/ -o my_template.katar    # パッケージ化
```

→ [テンプレートパッケージ](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/katar.md)

---

## その他

```bash
gospelo-kata schemas                                     # スキーマ一覧
gospelo-kata infer-schema template.kata.md               # スキーマ推論
gospelo-kata edit data.json                              # ブラウザエディター
gospelo-kata gen-schema-section checklist                # Specification セクション生成
gospelo-kata init-vscode --output .vscode                # VSCode タスク設定
```
