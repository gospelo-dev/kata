# gospelo-kata クイックスタート

5分で始める KATA Markdown™ ドキュメント生成。

---

## インストール

```bash
pip install gospelo-kata
```

依存: **PyYAML** (必須)、**openpyxl** (Excel 出力時のみ)

---

## 方法 A: テンプレート + data.yml で生成 (推奨)

組み込みテンプレートと YAML データを使う方法。最も実用的。

### 1. テンプレートを確認

```bash
gospelo-kata templates              # 一覧表示
gospelo-kata prepare checklist      # Prompt + Schema を確認
```

### 2. data.yml を作成

```bash
gospelo-kata prepare checklist -o data.yml   # スケルトン生成
```

生成された `data.yml` を編集してデータを入力します。AI スキル (`/kata-gen` 等) を使って自動生成することもできます。

### 3. ビルド + 検証

```bash
gospelo-kata build checklist data.yml -o outputs/
gospelo-kata lint outputs/checklist.kata.md
```

`build` はテンプレートとデータの結合・レンダリングをワンステップで実行します。

### 4. データ抽出 (ラウンドトリップ)

```bash
gospelo-kata extract outputs/checklist.kata.md
```

rendered output から元のデータを復元できます。

---

## 方法 B: セルフコンテインド .kata.md から生成

テンプレート・スキーマ・データをすべて 1 ファイルに書く方法。

### 1. ソースファイルを作成

````bash
cat > my_checklist.kata.md << 'EOF'
**Prompt**

```yaml
このテンプレートはタスクチェックリストを生成します。
items 配列に id, name, status を記述してください。
status は todo/done のいずれかを指定してください。
```

# {{ title }}

> Version: {{ version }}

| ID | 項目 | ステータス |
|:--:|------|:----------:|
{% for item in items %}| {{ item.id }} | {{ item.name }} | {{ item.status }} |
{% endfor %}

Total: {{ items | length }} items

<details>
<summary>Schema Reference</summary>

**Schema**

```yaml
title: string!
version: string
items[]!:
  id: string!
  name: string!
  status: enum(todo, done)
```

**Data**

```yaml
title: セキュリティチェックリスト
version: 1.0
items:
  - id: SEC-01
    name: 入力バリデーション
    status: todo
  - id: SEC-02
    name: SQLインジェクション対策
    status: done
```

</details>
EOF
````

### 2. レンダリング

```bash
gospelo-kata render my_checklist.kata.md -o outputs/my_checklist.kata.md
```

出力 `.kata.md` には `data-kata` 属性と Schema/Data セクションが自動付与されます。

### 3. Lint 検証

```bash
gospelo-kata lint outputs/my_checklist.kata.md
```

---

## ワークフロー概要

```
prepare → data.yml 作成 → build → lint → (修正ループ)
```

```
テンプレート + data.yml
  ↓ build (assemble + render)
レンダリング済み (.kata.md)  ← data-kata属性 + Schema/Data
  ↓ lint
検証 (0 errors)
  ↓ extract
データ復元 (ラウンドトリップ)
```

---

## 次のステップ

- [CLI リファレンス](cli-reference.md) — 全コマンド詳細
- [KATA Markdown™ フォーマット](kata-markdown-format.md) — テンプレート記法
- [Lint ルール一覧](lint-rules.md) — エラーコード解説
- [スキルガイド](skill-guide.md) — AI スキルの使い方
- [VSCode 連携](vscode-integration.md) — 拡張機能の設定
