# テンプレートパッケージ — KATA ARchive™ (.katar)

カスタムテンプレートの作成・パッケージ化・配布方法。

---

## 概要

KATA ARchive™ (`.katar`) は gospelo-kata のテンプレートパッケージフォーマットです。中身は標準的な ZIP 形式で、テンプレートに必要なファイル一式を1つのファイルにまとめます。

展開せずそのまま `./templates/` に配置するだけで、`prepare`、`build` などすべてのコマンドから利用できます。

**設計原則: 1パッケージ = 1テンプレート = 1スキーマ**

AI がスキーマを1つ読めばデータを生成できるよう、パッケージには1つのテンプレート（`_tpl.kata.md`）のみ含めます。複数テンプレートのデータを結合して Excel 等を生成する場合は、`generate` コマンドのオプション（`--prereq` 等）で対応します。

![KATA ARchive™ セキュリティアーキテクチャ](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/images/katar-security-architecture.jpg?raw=true)

---

## テンプレートの構成

テンプレートディレクトリに必要なファイル:

```
my_template/
├── manifest.json             # マニフェスト (必須)
├── my_template_tpl.kata.md   # テンプレート本体 (必須)
└── images/                   # 画像ファイル (任意)
```

### 追加ファイル

テンプレートディレクトリには `manifest.json` と `_tpl.kata.md` 以外に**画像ファイル**を含めることができます。

許可される画像形式: `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`, `.ico`, `.bmp`

用途の例:

- **ロゴ・アイコン** — ドキュメントに埋め込む画像アセット
- **図表・スクリーンショット** — テンプレートの補足資料

> **セキュリティ:** パッケージに含められるファイルはテンプレートと画像のみに制限されています。

---

## manifest.json

テンプレートのメタデータを定義するファイル。`pack` コマンドでパッケージ化する際に必須です。

```json
{
  "name": "my_template",
  "version": "1.0.0",
  "description": "Task list with status tracking",
  "author": "your-name",
  "url": "https://github.com/your-org/your-repo",
  "license": "MIT",
  "template": "my_template_tpl.kata.md",
  "requires": []
}
```

### フィールド

| フィールド | 必須 | 説明 |
|-----------|:----:|------|
| `name` | Yes | テンプレート名（コマンドで使用する識別子） |
| `version` | Yes | セマンティックバージョニング |
| `template` | Yes | テンプレート本体のファイル名 |
| `description` | No | テンプレートの説明文 |
| `author` | No | 作者名 |
| `url` | No | リポジトリやドキュメントの URL |
| `license` | No | ライセンス形式 (MIT, Apache-2.0 等) |
| `requires` | No | 依存する他テンプレート名の配列 |

### `requires` — テンプレート間の依存関係

複数テンプレートのデータを組み合わせて1つの成果物（Excel 等）を生成する場合、`requires` に依存先のテンプレート名を記述します。

```json
{
  "name": "test_spec",
  "requires": ["test_prereq"]
}
```

`prepare` 実行時に依存情報が表示され、AI は必要なテンプレートすべてのデータを生成できます:

```
$ gospelo-kata prepare test_spec
...
Requires: test_prereq
  → gospelo-kata prepare test_prereq
```

### `pack-init` でテンプレートを新規作成

```bash
gospelo-kata pack-init ./my_template/
```

以下の構成が自動生成されます:

```
my_template/
├── manifest.json             # マニフェスト (自動生成)
├── my_template_tpl.kata.md   # テンプレート本体 (空の雛形)
├── images/                   # 画像ファイル配置先 (任意)
└── outputs/                  # レンダリング出力先
```

既存ディレクトリに対して実行した場合は、`_tpl.kata.md` ファイルを自動検出して `manifest.json` の雛形を生成します。

---

## テンプレート本体 (`_tpl.kata.md`)

`**Prompt**`、`**Schema**`、`**Data**` ブロックと Jinja2 互換テンプレートを含むファイル。ファイル名は `manifest.json` の `template` フィールドで指定します。

````markdown
**Prompt**

```yaml
このテンプレートはタスクリストを生成します。
items 配列に各タスクの詳細を記述してください。
status は draft または done を指定してください。
```

# {{ title }}

> Version: {{ version }}

| ID | タスク | ステータス |
|----|--------|:----------:|
{% for item in items %}| {{ item.id }} | {{ item.name }} | {{ item.status }} |
{% endfor %}

<details>
<summary>Schema Reference</summary>

**Schema**

```yaml
title: string!
version: string
items[]!:
  id: string!
  name: string!
  status: enum(draft, done)
```

