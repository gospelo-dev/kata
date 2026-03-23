# クイックスタート

テンプレートを選んで、ビルドして、Data を編集するだけ。

---

## インストール

```bash
pip install gospelo-kata
```

---

## Step 1 --- テンプレートを選んでビルド

```bash
gospelo-kata templates                       # 一覧を表示
gospelo-kata build todo -o ./                # 初期値で todo.kata.md を生成
```

テンプレート内蔵のサンプルデータで `.kata.md` が生成されます。

## Step 2 --- Data ブロックを編集

生成された `.kata.md` の `<details>` 内にある **Data** ブロックの YAML を直接編集します。

```yaml
title: スプリントタスク
items:
  - id: "1"
    task: CI パイプライン構築
    status: done
  - id: "2"
    task: API テスト作成
    status: todo
```

## Step 3 --- sync to-html で本文を更新

```bash
gospelo-kata sync to-html todo.kata.md
```

Data の変更がテンプレートを通じて本文に反映されます。

## Step 4 --- 検証

```bash
gospelo-kata lint todo.kata.md
# → OK: todo.kata.md — no issues found
```

---

## LiveMorph で編集を続ける

### Data を変えたい → `sync to-html`

Data ブロックを編集してから:

```bash
gospelo-kata sync to-html todo.kata.md
```

### 本文を直接変えたい → `sync to-data`

本文中の span の値を編集してから:

```bash
gospelo-kata sync to-data todo.kata.md
```

> VS Code 拡張を使えば、保存時に自動で LiveMorph が実行されます。→ [VS Code 連携](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/vscode.md)

---

## まとめ

```
build    →  .kata.md (初期値で生成)  →  lint で検証
    ↓
Data 編集 → sync to-html (繰り返し)
本文編集  → sync to-data (繰り返し)
```

- **編集するのは Data ブロックまたは本文の span だけ**
- テンプレートやスキーマに触れる必要はありません

---

## 次のステップ

- [LiveMorph ガイド](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/livemorph.md) --- 双方向同期の詳細
- [テンプレート一覧](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/templates.md) --- 組み込みテンプレート
- [CLI リファレンス](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/cli-reference.md) --- 全コマンド詳細
- [VS Code 連携](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/vscode.md) --- 拡張機能の設定
