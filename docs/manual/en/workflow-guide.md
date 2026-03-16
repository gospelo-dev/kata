# Workflow Guide

How to manage the document generation pipeline.

---

## Workflow Steps

```
init -> validate -> generate -> lint -> review
```

| Step | Description | Automation |
|------|-------------|------------|
| `init` | Initialize templates and directories | `gospelo-kata init` |
| `validate` | Schema validation of JSON data | `gospelo-kata validate` |
| `generate` | Generate .kata.md documents | `gospelo-kata render` / `generate` |
| `lint` | Structural validation | `gospelo-kata lint` |
| `review` | Review deliverables (human or AI) | Manual |

---

## Basic Flow

### 1. Initialize

```bash
mkdir my_suite && cd my_suite
gospelo-kata init --type test_spec
```

Output:
```
my_suite/
+-- templates/          # Template files
+-- outputs/            # Output destination
+-- .workflow_status.json
```

### 2. Create source file and render

```bash
# Create source .kata.md (edit in editor)
vim xss_test.kata.md

# Render
gospelo-kata render xss_test.kata.md -o outputs/xss_test.kata.md
```

### 3. Validate

```bash
gospelo-kata lint outputs/xss_test.kata.md
```

### 4. Record status

```bash
gospelo-kata workflow-status --suite-dir . --mark-done init
gospelo-kata workflow-status --suite-dir . --mark-done validate --note "schema OK"
gospelo-kata workflow-status --suite-dir . --mark-done generate
gospelo-kata workflow-status --suite-dir . --mark-done lint --note "0 errors"
gospelo-kata workflow-status --suite-dir . --mark-done review --note "Extract verified"
```

### 5. Check progress

```bash
gospelo-kata workflow-status --suite-dir .
```

```
Template: test_spec
Round:    0
Progress: 5/5

  [OK] init (2026-03-16T10:00:00) schema OK
  [OK] validate (2026-03-16T10:01:00) schema OK
  [OK] generate (2026-03-16T10:01:05)
  [OK] lint (2026-03-16T10:01:10) 0 errors
  [OK] review (2026-03-16T10:02:00) Extract verified
```

---

## Retry (Fix Loop)

When lint reports errors, fix the source data and re-run.

```bash
# lint NG -> retry
gospelo-kata workflow-status --suite-dir . --retry --retry-reason "D016: HTML tag in span"

# Fix source -> re-render -> re-lint
gospelo-kata render xss_test.kata.md -o outputs/xss_test.kata.md
gospelo-kata lint outputs/xss_test.kata.md

# Re-mark steps
gospelo-kata workflow-status --suite-dir . --mark-done validate
gospelo-kata workflow-status --suite-dir . --mark-done generate
gospelo-kata workflow-status --suite-dir . --mark-done lint --note "0 errors"
```

`--retry` behavior:
1. Resets `validate` / `generate` / `lint` status
2. Increments `round` by 1
3. Records previous state in `history`

```
Round 0: init -> validate -> generate -> lint (NG)
  | --retry
Round 1: fix source -> validate -> generate -> lint (OK) -> review
```

---

## .workflow_status.json Structure

```json
{
  "template": "test_spec",
  "steps": {
    "init":     { "done": true, "at": "2026-03-16T10:00:00" },
    "validate": { "done": true, "at": "2026-03-16T10:01:00" },
    "generate": { "done": false },
    "lint":     { "done": false },
    "review":   { "done": false }
  },
  "round": 0,
  "history": []
}
```

---

## AI Integration Workflow

Recommended flow when working with AI (Claude, etc.):

### 1. Pass template specification to AI

```bash
gospelo-kata show-prompt test_spec   # AI instructions
gospelo-kata show-schema test_spec   # JSON Schema
```

### 2. Request data generation from AI

Ask AI to generate JSON/YAML data following the schema.

### 3. Validate -> Generate -> Lint

```bash
gospelo-kata validate data.json
gospelo-kata render source.kata.md -o outputs/result.kata.md
gospelo-kata lint outputs/result.kata.md
```

### 4. Feed errors back to AI

Pass lint errors to AI for data correction.

```bash
gospelo-kata lint outputs/result.kata.md --format vscode
# Pass the output directly to AI
```

### 5. Round-trip verification

```bash
gospelo-kata extract outputs/result.kata.md -o extracted.json
# Compare extracted.json with original data
```

---

## Directory Structure Patterns

### Single Document

```
project/
+-- source.kata.md
+-- outputs/
|   +-- source.kata.md
+-- .workflow_status.json
```

### Test Suite (Multiple Documents)

```
test_suite/
+-- 01_sql_injection/
|   +-- sql_injection.kata.md
|   +-- outputs/
|   |   +-- sql_injection.kata.md
|   |   +-- extracted.json
|   +-- templates/
|   +-- .workflow_status.json
+-- 02_xss/
|   +-- xss.kata.md
|   +-- outputs/
|   +-- .workflow_status.json
+-- checklist.json            # For coverage analysis
```

### Coverage Analysis

```bash
gospelo-kata coverage --checklist checklist.json --dir test_suite/
```

Checks whether `.kata.md` files exist in each subdirectory.
