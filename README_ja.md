# gospelo-kata — KATA Markdown™ for Human-AI Collaboration

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/gospelo-dev/kata/blob/main/LICENSE.md)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![AI Collaborative](https://img.shields.io/badge/AI-Collaborative-ff6f00.svg?logo=openai&logoColor=white)](#なぜ-gospelo-kata)
[![KATA Markdown](https://img.shields.io/badge/Format-KATA_Markdown-00bcd4.svg)](#kata-markdown-フォーマット)

**人間と AI の協同作業**のために設計されたドキュメントフォーマットおよびツールキットです。KATA Markdown™ はスキーマ・データ・テンプレートを1つのファイルに統合し、人間にも AI にも特別な指示なしで読み書きできるフォーマットです。

## なぜ gospelo-kata？

KATA Markdown は、人間と AI が同じドキュメントを読み、理解し、共同で作業できるように設計されています。フォーマットは自己記述的で、AI は埋め込まれたスキーマとプロンプトからテンプレート構造を自力で理解でき、人間も同じファイルを自然に読み書きできます。スキーマ・バリデーション・信頼管理によって AI の出力を安全な経路に導くハーネスとして機能し、自律型 AI が構造から逸脱せず安全に動作します。

AI でドキュメントを生成する際、よくある問題:

- **構造がない** — AI が出力する自由形式のテキストは検証や再利用が難しい
- **ラウンドトリップできない** — レンダリング後、元のデータを取り出せない
- **バリデーションがない** — スキーマ違反がレビューまで気づかれない
- **AI への指示が毎回必要** — 出力形式を毎回説明しなければならない

gospelo-kata は **単一の `.kata.md` ファイル** にすべてを含めることで解決します。スキーマ定義・構造化データ・Jinja2 互換テンプレート（組み込みエンジン、外部依存なし）を1ファイルに統合。埋め込みの `{#schema}` と `{#prompt}` ブロックにより、AI は外部の指示なしでテンプレートを理解できます。レンダリング出力は `data-kata` アノテーションでデータバインディングを保持し、ラウンドトリップ抽出と自動バリデーションを実現します。

## 特徴

- **人間と AI の協同フォーマット** — 人間にも AI にも同じファイルを読み書き・生成できる
- **自己記述的テンプレート** — 埋め込みの `{#schema}` と `{#prompt}` で AI が外部指示なしにテンプレートを理解
- **シングルファイル** — スキーマ、データ、テンプレートを1つの `.kata.md` に
- **YAML ショートハンドスキーマ** — 簡潔な型定義 (`string!`, `enum(a,b,c)`, `items[]!:`)
- **ラウンドトリップ** — レンダリング済みドキュメントから構造化データを抽出
- **Lint** — テンプレートとレンダリング出力の両方を検証 (20以上のルール)
- **AI フレンドリー** — `assemble` コマンドで AI は YAML データのみ生成すればOK
- **マルチフォーマット** — Markdown、Excel、HTML 出力
- **VSCode 拡張機能** — リアルタイム lint、ホバー情報、プレビュー CSS
- **最小依存** — コア機能は外部依存なし (Jinja2 3.1.6 互換エンジン組み込み、PyYAML 必須、openpyxl は Excel 用オプション)

## インストール

```bash
pip install gospelo-kata

# Excel 出力サポート付き
pip install gospelo-kata[excel]
```

Python 3.11+ が必要です。

## クイックスタート

### 1. ゼロからドキュメントを作成

```bash
cat > todo_tpl.kata.md << 'EOF'
{#schema
title: string!
items[]!:
  task: string!
  done: boolean
#}

{#data
title: スプリントタスク
items:
  - task: CI パイプライン構築
    done: true
  - task: API テスト作成
    done: false
  - task: ステージングデプロイ
    done: false
#}

# {{ title }}

| タスク | 完了 |
|--------|:----:|
{% for item in items %}| {{ item.task }} | {{ item.done }} |
{% endfor %}
EOF

gospelo-kata render todo_tpl.kata.md -o outputs/todo.kata.md
gospelo-kata lint outputs/todo.kata.md
```

### 2. 組み込みテンプレートを使う

```bash
# テンプレート一覧
gospelo-kata templates

# プロジェクトを初期化
gospelo-kata init --type checklist -o ./my-project/
```

### 3. AI ワークフロー (推奨)

AI は YAML データのみ生成し、`assemble` が組み込みテンプレートと結合します:

```bash
# 1. スキーマを確認
gospelo-kata show-schema checklist --format yaml

# 2. AI が スキーマに従って data.yml を作成

# 3. テンプレート + データを結合
gospelo-kata assemble --type checklist --data data.yml

# 4. レンダリングと検証
gospelo-kata render checklist_tpl.kata.md -o outputs/checklist.kata.md
gospelo-kata lint outputs/checklist.kata.md
```

### 4. データ抽出 (ラウンドトリップ)

```bash
gospelo-kata extract outputs/checklist.kata.md -o extracted.json
```

レンダリング済みドキュメントから元の構造化データを復元します。

## KATA Markdown フォーマット

`_tpl.kata.md` テンプレートファイルは3つのブロックで構成されます:

```markdown
{#schema
title: string!
version: string
categories[]!:
id: string!
name: string!
items[]!:
id: string!
status: enum(draft, pending, approve, reject)
tags: string[]
#}

{#data
title: セキュリティチェックリスト
version: "1.0"
categories:

- id: auth
  name: 認証・認可
  items: - id: auth-01
  status: draft
  tags: [web, api]
  #}

{#prompt
カテゴリと項目を含むセキュリティチェックリストを生成してください。
各項目には id、status (draft/pending/approve/reject)、tags が必要です。
#}

# {{ title }}

{% for cat in categories %}

## {{ cat.name }}

| ID                          | ステータス    | タグ              |
| --------------------------- | ------------- | ----------------- | ------------ | ------------- |
| {% for item in cat.items %} | {{ item.id }} | {{ item.status }} | {{ item.tags | join(", ") }} |

{% endfor %}
{% endfor %}
```

### スキーマショートハンド

| 記法                       | 意味                                        |
| -------------------------- | ------------------------------------------- |
| `string`                   | 任意文字列                                  |
| `string!`                  | 必須文字列                                  |
| `int`, `number`, `boolean` | 型付き値                                    |
| `enum(a, b, c)`            | 列挙型                                      |
| `string[]`                 | 文字列配列                                  |
| `items[]!:`                | 必須オブジェクト配列 (子をインデントで記述) |

### レンダリング出力

`gospelo-kata render` はアノテーション付き Markdown を出力します:

- `<span data-kata="p-{path}">value</span>` — データバインディング
- `<div data-kata-each="collection">` — ループマーカー
- `<details>` セクションに Schema + Data を付与 (再構築用)

## 組み込みテンプレート

| タイプ      | 説明                                                     |
| ----------- | -------------------------------------------------------- |
| `checklist` | カテゴリ・ステータス追跡・自動化レベル付きチェックリスト |
| `test_spec` | 前提条件と期待結果を含むテストケース仕様書               |
| `agenda`    | 決定事項・アクションアイテム・時間配分付き会議アジェンダ |

## CLI コマンド一覧

| コマンド          | 説明                                                          |
| ----------------- | ------------------------------------------------------------- |
| `templates`       | テンプレート一覧                                              |
| `init`            | テンプレートからプロジェクトを初期化                          |
| `render`          | `.kata.md` テンプレートをアノテーション付きでレンダリング     |
| `assemble`        | 組み込みテンプレート + データファイルを `_tpl.kata.md` に結合 |
| `lint`            | テンプレートとレンダリング済みドキュメントを検証              |
| `extract`         | レンダリング出力から構造化データを抽出                        |
| `validate`        | JSON/YAML データをスキーマに対して検証                        |
| `generate`        | JSON データから Markdown/Excel/HTML を生成                    |
| `show-schema`     | テンプレートのスキーマを表示                                  |
| `show-prompt`     | AI プロンプトを表示                                           |
| `fmt`             | `data-kata` span を自動フォーマット                           |
| `coverage`        | チェックリストカバレッジを分析                                |
| `edit`            | ブラウザベースのデータエディター                              |
| `workflow-status` | パイプラインの進捗管理                                        |

詳細は [CLI リファレンス](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/cli-reference.md) を参照。

## AI 連携

gospelo-kata は AI アシスタントとの連携を前提に設計されています。`assemble` コマンドにより、AI が生成するのはスキーマに従った YAML データだけで済みます。

**対応 AI ツール:**

- **Claude Code** — `skill/claude-code/` のスキルファイル
- **GitHub Copilot Chat** — `.github/copilot-instructions.md` による指示

3ステップワークフロー (`data.yml` → `assemble` → `render` + `lint`) は、コンテキストウィンドウの小さいモデルでも安定して動作します。

## VSCode 拡張機能

[VS Marketplace](https://marketplace.visualstudio.com/items?itemName=gospelo.kata-lint) からインストールできます。`kata-lint` 拡張機能の機能:

- Problems パネルへのリアルタイム lint 表示
- `data-kata` 属性のホバー情報
- kata 専用スタイルのプレビュー CSS

詳細は [VSCode 連携ガイド](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/vscode-integration.md) を参照。

## ドキュメント

- [クイックスタート](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/quick-start.md)
- [CLI リファレンス](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/cli-reference.md)
- [KATA Markdown フォーマット](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/kata-markdown-format.md)
- [Lint ルール一覧](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/lint-rules.md)
- [ワークフローガイド](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/workflow-guide.md)
- [VSCode 連携](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/vscode-integration.md)
- [Copilot セットアップ](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/copilot-setup.md)

## ライセンス

MIT — 商用利用を含め自由に利用できます。本ソフトウェアで生成したドキュメントやユーザーが作成したテンプレートの著作権はユーザーに帰属します。AI サービスと組み合わせて使用する場合、データが AI プロバイダーに送信される可能性があります。詳細は [LICENSE_ja.md](https://github.com/gospelo-dev/kata/blob/main/LICENSE_ja.md) を参照してください。
