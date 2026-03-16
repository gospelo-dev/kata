# GitHub Copilot セットアップガイド (gospelo-kata)

gospelo-kata を GitHub Copilot Chat (VSCode) と連携するためのガイド。

## 前提条件

- VSCode に GitHub Copilot 拡張機能がインストール済み
- `gospelo-kata` CLI がインストール済み (`pip install gospelo-kata`)

## セットアップ手順

### 1. インストラクションファイルの有効化

`.vscode/settings.json` に以下を追加:

```json
{
  "github.copilot.chat.codeGeneration.useInstructionFiles": true
}
```

この設定により、Copilot が `.github/copilot-instructions.md` をチャットセッションごとに自動読み込みする。この設定がない場合、Copilot は gospelo-kata のワークフロールールに従わない。

### 2. ターミナルコマンドの自動承認 (任意)

Copilot が `mkdir` などのターミナルコマンド実行時に毎回許可を求める場合、以下を追加:

```json
{
  "chat.tools.terminal.autoApprove": {
    "mkdir": true
  }
}
```

### 3. インストラクションファイル

`.github/copilot-instructions.md` は `useInstructionFiles` が有効な場合に Copilot が自動読み込みする。このファイルで3ステップのワークフロールールを定義:

1. `data.yaml` を生成 (YAML データのみ)
2. `gospelo-kata assemble` を実行 (`_tpl.kata.md` を構築)
3. `gospelo-kata render` + `gospelo-kata lint` を実行 (最終出力を生成)

主要な指示:
- 3つのステップを確認なしで連続実行すること
- `.kata.md` ファイルを手動で作成しないこと
- `{#schema}`、`{#data}`、`{#prompt}` ブロックを手書きしないこと

### 4. カスタムスキル (任意)

スキルファイルは `skill/copilot/` に配置し、`.github/copilot/skills/` からシンボリックリンクで参照:

```
.github/copilot/skills/
  gospelo-kata     -> ../../../skill/copilot/gospelo-kata
  gospelo-kata-gen -> ../../../skill/copilot/gospelo-kata-gen
```

新しいスキルのシンボリックリンクを追加する場合:

```bash
ln -s ../../../skill/copilot/{skill-name} .github/copilot/skills/{skill-name}
```

> **注意**: `.github/copilot/skills/` のカスタムスキルは Copilot のバージョンによっては自動読み込みされない場合がある。`copilot-instructions.md` による指示の方が確実。

## ファイル構成

```
.github/
  copilot-instructions.md       <- 自動読み込みされるワークフロールール
  copilot/skills/               <- カスタムスキルのシンボリックリンク
.vscode/
  settings.json                 <- Copilot 設定
skill/
  copilot/                      <- Copilot スキルのソースファイル
    gospelo-kata/SKILL.md
    gospelo-kata-gen/SKILL.md
    gospelo-kata-import/SKILL.md
```

## 使い方

Copilot Chat で生成したい内容を記述するだけで動作する:

```
「リーダー人材定着プロジェクト」のセキュリティチェックリストを作成してください。
出力先: docs/output/
テンプレート: checklist
カテゴリ: 認証・認可(auth)、データ保護(data)、インフラ(infra)
```

Copilot は `copilot-instructions.md` で定義された3ステップのワークフローに従って自動実行する。

## トラブルシューティング

| 問題 | 原因 | 解決方法 |
|------|------|----------|
| Copilot が `.kata.md` を直接作成する | インストラクションが読み込まれていない | settings.json の `useInstructionFiles: true` を確認 |
| Step 1 の後に許可を求めて停止する | 「確認不要」指示が不足 | `copilot-instructions.md` に連続実行の指示があるか確認 |
| YAML 構造が崩れる (インデント不正) | モデルのコンテキスト制限 | `assemble` コマンドで AI のテンプレート責任範囲を最小化 |
| `@workspace /skill-name` でスキルが認識されない | Copilot バージョンの制限 | カスタムスキルではなく `copilot-instructions.md` を使用 |

## Claude Code との違い

| 項目 | Copilot | Claude Code |
|------|---------|-------------|
| インストラクション読み込み | `.github/copilot-instructions.md` (自動) | `.claude/skills/` または CLAUDE.md |
| スキルファイル | `skill/copilot/` | `skill/claude-code/` |
| 設定 | `.vscode/settings.json` | Claude Code 設定 |
| 確認動作 | 明示的な「確認不要」指示が必要 | エージェントモードで自動実行 |
| モデル | GPT-5 mini (コンテキスト小) | Claude (コンテキスト大) |
