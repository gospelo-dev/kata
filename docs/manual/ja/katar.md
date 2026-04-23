# テンプレートパッケージ --- KATA ARchive&#8482; (.katar)

カスタムテンプレートの作成・パッケージ化・配布方法。

---

## 概要

KATA ARchive (.katar) は gospelo-kata のテンプレートパッケージフォーマットです。
ZIP ベースで展開不要。`./templates/` に置くだけで即利用。

**設計原則: 1 パッケージ = 1 テンプレート = 1 スキーマ**

![KATA ARchive セキュリティアーキテクチャ](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/images/katar-security-architecture.jpg?raw=true)

---

## テンプレートの構成

```
my_template/
├── manifest.json             # メタデータ (必須)
├── my_template_tpl.kata.md   # テンプレート本体 (必須)
└── images/                   # 画像アセット (任意)
    └── my_template/          # テンプレート名で名前空間を切る
        └── ...
```

### 画像アセットのパス規約

同梱画像は Data から `./images/{テンプレート名}/...` の形で参照します。
素の `./images/...` ではなく**テンプレート名を挟む**ことで、画像アセットを
持つテンプレートを複数インストールしてもファイル衝突が起こりません。

`storyboard` テンプレートの Data の例:

```yaml
characters:
  - id: alice
    icon: ./images/storyboard/characters/alice.png
  - id: bob
    icon: ./images/storyboard/characters/bob.png
cuts:
  - id: C-001
    image: ./images/storyboard/C-001.jpg
```

`.katar` アーカイブ内部では `storyboard/images/storyboard/...` の
構造でアセットが格納されるため、パッケージ内とレンダリング先の
作業ディレクトリで同じ相対パスが成立します。

---

## クイックスタート

```bash
# 1. 雛形を生成
gospelo-kata pack-init ./my_template/

# 2. テンプレート本体を編集 (Prompt + Schema + Jinja2 テンプレート)

# 3. パッケージ化
gospelo-kata pack ./my_template/ -o my_template.katar

# 4. インストール (templates/ にコピーするだけ)
cp my_template.katar ./templates/

# 5. 利用
gospelo-kata prepare my_template -o data.yml
gospelo-kata build my_template data.yml -o outputs/
```

---

## manifest.json

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

| フィールド | 必須 | 説明 |
|-----------|:----:|------|
| `name` | Yes | テンプレート名 (コマンドの識別子) |
| `version` | Yes | セマンティックバージョニング |
| `template` | Yes | テンプレート本体のファイル名 |
| `description` | No | テンプレートの説明文 |
| `author` | No | 作者名 |
| `url` | No | リポジトリ URL |
| `license` | No | ライセンス (MIT, Apache-2.0 等) |
| `requires` | No | 依存する他テンプレート名の配列 |
| `attributions` | No | 同梱した第三者アセットのクレジット配列(下記参照) |

### attributions

オプション。テンプレートに同梱している画像やフォント等、第三者アセットの
出所・ライセンス情報を記録するフィールド。`.katar` を利用する側が
上流の再配布条件を守るための手がかりになります。

```json
{
  "attributions": [
    {
      "files": ["images/storyboard/characters/alice.png"],
      "source": "Custom-drawn pictogram",
      "license": "MIT",
      "copyright": "Copyright 2026 your-name",
      "notes": "手書きシルエットを 1440×1440 で描画し 128×128 にダウンサンプル"
    }
  ]
}
```

各エントリの内訳は厳密に定まっておらず、`files` / `source` / `license`
/ `copyright` / `notes` など必要なものだけ書きます。

---

## テンプレート本体 (`_tpl.kata.md`)

````markdown
**Prompt**

```yaml
このテンプレートはタスクリストを生成します。
items 配列に各タスクの詳細を記述してください。
```

# {{ title }}

| ID | タスク | ステータス |
|----|--------|:----------:|
{% for item in items %}| {{ item.id }} | {{ item.name }} | {{ item.status }} |
{% endfor %}

<details>
<summary>Specification</summary>

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

---

## 検索順序

1. `./templates/{name}/` (ローカル・ディレクトリ)
2. `./templates/{name}.katar` (ローカル・パッケージ)
3. `gospelo_kata/templates/{name}/` (ビルトイン・ディレクトリ)
4. `gospelo_kata/templates/{name}.katar` (ビルトイン・パッケージ)

ローカルに同名があればビルトインより優先。

---

## セキュリティ

### 信頼管理

- 初回使用時に `**Prompt**` の内容を表示し、ユーザーの承認を求める
- 承認は `.template_trust.json` に記録
- Prompt が変更された場合、再度確認が必要

### ファイル制限

パッケージに含められるファイル:

- `manifest.json`
- `*_tpl.kata.md` (テンプレート本体)
- 画像 (`.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`, `.ico`, `.bmp`)

### サイズ制限

| 制限 | 上限 |
|------|------|
| ファイル数 | 100 |
| 単一ファイル | 10 MB |
| 合計展開サイズ | 50 MB |

### 整合性検証

`pack` コマンドは全ファイルの SHA-256 ハッシュを `manifest.json` の `_integrity` に記録。
読み込み時に再計算して一致を確認し、不一致なら読み込みを拒否。

レンダリング済み `.kata.md` にも構造整合性ハッシュが埋め込まれ、`lint` の D017 ルールで検証されます。

Data ブロックはハッシュ対象外 (データ編集は正常な操作のため)。

---

## 配布方法

- **Git リポジトリ** --- `templates/` に含める
- **ファイル共有** --- Slack、メール等で送付
- **社内レジストリ** --- Artifactory 等に保管
