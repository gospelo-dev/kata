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

## data-kata 属性の仕組み

LiveMorph は `data-kata` 属性で Data と HTML を対応付けます。

```html
<span data-kata="p-title">Security Checklist</span>
<span data-kata="p-items-0-qty" data-kata-type="integer">42</span>
<span data-kata="p-items-0-status" data-kata-type="enum" data-kata-enum="done">done</span>
<span data-kata="p-items-0-done" data-kata-type="boolean">true</span>
```

- `p-` プレフィックス: プロパティパス
- 配列の index はアンカーに埋め込む: `p-items-0-qty` → `items[0].qty`。
  これにより同じ要素をテンプレートの別箇所から参照しても extract が
  `arr[i]` の同じスロットへ上書きするだけで済み、ソース配列が
  膨張する問題が発生しない
- `-` 区切り: ネストしたプロパティ (`categories.items.status`)
- `data-kata-type`: 元の JSON Schema 型。`string` 以外で出力される
  (string はデフォルトのため省略)。認識される値: `integer` /
  `number` / `boolean` / `enum` / `array`。extract 時の型復元に使う
- `data-kata-enum`: 許可値(VS Code ホバーで表示)
- `data-kata-each`: 配列ループマーカー

`sync to-data` はこれらの span から値を抽出し、`data-kata-type`
(ある場合)と Specification セクションの schema shorthand を使って
型を含めてデータを再構築します。

### 隠し span

テンプレートには表示させたくないが round-trip で保持したいフィールドは
隠し span で埋め込めます:

```html
<span data-kata="p-characters-0-id" hidden>alice</span>
```

`storyboard` テンプレートの `characters[].id` はこの方式で、
読者には見せないが schema 上必須のため `sync to-data` で消えない
ようにしています。

---

## sync で注釈外のフィールドを保持する

`sync to-data` は、抽出結果を**既存 Data ブロックへのパッチ**として
適用します(まるごと置換ではありません)。テンプレートが `data-kata`
を付けずにレンダリングする部分(画像 `src`、スキーマに無い HTML 断片
など)は旧 Data から温存されるので、一度の保存で情報が静かに消える
ことはありません。

マージ規則:

- **Top-level スカラー**: 抽出値が優先、抽出に無いキーは旧 Data のまま
- **配列**: 抽出の長さが正(UI 側での削除も反映される)。残った要素は
  同 index の旧要素とマージし、注釈されていないフィールドは旧側が残る
- **ネストした dict**: 同じ規則で再帰

この仕組みがないと、例えば storyboard の cut の `image` パスは
最初の `sync to-data` で消えてしまう(extract が拾うのは
`<span data-kata="…">` に包まれた値だけだからです)。

---

## 注意事項

- `toHtml` と `toData` は排他的。同時に有効にしない
- `data-kata` 属性や span タグを壊すと `sync to-data` が機能しなくなる
- enum 値を変更する場合、スキーマの許可値のみ使用する
- **型は schema から復元される**: `data-kata-type="integer"` で "42"
  の span は Data ブロック側で `42`(int)に戻る。string 型フィールドに
  `", "` が含まれていても、Specification が `string` と宣言していれば
  配列に分割されない
