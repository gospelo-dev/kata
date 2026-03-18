**Prompt**

```yaml
This template generates a web security assessment checklist.
Categorize items by vulnerability type such as injection, authentication/authorization, and configuration/headers.
Describe specific verification steps and expected results in each item's requirements.
Use tags such as sqli, xss, dast, auth to classify assessment types.
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
description: Web Security Assessment Checklist
categories:
  - id: injection
    name: Injection
    items:
      - id: "1"
        name: SQL Injection
        name_ja: SQL Injection
        status: draft
        auto: full
        target: "API GW→Lambda"
        tags:
          - injection
          - sqli
          - dast
        requirements: "Normal: Standard parameters return expected response"
      - id: "2"
        name: XSS
        name_ja: Cross-Site Scripting
        status: draft
        auto: full
        target: "Frontend + API"
        tags:
          - injection
          - xss
          - dast
        requirements: "Reflected XSS: <script>alert(1)</script> must not be reflected as-is in HTML"
      - id: "3"
        name: Command Injection
        name_ja: OS Command Injection
        status: draft
        auto: full
        target: Lambda
        tags:
          - injection
          - command
          - dast
        requirements: "Detection: ; /bin/sleep 20 injection must not cause response delay (Time-based)"
      - id: "4"
        name: Path Traversal
        name_ja: Path Traversal
        status: draft
        auto: full
        target: "API GW→Lambda"
        tags:
          - injection
          - path_traversal
          - dast
        requirements: "Detection: ../../etc/passwd must not return system file contents"
  - id: auth
    name: Authentication & Authorization
    items:
      - id: "5"
        name: Brute Force
        name_ja: Brute Force Resistance
        status: draft
        auto: semi
        target: Cognito
        tags:
          - auth
          - brute_force
        requirements: "Rate limit: Consecutive failures (5+) on same account must trigger account lock or delay"
      - id: "6"
        name: IDOR
        name_ja: Insecure Direct Object Reference
        status: draft
        auto: partial
        target: "API GW→Lambda"
        tags:
          - auth
          - idor
        requirements: "Horizontal escalation: User A's token accessing User B's resource (user_id swap) must return 403"
      - id: "7"
        name: CSRF
        name_ja: Cross-Site Request Forgery
        status: draft
        auto: full
        target: API Gateway
        tags:
          - auth
          - csrf
        requirements: "Token validation: POST/PUT/DELETE requests without CSRF token must be rejected with 403"
  - id: config
    name: Configuration & Headers
    items:
      - id: "8"
        name: Security Headers
        name_ja: Security Headers
        status: draft
        auto: full
        target: CloudFront
        tags:
          - config
          - headers
        requirements: "HSTS: Strict-Transport-Security header must exist with max-age >= 31536000"
      - id: "9"
        name: Error Disclosure
        name_ja: Error Message Information Leak
        status: draft
        auto: full
        target: "Lambda / API GW"
        tags:
          - config
          - error
        requirements: "Stack trace: Stack trace must not be included in response on 500 error from invalid input"
      - id: "10"
        name: Dependency Check
        name_ja: Dependency Vulnerability Check
        status: draft
        auto: full
        target: "Astro / Lambda"
        tags:
          - config
          - sca
          - dependencies
        requirements: "npm audit: Zero high/critical vulnerabilities"
```

</details>
