# Unified Block Format

**更新日**: 2026-03-18
**バージョン**: 0.2.1

## 概要

テンプレートファイル（`_tpl.kata.md`）と出力ファイル（`outputs/*.kata.md`）のブロック形式を統一。
`{#schema}` / `{#data}` / `{#prompt}` の独自マーカー形式を非推奨とし、`**Schema**` / `**Data**` / `**Prompt**` + `` ```yaml `` コードブロック形式を推奨形式に変更。
テンプレートと出力の両方で `<details>` 内にスキーマ・データ・プロンプト・テンプレート本体を保持し、出力ファイルが自己完結する構成に変更。

## 変更内容

### 1. ブロック形式の統一（template.py）

**問題**: テンプレートは `{#schema ... #}` 形式、出力は `**Schema**` + `` ```yaml `` 形式で、パーサーが出力ファイルのスキーマを認識できなかった。

**修正内容**:

- `_SCHEMA_BOLD_CODEBLOCK_PATTERN` を追加: `**Schema**` + `` ```yaml `` 形式のスキーマ検出
- `_PROMPT_CODEBLOCK_PATTERN` を追加: `**Prompt**` + `` ```yaml `` 形式のプロンプト検出
- `_DATA_BOLD_CODEBLOCK_PATTERN` を追加: `**Data**` + `` ```yaml `` 形式のデータ検出
- `extract_schema` / `extract_data` でBold+コードブロック形式をフォールバック対応
- `Template` クラスで `prompt` と `template_body` をパースし `generate_schema_reference` に渡す
- `_strip_details_wrapper` を改善: `<details>` 内に複数ブロックがある場合スキーマのみ除去

### 2. リンターの拡張（linter.py）

**問題**: P001（プロンプト必須チェック）とS000（スキーマ検出）がBold+コードブロック形式に非対応。出力ファイルのテンプレートコードブロック内の `{{` `{%` がテンプレートモード判定を誤発動させていた。

**修正内容**:

- `_check_prompt_block`: `_PROMPT_CODEBLOCK_PATTERN` にも対応
- `_check_schema`: `_SCHEMA_BOLD_CODEBLOCK_PATTERN` にも対応
- `lint_file`: コードブロック内のテンプレート構文を除外してモード判定（`text_no_codeblocks`）

### 3. テストの追加

**修正内容**:

- `test_template.py`: Bold+コードブロック形式のスキーマ・データ・プロンプト抽出、`_strip_details_wrapper` マルチブロック対応、`generate_schema_reference` 出力構造のテスト（25テスト追加）
- `test_linter.py`: Bold形式のスキーマ/プロンプト検出、不正YAML、P001警告、コードブロック内テンプレート構文のモード判定テスト（6テスト追加）

### 4. サンプルファイルの再構成

**修正内容**:

- `docs/samples/` をEN/JA言語別ディレクトリに分離（`docs/samples/en/`, `docs/samples/ja/`）
- テンプレート・出力すべて新しいBold+コードブロック形式に移行
- 英語版サンプルを新規作成（Prompt・Data を英訳）

### 5. ドキュメント全面更新（旧形式を非推奨化）

**修正内容**:

- `kata-markdown-format.md`（EN/JA）: ソース構成・各ブロック説明・Schema Reference・ラウンドトリップ図をすべてBold+コードブロック形式に書き換え、旧形式は非推奨注記のみ
- `lint-rules.md`（EN/JA）: テンプレートモード説明、S対処、P001ルールを追記
- `quick-start.md`（EN/JA）: サンプルコードをBold+コードブロック形式に全面書き換え
- `cli-reference.md`（EN/JA）: `{#prompt}`/`{#schema}`/`{#data}` の参照をすべて更新
- `copilot-setup.md`（EN/JA）: ワークフロールールの記述を更新
- `template-package.md`（JA）: テンプレート本体のコード例・テキスト参照を更新

### 6. VSCode設定

**修正内容**:

- `.vscode/settings.json`: Markdownの `editor.formatOnSave` を無効化（YAMLインデント保護）

## 影響範囲

- テンプレートパーサー: 新しいブロック形式のサポート追加（旧形式は後方互換として維持）
- リンター: テンプレート/ドキュメントモード判定の改善
- 出力ファイル: 自己完結するファイル構成
- ドキュメント: 全マニュアルで旧形式を非推奨化、Bold+コードブロック形式のみ記載
- サンプル: EN/JA言語別ディレクトリ構成に移行

## テスト結果

- 全304テスト: 成功

## 関連ファイル

- `gospelo_kata/template.py`
- `gospelo_kata/linter.py`
- `tests/test_template.py`
- `tests/test_linter.py`
- `docs/samples/en/` (新規)
- `docs/samples/ja/` (新規)
- `docs/manual/en/kata-markdown-format.md`
- `docs/manual/en/lint-rules.md`
- `docs/manual/en/quick-start.md`
- `docs/manual/en/cli-reference.md`
- `docs/manual/en/copilot-setup.md`
- `docs/manual/ja/kata-markdown-format.md`
- `docs/manual/ja/lint-rules.md`
- `docs/manual/ja/quick-start.md`
- `docs/manual/ja/cli-reference.md`
- `docs/manual/ja/copilot-setup.md`
- `docs/manual/ja/template-package.md`
- `.vscode/settings.json`

## コミットコマンド

### 1. 統一ブロック形式対応 + テスト

```bash
git add gospelo_kata/template.py gospelo_kata/linter.py tests/test_template.py tests/test_linter.py development/update_logs/20260318-120848_unified-block-format.md && git commit -m "$(cat <<'EOF'
feat: support unified block format for schema, data, and prompt

- Add **Schema**/**Data**/**Prompt** + ```yaml code block patterns
- Fix template/document mode detection to ignore code blocks
- Include prompt and template body in Schema Reference output
- Improve _strip_details_wrapper for multi-block <details>
- Add 31 tests for unified block format support

EOF
)"
```

### 2. サンプルファイルの再構成（EN/JA分離）

```bash
git rm docs/samples/01_minimal_tpl.kata.md docs/samples/02_web_security_tpl.kata.md docs/samples/03_api_testing_tpl.kata.md docs/samples/04_infra_audit_tpl.kata.md docs/samples/outputs/01_minimal.kata.md docs/samples/outputs/02_web_security.kata.md docs/samples/outputs/03_api_testing.kata.md docs/samples/outputs/04_infra_audit.kata.md && git add docs/samples/en/ docs/samples/ja/ && git commit -m "$(cat <<'EOF'
docs: reorganize samples into en/ja directories with unified block format

- Split samples into docs/samples/en/ and docs/samples/ja/
- Create English translations of templates and rendered outputs
- Migrate all samples to **Prompt** + **Schema** + **Data** format

EOF
)"
```

### 3. ドキュメント全面更新 + バージョンアップ + skill ZIP

```bash
git add docs/manual/en/kata-markdown-format.md docs/manual/en/lint-rules.md docs/manual/en/quick-start.md docs/manual/en/cli-reference.md docs/manual/en/copilot-setup.md docs/manual/ja/kata-markdown-format.md docs/manual/ja/lint-rules.md docs/manual/ja/quick-start.md docs/manual/ja/cli-reference.md docs/manual/ja/copilot-setup.md docs/manual/ja/template-package.md pyproject.toml gospelo_kata/__init__.py vscode-kata-lint/package.json skill/gospelo-kata-skill-claude-code-v0.2.1.zip skill/gospelo-kata-skill-copilot-v0.2.1.zip && git commit -m "$(cat <<'EOF'
release: v0.2.1 — unified block format, deprecate legacy {#...#} syntax

- Bump version to 0.2.1
- Rewrite all manual pages to use Bold+codeblock format
- Mark {#schema}/{#data}/{#prompt} as deprecated
- Rebuild skill ZIPs for v0.2.1

EOF
)"
```
