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
description: AWSインフラ設定監査チェックリスト
categories:
  - id: iam
    name: IAM・アクセス制御
    items:
      - id: IAM-01
        name: Root Account MFA
        name_ja: ルートアカウントMFA有効化
        status: draft
        auto: full
        target: IAM
        tags:
          - iam
          - mfa
          - root
        requirements: "get-account-summary で AccountMFAEnabled=1 を確認"
      - id: IAM-02
        name: Unused IAM Credentials
        name_ja: 未使用IAMクレデンシャル検出
        status: draft
        auto: full
        target: IAM
        tags:
          - iam
          - credentials
          - hygiene
        requirements: "generate-credential-report で 90日以上未使用のキーを検出"
  - id: storage
    name: ストレージ・暗号化
    items:
      - id: S3-01
        name: S3 Public Access Block
        name_ja: S3パブリックアクセスブロック
        status: draft
        auto: full
        target: S3
        tags:
          - s3
          - public_access
          - storage
        requirements: "get-public-access-block で全4項目がtrueか確認"
      - id: KMS-01
        name: KMS Key Rotation
        name_ja: KMSキーローテーション
        status: draft
        auto: full
        target: KMS
        tags:
          - kms
          - encryption
          - rotation
        requirements: "get-key-rotation-status で有効化を確認"
  - id: logging
    name: ログ・監査
    items:
      - id: LOG-01
        name: CloudTrail Enabled
        name_ja: CloudTrail有効化
        status: draft
        auto: full
        target: CloudTrail
        tags:
          - cloudtrail
          - logging
          - audit
        requirements: "describe-trails + get-trail-status で全リージョン有効化を確認"
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
