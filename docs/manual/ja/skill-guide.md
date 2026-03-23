# スキルガイド

AI スキルの使い分け。

---

## 基本ワークフロー

すべてのスキルは共通のワークフローに従います:

```
build (初期値で生成) → Data ブロック編集 → sync to-html → lint → (修正ループ)
```

| ステップ | コマンド | 説明 |
|---------|---------|------|
| ビルド | `gospelo-kata build {template} -o ./` | 初期値で .kata.md を生成 |
| 同期 | `gospelo-kata sync to-html {file}` | Data → 本文を更新 |
| 検証 | `gospelo-kata lint {file}` | 構造・スキーマ検証 |
| 抽出 | `gospelo-kata extract {file}` | レンダリング済みからデータ復元 |

AI スキルは `.kata.md` の Data ブロックを直接生成・編集します。外部 data.yml は不要です。

---

## スキル一覧

| スキル | 用途 | データの入手元 |
|--------|------|--------------|
| `/kata-gen` | ゼロからデータ生成 | AI が Prompt に従って創作 |
| `/kata-convert` | 既存ドキュメント変換 | Markdown / テキスト / CSV 等 |
| `/kata-collect` | Web 検索でデータ収集 | インターネット上の情報 |
| `/kata-import` | 構造化ソース変換 | OpenAPI / Swagger 等 |
| `/kata-pack` | テンプレート管理 | — |

---

## どのスキルを使うか

```
データはどこから来る？
├─ AI が考える          → /kata-gen
├─ 既存ドキュメント      → /kata-convert
├─ Web 上の情報         → /kata-collect
├─ 構造化ファイル        → /kata-import
テンプレートを作る？     → /kata-pack
```

手動で Data を編集する場合はスキル不要。CLI を直接使用: `build → Data 編集 → sync to-html → lint`

---

## 使用例

### /kata-gen — AI にゼロから生成させる

```
/kata-gen checklist
```

「Web アプリのセキュリティチェックリストを作って」等、要件を伝えるだけ。

### /kata-convert — 既存ドキュメントを変換

```
/kata-convert docs/old_checklist.md checklist
```

### /kata-collect — Web 検索でデータ収集

```
/kata-collect checklist
```

OWASP Top 10、RFC 等の公開情報を検索してデータを生成。

### /kata-import — OpenAPI / Swagger から変換

```
/kata-import swagger.json test_spec
```

### /kata-pack — テンプレート管理

```
/kata-pack
```

テンプレートの展開・修正・再パック・テストを一括実行。

---

## 修正ループ

lint でエラーが出た場合:

```bash
# 1. Data ブロックを修正
# 2. sync + lint
gospelo-kata sync to-html document.kata.md
gospelo-kata lint document.kata.md
# エラーが 0 になるまで繰り返す
```