**Data**

```yaml
```

</details>
````

**ポイント:**

- `**Prompt**` + `` ```yaml `` — AI がデータ生成時に参照する説明文
- `**Schema**` + `` ```yaml `` — AI がデータ構造を理解するためのスキーマ定義
- `**Data**` + `` ```yaml `` — `build` コマンドがデータを挿入する位置（空でも記述推奨）
- テンプレート本文 — Jinja2 互換構文で記述

---

## パッケージ化

`.katar` の作成は `gospelo-kata pack` コマンドのみで行います。手動で ZIP ファイルを作成・リネームしないでください。

### 手順

```bash
# 1. テンプレートの雛形を生成
gospelo-kata pack-init ./my_template/

# 2. テンプレート本体を編集
#    my_template/my_template_tpl.kata.md に **Prompt**, **Schema**, テンプレートを記述

# 3. manifest.json を編集
#    author, url, license 等を記入

# 4. パッケージ化
gospelo-kata pack ./my_template/
```

`my_template.katar` が生成されます。

出力先を指定する場合:

```bash
gospelo-kata pack ./my_template/ -o ./dist/my_template.katar
```

### バリデーション

`pack` コマンドは以下を検証します:

- `manifest.json` が存在すること
- `name`, `version`, `template` フィールドがあること
- `template` で指定されたファイルが存在すること

---

## インストール

### `init --from-package` でインストール

```bash
gospelo-kata init --from-package my_template.katar
```

`./templates/my_template.katar` にコピーされます（展開されません）。

### 手動配置

`.katar` ファイルを直接 `./templates/` にコピーしても動作します:

```bash
cp my_template.katar ./templates/
```

---

## 使い方

インストール後は組み込みテンプレートと同じように利用できます:

```bash
# テンプレート一覧で確認（バージョンも表示されます）
gospelo-kata templates

# Prompt + Schema 確認、スケルトン data.yml 生成
gospelo-kata prepare my_template -o data.yml

# data.yml を編集後、ビルド + 検証
gospelo-kata build my_template data.yml -o outputs/
gospelo-kata lint outputs/my_template.kata.md
```

---

## テンプレートの検索順序

コマンド実行時のテンプレート検索順序:

1. **ローカル** `./templates/{name}/` (ディレクトリ)
2. **ローカル** `./templates/{name}.katar` (パッケージ)
3. **ビルトイン** `gospelo_kata/templates/{name}/` (ディレクトリ)
4. **ビルトイン** `gospelo_kata/templates/{name}.katar` (パッケージ)

ローカルに同名のテンプレートがあれば、ビルトインより優先されます。

---

## テンプレート作成のベストプラクティス

### スキーマ設計

- 必須フィールドには `!` を付ける (`string!`, `items[]!:`)
- enum で選択肢を制限する (`enum(draft, pending, approve, reject)`)
- `name_ja` フィールドを用意して多言語対応に備える

### プロンプト設計

- テンプレートの目的を簡潔に説明する
- 各フィールドの意味と制約を記述する
- AI が迷わないよう具体例を含める

### テスト

パッケージ化の前にテンプレートが正しく動作するか確認:

```bash
# テストデータでビルド + lint
gospelo-kata build my_template test_data.yml -o outputs/
gospelo-kata lint outputs/my_template.kata.md

# ラウンドトリップ確認
gospelo-kata extract outputs/my_template.kata.md
```

---

## AI スキルでの利用

Claude Code や GitHub Copilot で `/gospelo-kata-pack` スキルを使うと、テンプレートの展開・修正・再パック・テストを AI が一気に実行できます。

```
/gospelo-kata-pack
```

スキルの詳細は `skill/claude-code/gospelo-kata-pack/SKILL.md` を参照。

---

## 配布

`.katar` ファイルは以下の方法で配布できます:

- **Git リポジトリ** — プロジェクトの `templates/` に含める
- **ファイル共有** — Slack、メール等で直接送付
- **社内パッケージレジストリ** — Artifactory 等に保管

`.katar` は単一ファイルなので、どの方法でも簡単に配布できます。

---

## セキュリティ

安全対策として、テンプレートは**ユーザーが明示的に許可したもの**のみ AI ワークフロー（`build` コマンド等）で使用できます。

### テンプレートの信頼管理

- 初めて使用するテンプレートは、`**Prompt**` ブロックの内容が表示され、ユーザーの確認が求められます
- 許可すると `.template_trust.json` に記録され、以降は確認なしで利用できます
- テンプレートの `**Prompt**` が変更された場合、再度確認が必要になります

```bash
# Prompt + Schema を確認
gospelo-kata prepare my_template

