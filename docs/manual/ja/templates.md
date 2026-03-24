# テンプレート一覧

gospelo-kata に組み込まれている KATA ARchive (.katar) テンプレート。

```bash
gospelo-kata templates    # 一覧表示
```

---

## 汎用

| テンプレート | 説明 | 主な用途 |
|-------------|------|---------|
| `todo` | TODO リスト (タスク・ステータス管理) | プロジェクト管理 |
| `agenda` | 会議アジェンダ (出席者・議題・決定事項) | ミーティング |
| `checklist` | 構造化チェックリスト (カテゴリ・項目・ステータス) | 品質管理・監査 |

## セキュリティテスト

| テンプレート | 説明 | 依存 |
|-------------|------|------|
| `test_spec` | テストケース仕様書 | `test_prereq` |
| `test_prereq` | テスト前提条件・環境セットアップ | --- |
| `pretest_review` | テスト前レビューチェックリスト | `test_spec`, `test_prereq` |
| `api_test` | API テスト仕様 (エンドポイント・認証・レスポンス検証) | --- |
| `header_test` | HTTP レスポンスヘッダー検査 | --- |
| `infra_test` | クラウドインフラ構成・セキュリティ監査 | --- |
| `load_test` | 負荷・レートリミットテスト | --- |
| `scan_results` | ソースコードスキャン結果レポート | --- |

---

## テンプレートの使い方

### 1. スケルトン生成

```bash
gospelo-kata prepare test_spec -o data.yml
```

テンプレートの **Prompt** と **Schema** が表示され、`data.yml` にスキーマに基づく雛形が出力されます。

### 2. ビルド

```bash
gospelo-kata build test_spec data.yml -o outputs/
```

### 3. 依存テンプレートとの結合

`test_spec` は `test_prereq` のデータを参照します。Excel 出力時に結合できます:

```bash
gospelo-kata generate test_spec.json -f excel --prereq prereq.json -o test.xlsx
```

---

## カラースキーム

Style ブロックで `colorScheme` を指定すると、enum 値のセマンティックカラーが変わります。

```yaml
colorScheme: vivid
```

### default --- Asagi

澄んだライトブルー系、白背景。

![default](https://github.com/gospelo-dev/kata/blob/main/docs/examples/ja/color_schemes/images/todo_default.png?raw=true)

### pastel --- Jelly Mint

ミントグリーン + ダスティローズ。

![pastel](https://github.com/gospelo-dev/kata/blob/main/docs/examples/ja/color_schemes/images/todo_pastel.png?raw=true)

### vivid --- Vivid Gradient

パープル + シアンの高コントラスト。

![vivid](https://github.com/gospelo-dev/kata/blob/main/docs/examples/ja/color_schemes/images/todo_vivid.png?raw=true)

### monochrome --- Sumi-ink

水墨画風モノクロ + 紅アクセント。

![monochrome](https://github.com/gospelo-dev/kata/blob/main/docs/examples/ja/color_schemes/images/todo_monochrome.png?raw=true)

### ocean --- Blue Aura

ブルーグレー + テラコッタ。

![ocean](https://github.com/gospelo-dev/kata/blob/main/docs/examples/ja/color_schemes/images/todo_ocean.png?raw=true)

### カスタム enumColors

enum 値ごとにセマンティックロールを指定できます:

```yaml
colorScheme: vivid
enumColors:
  status:
    todo: neutral
    done: positive
    blocked: negative
```

---

## カスタムテンプレートの作成

独自のテンプレートを作成して `.katar` パッケージとして配布できます。

```bash
gospelo-kata pack-init ./my_template/    # 雛形作成
# ... テンプレートを編集 ...
gospelo-kata pack ./my_template/ -o my_template.katar
```

→ [テンプレートパッケージ](https://github.com/gospelo-dev/kata/blob/main/docs/manual/ja/katar.md)
