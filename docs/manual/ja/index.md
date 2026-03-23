# gospelo-kata

**KATA Markdown&#8482;** --- テンプレートから構造化ドキュメントを生成・検証・双方向同期するツールキット。

```
pip install gospelo-kata
```

---

### LiveMorph --- 双方向リアルタイム同期

Data と HTML を自由に行き来。編集した側がもう一方に即座に反映されます。

| 方向 | コマンド | 動作 |
|------|---------|------|
| Data → HTML | `sync to-html` | Data ブロックを編集 → テンプレート再実行 → 本文を更新 |
| HTML → Data | `sync to-data` | 本文の span を編集 → Data ブロックに抽出 → 再レンダリング |

VS Code 拡張では **ステータスバー** からワンクリックで方向を切替。保存時に自動同期。

→ [LiveMorph ガイド](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/livemorph.md)

---

### Human-AI Readable --- 人にも AI にも読める

1 つの `.kata.md` ファイルに **テンプレート・スキーマ・データ・本文** をすべて格納。
GitHub 上でそのままレビュー可能。AI は Prompt + Schema を読んでデータを自動生成。

```
.kata.md (セルフコンテインド)
├── Prompt        ... AI 向け指示
├── Template      ... Jinja2 テンプレート
├── Schema        ... YAML shorthand 型定義
├── Data          ... YAML データ
└── Body          ... レンダリング済み本文 (data-kata span)
```

→ [KATA Markdown フォーマット](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/kata-markdown-format.md)

---

### Secure Packaging --- KATA ARchive&#8482; (.katar)

テンプレートを **1 パッケージ = 1 テンプレート = 1 スキーマ** で安全に配布。
ZIP ベースで展開不要。`./templates/` に置くだけで即利用。

```bash
gospelo-kata pack ./my_template/ -o my_template.katar
gospelo-kata build my_template -o ./
```

→ [テンプレートパッケージ](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/katar.md)

---

## 組み込みテンプレート

| テンプレート | 用途 |
|-------------|------|
| `todo` | TODO リスト |
| `agenda` | 会議アジェンダ |
| `checklist` | 構造化チェックリスト |
| `test_spec` | テストケース仕様書 |
| `api_test` | API テスト仕様 |
| `header_test` | HTTP ヘッダー検査 |
| `infra_test` | インフラ監査 |
| `load_test` | 負荷テスト仕様 |
| `scan_results` | ソースコードスキャン結果 |
| `test_prereq` | テスト前提条件 |
| `pretest_review` | テスト前レビュー |

→ [テンプレート一覧](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/templates.md)

---

## ドキュメント

| ページ | 概要 |
|--------|------|
| [クイックスタート](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/quick-start.md) | インストールから初回レンダリングまで |
| [LiveMorph ガイド](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/livemorph.md) | 双方向同期の使い方 |
| [テンプレート一覧](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/templates.md) | 組み込みテンプレート + カラースキーム |
| [KATA Markdown フォーマット](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/kata-markdown-format.md) | テンプレート記法・出力構造 |
| [CLI リファレンス](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/cli-reference.md) | 全コマンドのオプション詳細 |
| [Lint ルール一覧](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/lint-rules.md) | エラーコード (S/T/F/V/D/E) と対処法 |
| [VS Code 連携](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/vscode.md) | 拡張機能・LiveMorph・ホバー |
| [テンプレートパッケージ](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/katar.md) | .katar の作成・配布 |
| [Copilot セットアップ](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/copilot-setup.md) | GitHub Copilot Chat 連携 |
| [スキルガイド](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/skill-guide.md) | AI スキルの使い方 |
