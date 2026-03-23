# VS Code 連携

kata-lint VS Code 拡張機能の設定と使い方。

---

## インストール

```bash
cd vscode-kata-lint
npm install && npm run compile
npx vsce package
code --install-extension kata-lint-*.vsix
```

前提条件:
- `gospelo-kata` CLI が PATH に通っていること
- Python 3.11+

---

## 機能一覧

### 1. リアルタイム Lint

`.kata.md` ファイルの保存時・開いた時に自動で lint を実行し、Problems パネルにエラーを表示します。

### 2. LiveMorph (双方向同期)

Data ブロックと HTML 本文を双方向に同期。コンテキストメニューまたは保存時の自動実行に対応。

→ 詳細は [LiveMorph ガイド](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/livemorph.md)

### 3. ホバー情報

`data-kata` 属性にカーソルを合わせると、スキーマプロパティの型情報がポップアップ表示されます。

表示内容:
- プロパティ名
- 型 (`string`, `enum`, `array` 等)
- required / optional
- enum の許可値一覧
- minLength / maxLength

### 4. プレビュー CSS

`.kata.md` の Markdown プレビュー時に kata 専用スタイル (`kata-card` 等) が適用されます。

---

## コンテキストメニュー

`.kata.md` ファイル上で右クリック:

| メニュー項目 | 動作 |
|-------------|------|
| **Kata: Sync to HTML** | Data → 本文を同期 + モードを `toHtml` に設定 |
| **Kata: Sync to Data** | 本文 → Data を同期 + モードを `toData` に設定 |
| **Kata: Sync OFF** | 自動同期を無効化 |
| **Kata: Lint File** | lint のみ実行 |

---

## ステータスバー

`.kata.md` ファイルを開くと、ステータスバーに同期モードが表示されます。
クリックすると QuickPick でモードを切り替えられます。

| 表示 | 意味 |
|------|------|
| `Sync: OFF` | 自動同期なし |
| `→ Sync: to HTML` | 保存時に Data → 本文 |
| `← Sync: to Data` | 保存時に 本文 → Data |

---

## 設定一覧

`settings.json`:

```json
{
  "kataLint.lintOnSave": true,
  "kataLint.lintOnOpen": true,
  "kataLint.syncOnSave": "off",
  "kataLint.pythonPath": "python",
  "kataLint.severity.info": "Information",
  "kataLint.exclude": []
}
```

| 設定 | デフォルト | 説明 |
|------|-----------|------|
| `kataLint.lintOnSave` | `true` | 保存時に自動 lint |
| `kataLint.lintOnOpen` | `true` | ファイルを開いた時に自動 lint |
| `kataLint.syncOnSave` | `"off"` | 保存時の同期モード (`"off"` / `"toHtml"` / `"toData"`) |
| `kataLint.pythonPath` | `"python"` | Python のパス |
| `kataLint.severity.info` | `"Information"` | info レベルの表示 (Error/Warning/Information/Hint) |
| `kataLint.exclude` | `[]` | 除外パターン (glob) |

---

## タスク設定 (tasks.json)

`init-vscode` コマンドで lint タスクを自動生成:

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
          "file": 1, "line": 2, "column": 3,
          "severity": 4, "code": 5, "message": 6
        }
      },
      "group": "test",
      "presentation": { "reveal": "silent" }
    }
  ]
}
```

`Cmd+Shift+P` → `Tasks: Run Task` → `kata: lint current file` で実行。

---

## トラブルシューティング

### gospelo-kata が見つからない

```
kata-lint: gospelo-kata is not installed. Run: pip install gospelo-kata
```

`kataLint.pythonPath` を正しいパスに設定:

```json
{
  "kataLint.pythonPath": "/path/to/venv/bin/python"
}
```

### ホバーで型情報が表示されない

Specification セクションが `<details>` 内の YAML shorthand 形式であることを確認。

### 同期が動作しない

1. ステータスバーで同期モードが `OFF` 以外になっていることを確認
2. `gospelo-kata` CLI が動作することを確認: `gospelo-kata -V`
3. `Cmd+Shift+P` → `Developer: Reload Window` でリロード
