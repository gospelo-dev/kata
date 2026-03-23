# LiveMorph --- 双方向リアルタイム同期

Data ブロックと HTML 本文を双方向に同期。どちらを編集しても、もう一方が自動更新されます。

---

## 概念

![LiveMorph コンセプト図](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/images/livemorph-concept.jpg?raw=true)

| 方向 | コマンド | 動作 |
|------|---------|------|
| Data → HTML | `sync to-html` | Data を編集 → テンプレート再実行 → 本文を更新 |
| HTML → Data | `sync to-data` | 本文の span を編集 → Data に抽出 → 再レンダリング |

---

## 基本ワークフロー

```bash
# 1. テンプレートから .kata.md を生成 (初期値)
gospelo-kata build todo -o ./

# 2. .kata.md の Data ブロックを編集

# 3. 本文に反映
gospelo-kata sync to-html todo.kata.md

# 4. 検証
gospelo-kata lint todo.kata.md
```

以後は Data 編集 → `sync to-html` の繰り返し。外部 data.yml は不要。

---

## CLI

```bash
gospelo-kata sync to-html document.kata.md   # Data → 本文
gospelo-kata sync to-data document.kata.md   # 本文 → Data
```

---

## VS Code

### コンテキストメニュー (右クリック)

| メニュー | 動作 |
|---------|------|
| **Sync to HTML** | Data → 本文 + モードを `toHtml` に設定 |
| **Sync to Data** | 本文 → Data + モードを `toData` に設定 |
| **Sync OFF** | 自動同期を無効化 |
| **Lint File** | lint のみ実行 |

### ステータスバー

| 表示 | 意味 |
|------|------|
| `Sync: OFF` | 自動同期なし |
| `→ Sync: to HTML` | 保存時に Data → 本文 |
| `← Sync: to Data` | 保存時に 本文 → Data |

クリックで QuickPick からモード切替。

### 設定

```json
{ "kataLint.syncOnSave": "off" }
```

`"off"` (デフォルト) / `"toHtml"` / `"toData"`

---

## 注意事項

- `toHtml` と `toData` は排他的。同時に有効にしない
- `data-kata` 属性や span タグを壊すと `sync to-data` が機能しなくなる
- enum 値を変更する場合、スキーマの許可値のみ使用する
