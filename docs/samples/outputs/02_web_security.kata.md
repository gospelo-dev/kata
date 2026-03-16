# <span data-kata="p-description">Webセキュリティ診断チェックリスト</span>

> Version: <span data-kata="p-version">1.0</span>

## <span data-kata="p-categories-id">injection</span>. <span data-kata="p-categories-name">インジェクション系</span>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-items-id">1</span>. <span data-kata="p-categories-items-name">SQL Injection</span>** <span class="kata-badge kata-badge-draft"><span data-kata="p-categories-items-status">draft</span></span>

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-items-name-ja">SQLインジェクション</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-items-target">API GW→Lambda</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-items-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-items-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-items-tags">injection, sqli, dast</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-items-requirements">正常系: 通常パラメータで期待通りのレスポンスが返る</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-items-id">2</span>. <span data-kata="p-categories-items-name">XSS</span>** <span class="kata-badge kata-badge-draft"><span data-kata="p-categories-items-status">draft</span></span>

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-items-name-ja">クロスサイトスクリプティング</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-items-target">フロントエンド + API</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-items-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-items-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-items-tags">injection, xss, dast</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-items-requirements">Reflected XSS: &lt;script&gt;alert(1)&lt;/script&gt;がHTMLにそのまま反映されないこと</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-items-id">3</span>. <span data-kata="p-categories-items-name">Command Injection</span>** <span class="kata-badge kata-badge-draft"><span data-kata="p-categories-items-status">draft</span></span>

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-items-name-ja">OSコマンドインジェクション</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-items-target">Lambda</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-items-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-items-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-items-tags">injection, command, dast</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-items-requirements">検出: ; /bin/sleep 20 挿入でレスポンス遅延が発生しないこと (Time-based)</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-items-id">4</span>. <span data-kata="p-categories-items-name">Path Traversal</span>** <span class="kata-badge kata-badge-draft"><span data-kata="p-categories-items-status">draft</span></span>

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-items-name-ja">パストラバーサル</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-items-target">API GW→Lambda</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-items-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-items-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-items-tags">injection, path_traversal, dast</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-items-requirements">検出: ../../etc/passwd でシステムファイルの内容が返らないこと</span>

</td>
</tr>
</table>

## <span data-kata="p-categories-id">auth</span>. <span data-kata="p-categories-name">認証・認可</span>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-items-id">5</span>. <span data-kata="p-categories-items-name">Brute Force</span>** <span class="kata-badge kata-badge-draft"><span data-kata="p-categories-items-status">draft</span></span>

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-items-name-ja">ブルートフォース耐性</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-items-target">Cognito</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-items-auto">semi</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-items-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-items-tags">auth, brute_force</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-items-requirements">レート制限: 同一アカウントへの連続失敗（5回以上）でアカウントロックまたは遅延が発生すること</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-items-id">6</span>. <span data-kata="p-categories-items-name">IDOR</span>** <span class="kata-badge kata-badge-draft"><span data-kata="p-categories-items-status">draft</span></span>

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-items-name-ja">認可制御の不備</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-items-target">API GW→Lambda</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-items-auto">partial</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-items-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-items-tags">auth, idor</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-items-requirements">水平権限昇格: ユーザーAのトークンでユーザーBのリソース（user_id差し替え）にアクセスし403が返ること</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-items-id">7</span>. <span data-kata="p-categories-items-name">CSRF</span>** <span class="kata-badge kata-badge-draft"><span data-kata="p-categories-items-status">draft</span></span>

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-items-name-ja">クロスサイトリクエストフォージェリ</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-items-target">API Gateway</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-items-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-items-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-items-tags">auth, csrf</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-items-requirements">トークン検証: CSRFトークンなしでPOST/PUT/DELETEリクエストが403で拒否されること</span>

</td>
</tr>
</table>

## <span data-kata="p-categories-id">config</span>. <span data-kata="p-categories-name">設定・ヘッダー</span>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-items-id">8</span>. <span data-kata="p-categories-items-name">Security Headers</span>** <span class="kata-badge kata-badge-draft"><span data-kata="p-categories-items-status">draft</span></span>

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-items-name-ja">セキュリティヘッダー</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-items-target">CloudFront</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-items-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-items-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-items-tags">config, headers</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-items-requirements">HSTS: Strict-Transport-Security ヘッダーが存在し max-age &gt;= 31536000 であること</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-items-id">9</span>. <span data-kata="p-categories-items-name">Error Disclosure</span>** <span class="kata-badge kata-badge-draft"><span data-kata="p-categories-items-status">draft</span></span>

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-items-name-ja">エラーメッセージ情報漏洩</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-items-target">Lambda / API GW</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-items-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-items-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-items-tags">config, error</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-items-requirements">スタックトレース: 不正入力で500エラー発生時にスタックトレースがレスポンスに含まれないこと</span>