# build 時に未許可テンプレートは確認を求められる
gospelo-kata build my_template data.yml -o outputs/
```

### パッケージのファイル制限

パッケージに含められるファイルは以下のみに制限されています:

- `manifest.json`
- `*_tpl.kata.md` (テンプレート本体)
- 画像ファイル (`.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`, `.ico`, `.bmp`)

上記以外のファイルは `pack` コマンドで拒否され、読み込み時もアクセスできません。

### パッケージのサイズ制限

悪意あるパッケージからの保護として、以下のサイズ制限が適用されます:

| 制限項目 | 上限値 |
|---------|--------|
| ファイル数 | 100 ファイル |
| 単一ファイルサイズ | 10 MB |
| 合計展開サイズ | 50 MB |

制限を超えるパッケージはエラーとなり、読み込まれません。

### パッケージの整合性検証

`.katar` パッケージには**改ざん検出**の仕組みが組み込まれています。

**仕組み:**

1. `gospelo-kata pack` でパッケージを作成する際、全ファイルの内容から SHA-256 ハッシュ値を計算します
2. 計算したハッシュ値を `manifest.json` の `_integrity` フィールドに記録します
3. パッケージを読み込む際、ファイル内容から再度ハッシュ値を計算し、`_integrity` と一致するか確認します
4. 一致しなければ「パッケージが改ざんされた」と判断し、読み込みを拒否します

これは「封筒の封印」のようなものです。封印が破られていれば中身が改ざんされた可能性があるとわかります。

### レンダリング済みドキュメントの構造整合性

レンダリング済み `.kata.md` ファイルにも改ざん検出の仕組みがあります。

**仕組み:**

1. `gospelo-kata build`（または `render`）実行時、`<details>` セクション内の Prompt・テンプレート本体・Schema からハッシュ値を計算します（Data ブロックは除外）
2. 計算したハッシュ値を HTML コメント `<!-- kata-structure-integrity: sha256:... -->` として埋め込みます
3. `gospelo-kata lint` 実行時、同じ計算を再度行い、埋め込みハッシュと照合します
4. 不一致の場合、`D017` warning を報告します

Data ブロックを除外しているのは、ユーザーがデータを編集するのは正常な操作だからです。検出したいのは、テンプレート構造（Prompt・Schema・テンプレート本体）の意図しない変更です。

### なぜこの仕組みを公開しても安全なのか

暗号学には**ケルクホフスの原則**という考え方があります。「セキュリティはアルゴリズムを秘密にすることではなく、鍵を秘密にすることで保つべき」という原則です。

gospelo-kata のハッシュ検証は、世界中で広く使われている SHA-256 アルゴリズムに基づいています。仕組みを知っていても、ハッシュ値が一致するようにファイル内容を改ざんすることは計算上不可能です。つまり、アルゴリズムを公開しても安全性は変わりません。

### 整合性検証の限界と補完

ここで重要な注意点があります。

**整合性検証は「改ざん検出」であり、「作成者の証明」ではありません。**

たとえば、攻撃者が `gospelo-kata pack` コマンドを使って悪意あるテンプレートを作成した場合、そのパッケージのハッシュ値は正しく計算されます。整合性検証だけでは「誰が作ったか」は判断できません。

この限界を補うのが**信頼管理（Trust）**の仕組みです:

- 未知のテンプレートを初めて使う際、`**Prompt**` の内容が表示され、ユーザーの明示的な承認が必要です
- 承認なしにテンプレートが自動実行されることはありません
- テンプレートの `**Prompt**` が変更された場合、再度確認が求められます

整合性検証と信頼管理の2層構造により、「改ざんされていないこと」と「ユーザーが意図的に許可したこと」の両方を確認できます。

### 既知の懸念事項

| 懸念 | 対策状況 |
|------|---------|
| 悪意ある第三者が正規の `.katar` を作成できる | 信頼管理（Prompt 承認）で補完。初回利用時にユーザー確認が必須 |
| `.katar` の作成者を暗号学的に証明できない | 現時点ではデジタル署名に未対応。配布元の信頼性はユーザーが判断する必要がある |
| AI が Prompt の安全性を正しく評価できない | Prompt の内容はユーザーに表示される。最終判断はユーザーが行う |
| レンダリング後に Data ブロックが改ざんされる可能性 | Data は構造ハッシュの対象外。Data の正確性はスキーマバリデーション（lint）で検証 |
