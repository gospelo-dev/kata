**Prompt**

```yaml
This template generates an AWS infrastructure configuration audit checklist.
Categorize items by AWS service perspective such as IAM, storage, and logging.
Use service-prefixed IDs for each item (e.g., IAM-01, S3-01).
Describe specific AWS CLI commands and values to verify in requirements.
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
description: AWS Infrastructure Audit Checklist
categories:
  - id: iam
    name: IAM & Access Control
    items:
      - id: IAM-01
        name: Root Account MFA
        name_ja: Root Account MFA Enabled
        status: draft
        auto: full
        target: IAM
        tags:
          - iam
          - mfa
          - root
        requirements: "Verify AccountMFAEnabled=1 via get-account-summary"
      - id: IAM-02
        name: Unused IAM Credentials
        name_ja: Unused IAM Credential Detection
        status: draft
        auto: full
        target: IAM
        tags:
          - iam
          - credentials
          - hygiene
        requirements: "Detect keys unused for 90+ days via generate-credential-report"
  - id: storage
    name: Storage & Encryption
    items:
      - id: S3-01
        name: S3 Public Access Block
        name_ja: S3 Public Access Block
        status: draft
        auto: full
        target: S3
        tags:
          - s3
          - public_access
          - storage
        requirements: "Verify all 4 settings are true via get-public-access-block"
      - id: KMS-01
        name: KMS Key Rotation
        name_ja: KMS Key Rotation
        status: draft
        auto: full
        target: KMS
        tags:
          - kms
          - encryption
          - rotation
        requirements: "Verify enabled via get-key-rotation-status"
  - id: logging
    name: Logging & Audit
    items:
      - id: LOG-01
        name: CloudTrail Enabled
        name_ja: CloudTrail Enabled
        status: draft
        auto: full
        target: CloudTrail
        tags:
          - cloudtrail
          - logging
          - audit
        requirements: "Verify enabled in all regions via describe-trails + get-trail-status"
```

</details>
