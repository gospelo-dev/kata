# <span data-kata="p-description">最小構成のチェックリスト</span>

> Version: <span data-kata="p-version">1.0</span>

## <span data-kata="p-categories-0-id">basic</span>. <span data-kata="p-categories-0-name">基本テスト</span>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-0-items-0-id">1</span>. <span data-kata="p-categories-0-items-0-name">Login Function</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-0-items-0-name-ja">ログイン機能</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-0-items-0-target">/api/auth/login</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-0-items-0-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-approve"><span data-kata="p-categories-0-items-0-status">approve</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-0-items-0-tags">auth</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-0-items-0-requirements">正常系: 有効なメール+パスワードで200とJWTトークンが返る</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-0-items-1-id">2</span>. <span data-kata="p-categories-0-items-1-name">User Registration</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-0-items-1-name-ja">ユーザー登録</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-0-items-1-target">/api/auth/register</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-0-items-1-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-reject"><span data-kata="p-categories-0-items-1-status">reject</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-0-items-1-tags">auth</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-0-items-1-requirements">正常系: 必須フィールド入力で201とユーザーオブジェクトが返る</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-0-items-2-id">3</span>. <span data-kata="p-categories-0-items-2-name">Data Export</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-0-items-2-name-ja">データエクスポート</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-0-items-2-target">/api/export</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-0-items-2-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-0-items-2-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-0-items-2-tags">data</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-0-items-2-requirements">正常系: CSV形式でデータがダウンロードできる</span>

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
description: 最小構成のチェックリスト
categories:
- id: basic
  name: 基本テスト
  items:
  - id: '1'
    name: Login Function
    name_ja: ログイン機能
    status: approve
    auto: full
    target: /api/auth/login
    tags:
    - auth
    requirements: '正常系: 有効なメール+パスワードで200とJWTトークンが返る'
  - id: '2'
    name: User Registration
    name_ja: ユーザー登録
    status: reject
    auto: full
    target: /api/auth/register
    tags:
    - auth
    requirements: '正常系: 必須フィールド入力で201とユーザーオブジェクトが返る'
  - id: '3'
    name: Data Export
    name_ja: データエクスポート
    status: draft
    auto: full
    target: /api/export
    tags:
    - data
    requirements: '正常系: CSV形式でデータがダウンロードできる'
```

</details>
