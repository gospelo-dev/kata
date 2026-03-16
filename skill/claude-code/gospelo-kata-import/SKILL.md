---
name: gospelo-kata-import
description: 外部ソース (swagger.json, OpenAPI等) から KATA Markdown テスト仕様書を生成
---

# /kata-import — 外部ソースから KATA Markdown™ 変換

swagger.json / OpenAPI 仕様などの外部ソースを読み取り、gospelo-kata のテスト仕様書 (.kata.md) を自動生成するスキル。

---

## 対応ソース

| ソース | 拡張子 | 説明 |
|--------|--------|------|
| OpenAPI / Swagger | `.json`, `.yaml` | REST API 仕様 → API テスト仕様書 |

---

## ワークフロー

### Step 1: ソースファイルの読み取り

ユーザーが指定した swagger.json / OpenAPI ファイルを読み取る。

```bash
# ファイルを読み取る (Read ツール使用)
```

以下の情報を抽出:
- **info**: API 名、バージョン
- **paths**: 各エンドポイント (method + path)
- **parameters**: クエリ/パス/ヘッダーパラメータ
- **requestBody**: リクエストボディのスキーマ
- **responses**: レスポンスコードと説明
- **security**: 認証方式
- **tags**: カテゴリ分類

### Step 2: テストケースの設計

各エンドポイントから以下の観点でテストケースを生成:

#### カテゴリ分類ルール

| OpenAPI 情報 | テストカテゴリ |
|-------------|--------------|
| tag | そのまま category に使用 |
| tag なし | path の第1セグメントを使用 (e.g., `/users/...` → `users`) |
| security あり | `認証・認可` カテゴリを追加 |

#### テストケース生成ルール

各エンドポイントに対して、以下のテストケースを検討:

1. **正常系**: 正しいパラメータでリクエストし、期待するレスポンスコード (200/201) を確認
2. **バリデーション**: required パラメータを欠落させ、400 エラーを確認
3. **認証**: security 定義があれば、トークンなし/不正トークンで 401/403 を確認
4. **境界値**: minLength/maxLength/minimum/maximum があれば境界値テスト
5. **存在しないリソース**: path パラメータ付きエンドポイントで存在しない ID → 404

#### test_id 採番ルール

```
{PREFIX}-{連番:02d}
```

- PREFIX はユーザー指定、またはAPI名から自動生成 (e.g., `USER-API` → `UA`)
- 連番はカテゴリ順に通し番号

#### priority 判定ルール

| 条件 | priority |
|------|----------|
| POST/PUT/DELETE メソッド | high |
| security 定義あり | high |
| GET で path パラメータなし | medium |
| GET で path パラメータあり | medium |
| OPTIONS/HEAD | low |

### Step 3: .kata.md ソースファイル生成

以下の形式で `.kata.md` ファイルを生成:

```markdown
{#schema
test_name: string
test_id_prefix: string
version: string
test_cases[]!:
  test_id: string!
  category: string!
  description: string!
  expected_result: string!
  priority: enum(high, medium, low)
  tags: string[]
#}

{#data
test_name: {API名} テスト仕様書
test_id_prefix: {PREFIX}
version: {APIバージョン}
test_cases:
  - test_id: {PREFIX}-01
    category: {カテゴリ}
    description: {テスト内容の説明}
    expected_result: {期待される結果}
    priority: high
    tags:
      - {HTTPメソッド小文字}
      - {タグ}
  ...
#}

# {{ test_name }}

> Prefix: {{ test_id_prefix }} | Version: {{ version }}

## Test Cases

| ID | Category | Description | Expected Result | Priority | Tags |
|:--:|----------|-------------|-----------------|:--------:|------|
{% for case in test_cases %}| {{ case.test_id }} | {{ case.category }} | {{ case.description }} | {{ case.expected_result }} | {{ case.priority }} | {{ case.tags | join(", ") }} |
{% endfor %}

Total: {{ test_cases | length }} test cases
```

### Step 4: レンダリング・検証