</td>
</tr>
</table>

<table class="kata-card">
<tr>
<td class="kata-left">

**<span data-kata="p-categories-items-id">10</span>. <span data-kata="p-categories-items-name">Dependency Check</span>** <span class="kata-badge kata-badge-draft"><span data-kata="p-categories-items-status">draft</span></span>

<table class="kata-props">
<tr><td colspan="2"><b><span data-kata="p-categories-items-name-ja">依存パッケージ脆弱性</span></b></td></tr>
<tr><td>target</td><td><span data-kata="p-categories-items-target">Astro / Lambda</span></td></tr>
<tr><td>auto</td><td><span data-kata="p-categories-items-auto">full</span></td></tr>
<tr><td>status</td><td><span class="kata-status-draft"><span data-kata="p-categories-items-status">draft</span></span></td></tr>
<tr><td>tags</td><td><span data-kata="p-categories-items-tags">config, sca, dependencies</span></td></tr>
</table>

</td>
<td class="kata-right">

- <span data-kata="p-categories-items-requirements">npm audit: high/critical の脆弱性が0件であること</span>

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
description: Webセキュリティ診断チェックリスト
categories:
- id: injection
  name: インジェクション系
  items:
  - id: '1'
    name: SQL Injection
    name_ja: SQLインジェクション
    status: draft
    auto: full
    target: API GW→Lambda
    tags:
    - injection
    - sqli
    - dast
    requirements: '正常系: 通常パラメータで期待通りのレスポンスが返る'
  - id: '2'
    name: XSS
    name_ja: クロスサイトスクリプティング
    status: draft
    auto: full
    target: フロントエンド + API
    tags:
    - injection
    - xss
    - dast
    requirements: 'Reflected XSS: <script>alert(1)</script>がHTMLにそのまま反映されないこと'
  - id: '3'
    name: Command Injection
    name_ja: OSコマンドインジェクション
    status: draft
    auto: full
    target: Lambda
    tags:
    - injection
    - command
    - dast
    requirements: '検出: ; /bin/sleep 20 挿入でレスポンス遅延が発生しないこと (Time-based)'
  - id: '4'
    name: Path Traversal
    name_ja: パストラバーサル
    status: draft
    auto: full
    target: API GW→Lambda
    tags:
    - injection
    - path_traversal
    - dast
    requirements: '検出: ../../etc/passwd でシステムファイルの内容が返らないこと'
- id: auth
  name: 認証・認可
  items:
  - id: '5'
    name: Brute Force
    name_ja: ブルートフォース耐性
    status: draft
    auto: semi
    target: Cognito
    tags:
    - auth
    - brute_force
    requirements: 'レート制限: 同一アカウントへの連続失敗（5回以上）でアカウントロックまたは遅延が発生すること'
  - id: '6'
    name: IDOR
    name_ja: 認可制御の不備
    status: draft
    auto: partial
    target: API GW→Lambda
    tags:
    - auth
    - idor
    requirements: '水平権限昇格: ユーザーAのトークンでユーザーBのリソース（user_id差し替え）にアクセスし403が返ること'
  - id: '7'
    name: CSRF
    name_ja: クロスサイトリクエストフォージェリ
    status: draft
    auto: full
    target: API Gateway
    tags:
    - auth
    - csrf
    requirements: 'トークン検証: CSRFトークンなしでPOST/PUT/DELETEリクエストが403で拒否されること'
- id: config
  name: 設定・ヘッダー
  items:
  - id: '8'
    name: Security Headers
    name_ja: セキュリティヘッダー
    status: draft
    auto: full
    target: CloudFront
    tags:
    - config
    - headers
    requirements: 'HSTS: Strict-Transport-Security ヘッダーが存在し max-age >= 31536000 であること'
  - id: '9'
    name: Error Disclosure
    name_ja: エラーメッセージ情報漏洩
    status: draft
    auto: full
    target: Lambda / API GW
    tags:
    - config
    - error
    requirements: 'スタックトレース: 不正入力で500エラー発生時にスタックトレースがレスポンスに含まれないこと'
  - id: '10'
    name: Dependency Check
    name_ja: 依存パッケージ脆弱性
    status: draft
    auto: full
    target: Astro / Lambda
    tags:
    - config
    - sca
    - dependencies
    requirements: 'npm audit: high/critical の脆弱性が0件であること'
```

</details>
