# VSCode 連携ガイド

kata-lint VSCode 拡張機能の設定と使い方。

---

## 拡張機能のインストール

### VSIX からインストール

```bash
# ビルド
cd vscode-kata-lint
npm install && npm run compile
npx vsce package

# インストール
code --install-extension kata-lint-0.1.0.vsix
```

### 前提条件

- `gospelo-kata` CLI がインストール済みで、PATH が通っていること
- Python 3.11+

---

## 機能一覧

### 1. リアルタイム Lint

`.kata.md` ファイルの保存時・開いた時に自動で lint を実行し、Problems パネルにエラーを表示します。

**設定** (`settings.json`):

```json
{
  "kataLint.lintOnSave": true,
  "kataLint.lintOnOpen": true,
  "kataLint.pythonPath": "python",
  "kataLint.severity.info": "Information",
  "kataLint.exclude": []
}
```

| 設定 | デフォルト | 説明 |
|------|-----------|------|
| `kataLint.lintOnSave` | `true` | 保存時に自動 lint |
| `kataLint.lintOnOpen` | `true` | ファイルを開いた時に自動 lint |
| `kataLint.pythonPath` | `"python"` | Python のパス |
| `kataLint.severity.info` | `"Information"` | info レベルの表示 (Error/Warning/Information/Hint) |
| `kataLint.exclude` | `[]` | 除外パターン (glob) |

### 2. ホバー情報

`data-kata` 属性にカーソルを合わせると、スキーマプロパティの型情報がポップアップ表示されます。

**表示内容**:
- プロパティ名
- 型 (`string`, `enum`, `array` 等)
- required / optional
- enum の許可値一覧
- minLength / maxLength

**対応フォーマット**: Schema Reference セクションの YAML shorthand コードブロックから情報を読み取ります。

```html
<!-- カーソルをここに合わせると → -->
<span data-kata="p-test-cases-priority">high</span>
```

ポップアップ:
```
**test_cases.priority**
- type: `enum` *(required)*
- enum: `high` | `medium` | `low`
```

### 3. データ同期 (Sync Data)

`.kata.md` ファイルを保存すると、本文中の `data-kata` span の値が Schema Reference 内の Data YAML ブロックに自動同期されます。

**動作の流れ**:
1. ファイル保存 (⌘+S)
2. `gospelo-kata fmt` が自動実行され、span の値を Data YAML に反映
3. エディタが更新される
4. lint が再実行される

**手動実行**: エディタ上で右クリック → 「Kata: Sync Data」

**設定** (`settings.json`):

```json
{
  "kataLint.syncOnSave": true
}
```

| 設定 | デフォルト | 説明 |
|------|-----------|------|
| `kataLint.syncOnSave` | `true` | 保存時に自動データ同期 |

> **注意**: Data YAML は span から自動生成される読み取り専用のスナップショットです。値の編集は常に本文の span 側で行ってください。

### 4. プレビュー CSS

`.kata.md` の Markdown プレビュー時に kata 専用スタイル (`kata-card` 等) が適用されます。

---

## タスク設定 (tasks.json)

`init-vscode` コマンドで lint-on-save タスクを生成:

```bash
gospelo-kata init-vscode --output .vscode
```

生成される `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "kata: lint current file",
      "type": "shell",
      "command": "gospelo-kata",
      "args": ["lint", "--format", "vscode", "${file}"],
      "problemMatcher": {
        "owner": "kata-lint",
        "fileLocation": "absolute",
        "pattern": {
          "regexp": "^(.+):(\\d+):(\\d+):\\s+(error|warning|info)\\s+\\[(.+?)\\]\\s+(.+)$",
          "file": 1,
          "line": 2,
          "column": 3,
          "severity": 4,
          "code": 5,
          "message": 6
        }
      },
      "group": "test",
      "presentation": { "reveal": "silent" }
    }
  ]
}
```

**使い方**:
1. `Cmd+Shift+P` → `Tasks: Run Task` → `kata: lint current file`
2. エラーは Problems パネルに表示

---

## トラブルシューティング

### gospelo-kata が見つからない

```
kata-lint: gospelo-kata is not installed. Run: pip install gospelo-kata
```

**対処**: `kataLint.pythonPath` を正しい Python パスに設定:

```json
{
  "kataLint.pythonPath": "/path/to/venv/bin/python"
}
```

### ホバーで型情報が表示されない

**原因**: Schema Reference セクションが `<details>` 内の YAML shorthand 形式であることを確認。

**必要な構造**:
```html
<details>
<summary>Schema Reference</summary>

**Schema**

```yaml
property_name: type!
```

</details>
```

レガシー形式 (`#### <a id="p-xxx">`) にも対応していますが、YAML shorthand が優先されます。

### lint 結果が更新されない

`Cmd+Shift+P` → `Developer: Reload Window` でリロード。
