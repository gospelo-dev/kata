**Prompt**

```yaml
This template generates a REST API test checklist.
Categorize items by API perspective such as CRUD operations and authentication patterns.
Describe HTTP method and endpoint path (e.g., POST /api/v1/resources) in each item's target.
Describe expected responses for normal and error cases (including status codes) in requirements.
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

```

</details>
