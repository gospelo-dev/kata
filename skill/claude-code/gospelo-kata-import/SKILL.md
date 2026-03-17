---
name: gospelo-kata-import
description: Generate KATA Markdown™ test specifications from external sources (swagger.json, OpenAPI, etc.)
---

# /kata-import — Convert External Sources to KATA Markdown™

A skill that reads external sources such as swagger.json / OpenAPI specifications and automatically generates gospelo-kata test specification documents (.kata.md).

---

## Supported Sources

| Source | Extensions | Description |
|--------|-----------|-------------|
| OpenAPI / Swagger | `.json`, `.yaml` | REST API spec → API test specification |

---

## Workflow

### Step 1: Read the Source File

Read the swagger.json / OpenAPI file specified by the user.

```bash
# Read the file (using Read tool)
```

Extract the following information:
- **info**: API name, version
- **paths**: Each endpoint (method + path)
- **parameters**: Query/path/header parameters
- **requestBody**: Request body schema
- **responses**: Response codes and descriptions
- **security**: Authentication methods
- **tags**: Category classification

### Step 2: Design Test Cases

Generate test cases from each endpoint using the following perspectives:

#### Category Classification Rules

| OpenAPI Info | Test Category |
|-------------|--------------|
| tag | Use directly as category |
| No tag | Use the first path segment (e.g., `/users/...` → `users`) |
| security present | Add `Authentication & Authorization` category |

#### Test Case Generation Rules

For each endpoint, consider the following test cases:

1. **Happy path**: Request with correct parameters and verify expected response code (200/201)
2. **Validation**: Omit required parameters and verify 400 error
3. **Authentication**: If security is defined, verify 401/403 with no token/invalid token
4. **Boundary values**: If minLength/maxLength/minimum/maximum exist, test boundary values
5. **Non-existent resource**: For endpoints with path parameters, use a non-existent ID → 404

#### test_id Numbering Rules

```
{PREFIX}-{sequential:02d}
```

- PREFIX is user-specified, or auto-generated from the API name (e.g., `USER-API` → `UA`)
- Sequential numbers are ordered by category

#### Priority Rules

| Condition | Priority |
|-----------|----------|
| POST/PUT/DELETE method | high |
| security defined | high |
| GET without path parameters | medium |
| GET with path parameters | medium |
| OPTIONS/HEAD | low |

### Step 3: Generate .kata.md Source File

Generate a `.kata.md` file in the following format:

```markdown
{#schema
test_name: string
test_id_prefix: string
version: string
test_cases[]!:
  test_id: string!
  category: string!
  description: string!
  expected_result: string!
  priority: enum(high, medium, low)
  tags: string[]
#}

{#data
test_name: {API name} Test Specification
test_id_prefix: {PREFIX}
version: {API version}
test_cases:
  - test_id: {PREFIX}-01
    category: {category}
    description: {test description}
    expected_result: {expected result}
    priority: high
    tags:
      - {HTTP method lowercase}
      - {tag}
  ...
#}

# {{ test_name }}

> Prefix: {{ test_id_prefix }} | Version: {{ version }}

## Test Cases

| ID | Category | Description | Expected Result | Priority | Tags |
|:--:|----------|-------------|-----------------|:--------:|------|
{% for case in test_cases %}| {{ case.test_id }} | {{ case.category }} | {{ case.description }} | {{ case.expected_result }} | {{ case.priority }} | {{ case.tags | join(", ") }} |
{% endfor %}

Total: {{ test_cases | length }} test cases
```

### Step 4: Render & Verify

```bash
# Render
gospelo-kata render {source}.kata.md -o outputs/{source}.kata.md

# Lint verification
gospelo-kata lint outputs/{source}.kata.md

# Data extraction (round-trip check)
gospelo-kata extract outputs/{source}.kata.md
```

Verify that lint errors are 0. If D016 (HTML in span) appears:

```bash
gospelo-kata fmt outputs/{source}.kata.md
```

---

## Conversion Example

### Input: swagger.json (excerpt)

```json
{
  "info": { "title": "User Management API", "version": "2.0.0" },
  "paths": {
    "/users": {
      "get": {
        "tags": ["users"],
        "summary": "List all users",
        "parameters": [
          { "name": "page", "in": "query", "schema": { "type": "integer" } }
        ],
        "responses": { "200": { "description": "User list" } }
      },
      "post": {
        "tags": ["users"],
        "summary": "Create a new user",
        "security": [{ "bearerAuth": [] }],
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "required": ["name", "email"],
                "properties": {
                  "name": { "type": "string", "minLength": 1 },
                  "email": { "type": "string", "format": "email" }
                }
              }
            }
          }
        },
        "responses": {
          "201": { "description": "User created" },
          "400": { "description": "Validation error" },
          "401": { "description": "Unauthorized" }
        }
      }
    },
    "/users/{id}": {
      "get": {
        "tags": ["users"],
        "summary": "Get user by ID",
        "parameters": [
          { "name": "id", "in": "path", "required": true }
        ],
        "responses": {
          "200": { "description": "User details" },
          "404": { "description": "User not found" }
        }
      }
    }
  }
}
```

### Output: Test Cases (data section)

```yaml
test_name: User Management API Test Specification
test_id_prefix: UMA
version: 2.0.0
test_cases:
  - test_id: UMA-01
    category: users
    description: GET /users — Retrieve user list without pagination parameters and verify 200 is returned
    expected_result: Status 200. User list returned as a JSON array
    priority: medium
    tags:
      - get
      - users
      - list
  - test_id: UMA-02
    category: users
    description: POST /users — Create a user with required fields (name, email) and verify 201 is returned
    expected_result: Status 201. Created user information is returned
    priority: high
    tags:
      - post
      - users
      - create
  - test_id: UMA-03
    category: users
    description: POST /users — Omit the name field and verify 400 validation error is returned
    expected_result: Status 400. Error message includes the missing field name
    priority: high
    tags:
      - post
      - users
      - validation
  - test_id: UMA-04
    category: users
    description: POST /users — Request without authentication token and verify 401 is returned
    expected_result: Status 401. Authentication error message is returned
    priority: high
    tags:
      - post
      - users
      - authentication
  - test_id: UMA-05
    category: users
    description: GET /users/{id} — Request with an existing user ID and verify 200 with user details is returned
    expected_result: Status 200. User information for the specified ID is returned
    priority: medium
    tags:
      - get
      - users
      - detail
  - test_id: UMA-06
    category: users
    description: GET /users/{id} — Request with a non-existent user ID and verify 404 is returned
    expected_result: Status 404. Resource not found error message is returned
    priority: medium
    tags:
      - get
      - users
      - not-found
```

---

## Notes

- Write description and expected_result in **the user's language** (English by default)
- Data containing HTML tags is automatically sanitized during rendering
- Prioritize **practicality over exhaustiveness** — select representative cases rather than all combinations
- After generation, confirm with the user if they want to add, remove, or modify test cases
- The `params` field is optional — use it to record request parameter details as needed

---

## Usage Examples

```
/kata-import Generate an API test specification from swagger.json
/kata-import Create test cases from openapi.yaml endpoints
```
