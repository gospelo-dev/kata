# gospelo-kata

**KATA Markdown&#8482;** --- A toolkit for generating, validating, and bidirectionally syncing structured documents from templates.

```
pip install gospelo-kata
```

---

### LiveMorph --- Bidirectional Real-time Sync

Freely move between Data and HTML. Edits on either side are instantly reflected in the other.

| Direction | Command | Action |
|-----------|---------|--------|
| Data → HTML | `sync to-html` | Edit Data block → re-execute template → update body |
| HTML → Data | `sync to-data` | Edit body spans → extract to Data block → re-render |

In the VS Code extension, switch direction with one click from the **status bar**. Auto-sync on save.

→ [LiveMorph Guide](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/livemorph.md)

---

### Human-AI Readable --- Readable by Both Humans and AI

A single `.kata.md` file contains **template, schema, data, and body**.
Reviewable directly on GitHub. AI reads Prompt + Schema to auto-generate data.

```
.kata.md (self-contained)
├── Prompt        ... Instructions for AI
├── Template      ... Jinja2 template
├── Schema        ... YAML shorthand type definitions
├── Data          ... YAML data
└── Body          ... Rendered body (data-kata spans)
```

→ [KATA Markdown Format](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/kata-markdown-format.md)

---

### Secure Packaging --- KATA ARchive&#8482; (.katar)

Distribute templates safely as **1 package = 1 template = 1 schema**.
ZIP-based, no extraction needed. Just place in `./templates/` and use immediately.

```bash
gospelo-kata pack ./my_template/ -o my_template.katar
gospelo-kata build my_template data.yml -o outputs/
```

→ [Template Package](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/katar.md)

---

## Built-in Templates

| Template | Purpose |
|----------|---------|
| `todo` | TODO list |
| `agenda` | Meeting agenda |
| `checklist` | Structured checklist |
| `test_spec` | Test case specification |
| `api_test` | API test specification |
| `header_test` | HTTP header inspection |
| `infra_test` | Infrastructure audit |
| `load_test` | Load test specification |
| `scan_results` | Source code scan report |
| `test_prereq` | Test prerequisites |
| `pretest_review` | Pre-test review |

→ [Template List](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/templates.md)

---

## Documentation

| Page | Overview |
|------|----------|
| [Quick Start](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/quick-start.md) | From install to first render |
| [LiveMorph Guide](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/livemorph.md) | Bidirectional sync usage |
| [Template List](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/templates.md) | Built-in templates + color schemes |
| [KATA Markdown Format](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/kata-markdown-format.md) | Template syntax and output structure |
| [CLI Reference](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/cli-reference.md) | All command options |
| [Lint Rules](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/lint-rules.md) | Error codes (S/T/F/V/D/E) and fixes |
| [VS Code Integration](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/vscode.md) | Extension, LiveMorph, hover |
| [Template Package](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/katar.md) | .katar creation and distribution |
| [Copilot Setup](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/copilot-setup.md) | GitHub Copilot Chat integration |
| [Skill Guide](https://github.com/gospelo-dev/kata/blob/main/docs/manual/en/skill-guide.md) | AI skill usage |
