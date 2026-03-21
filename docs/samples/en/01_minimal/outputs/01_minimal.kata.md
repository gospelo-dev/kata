# <span data-kata="p-description">Minimal Checklist</span>

> Version: <span data-kata="p-version">1.0</span>

## <span data-kata="p-categories-0-id">basic</span>. <span data-kata="p-categories-0-name">Basic Tests</span>

<table class="kata-card">

<tr>
<td class="kata-left">

**<span data-kata="p-categories-0-items-0-id">1</span>. <span data-kata="p-categories-0-items-0-name">Login Function</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-0-items-0-name-ja">Login Function</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-0-items-0-target">/api/auth/login</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-0-items-0-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-approve"><span data-kata="p-categories-0-items-0-status">approve</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-0-items-0-tags">auth</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-0-items-0-requirements">Normal: Valid email + password returns 200 with JWT token</span>


</td>
</tr>
</table>

<table class="kata-card">

<tr>
<td class="kata-left">

**<span data-kata="p-categories-0-items-1-id">2</span>. <span data-kata="p-categories-0-items-1-name">User Registration</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-0-items-1-name-ja">User Registration</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-0-items-1-target">/api/auth/register</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-0-items-1-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-reject"><span data-kata="p-categories-0-items-1-status">reject</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-0-items-1-tags">auth</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-0-items-1-requirements">Normal: Required fields input returns 201 with user object</span>


</td>
</tr>
</table>

<table class="kata-card">

<tr>
<td class="kata-left">

**<span data-kata="p-categories-0-items-2-id">3</span>. <span data-kata="p-categories-0-items-2-name">Data Export</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-0-items-2-name-ja">Data Export</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-0-items-2-target">/api/export</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-0-items-2-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-0-items-2-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-0-items-2-tags">data</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-0-items-2-requirements">Normal: Data can be downloaded in CSV format</span>


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
This template generates a checklist-style specification document.
Describe categories in the categories array, and check items in each category's items array.
status must be one of draft/pending/approve/reject.
auto must be one of full/semi/partial/manual.

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
description: Minimal Checklist
categories:
- id: basic
  name: Basic Tests
  items:
  - id: '1'
    name: Login Function
    name_ja: Login Function
    status: approve
    auto: full
    target: /api/auth/login
    tags:
    - auth
    requirements: 'Normal: Valid email + password returns 200 with JWT token'
  - id: '2'
    name: User Registration
    name_ja: User Registration
    status: reject
    auto: full
    target: /api/auth/register
    tags:
    - auth
    requirements: 'Normal: Required fields input returns 201 with user object'
  - id: '3'
    name: Data Export
    name_ja: Data Export
    status: draft
    auto: full
    target: /api/export
    tags:
    - data
    requirements: 'Normal: Data can be downloaded in CSV format'
```

<!-- kata-structure-integrity: sha256:0b657a98b271dea60df282efc4527c4a8ced7e860fbde978f69a77145b24fb44 -->
</details>
