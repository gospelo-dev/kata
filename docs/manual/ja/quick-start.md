# gospelo-kata クイックスタート

テンプレートを選んで、データを埋めるだけ。

---

## インストール

```bash
pip install gospelo-kata
```

---

## Step 1 — 空のドキュメントを作る

```bash
gospelo-kata templates                       # テンプレート一覧
gospelo-kata prepare agenda -o data.yml      # スケルトン YAML を生成
gospelo-kata build agenda data.yml -o ./ --no-validate   # 空の .kata.md を生成
```

`agenda.kata.md` ができます。中身はまだ空欄ですが、テンプレート・スキーマ・Data ブロックがすべて入った状態です。

## Step 2 — Data ブロックを編集する

`agenda.kata.md` を開き、末尾の `**Data**` セクション内の YAML を編集します。

```yaml
title: 週次定例ミーティング
date: "2026-03-24"
attendees:
  - name: 田中
    role: Chair
  - name: 鈴木
    role: Scribe
agenda:
  - id: A-01
    topic: 先週のアクションアイテム確認
  - id: A-02
    topic: リリース計画レビュー
```

> AI スキル (`/kata-gen` 等) を使えば、この YAML を自動生成することもできます。

## Step 3 — Sync してドキュメントを生成する

```bash
gospelo-kata sync agenda.kata.md -o agenda.kata.md
gospelo-kata lint agenda.kata.md
# → OK: agenda.kata.md — no issues found
```

Data ブロックの内容が本文に反映されます。修正したいときは Data を編集して `sync` を再実行するだけです。

---

## まとめ

```
build --no-validate  →  .kata.md (空)
         ↓
   Data ブロックを編集
         ↓
   sync  →  .kata.md (完成)  →  lint で検証
         ↓
   修正? → Data を編集 → sync (繰り返し)
```

ポイント:
- **編集するのは Data ブロックだけ**。テンプレートやスキーマに触れる必要はありません
- `sync` は何度でも実行できます。Data を変えて sync するだけで本文が更新されます
- `gospelo-kata export agenda.kata.md --part data` でデータだけ取り出せます

---

## 次のステップ

- [CLI リファレンス](cli-reference.md) — 全コマンド詳細
- [KATA Markdown™ フォーマット](kata-markdown-format.md) — テンプレート記法・セルフコンテインド方式
- [Lint ルール一覧](lint-rules.md) — エラーコード解説
- [スキルガイド](skill-guide.md) — AI スキルの使い方
- [VSCode 連携](vscode-integration.md) — 拡張機能の設定
