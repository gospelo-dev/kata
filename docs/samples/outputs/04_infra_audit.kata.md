# <span data-kata="p-description">AWSインフラ設定監査チェックリスト</span>

> Version: <span data-kata="p-version">1.0</span>

## <span data-kata="p-categories-id">iam</span>. <span data-kata="p-categories-name">IAM・アクセス制御</span>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-items-id">IAM-01</span>. <span data-kata="p-categories-items-name">Root Account MFA</span>** <span class="kata-badge kata-badge-draft"><span data-kata="p-categories-items-status">draft</span></span>

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-items-name-ja">ルートアカウントMFA有効化</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-items-target">IAM</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-items-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-items-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-items-tags">iam, mfa, root</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-items-requirements">get-account-summary で AccountMFAEnabled=1 を確認</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-items-id">IAM-02</span>. <span data-kata="p-categories-items-name">Unused IAM Credentials</span>** <span class="kata-badge kata-badge-draft"><span data-kata="p-categories-items-status">draft</span></span>

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-items-name-ja">未使用IAMクレデンシャル検出</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-items-target">IAM</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-items-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-items-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-items-tags">iam, credentials, hygiene</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-items-requirements">generate-credential-report で 90日以上未使用のキーを検出</span>

</td>
</tr>
</table>

## <span data-kata="p-categories-id">storage</span>. <span data-kata="p-categories-name">ストレージ・暗号化</span>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-items-id">S3-01</span>. <span data-kata="p-categories-items-name">S3 Public Access Block</span>** <span class="kata-badge kata-badge-draft"><span data-kata="p-categories-items-status">draft</span></span>

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-items-name-ja">S3パブリックアクセスブロック</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-items-target">S3</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-items-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-items-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-items-tags">s3, public_access, storage</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-items-requirements">get-public-access-block で全4項目がtrueか確認</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-items-id">KMS-01</span>. <span data-kata="p-categories-items-name">KMS Key Rotation</span>** <span class="kata-badge kata-badge-draft"><span data-kata="p-categories-items-status">draft</span></span>

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-items-name-ja">KMSキーローテーション</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-items-target">KMS</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-items-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-items-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-items-tags">kms, encryption, rotation</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-items-requirements">get-key-rotation-status で有効化を確認</span>

</td>
</tr>
</table>

## <span data-kata="p-categories-id">logging</span>. <span data-kata="p-categories-name">ログ・監査</span>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-items-id">LOG-01</span>. <span data-kata="p-categories-items-name">CloudTrail Enabled</span>** <span class="kata-badge kata-badge-draft"><span data-kata="p-categories-items-status">draft</span></span>

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-items-name-ja">CloudTrail有効化</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-items-target">CloudTrail</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-items-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-items-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-items-tags">cloudtrail, logging, audit</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-items-requirements">describe-trails + get-trail-status で全リージョン有効化を確認</span>

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
    requirements: get-account-summary で AccountMFAEnabled=1 を確認
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
    requirements: generate-credential-report で 90日以上未使用のキーを検出
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
    requirements: get-public-access-block で全4項目がtrueか確認
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
    requirements: get-key-rotation-status で有効化を確認
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
    requirements: describe-trails + get-trail-status で全リージョン有効化を確認
```

</details>