```bash
# レンダリング
gospelo-kata render {source}.kata.md -o outputs/{source}.kata.md

# Lint 検証
gospelo-kata lint outputs/{source}.kata.md

# データ抽出 (ラウンドトリップ確認)
gospelo-kata extract outputs/{source}.kata.md
```

Lint エラーが 0 であることを確認。D016 (HTML in span) が出た場合:

```bash
gospelo-kata fmt outputs/{source}.kata.md
```

---

## 変換例

### 入力: swagger.json (抜粋)

```json
{
  "info": { "title": "User Management API", "version": "2.0.0" },
  "paths": {
    "/users": {
      "get": {
        "tags": ["users"],
        "summary": "List all users",
        "parameters": [
          { "name": "page", "in": "query", "schema": { "type": "integer" } }
        ],
        "responses": { "200": { "description": "User list" } }
      },
      "post": {
        "tags": ["users"],
        "summary": "Create a new user",
        "security": [{ "bearerAuth": [] }],
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "required": ["name", "email"],
                "properties": {
                  "name": { "type": "string", "minLength": 1 },
                  "email": { "type": "string", "format": "email" }
                }
              }
            }
          }
        },
        "responses": {
          "201": { "description": "User created" },
          "400": { "description": "Validation error" },
          "401": { "description": "Unauthorized" }
        }
      }
    },
    "/users/{id}": {
      "get": {
        "tags": ["users"],
        "summary": "Get user by ID",
        "parameters": [
          { "name": "id", "in": "path", "required": true }
        ],
        "responses": {
          "200": { "description": "User details" },
          "404": { "description": "User not found" }
        }
      }
    }
  }
}
```

### 出力: テストケース (data セクション)

```yaml
test_name: User Management API テスト仕様書
test_id_prefix: UMA
version: 2.0.0
test_cases:
  - test_id: UMA-01
    category: users
    description: GET /users — ページネーションパラメータなしでユーザー一覧を取得し、200 が返ることを確認
    expected_result: ステータス 200。ユーザー一覧が JSON 配列で返却される
    priority: medium
    tags:
      - get
      - users
      - list
  - test_id: UMA-02
    category: users
    description: POST /users — 必須フィールド (name, email) を含むリクエストでユーザーを作成し、201 が返ることを確認
    expected_result: ステータス 201。作成されたユーザー情報が返却される
    priority: high
    tags:
      - post
      - users
      - create
  - test_id: UMA-03
    category: users
    description: POST /users — name を欠落させてリクエストし、400 バリデーションエラーが返ることを確認
    expected_result: ステータス 400。エラーメッセージに欠落フィールド名が含まれる
    priority: high
    tags:
      - post
      - users
      - validation
  - test_id: UMA-04
    category: users
    description: POST /users — 認証トークンなしでリクエストし、401 が返ることを確認
    expected_result: ステータス 401。認証エラーメッセージが返却される
    priority: high
    tags:
      - post
      - users
      - authentication
  - test_id: UMA-05
    category: users
    description: GET /users/{id} — 存在するユーザー ID でリクエストし、200 とユーザー詳細が返ることを確認
    expected_result: ステータス 200。指定した ID のユーザー情報が返却される
    priority: medium
    tags:
      - get
      - users
      - detail
  - test_id: UMA-06
    category: users
    description: GET /users/{id} — 存在しないユーザー ID でリクエストし、404 が返ることを確認
    expected_result: ステータス 404。リソース未検出のエラーメッセージが返却される
    priority: medium
    tags:
      - get
      - users
      - not-found
```

---

## 注意事項

- description と expected_result は**日本語**で記述する (ユーザーの指示がない限り)
- HTML タグを含むデータは render 時に自動サニタイズされる
- テストケースは網羅性より**実用性を優先** — 全組み合わせではなく代表的なケースを選定
- 生成後、ユーザーにテストケースの追加・削除・修正の要望を確認する
- `params` フィールドはオプション — 必要に応じてリクエストパラメータの詳細を記録可能

---

## 使用例

```
/kata-import swagger.json からAPIテスト仕様書を生成して
/kata-import openapi.yaml のエンドポイントからテストケースを作って
```
