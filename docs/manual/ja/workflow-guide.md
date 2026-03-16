# ワークフローガイド

ドキュメント生成パイプラインの管理方法。

---

## ワークフローステップ

```
init → validate → generate → lint → review
```

| ステップ | 説明 | 自動化 |
|---------|------|--------|
| `init` | テンプレート・ディレクトリの初期化 | `gospelo-kata init` |
| `validate` | JSON データのスキーマ検証 | `gospelo-kata validate` |
| `generate` | .kata.md ドキュメント生成 | `gospelo-kata render` / `generate` |
| `lint` | 構造検証 | `gospelo-kata lint` |
| `review` | 成果物の確認 (人間 or AI) | 手動 |

---

## 基本的な流れ

### 1. 初期化

```bash
mkdir my_suite && cd my_suite
gospelo-kata init --type test_spec
```

生成物:
```
my_suite/
├── templates/          # テンプレートファイル群
├── outputs/            # 出力先
└── .workflow_status.json
```

### 2. ソースファイル作成・レンダリング

```bash
# ソース .kata.md を作成 (エディタで編集)
vim xss_test.kata.md

# レンダリング
gospelo-kata render xss_test.kata.md -o outputs/xss_test.kata.md
```

### 3. 検証

```bash
gospelo-kata lint outputs/xss_test.kata.md
```

### 4. ステータス記録

```bash
gospelo-kata workflow-status --suite-dir . --mark-done init
gospelo-kata workflow-status --suite-dir . --mark-done validate --note "schema OK"
gospelo-kata workflow-status --suite-dir . --mark-done generate
gospelo-kata workflow-status --suite-dir . --mark-done lint --note "0 errors"
gospelo-kata workflow-status --suite-dir . --mark-done review --note "Extract verified"
```

### 5. 進捗確認

```bash
gospelo-kata workflow-status --suite-dir .
```

```
Template: test_spec
Round:    0
Progress: 5/5

  [OK] init (2026-03-16T10:00:00) schema OK
  [OK] validate (2026-03-16T10:01:00) schema OK
  [OK] generate (2026-03-16T10:01:05)
  [OK] lint (2026-03-16T10:01:10) 0 errors
  [OK] review (2026-03-16T10:02:00) Extract verified
```

---

## リトライ (修正ループ)

lint でエラーが出た場合、ソースデータを修正して再実行します。

```bash
# lint NG → リトライ
gospelo-kata workflow-status --suite-dir . --retry --retry-reason "D016: HTML tag in span"

# ソースを修正 → 再レンダリング → 再 lint
gospelo-kata render xss_test.kata.md -o outputs/xss_test.kata.md
gospelo-kata lint outputs/xss_test.kata.md

# ステップを再マーク
gospelo-kata workflow-status --suite-dir . --mark-done validate
gospelo-kata workflow-status --suite-dir . --mark-done generate
gospelo-kata workflow-status --suite-dir . --mark-done lint --note "0 errors"
```

`--retry` の動作:
1. `validate` / `generate` / `lint` のステータスをリセット
2. `round` を +1 にインクリメント
3. 前回の状態を `history` に記録

```
Round 0: init → validate → generate → lint (NG)
  ↓ --retry
Round 1: ソース修正 → validate → generate → lint (OK) → review
```

---

## .workflow_status.json 構造

```json
{
  "template": "test_spec",
  "steps": {
    "init":     { "done": true, "at": "2026-03-16T10:00:00" },
    "validate": { "done": true, "at": "2026-03-16T10:01:00" },
    "generate": { "done": false },
    "lint":     { "done": false },
    "review":   { "done": false }
  },
  "round": 0,
  "history": []
}
```

---

## AI 連携ワークフロー

AI (Claude 等) と連携する場合の推奨フロー:

### 1. テンプレート仕様を AI に渡す

```bash
gospelo-kata show-prompt test_spec   # AI 向け説明
gospelo-kata show-schema test_spec   # JSON Schema
```

### 2. AI にデータ生成を依頼

スキーマに従った JSON/YAML データの生成を依頼。

### 3. バリデーション → 生成 → Lint

```bash
gospelo-kata validate data.json
gospelo-kata render source.kata.md -o outputs/result.kata.md
gospelo-kata lint outputs/result.kata.md
```

### 4. エラーがある場合は AI にフィードバック

Lint エラーを AI に渡し、データを修正してもらいます。

```bash
gospelo-kata lint outputs/result.kata.md --format vscode
# 出力をそのまま AI に渡す
```

### 5. ラウンドトリップ検証

```bash
gospelo-kata extract outputs/result.kata.md -o extracted.json
# extracted.json と元データを比較
```

---

## ディレクトリ構成パターン

### 単一ドキュメント

```
project/
├── source.kata.md
├── outputs/
│   └── source.kata.md
└── .workflow_status.json
```

### テストスイート (複数ドキュメント)

```
test_suite/
├── 01_sql_injection/
│   ├── sql_injection.kata.md
│   ├── outputs/
│   │   ├── sql_injection.kata.md
│   │   └── extracted.json
│   ├── templates/
│   └── .workflow_status.json
├── 02_xss/
│   ├── xss.kata.md
│   ├── outputs/
│   └── .workflow_status.json
└── checklist.json            # カバレッジ分析用
```

### カバレッジ分析

```bash
gospelo-kata coverage --checklist checklist.json --dir test_suite/
```

各サブディレクトリに `.kata.md` が存在するかを判定。
