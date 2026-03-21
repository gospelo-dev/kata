---
name: gospelo-kata-dict
description: Generate search dictionaries for gospelo-kata-retrieval by scanning project source code
---

# /kata-dict -- Search Dictionary Generator for KATA Retrieval

Scan a project directory to collect identifiers, then generate a domain-specific
search dictionary (`dictionaries/{domain}.yaml`) that powers gospelo-kata-retrieval.

All reports and generated content must be in the user's default language.

Execute all 3 steps without interruption. Do not ask for confirmation between steps.

---

## Overview

```
Step 1: Scan (script)    python scan.py  -> identifiers.yaml
Step 2: Generate (LLM)   Read identifiers.yaml -> write dictionary YAML
Step 3: Validate (script) python validate.py -> PASS/FAIL
```

The dictionary enables high-precision code search WITHOUT LLM at query time.
LLM cost is only incurred once during dictionary generation.

### Script Location

Scripts are bundled with this skill:

```
{skill_dir}/scripts/scan.py       # Step 1: AST/regex identifier extraction
{skill_dir}/scripts/validate.py   # Step 3: dictionary validation
```

Find the skill directory by locating this SKILL.md file.

---

## Step 1: Scan Source Code (script)

Run the scan script to collect identifiers. This is deterministic and fast (no LLM).

```bash
python {skill_dir}/scripts/scan.py \
  --dir {target_dir} \
  --output {output_dir}/identifiers.yaml \
  --top 200
```

Multiple directories:

```bash
python {skill_dir}/scripts/scan.py \
  --dir src/bff/ \
  --dir infra/modules/ \
  --lang python,terraform \
  --output identifiers.yaml
```

The script:
- Discovers files (excludes `.venv/`, `node_modules/`, `__pycache__/`, `.git/`)
- Extracts identifiers per language:
  - **Python**: functions, classes, decorators, imports, constants, string patterns (AST)
  - **TypeScript**: exports, imports, components (regex)
  - **Terraform**: resources, variables, modules, outputs (regex)
  - **Markdown**: headings (regex)
- Counts frequency, keeps top N identifiers
- Groups by domain (auth, encryption, network, etc.) using keyword hints
- Outputs `identifiers.yaml` with metadata, top identifiers, and domain groups

Read the output file before proceeding to Step 2.

---

## Step 2: Generate Dictionary (LLM)

Read `identifiers.yaml` from Step 1. For each domain group that has relevant
identifiers, generate a concept entry in the dictionary.

### Entry Format

```yaml
{concept_id}:
  ja: [Japanese search query candidates]
  en: [English search query candidates]
  keywords:
    # Generic identifiers used in any project
    - auth
    - login
  project_specific:
    # Identifiers actually found in THIS project's source code (from Step 1)
    - CognitoUserManagementService
    - InitiateAuth
  patterns:
    # Regex patterns for grep (must be valid regex)
    - "HTTPBearer|HTTPAuthorizationCredentials"
    - "Authorization.*Bearer"
  decorators:
    # Framework-specific decorators (optional)
    - "Depends(get_current_user)"
  headers:
    # HTTP headers (optional, web projects only)
    - "Authorization"
    - "X-Tenant-ID"
  related: [other_concept_ids]
```

### Generation Rules

1. **`project_specific` must only contain identifiers from `identifiers.yaml`.**
   Cross-reference against `domain_groups` and `top_identifiers` in the scan output.
   Never hallucinate identifiers. If unsure, omit.

2. **`keywords` are generic** -- common across any project in this domain.
   These ARE based on domain knowledge (not project-specific).

3. **`patterns` must be valid regex.** Escape special characters.
   Prefer alternation (`a|b`) over complex patterns.

4. **`related` creates a graph** -- enables chained search.
   If searching "auth" finds a file, the searcher can follow `related: [session]`
   to expand the search to session-related files.

5. **Avoid overly broad keywords** that match everything:
   BAD: `data`, `value`, `result`, `response`, `config`, `utils`
   GOOD: `auth_config`, `session_data`, `error_response`

6. **Include case variants** in `keywords`:
   `auth_middleware`, `authMiddleware`, `AuthMiddleware`

7. **One concept = one entry.** Do not duplicate.

### Domain Templates

The user specifies a domain. Use these as starting concept groups
(only generate entries for concepts that have actual identifiers in Step 1):

**security** (web application security testing):
```
auth, session, authz, injection, xss, encryption, tenant,
input_validation, cors, csrf, csp, ssrf, error_disclosure,
logging, network, s3_security, email_security, dependency, api_gateway
```

**api** (API documentation / testing):
```
endpoints, request, response, error_handling, pagination,
authentication, rate_limiting, versioning, serialization
```

**infra** (infrastructure / IaC):
```
compute, storage, network, iam, encryption, monitoring,
backup, dns, cdn, container, database, messaging
```

### File Header

```yaml
# gospelo-kata-retrieval dictionary
# domain: {domain}
# generated_from: {target_dir}
# lang: [{detected_languages}]
# generated_at: {ISO 8601 timestamp}
# entry_count: {number of concept entries}
```

### Output Path

```
{output_dir}/dictionaries/{domain}.yaml
```

Create `dictionaries/` if it does not exist.

---

## Step 3: Validate Dictionary (script)

Run the validation script immediately after writing the dictionary.

```bash
python {skill_dir}/scripts/validate.py \
  --dict {output_dir}/dictionaries/{domain}.yaml \
  --dir {target_dir}
```

The script checks:
1. YAML is parseable (no syntax errors)
2. Every `project_specific` value exists in source code
3. Every `patterns` value is valid regex
4. No duplicate concept entries
5. All `related` references point to existing concept IDs
6. Warns about overly broad keywords

If validation fails:
- Read the error report
- Fix the dictionary (adjust project_specific / patterns / related)
- Re-run validation until PASS

---

## Usage Examples

```
/kata-dict security --dir src/bff/ --output docs/kata_test/
/kata-dict api --dir src/bff/api/
/kata-dict infra --dir infra/modules/
/kata-dict security --dir src/bff/ --dir infra/modules/ --lang python,terraform
```

### Arguments

| Argument | Required | Description |
|----------|:--------:|-------------|
| `{domain}` | Yes | Domain name: `security`, `api`, `infra`, or custom |
| `--dir` | Yes | Target directory to scan (can specify multiple) |
| `--output` | No | Output directory (default: current directory) |
| `--lang` | No | Filter languages (default: auto-detect from extensions) |
| `--extend` | No | Path to existing dictionary to extend (add new entries only) |

---

## Extending an Existing Dictionary

When `--extend` is specified:

1. Read the existing dictionary
2. Run Step 1 scan
3. In Step 2, only generate entries for concepts NOT already in the dictionary
4. Merge and write the combined dictionary

This allows incremental dictionary building as the project evolves.

---

## Prohibited

- Do not hallucinate identifiers in `project_specific` -- every value must come from Step 1
- Do not generate entries for concepts with zero project-specific identifiers
- Do not use overly broad keywords (`data`, `value`, `config`, etc.)
- Do not write invalid regex in `patterns`
- Do not skip Step 1 -- always run scan.py first, then generate
- Do not skip Step 3 -- always run validate.py after writing the dictionary
