# <span data-kata="p-description">AWS Infrastructure Audit Checklist</span>

> Version: <span data-kata="p-version">1.0</span>

## <span data-kata="p-categories-0-id">iam</span>. <span data-kata="p-categories-0-name">IAM &amp; Access Control</span>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-0-items-0-id">IAM-01</span>. <span data-kata="p-categories-0-items-0-name">Root Account MFA</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-0-items-0-name-ja">Root Account MFA Enabled</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-0-items-0-target">IAM</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-0-items-0-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-0-items-0-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-0-items-0-tags">iam, mfa, root</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-0-items-0-requirements">Verify AccountMFAEnabled=1 via get-account-summary</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-0-items-1-id">IAM-02</span>. <span data-kata="p-categories-0-items-1-name">Unused IAM Credentials</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-0-items-1-name-ja">Unused IAM Credential Detection</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-0-items-1-target">IAM</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-0-items-1-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-0-items-1-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-0-items-1-tags">iam, credentials, hygiene</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-0-items-1-requirements">Detect keys unused for 90+ days via generate-credential-report</span>

</td>
</tr>
</table>

## <span data-kata="p-categories-1-id">storage</span>. <span data-kata="p-categories-1-name">Storage &amp; Encryption</span>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-1-items-0-id">S3-01</span>. <span data-kata="p-categories-1-items-0-name">S3 Public Access Block</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-1-items-0-name-ja">S3 Public Access Block</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-1-items-0-target">S3</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-1-items-0-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-1-items-0-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-1-items-0-tags">s3, public_access, storage</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-1-items-0-requirements">Verify all 4 settings are true via get-public-access-block</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-1-items-1-id">KMS-01</span>. <span data-kata="p-categories-1-items-1-name">KMS Key Rotation</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-1-items-1-name-ja">KMS Key Rotation</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-1-items-1-target">KMS</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-1-items-1-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-1-items-1-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-1-items-1-tags">kms, encryption, rotation</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-1-items-1-requirements">Verify enabled via get-key-rotation-status</span>

</td>
</tr>
</table>

## <span data-kata="p-categories-2-id">logging</span>. <span data-kata="p-categories-2-name">Logging &amp; Audit</span>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-2-items-0-id">LOG-01</span>. <span data-kata="p-categories-2-items-0-name">CloudTrail Enabled</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-2-items-0-name-ja">CloudTrail Enabled</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-2-items-0-target">CloudTrail</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-2-items-0-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-2-items-0-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-2-items-0-tags">cloudtrail, logging, audit</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-2-items-0-requirements">Verify enabled in all regions via describe-trails + get-trail-status</span>

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
This template generates an AWS infrastructure configuration audit checklist.
Categorize items by AWS service perspective such as IAM, storage, and logging.
Use service-prefixed IDs for each item (e.g., IAM-01, S3-01).
Describe specific AWS CLI commands and values to verify in requirements.

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
    requirements: Verify AccountMFAEnabled=1 via get-account-summary
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
    requirements: Detect keys unused for 90+ days via generate-credential-report
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
    requirements: Verify all 4 settings are true via get-public-access-block
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
    requirements: Verify enabled via get-key-rotation-status
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
    requirements: Verify enabled in all regions via describe-trails + get-trail-status
```

<!-- kata-structure-integrity: sha256:0f86b4f666b184597d4ec28ec5933bb13339346013885dbc39b8ee7b35be3c2f -->
</details>
