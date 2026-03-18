# <span data-kata="p-description">REST API Test Checklist</span>

> Version: <span data-kata="p-version">1.0</span>

## <span data-kata="p-categories-0-id">crud</span>. <span data-kata="p-categories-0-name">CRUD Operations</span>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-0-items-0-id">1</span>. <span data-kata="p-categories-0-items-0-name">Create Resource</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-0-items-0-name-ja">Create Resource (POST)</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-0-items-0-target">POST /api/v1/resources</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-0-items-0-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-0-items-0-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-0-items-0-tags">crud, create, validation</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-0-items-0-requirements">Normal: Request with required fields (name, email, etc.) returns 201 Created with resource object</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-0-items-1-id">2</span>. <span data-kata="p-categories-0-items-1-name">Read Resource</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-0-items-1-name-ja">Read Resource (GET)</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-0-items-1-target">GET /api/v1/resources/:id</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-0-items-1-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-0-items-1-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-0-items-1-tags">crud, read, pagination</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-0-items-1-requirements">Single read: Existing ID returns 200 with resource object</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-0-items-2-id">3</span>. <span data-kata="p-categories-0-items-2-name">Update Resource</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-0-items-2-name-ja">Update Resource (PUT/PATCH)</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-0-items-2-target">PUT /api/v1/resources/:id</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-0-items-2-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-0-items-2-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-0-items-2-tags">crud, update</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-0-items-2-requirements">PUT: Request with all fields returns 200 with updated resource</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-0-items-3-id">4</span>. <span data-kata="p-categories-0-items-3-name">Delete Resource</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-0-items-3-name-ja">Delete Resource (DELETE)</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-0-items-3-target">DELETE /api/v1/resources/:id</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-0-items-3-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-0-items-3-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-0-items-3-tags">crud, delete</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-0-items-3-requirements">Normal: Existing ID returns 204 No Content and resource is deleted</span>

</td>
</tr>
</table>

## <span data-kata="p-categories-1-id">auth_pattern</span>. <span data-kata="p-categories-1-name">Authentication Patterns</span>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-1-items-0-id">5</span>. <span data-kata="p-categories-1-items-0-name">Bearer Token Auth</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-1-items-0-name-ja">Bearer Token Authentication</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-1-items-0-target">All endpoints</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-1-items-0-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-1-items-0-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-1-items-0-tags">auth, bearer, jwt</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-1-items-0-requirements">Normal: Request with valid Bearer token returns 200</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-1-items-1-id">6</span>. <span data-kata="p-categories-1-items-1-name">Role-Based Access</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-1-items-1-name-ja">Role-Based Access Control</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-1-items-1-target">Admin endpoints</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-1-items-1-auto">semi</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-1-items-1-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-1-items-1-tags">auth, rbac, role</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-1-items-1-requirements">Admin: Admin token accessing admin APIs (user management, etc.) returns 200</span>

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

**Prompt**

```yaml
This template generates a REST API test checklist.
Categorize items by API perspective such as CRUD operations and authentication patterns.
Describe HTTP method and endpoint path (e.g., POST /api/v1/resources) in each item's target.
Describe expected responses for normal and error cases (including status codes) in requirements.

```

```kata:template
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
```

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
description: REST API Test Checklist
categories:
- id: crud
  name: CRUD Operations
  items:
  - id: '1'
    name: Create Resource
    name_ja: Create Resource (POST)
    status: draft
    auto: full
    target: POST /api/v1/resources
    tags:
    - crud
    - create
    - validation
    requirements: 'Normal: Request with required fields (name, email, etc.) returns
      201 Created with resource object'
  - id: '2'
    name: Read Resource
    name_ja: Read Resource (GET)
    status: draft
    auto: full
    target: GET /api/v1/resources/:id
    tags:
    - crud
    - read
    - pagination
    requirements: 'Single read: Existing ID returns 200 with resource object'
  - id: '3'
    name: Update Resource
    name_ja: Update Resource (PUT/PATCH)
    status: draft
    auto: full
    target: PUT /api/v1/resources/:id
    tags:
    - crud
    - update
    requirements: 'PUT: Request with all fields returns 200 with updated resource'
  - id: '4'
    name: Delete Resource
    name_ja: Delete Resource (DELETE)
    status: draft
    auto: full
    target: DELETE /api/v1/resources/:id
    tags:
    - crud
    - delete
    requirements: 'Normal: Existing ID returns 204 No Content and resource is deleted'
- id: auth_pattern
  name: Authentication Patterns
  items:
  - id: '5'
    name: Bearer Token Auth
    name_ja: Bearer Token Authentication
    status: draft
    auto: full
    target: All endpoints
    tags:
    - auth
    - bearer
    - jwt
    requirements: 'Normal: Request with valid Bearer token returns 200'
  - id: '6'
    name: Role-Based Access
    name_ja: Role-Based Access Control
    status: draft
    auto: semi
    target: Admin endpoints
    tags:
    - auth
    - rbac
    - role
    requirements: 'Admin: Admin token accessing admin APIs (user management, etc.)
      returns 200'
```

</details>
