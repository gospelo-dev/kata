# Skill Guide — Usage by Use Case

How to use KATA Markdown™ AI skills organized by use case.

---

## Basic Workflow

All skills follow a common workflow:

```
prepare → data.yml creation → import-data → build → lint → (fix loop)
```

| Step | Command | Description |
|------|---------|-------------|
| Prepare | `gospelo-kata prepare {template}` | Show template info + generate empty data.yml |
| Export | `gospelo-kata export {template} --part prompt,schema` | Fast extraction of prompt and schema (AI use) |
| Import | `gospelo-kata import-data {template} data.yml -q` | Validate data.yml against schema before build |
| Build | `gospelo-kata build {template} data.yml` | Template + data → final output |
| Validate | `gospelo-kata lint {output}.kata.md` | Structure & schema validation |
| Extract | `gospelo-kata extract {output}.kata.md` | Recover data from rendered output |

---

## Skills Overview

| Skill | Purpose | Data Source |
|-------|---------|-------------|
| `/kata` | Basic operations | Manual (write data.yml yourself) |
| `/kata-gen` | Generate data from scratch | AI creates from Prompt |
| `/kata-convert` | Convert existing documents | Existing Markdown / text / CSV etc. |
| `/kata-collect` | Collect data via web search | Internet sources |
| `/kata-import` | Convert structured sources | OpenAPI / Swagger etc. |
| `/kata-pack` | Template management | — |

---

## Use Case 1: Inspect Template and Create Data Manually

**Skill**: `/kata`

Inspect an existing template, write `data.yml` yourself, and generate the document.

```bash
# 1. List available templates
gospelo-kata templates

# 2. View template info and generate empty data.yml
gospelo-kata prepare checklist -o data.yml

# 3. Edit data.yml (manually or with AI assistance)

# 4. Validate data, build, and lint
gospelo-kata import-data checklist data.yml -q
gospelo-kata build checklist data.yml -o outputs/
gospelo-kata lint outputs/checklist.kata.md
```

**Best for**:
- Understanding template structure
- Fine-grained control over data content
- Having a smaller AI generate data from the schema

---

## Use Case 2: Have AI Generate Data from Scratch

**Skill**: `/kata-gen`

AI reads the template's Prompt and Schema, then generates data according to your requirements.

```
/kata-gen checklist
```

**Examples**:
- "Create a web application security checklist"
- "Create an authentication API test specification"
- "Create an agenda for next week's sprint planning meeting"

**Best for**:
- Creating new documents from scratch
- No source data available
- Drafting based on AI knowledge

---

## Use Case 3: Convert Existing Documents to KATA Format

**Skill**: `/kata-convert`

Reads existing documents in custom formats (Markdown, text, CSV, etc.) and converts them to `data.yml` conforming to a KATA template schema.

```
/kata-convert docs/old_checklist.md checklist
```

**Examples**:
- Migrate checklists managed in Excel to KATA Markdown
- Unify existing test specifications into a new template format
- Convert meeting notes text into an agenda template

**Best for**:
- Existing document assets available
- Unifying formats
- Migrating from old template versions to the latest

---

## Use Case 4: Collect Data via Web Search

**Skill**: `/kata-collect`

Performs web searches on topics specified in the template's Prompt (OWASP, RFC, etc.) and generates data from collected information.

```
/kata-collect checklist
```

**Examples**:
- Security checklist based on OWASP Top 10
- Infrastructure audit items based on latest industry standards
- API test cases based on RFCs

**Best for**:
- Up-to-date information needed
- Data based on authoritative sources (official docs, standards, RFCs)
- Specific research targets specified in the Prompt

---

## Use Case 5: Generate Test Specifications from OpenAPI / Swagger

**Skill**: `/kata-import`

Reads structured specification files like OpenAPI or Swagger and auto-generates test cases per endpoint.

```
/kata-import swagger.json test_spec
```

**Examples**:
- Auto-generate API test specifications from `swagger.json`
- Create comprehensive test cases from `openapi.yaml` endpoints

**Best for**:
- Machine-readable specification files available
- Efficient API test specification creation
- Comprehensive per-endpoint test case coverage

---

## Use Case 6: Create, Edit, and Distribute Templates

**Skill**: `/kata-pack`

Create custom templates and distribute them as `.katar` packages.

```
/kata-pack
```

**Examples**:
- Create project-specific checklist templates
- Customize existing template schemas
- Package team templates for sharing

**Best for**:
- Built-in templates don't meet requirements
- Distributing unified formats across a team
- Customizing template schemas and layouts

---

## Which Skill Should I Use?

```
Where does the data come from?
│
├─ Write it yourself      → /kata
├─ AI generates it        → /kata-gen
├─ Existing documents     → /kata-convert
├─ Web sources            → /kata-collect
├─ Structured files       → /kata-import
│
Creating a template?      → /kata-pack
```

---

## Fix Loop

When lint reports errors, fix the data and rebuild:

```bash
# 1. Check lint errors
gospelo-kata lint outputs/checklist.kata.md

# 2. Fix data.yml

# 3. Validate, rebuild, and revalidate
gospelo-kata import-data checklist data.yml -q
gospelo-kata build checklist data.yml -o outputs/
gospelo-kata lint outputs/checklist.kata.md

# Repeat until 0 errors
```

---

## Directory Structure

### Single Document

```
project/
├── data.yml              # Data
├── outputs/
│   └── checklist.kata.md  # Final output
```

### Test Suite (Multiple Documents)

```
test_suite/
├── 01_sql_injection/
│   ├── data.yml
│   └── outputs/
│       └── test_spec.kata.md
├── 02_xss/
│   ├── data.yml
│   └── outputs/
│       └── test_spec.kata.md
└── checklist.json          # For coverage analysis
```

### Coverage Analysis

```bash
gospelo-kata coverage --checklist checklist.json --dir test_suite/
```

---

## Round-trip Verification

Recover original data from rendered documents to verify correct conversion:

```bash
gospelo-kata extract outputs/checklist.kata.md -o extracted.yml
# Compare extracted.yml with the original data.yml
```

---

## Common Notes

- All skills follow the `data.yml` → `import-data` → `build` → `lint` flow to produce final output
- `data.yml` is written in YAML format (not JSON)
- Prompt blocks are used only as data generation guidelines
- Fix `data.yml` and rebuild until lint errors reach 0
