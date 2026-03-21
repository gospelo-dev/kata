# <span data-kata="p-description">Web Security Assessment Checklist</span>

> Version: <span data-kata="p-version">1.0</span>

## <span data-kata="p-categories-0-id">injection</span>. <span data-kata="p-categories-0-name">Injection</span>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-0-items-0-id">1</span>. <span data-kata="p-categories-0-items-0-name">SQL Injection</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-0-items-0-name-ja">SQL Injection</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-0-items-0-target">API GW→Lambda</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-0-items-0-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-0-items-0-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-0-items-0-tags">injection, sqli, dast</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-0-items-0-requirements">Normal: Standard parameters return expected response</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-0-items-1-id">2</span>. <span data-kata="p-categories-0-items-1-name">XSS</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-0-items-1-name-ja">Cross-Site Scripting</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-0-items-1-target">Frontend + API</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-0-items-1-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-0-items-1-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-0-items-1-tags">injection, xss, dast</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-0-items-1-requirements">Reflected XSS: &lt;script&gt;alert(1)&lt;/script&gt; must not be reflected as-is in HTML</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-0-items-2-id">3</span>. <span data-kata="p-categories-0-items-2-name">Command Injection</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-0-items-2-name-ja">OS Command Injection</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-0-items-2-target">Lambda</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-0-items-2-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-0-items-2-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-0-items-2-tags">injection, command, dast</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-0-items-2-requirements">Detection: ; /bin/sleep 20 injection must not cause response delay (Time-based)</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-0-items-3-id">4</span>. <span data-kata="p-categories-0-items-3-name">Path Traversal</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-0-items-3-name-ja">Path Traversal</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-0-items-3-target">API GW→Lambda</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-0-items-3-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-0-items-3-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-0-items-3-tags">injection, path_traversal, dast</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-0-items-3-requirements">Detection: ../../etc/passwd must not return system file contents</span>

</td>
</tr>
</table>

## <span data-kata="p-categories-1-id">auth</span>. <span data-kata="p-categories-1-name">Authentication &amp; Authorization</span>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-1-items-0-id">5</span>. <span data-kata="p-categories-1-items-0-name">Brute Force</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-1-items-0-name-ja">Brute Force Resistance</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-1-items-0-target">Cognito</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-1-items-0-auto">semi</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-1-items-0-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-1-items-0-tags">auth, brute_force</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-1-items-0-requirements">Rate limit: Consecutive failures (5+) on same account must trigger account lock or delay</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-1-items-1-id">6</span>. <span data-kata="p-categories-1-items-1-name">IDOR</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-1-items-1-name-ja">Insecure Direct Object Reference</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-1-items-1-target">API GW→Lambda</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-1-items-1-auto">partial</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-1-items-1-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-1-items-1-tags">auth, idor</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-1-items-1-requirements">Horizontal escalation: User A's token accessing User B's resource (user_id swap) must return 403</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-1-items-2-id">7</span>. <span data-kata="p-categories-1-items-2-name">CSRF</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-1-items-2-name-ja">Cross-Site Request Forgery</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-1-items-2-target">API Gateway</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-1-items-2-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-1-items-2-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-1-items-2-tags">auth, csrf</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-1-items-2-requirements">Token validation: POST/PUT/DELETE requests without CSRF token must be rejected with 403</span>

</td>
</tr>
</table>

