# Template List

Built-in KATA ARchive (.katar) templates included with gospelo-kata.

```bash
gospelo-kata templates    # List all templates
```

---

## General Purpose

| Template | Description | Use Case |
|----------|------------|----------|
| `todo` | TODO list (task & status tracking) | Project management |
| `agenda` | Meeting agenda (attendees, topics, decisions) | Meetings |
| `checklist` | Structured checklist (categories, items, status) | QA, audits |

## Security Testing

| Template | Description | Depends On |
|----------|------------|------------|
| `test_spec` | Test case specification | `test_prereq` |
| `test_prereq` | Test prerequisites & environment setup | --- |
| `pretest_review` | Pre-test review checklist | `test_spec`, `test_prereq` |
| `api_test` | API test specification (endpoints, auth, response validation) | --- |
| `header_test` | HTTP response header inspection | --- |
| `infra_test` | Cloud infrastructure config & security audit | --- |
| `load_test` | Load & rate-limiting test | --- |
| `scan_results` | Source code scan results report | --- |

---

## Using a Template

### 1. Generate Scaffold

```bash
gospelo-kata prepare test_spec -o data.yml
```

Displays the template's **Prompt** and **Schema**, and outputs a scaffold `data.yml`.

### 2. Build

```bash
gospelo-kata build test_spec data.yml -o outputs/
```

### 3. Combining Dependent Templates

`test_spec` references `test_prereq` data. They can be combined in Excel output:

```bash
gospelo-kata generate test_spec.json -f excel --prereq prereq.json -o test.xlsx
```

---

## Color Schemes

Set `colorScheme` in the Style block to change semantic colors for enum values.

```yaml
colorScheme: vivid
```

### default --- Asagi

Clean light blue on white.

![default](https://github.com/gospelo-dev/kata/blob/main/docs/examples/en/color_schemes/images/todo_default.png?raw=true)

### pastel --- Jelly Mint

Mint green + dusty rose.

![pastel](https://github.com/gospelo-dev/kata/blob/main/docs/examples/en/color_schemes/images/todo_pastel.png?raw=true)

### vivid --- Vivid Gradient

Purple + cyan, high contrast.

![vivid](https://github.com/gospelo-dev/kata/blob/main/docs/examples/en/color_schemes/images/todo_vivid.png?raw=true)

### monochrome --- Sumi-ink

Ink-wash monochrome + crimson accent.

![monochrome](https://github.com/gospelo-dev/kata/blob/main/docs/examples/en/color_schemes/images/todo_monochrome.png?raw=true)

### ocean --- Blue Aura

Blue-grey + terracotta.

![ocean](https://github.com/gospelo-dev/kata/blob/main/docs/examples/en/color_schemes/images/todo_ocean.png?raw=true)

### Custom enumColors

Assign semantic roles per enum value:

```yaml
colorScheme: vivid
enumColors:
  status:
    todo: neutral
    done: positive
    blocked: negative
```

---

## Creating Custom Templates

Create your own templates and distribute them as `.katar` packages.

```bash
gospelo-kata pack-init ./my_template/    # Generate scaffold
# ... edit the template ...
gospelo-kata pack ./my_template/ -o my_template.katar
```

→ [Template Package](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/katar.md)
