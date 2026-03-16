{#schema
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
#}

{#data
version: "1.0"
description: 最小構成のチェックリスト
categories:
  - id: basic
    name: 基本テスト
    items:
      - id: "1"
        name: Login Function
        name_ja: ログイン機能
        status: approve
        auto: full
        target: /api/auth/login
        tags:
          - auth
        requirements: "正常系: 有効なメール+パスワードで200とJWTトークンが返る"
      - id: "2"
        name: User Registration
        name_ja: ユーザー登録
        status: reject
        auto: full
        target: /api/auth/register
        tags:
          - auth
        requirements: "正常系: 必須フィールド入力で201とユーザーオブジェクトが返る"
      - id: "3"
        name: Data Export
        name_ja: データエクスポート
        status: draft
        auto: full
        target: /api/export
        tags:
          - data
        requirements: "正常系: CSV形式でデータがダウンロードできる"
#}

# {{ description }}

{% if version %}> Version: {{ version }}

{% endif %}{% for cat in categories %}## {{ cat.id }}. {{ cat.name }}

{% for item in cat.items %}<table class="kata-card">
<tr>
<td class="kata-left">

**{{ item.id }}. {{ item.name }}** <span class="kata-badge kata-badge-{{ item.status | default("draft") }}">{{ item.status | default("draft") }}</span>

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