## <span data-kata="p-categories-2-id">config</span>. <span data-kata="p-categories-2-name">Configuration &amp; Headers</span>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-2-items-0-id">8</span>. <span data-kata="p-categories-2-items-0-name">Security Headers</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-2-items-0-name-ja">Security Headers</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-2-items-0-target">CloudFront</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-2-items-0-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-2-items-0-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-2-items-0-tags">config, headers</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-2-items-0-requirements">HSTS: Strict-Transport-Security header must exist with max-age &gt;= 31536000</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-2-items-1-id">9</span>. <span data-kata="p-categories-2-items-1-name">Error Disclosure</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-2-items-1-name-ja">Error Message Information Leak</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-2-items-1-target">Lambda / API GW</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-2-items-1-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-2-items-1-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-2-items-1-tags">config, error</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-2-items-1-requirements">Stack trace: Stack trace must not be included in response on 500 error from invalid input</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-2-items-2-id">10</span>. <span data-kata="p-categories-2-items-2-name">Dependency Check</span>**

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-2-items-2-name-ja">Dependency Vulnerability Check</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-2-items-2-target">Astro / Lambda</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-2-items-2-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-2-items-2-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-2-items-2-tags">config, sca, dependencies</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-2-items-2-requirements">npm audit: Zero high/critical vulnerabilities</span>

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
This template generates a web security assessment checklist.
Categorize items by vulnerability type such as injection, authentication/authorization, and configuration/headers.
Describe specific verification steps and expected results in each item's requirements.
Use tags such as sqli, xss, dast, auth to classify assessment types.

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
description: Web Security Assessment Checklist
categories:
- id: injection
  name: Injection
  items:
  - id: '1'
    name: SQL Injection
    name_ja: SQL Injection
    status: draft
    auto: full
    target: API GW→Lambda
    tags:
    - injection
    - sqli
    - dast
    requirements: 'Normal: Standard parameters return expected response'
  - id: '2'
    name: XSS
    name_ja: Cross-Site Scripting
    status: draft
    auto: full
    target: Frontend + API
    tags:
    - injection
    - xss
    - dast
    requirements: 'Reflected XSS: <script>alert(1)</script> must not be reflected
      as-is in HTML'
  - id: '3'
    name: Command Injection
    name_ja: OS Command Injection
    status: draft
    auto: full
    target: Lambda
    tags:
    - injection
    - command
    - dast
    requirements: 'Detection: ; /bin/sleep 20 injection must not cause response delay
      (Time-based)'
  - id: '4'
    name: Path Traversal
    name_ja: Path Traversal
    status: draft
    auto: full
    target: API GW→Lambda
    tags:
    - injection
    - path_traversal
    - dast
    requirements: 'Detection: ../../etc/passwd must not return system file contents'
- id: auth
  name: Authentication & Authorization
  items:
  - id: '5'
    name: Brute Force
    name_ja: Brute Force Resistance
    status: draft
    auto: semi
    target: Cognito
    tags:
    - auth
    - brute_force
    requirements: 'Rate limit: Consecutive failures (5+) on same account must trigger
      account lock or delay'
  - id: '6'
    name: IDOR
    name_ja: Insecure Direct Object Reference
    status: draft
    auto: partial
    target: API GW→Lambda
    tags:
    - auth
    - idor
    requirements: 'Horizontal escalation: User A''s token accessing User B''s resource
      (user_id swap) must return 403'
  - id: '7'
    name: CSRF
    name_ja: Cross-Site Request Forgery
    status: draft
    auto: full
    target: API Gateway
    tags:
    - auth
    - csrf
    requirements: 'Token validation: POST/PUT/DELETE requests without CSRF token must
      be rejected with 403'
- id: config
  name: Configuration & Headers
  items:
  - id: '8'
    name: Security Headers
    name_ja: Security Headers
    status: draft
    auto: full
    target: CloudFront
    tags:
    - config
    - headers
    requirements: 'HSTS: Strict-Transport-Security header must exist with max-age
      >= 31536000'
  - id: '9'
    name: Error Disclosure
    name_ja: Error Message Information Leak
    status: draft
    auto: full
    target: Lambda / API GW
    tags:
    - config
    - error
    requirements: 'Stack trace: Stack trace must not be included in response on 500
      error from invalid input'
  - id: '10'
    name: Dependency Check
    name_ja: Dependency Vulnerability Check
    status: draft
    auto: full
    target: Astro / Lambda
    tags:
    - config
    - sca
    - dependencies
    requirements: 'npm audit: Zero high/critical vulnerabilities'
```

<!-- kata-structure-integrity: sha256:a6edf575d5148de2bb6cb46e3392ee96ef3d423f40621035062ab900d1bdfdc0 -->
</details>
