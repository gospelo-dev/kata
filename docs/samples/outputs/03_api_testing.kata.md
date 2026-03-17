# <span data-kata="p-description">REST API テストチェックリスト</span>

> Version: <span data-kata="p-version">1.0</span>

## <span data-kata="p-categories-0-id">crud</span>. <span data-kata="p-categories-0-name">CRUD操作</span>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-0-items-0-id">1</span>. <span data-kata="p-categories-0-items-0-name">Create Resource</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-0-items-0-name-ja">リソース作成 (POST)</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-0-items-0-target">POST /api/v1/resources</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-0-items-0-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-0-items-0-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-0-items-0-tags">crud, create, validation</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-0-items-0-requirements">正常系: 必須フィールド(name, email等)を含むリクエストで201 Createdとリソースオブジェクトが返ること</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-0-items-1-id">2</span>. <span data-kata="p-categories-0-items-1-name">Read Resource</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-0-items-1-name-ja">リソース取得 (GET)</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-0-items-1-target">GET /api/v1/resources/:id</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-0-items-1-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-0-items-1-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-0-items-1-tags">crud, read, pagination</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-0-items-1-requirements">単体取得: 存在するIDで200とリソースオブジェクトが返ること</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-0-items-2-id">3</span>. <span data-kata="p-categories-0-items-2-name">Update Resource</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-0-items-2-name-ja">リソース更新 (PUT/PATCH)</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-0-items-2-target">PUT /api/v1/resources/:id</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-0-items-2-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-0-items-2-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-0-items-2-tags">crud, update</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-0-items-2-requirements">PUT: 全フィールドを含むリクエストで200と更新後リソースが返ること</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-0-items-3-id">4</span>. <span data-kata="p-categories-0-items-3-name">Delete Resource</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-0-items-3-name-ja">リソース削除 (DELETE)</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-0-items-3-target">DELETE /api/v1/resources/:id</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-0-items-3-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-0-items-3-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-0-items-3-tags">crud, delete</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-0-items-3-requirements">正常系: 存在するIDで204 No Contentが返りリソースが削除されること</span>

</td>
</tr>
</table>

## <span data-kata="p-categories-1-id">auth_pattern</span>. <span data-kata="p-categories-1-name">認証パターン</span>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-1-items-0-id">5</span>. <span data-kata="p-categories-1-items-0-name">Bearer Token Auth</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-1-items-0-name-ja">Bearerトークン認証</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-1-items-0-target">全エンドポイント</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-1-items-0-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-1-items-0-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-1-items-0-tags">auth, bearer, jwt</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-1-items-0-requirements">正常系: 有効なBearerトークン付きリクエストで200が返ること</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-1-items-1-id">6</span>. <span data-kata="p-categories-1-items-1-name">Role-Based Access</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-1-items-1-name-ja">ロールベースアクセス制御</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-1-items-1-target">管理者向けエンドポイント</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-1-items-1-auto">semi</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-1-items-1-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-1-items-1-tags">auth, rbac, role</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-1-items-1-requirements">admin: 管理者トークンで管理者向けAPI(ユーザー管理等)にアクセスし200が返ること</span>

</td>
</tr>
</table>



<style>
table { table-layout: fixed; width: 100%; display: table !important; overflow: visible !important; }
table th, table td { overflow-wrap: break-word; word-break: break-word; vertical-align: top; }
.markdown-preview { max-width: 100% !important; padding-left: 2em !important; padding-right: 2em !important; }
</style>

---

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
version: '1.0'
description: REST API テストチェックリスト
categories:
- id: crud
  name: CRUD操作
  items:
  - id: '1'
    name: Create Resource
    name_ja: リソース作成 (POST)
    status: draft
    auto: full
    target: POST /api/v1/resources
    tags:
    - crud
    - create
    - validation
    requirements: '正常系: 必須フィールド(name, email等)を含むリクエストで201 Createdとリソースオブジェクトが返ること'
  - id: '2'
    name: Read Resource
    name_ja: リソース取得 (GET)
    status: draft
    auto: full
    target: GET /api/v1/resources/:id
    tags:
    - crud
    - read
    - pagination
    requirements: '単体取得: 存在するIDで200とリソースオブジェクトが返ること'
  - id: '3'
    name: Update Resource
    name_ja: リソース更新 (PUT/PATCH)
    status: draft
    auto: full
    target: PUT /api/v1/resources/:id
    tags:
    - crud
    - update
    requirements: 'PUT: 全フィールドを含むリクエストで200と更新後リソースが返ること'
  - id: '4'
    name: Delete Resource
    name_ja: リソース削除 (DELETE)
    status: draft
    auto: full
    target: DELETE /api/v1/resources/:id
    tags:
    - crud
    - delete
    requirements: '正常系: 存在するIDで204 No Contentが返りリソースが削除されること'
- id: auth_pattern
  name: 認証パターン
  items:
  - id: '5'
    name: Bearer Token Auth
    name_ja: Bearerトークン認証
    status: draft
    auto: full
    target: 全エンドポイント
    tags:
    - auth
    - bearer
    - jwt
    requirements: '正常系: 有効なBearerトークン付きリクエストで200が返ること'
  - id: '6'
    name: Role-Based Access
    name_ja: ロールベースアクセス制御
    status: draft
    auto: semi
    target: 管理者向けエンドポイント
    tags:
    - auth
    - rbac
    - role
    requirements: 'admin: 管理者トークンで管理者向けAPI(ユーザー管理等)にアクセスし200が返ること'
```

</details>
