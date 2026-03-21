# プロンプト設計ガイドライン

KATA テンプレートの `**Prompt**` ブロックを記述する際のルール。

---

## 設計原則

1. **英語のみ** — 一貫性のため英語で記述する
2. **3部構成** — (a) テンプレートの目的（1行）、(b) 主要フィールドのセマンティクス（2-3行）、(c) enum 等の制約の意味説明（0-2行）
3. **構文を書かない** — スキーマ記法、Jinja2 構文、出力構造はプロンプトに含めない
4. **ツール操作を書かない** — CLI コマンドやワークフロー手順は [SKILL.md](https://github.com/gospelo-dev/kata/tree/main/skill) 等に記載する
5. **スキーマが真実の源** — 型制約、必須フィールド、構造は Schema ブロックのみで定義する

---

## フォーマット

```yaml
{テンプレートが生成するものの1行説明}
{主要な配列/オブジェクトフィールドの埋め方: 2-3行}
{enum のセマンティクス説明（ドメイン固有の補足が必要な場合）: 0-2行}
```

目標: **3-6行**。

---

## 例

### 良い例（5行）

```yaml
This template generates a structured checklist document with categories and actionable items.
Each categories entry groups related items under an id and name.
Each item has a unique id, name (English), name_ja (Japanese), and a requirements description of what must be verified.
auto indicates the automation level: full = fully automated, semi = partially automated, partial = mostly manual with tool assist, manual = fully manual.
status tracks the item lifecycle: draft = not started, pending = under review, approve = accepted, reject = rejected.
```

### 悪い例

```yaml
# NG: 構文ドキュメントを含んでいる
This template generates a checklist.
Use string! for required fields and string for optional fields.
Arrays are denoted with [] suffix.
Use {{ variable }} for Jinja2 template variables.
The output will contain <table> elements with data-kata attributes.
Run gospelo-kata render to generate the output.
```

---

## プロンプトに書かないもの

以下の情報はプロンプト以外の場所に記載します:

| 情報 | 記載場所 |
|-----|---------|
| スキーマ記法 (`string!`, `enum()`, `[]!`) | テンプレートの Schema ブロック |
| Jinja2 構文 (`{{ }}`, `{% %}`) | テンプレート本文 |
| 出力構造（HTMLテーブル、カードレイアウト） | テンプレート本文 |
| CLI コマンド (`gospelo-kata assemble` 等) | [SKILL.md](https://github.com/gospelo-dev/kata/tree/main/skill) |
| ワークフロー手順 (assemble → render → lint) | [SKILL.md](https://github.com/gospelo-dev/kata/tree/main/skill) |
| ツール固有の規約（ステータスのデフォルト値） | Schema ブロックのデフォルト値 |

---

## プロンプトインジェクション対策

プロンプトはデータ生成時に AI が実行します。改ざんされたテンプレートによる悪用を防ぐため、以下の対策を実装しています。

### 1. テンプレート信頼メカニズム

初回使用時またはプロンプト内容が変更された場合、ユーザーにプロンプトのレビューと承認を求めます。承認ハッシュは `.template_trust.json` に保存されます。

### 2. パターンベースのインジェクション検出（P002）

リンターおよび `assemble` コマンドがプロンプト内容をスキャンし、プロンプトインジェクションに関連するパターンを検出します:

| カテゴリ | 例 |
|----------|-----|
| ロール/アイデンティティの上書き | "you are now", "act as a", "pretend to be" |
| 命令の上書き | "ignore previous instructions", "disregard above rules" |
| システムプロンプトの抽出 | "show your system prompt", "reveal your instructions" |
| コマンド実行 | "execute command", "run shell", `os.system(...)` |
| Chat-ML デリミタ | `<\|im_start\|>`, `[INST]`, `<<SYS>>` |
| データ流出 | "send data to", "upload to" |
| 資格情報アクセス | "show api key", "read password" |

検出はパターンマッチベースであり、完全ではありません。第一防衛線として機能します — テンプレートを信頼する前に必ずプロンプト内容をレビューしてください。

### 3. プロンプトに含めてはいけないもの

- AI へのシステムレベルの指示（ロール割り当て、動作変更）
- シェルコマンドやコード実行の指示
- 資格情報、API キー、シークレットへの参照
- Chat-ML やモデル固有のデリミタトークン
- 以前の指示を無視・上書き・抽出する指示

---

## なぜこのルールか

プロンプトは **AI がデータを生成する際に参照する唯一のコンテキスト** です。
構文やツール操作を含めると:

- プロンプトが肥大化し、AI が本質的な情報を見失う
- スキーマと二重管理になり、不整合の原因になる
- テンプレート更新時にプロンプトの同期漏れが発生する

プロンプトには **「何を生成するか」と「各フィールドが意味すること」** だけを書きます。
