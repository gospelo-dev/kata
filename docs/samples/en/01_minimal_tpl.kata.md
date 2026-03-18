**Prompt**

```yaml
This template generates a checklist-style specification document.
Describe categories in the categories array, and check items in each category's items array.
status must be one of draft/pending/approve/reject.
auto must be one of full/semi/partial/manual.
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
description: Minimal Checklist
categories:
- id: basic
  name: Basic Tests
  items:
    - id: "1"
      name: Login Function
      name_ja: Login Function
      status: approve
      auto: full
      target: /api/auth/login
      tags:
        - auth
      requirements: "Normal: Valid email + password returns 200 with JWT token"
    - id: "2"
      name: User Registration
      name_ja: User Registration
      status: reject
      auto: full
      target: /api/auth/register
      tags:
        - auth
      requirements: "Normal: Required fields input returns 201 with user object"
    - id: "3"
      name: Data Export
      name_ja: Data Export
      status: draft
      auto: full
      target: /api/export
      tags:
        - data
      requirements: "Normal: Data can be downloaded in CSV format"
```

</details>
