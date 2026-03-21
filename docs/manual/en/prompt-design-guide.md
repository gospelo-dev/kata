# Prompt Design Guide

Rules for writing `**Prompt**` blocks in KATA templates.

---

## Design Principles

1. **English only** — prompts are written in English for consistency
2. **3-part structure** — (a) what it generates (1 line), (b) how to fill key fields (2-3 lines), (c) enum semantics if needed (0-2 lines)
3. **No syntax documentation** — schema notation, Jinja2 syntax, and output structure are never in the prompt
4. **No tool instructions** — CLI commands and workflow steps belong in [SKILL.md](https://github.com/gospelo-dev/kata/tree/main/skill), not in the prompt
5. **Schema is the source of truth** — type constraints, required fields, and structure are defined in the Schema block only

---

## Format

```yaml
{one-line description of what this template generates}
{2-3 lines: how to populate the main array/object fields}
{0-2 lines: enum semantics if domain-specific clarification is needed}
```

Target: **3-6 lines** per prompt.

---

## Examples

### Good (5 lines)

```yaml
This template generates a structured checklist document with categories and actionable items.
Each categories entry groups related items under an id and name.
Each item has a unique id, name (English), name_ja (Japanese), and a requirements description of what must be verified.
auto indicates the automation level: full = fully automated, semi = partially automated, partial = mostly manual with tool assist, manual = fully manual.
status tracks the item lifecycle: draft = not started, pending = under review, approve = accepted, reject = rejected.
```

### Bad

```yaml
# NG: contains syntax documentation
This template generates a checklist.
Use string! for required fields and string for optional fields.
Arrays are denoted with [] suffix.
Use {{ variable }} for Jinja2 template variables.
The output will contain <table> elements with data-kata attributes.
Run gospelo-kata render to generate the output.
```

---

## What Is NOT in Prompts

The following information belongs elsewhere and must never appear in prompt blocks:

| Information | Where It Belongs |
|---|---|
| Schema notation (`string!`, `enum()`, `[]!`) | Schema block in the template |
| Jinja2 syntax (`{{ }}`, `{% %}`) | Template body |
| Output structure (HTML tables, card layout) | Template body |
| CLI commands (`gospelo-kata assemble`, etc.) | [SKILL.md](https://github.com/gospelo-dev/kata/tree/main/skill) |
| Workflow steps (assemble → render → lint) | [SKILL.md](https://github.com/gospelo-dev/kata/tree/main/skill) |
| Tool-specific conventions (status defaults) | Schema block default values |

---

## Prompt Injection Countermeasures

Prompts are executed by AI when generating data. To prevent misuse through tampered templates, the following safeguards are in place:

### 1. Template Trust Mechanism

On first use or when prompt content changes, the user is asked to review and approve the prompt before execution. The approval hash is stored in `.template_trust.json`.

### 2. Pattern-based Injection Detection (P002)

The linter and `assemble` command scan prompt content for patterns commonly associated with prompt injection:

| Category | Examples |
|----------|----------|
| Role/identity override | "you are now", "act as a", "pretend to be" |
| Instruction override | "ignore previous instructions", "disregard above rules" |
| System prompt extraction | "show your system prompt", "reveal your instructions" |
| Command execution | "execute command", "run shell", `os.system(...)` |
| Chat-ML delimiters | `<\|im_start\|>`, `[INST]`, `<<SYS>>` |
| Data exfiltration | "send data to", "upload to" |
| Credential access | "show api key", "read password" |

Detection is pattern-match based and not exhaustive. It serves as a first line of defense — always review prompt content before trusting a template.

### 3. What Prompts Must NOT Contain

- System-level instructions to AI (role assignment, behavior modification)
- Shell commands or code execution directives
- References to credentials, API keys, or secrets
- Chat-ML or model-specific delimiter tokens
- Instructions to ignore, override, or extract prior instructions

---

## Why These Rules

The prompt is the **only context an AI refers to when generating data**.
Including syntax or tool instructions causes:

- Prompt bloat that obscures essential information for the AI
- Dual maintenance with the schema, leading to inconsistencies
- Sync failures when templates are updated but prompts are not

Prompts should contain only **"what to generate"** and **"what each field means"**.
