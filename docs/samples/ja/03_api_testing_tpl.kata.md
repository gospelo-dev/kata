**Prompt**

```yaml
このテンプレートはREST APIテストチェックリストを生成します。
categories はCRUD操作・認証パターンなどAPI観点で分類してください。
各 item の target には HTTP メソッドとエンドポイントパス（例: POST /api/v1/resources）を記述してください。
requirements には正常系・異常系の期待レスポンス（ステータスコード含む）を記述してください。
```

# {{ description }}

{% if version %}> Version: {{ version }}

{% endif %}{% for cat in categories %}## {{ cat.id }}. {{ cat.name }}

{% for item in cat.items %}<table class="kata-card">
<tr>
<td class="kata-left">

**{{ item.id }}. {{ item.name }}**

<table class="kata-props">
<tr><td colspan="2"><b>{{ item.name_ja | default(item.name) }}</b></td></tr>
<tr><td>target</td><td>{{ item.target | default("") }}</td></tr>
<tr><td>auto</td><td>{{ item.auto | default("manual") }}</td></tr>
<tr><td>status</td><td><span class="kata-status-{{ item.status | default("draft") }}">{{ item.status | default("draft") }}</span></td></tr>
<tr><td>tags</td><td>{{ item.tags | default([]) | join(", ") }}</td></tr>
</table>

</td>
<td class="kata-right">

{% if item.requirements %}- {{ item.requirements }}
{% endif %}
</td>
</tr>
</table>

{% endfor %}{% endfor %}

<details>
<summary>Schema Reference</summary>

**Schema**

```yaml
version: string!
description: string!
categories[]!:
  id: string!
  name: string!
  items[]!:
    id: string!
    name: string!
    name_ja: string!
    target: string
    auto: enum(full, semi, partial, manual)
    status: enum(draft, pending, approve, reject)
    requirements: string
    tags: string[]
```

**Data**

```yaml
version: "1.0"
description: REST API テストチェックリスト
categories:
  - id: crud
    name: CRUD操作
    items:
      - id: "1"
        name: Create Resource
        name_ja: リソース作成 (POST)
        status: draft
        auto: full
        target: POST /api/v1/resources
        tags:
          - crud
          - create
          - validation
        requirements: "正常系: 必須フィールド(name, email等)を含むリクエストで201 Createdとリソースオブジェクトが返ること"
      - id: "2"
        name: Read Resource
        name_ja: リソース取得 (GET)
        status: draft
        auto: full
        target: GET /api/v1/resources/:id
        tags:
          - crud
          - read
          - pagination
        requirements: "単体取得: 存在するIDで200とリソースオブジェクトが返ること"
      - id: "3"
        name: Update Resource
        name_ja: リソース更新 (PUT/PATCH)
        status: draft
        auto: full
        target: PUT /api/v1/resources/:id
        tags:
          - crud
          - update
        requirements: "PUT: 全フィールドを含むリクエストで200と更新後リソースが返ること"
      - id: "4"
        name: Delete Resource
        name_ja: リソース削除 (DELETE)
        status: draft
        auto: full
        target: DELETE /api/v1/resources/:id
        tags:
          - crud
          - delete
        requirements: "正常系: 存在するIDで204 No Contentが返りリソースが削除されること"
  - id: auth_pattern
    name: 認証パターン
    items:
      - id: "5"
        name: Bearer Token Auth
        name_ja: Bearerトークン認証
        status: draft
        auto: full
        target: 全エンドポイント
        tags:
          - auth
          - bearer
          - jwt
        requirements: "正常系: 有効なBearerトークン付きリクエストで200が返ること"
      - id: "6"
        name: Role-Based Access
        name_ja: ロールベースアクセス制御
        status: draft
        auto: semi
        target: 管理者向けエンドポイント
        tags:
          - auth
          - rbac
          - role
        requirements: "admin: 管理者トークンで管理者向けAPI(ユーザー管理等)にアクセスし200が返ること"
```

</details>
