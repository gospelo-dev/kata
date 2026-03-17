# gospelo-kata クイックスタート

5分で始める KATA Markdown™ ドキュメント生成。

---

## インストール

```bash
pip install gospelo-kata
```

依存: **PyYAML** (必須)、**openpyxl** (Excel 出力時のみ)

---

## 方法 A: セルフコンテインド .kata.md から生成

テンプレート・スキーマ・データをすべて 1 ファイルに書く方法。最もシンプル。

### 1. ソースファイルを作成

```bash
cat > my_checklist.kata.md << 'EOF'
{#schema
title: string!
version: string
items[]!:
  id: string!
  name: string!
  status: enum(todo, done)
#}

{#data
title: セキュリティチェックリスト
version: 1.0
items:
  - id: SEC-01
    name: 入力バリデーション
    status: todo
  - id: SEC-02
    name: SQLインジェクション対策
    status: done
#}

# {{ title }}

> Version: {{ version }}

| ID | 項目 | ステータス |
|:--:|------|:----------:|
{% for item in items %}| {{ item.id }} | {{ item.name }} | {{ item.status }} |
{% endfor %}

Total: {{ items | length }} items
EOF
```

### 2. レンダリング

```bash
gospelo-kata render my_checklist.kata.md -o outputs/my_checklist.kata.md
```

出力 `.kata.md` には `data-kata` 属性と Schema/Data セクションが自動付与されます。

### 3. Lint 検証

```bash
gospelo-kata lint outputs/my_checklist.kata.md
```

### 4. データ抽出 (ラウンドトリップ)

```bash
gospelo-kata extract outputs/my_checklist.kata.md
```

rendered output から元の JSON データを復元できます。

---

## 方法 B: テンプレート + JSON で生成

組み込みテンプレートと JSON データを分離する方法。

### 1. テンプレート初期化

```bash
gospelo-kata init --type test_spec -o ./my_project/
```

`templates/`、`outputs/`、`.workflow_status.json` が生成されます。

### 2. JSON データを作成・バリデーション

```bash
gospelo-kata validate my_data.json --schema test_spec
```

### 3. ドキュメント生成

```bash
gospelo-kata generate my_data.json -f markdown -o output.kata.md
```

---

## ワークフロー概要

```
ソース (.kata.md)
  ↓ render
レンダリング済み (.kata.md)  ← data-kata属性 + Schema/Data
  ↓ lint
検証 (0 errors)
  ↓ extract
JSON データ復元 (ラウンドトリップ)
```

---

## 次のステップ

- [CLI リファレンス](cli-reference.md) — 全コマンド詳細
- [KATA Markdown™ フォーマット](kata-markdown-format.md) — テンプレート記法
- [Lint ルール一覧](lint-rules.md) — エラーコード解説
- [ワークフローガイド](workflow-guide.md) — 生成パイプライン管理
- [VSCode 連携](vscode-integration.md) — 拡張機能の設定
