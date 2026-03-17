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
description: Webセキュリティ診断チェックリスト
categories:
  - id: injection
    name: インジェクション系
    items:
      - id: "1"
        name: SQL Injection
        name_ja: SQLインジェクション
        status: draft
        auto: full
        target: "API GW\u2192Lambda"
        tags:
          - injection
          - sqli
          - dast
        requirements: "正常系: 通常パラメータで期待通りのレスポンスが返る"
      - id: "2"
        name: XSS
        name_ja: クロスサイトスクリプティング
        status: draft
        auto: full
        target: "フロントエンド + API"
        tags:
          - injection
          - xss
          - dast
        requirements: "Reflected XSS: <script>alert(1)</script>がHTMLにそのまま反映されないこと"
      - id: "3"
        name: Command Injection
        name_ja: OSコマンドインジェクション
        status: draft
        auto: full
        target: Lambda
        tags:
          - injection
          - command
          - dast
        requirements: "検出: ; /bin/sleep 20 挿入でレスポンス遅延が発生しないこと (Time-based)"
      - id: "4"
        name: Path Traversal
        name_ja: パストラバーサル
        status: draft
        auto: full
        target: "API GW\u2192Lambda"
        tags:
          - injection
          - path_traversal
          - dast
        requirements: "検出: ../../etc/passwd でシステムファイルの内容が返らないこと"
  - id: auth
    name: 認証・認可
    items:
      - id: "5"
        name: Brute Force
        name_ja: ブルートフォース耐性
        status: draft
        auto: semi
        target: Cognito
        tags:
          - auth
          - brute_force
        requirements: "レート制限: 同一アカウントへの連続失敗（5回以上）でアカウントロックまたは遅延が発生すること"
      - id: "6"
        name: IDOR
        name_ja: 認可制御の不備
        status: draft
        auto: partial
        target: "API GW\u2192Lambda"
        tags:
          - auth
          - idor
        requirements: "水平権限昇格: ユーザーAのトークンでユーザーBのリソース（user_id差し替え）にアクセスし403が返ること"
      - id: "7"
        name: CSRF
        name_ja: クロスサイトリクエストフォージェリ
        status: draft
        auto: full
        target: API Gateway
        tags:
          - auth
          - csrf
        requirements: "トークン検証: CSRFトークンなしでPOST/PUT/DELETEリクエストが403で拒否されること"
  - id: config
    name: 設定・ヘッダー
    items:
      - id: "8"
        name: Security Headers
        name_ja: セキュリティヘッダー
        status: draft
        auto: full
        target: CloudFront
        tags:
          - config
          - headers
        requirements: "HSTS: Strict-Transport-Security ヘッダーが存在し max-age >= 31536000 であること"
      - id: "9"
        name: Error Disclosure
        name_ja: エラーメッセージ情報漏洩
        status: draft
        auto: full
        target: "Lambda / API GW"
        tags:
          - config
          - error
        requirements: "スタックトレース: 不正入力で500エラー発生時にスタックトレースがレスポンスに含まれないこと"
      - id: "10"
        name: Dependency Check
        name_ja: 依存パッケージ脆弱性
        status: draft
        auto: full
        target: "Astro / Lambda"
        tags:
          - config
          - sca
          - dependencies
        requirements: "npm audit: high/critical の脆弱性が0件であること"
#}

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
