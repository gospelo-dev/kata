# スキルガイド — ユースケース別の使い方

KATA Markdown™ の AI スキルをユースケース別に解説します。

---

## 基本ワークフロー

すべてのスキルは共通のワークフローに従います:

```
prepare → data.yml 作成 → import-data → build → lint → (修正ループ)
```

| ステップ | コマンド | 説明 |
|---------|---------|------|
| 準備 | `gospelo-kata prepare {template}` | テンプレート情報表示 + 空 data.yml 生成 |
| 抽出 | `gospelo-kata export {template} --part prompt,schema` | プロンプト・スキーマの高速抽出 (AI 用) |
| データ検証 | `gospelo-kata import-data {template} data.yml -q` | build 前のスキーマ検証 |
| ビルド | `gospelo-kata build {template} data.yml` | テンプレート + データ → 最終出力 |
| 検証 | `gospelo-kata lint {output}.kata.md` | 構造・スキーマ検証 |
| 抽出 | `gospelo-kata extract {output}.kata.md` | レンダリング済みからデータ復元 |

---

## スキル一覧

| スキル | 用途 | データの入手元 |
|--------|------|--------------|
| `/kata` | 基本操作 | 手動（data.yml を自分で書く） |
| `/kata-gen` | ゼロからデータ生成 | AI が Prompt に従って創作 |
| `/kata-convert` | 既存ドキュメント変換 | 既存の Markdown / テキスト / CSV 等 |
| `/kata-collect` | Web 検索でデータ収集 | インターネット上の情報 |
| `/kata-import` | 構造化ソース変換 | OpenAPI / Swagger 等の機械可読ファイル |
| `/kata-pack` | テンプレート管理 | — |

---

## ユースケース 1: テンプレートの確認と手動データ作成

**スキル**: `/kata`

既存のテンプレートを確認し、自分で `data.yml` を書いてドキュメントを生成する。

```bash
# 1. テンプレート一覧を確認
gospelo-kata templates

# 2. テンプレート情報を見て空の data.yml を生成
gospelo-kata prepare checklist -o data.yml

# 3. data.yml を編集（手動またはAIに依頼）

# 4. データ検証、ビルド、lint
gospelo-kata import-data checklist data.yml -q
gospelo-kata build checklist data.yml -o outputs/
gospelo-kata lint outputs/checklist.kata.md
```

**向いているケース**:
- テンプレートの構造を理解したい
- データの内容を細かくコントロールしたい
- 小さい AI にスキーマを見せてデータを作らせたい

---

## ユースケース 2: AI にゼロからデータを生成させる

**スキル**: `/kata-gen`

AI がテンプレートの Prompt と Schema を読み、ユーザーの要件に従ってデータを生成する。

```
/kata-gen checklist
```

**例**:
- 「Web アプリケーションのセキュリティチェックリストを作って」
- 「認証 API のテスト仕様書を作って」
- 「来週のスプリント計画会議のアジェンダを作って」

**向いているケース**:
- 新規にドキュメントを作りたい
- 元になるデータがない
- AI の知識をベースにドラフトを作りたい

---

## ユースケース 3: 既存ドキュメントを KATA 形式に変換する

**スキル**: `/kata-convert`

独自フォーマットの既存ドキュメント（Markdown、テキスト、CSV 等）を読み取り、KATA テンプレートのスキーマに合わせた `data.yml` に変換する。

```
/kata-convert docs/old_checklist.md checklist
```

**例**:
- Excel で管理していたチェックリストを KATA Markdown に移行
- 既存のテスト仕様書を新しいテンプレート形式に統一
- 議事録テキストをアジェンダテンプレートに変換

**向いているケース**:
- 既存のドキュメント資産がある
- フォーマットを統一したい
- 古いバージョンのテンプレートから最新版に移行したい

---

## ユースケース 4: Web 検索でデータを収集して生成する

**スキル**: `/kata-collect`

テンプレートの Prompt に記載されたトピック（OWASP、RFC 等）について Web 検索を行い、収集した情報からデータを生成する。

```
/kata-collect checklist
```

**例**:
- OWASP Top 10 に基づくセキュリティチェックリスト
- 最新の業界標準に基づくインフラ監査項目
- RFC に基づく API テストケース

**向いているケース**:
- 最新の情報が必要
- 権威あるソース（公式ドキュメント、標準規格）に基づくデータが必要
- Prompt に具体的な調査対象が指定されている

---

## ユースケース 5: OpenAPI / Swagger からテスト仕様書を生成する

**スキル**: `/kata-import`

OpenAPI や Swagger 等の構造化された仕様ファイルを読み取り、エンドポイントごとにテストケースを自動生成する。

```
/kata-import swagger.json test_spec
```

**例**:
- `swagger.json` から API テスト仕様書を自動生成
- `openapi.yaml` のエンドポイント一覧からテストケースを網羅

**向いているケース**:
- 機械可読な仕様ファイルがある
- API テスト仕様書を効率的に作りたい
- エンドポイントごとのテストケースを網羅したい

---

## ユースケース 6: テンプレートの作成・編集・配布

**スキル**: `/kata-pack`

独自のテンプレートを作成し、`.katar` パッケージとして配布する。

```
/kata-pack
```

**例**:
- プロジェクト固有のチェックリストテンプレートを作成
- 既存テンプレートのスキーマをカスタマイズ
- チーム用テンプレートをパッケージ化して共有

**向いているケース**:
- 組み込みテンプレートでは要件を満たせない
- チームで統一フォーマットを配布したい
- テンプレートのスキーマやレイアウトをカスタマイズしたい

---

## どのスキルを使うべきか

```
データはどこから来る？
│
├─ 自分で書く           → /kata
├─ AI が考える          → /kata-gen
├─ 既存ドキュメント      → /kata-convert
├─ Web 上の情報         → /kata-collect
├─ 構造化ファイル        → /kata-import
│
テンプレートを作る？     → /kata-pack
```

---

## 修正ループ

lint でエラーが出た場合、データを修正して再ビルドします:

```bash
# 1. lint エラーを確認
gospelo-kata lint outputs/checklist.kata.md

# 2. data.yml を修正

# 3. データ検証、再ビルド、再検証
gospelo-kata import-data checklist data.yml -q
gospelo-kata build checklist data.yml -o outputs/
gospelo-kata lint outputs/checklist.kata.md

# エラーが 0 になるまで繰り返す
```

---

## ディレクトリ構成

### 単一ドキュメント

```
project/
├── data.yml              # データ
├── outputs/
│   └── checklist.kata.md  # 最終出力
```

### テストスイート（複数ドキュメント）

```
test_suite/
├── 01_sql_injection/
│   ├── data.yml
│   └── outputs/
│       └── test_spec.kata.md
├── 02_xss/
│   ├── data.yml
│   └── outputs/
│       └── test_spec.kata.md
└── checklist.json          # カバレッジ分析用
```

### カバレッジ分析

```bash
gospelo-kata coverage --checklist checklist.json --dir test_suite/
```

---

## ラウンドトリップ検証

レンダリング済みドキュメントから元のデータを復元し、正しく変換されたか確認できます:

```bash
gospelo-kata extract outputs/checklist.kata.md -o extracted.yml
# extracted.yml と元の data.yml を比較
```

---

## 共通の注意事項

- すべてのスキルは `data.yml` → `import-data` → `build` → `lint` の流れで最終出力を生成します
- `data.yml` は YAML 形式で記述します（JSON は使用しません）
- Prompt ブロックはデータ生成のガイドラインとしてのみ使用します
- lint エラーが 0 になるまで `data.yml` を修正して再ビルドします
