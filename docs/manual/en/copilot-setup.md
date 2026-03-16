# GitHub Copilot Setup for gospelo-kata

Guide for integrating gospelo-kata with GitHub Copilot Chat in VSCode.

## Prerequisites

- VSCode with GitHub Copilot extension installed
- `gospelo-kata` CLI installed (`pip install gospelo-kata`)

## Setup Steps

### 1. Enable instruction files

Add the following to `.vscode/settings.json`:

```json
{
  "github.copilot.chat.codeGeneration.useInstructionFiles": true
}
```

This tells Copilot to load `.github/copilot-instructions.md` automatically on every chat session. Without this setting, Copilot will not follow the gospelo-kata workflow rules.

### 2. Auto-approve terminal commands (optional)

If Copilot keeps asking for permission to run terminal commands like `mkdir`, add:

```json
{
  "chat.tools.terminal.autoApprove": {
    "mkdir": true
  }
}
```

### 3. Instruction file

The file `.github/copilot-instructions.md` is automatically loaded by Copilot when `useInstructionFiles` is enabled. It defines the 3-step workflow rules:

1. Generate `data.yaml` (YAML data only)
2. Run `gospelo-kata assemble` (builds `_tpl.kata.md`)
3. Run `gospelo-kata render` + `gospelo-kata lint` (produces final output)

Key directives in this file:
- Execute all 3 steps continuously without asking for confirmation
- Never create `.kata.md` files by hand
- Never write `{#schema}`, `{#data}`, or `{#prompt}` blocks manually

### 4. Custom skills (optional)

Skill files are located in `skill/copilot/` and symlinked from `.github/copilot/skills/`:

```
.github/copilot/skills/
  gospelo-kata     -> ../../../skill/copilot/gospelo-kata
  gospelo-kata-gen -> ../../../skill/copilot/gospelo-kata-gen
```

To add a new skill symlink:

```bash
ln -s ../../../skill/copilot/{skill-name} .github/copilot/skills/{skill-name}
```

> **Note**: Custom skills in `.github/copilot/skills/` may not be loaded automatically depending on the Copilot version. The `copilot-instructions.md` approach is more reliable.

## File Structure

```
.github/
  copilot-instructions.md       <- Auto-loaded workflow rules
  copilot/skills/               <- Custom skill symlinks
.vscode/
  settings.json                 <- Copilot settings
skill/
  copilot/                      <- Copilot skill source files
    gospelo-kata/SKILL.md
    gospelo-kata-gen/SKILL.md
    gospelo-kata-import/SKILL.md
```

## Usage

In Copilot Chat, simply describe what you want to generate:

```
「リーダー人材定着プロジェクト」のセキュリティチェックリストを作成してください。
出力先: docs/output/
テンプレート: checklist
カテゴリ: 認証・認可(auth)、データ保護(data)、インフラ(infra)
```

Copilot will automatically follow the 3-step workflow defined in `copilot-instructions.md`.

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Copilot creates `.kata.md` directly | Instructions not loaded | Verify `useInstructionFiles: true` in settings.json |
| Copilot stops after Step 1 asking permission | Missing "no confirmation" directive | Check `copilot-instructions.md` has continuous execution instructions |
| YAML structure broken (wrong indentation) | Model context limitation | Use `assemble` command to minimize AI's template responsibility |
| Skills not recognized via `@workspace /skill-name` | Copilot version limitation | Use `copilot-instructions.md` instead of custom skills directory |

## Differences from Claude Code Setup

| Aspect | Copilot | Claude Code |
|--------|---------|-------------|
| Instruction loading | `.github/copilot-instructions.md` (auto) | `.claude/skills/` or CLAUDE.md |
| Skill files | `skill/copilot/` | `skill/claude-code/` |
| Settings | `.vscode/settings.json` | Claude Code config |
| Confirmation behavior | Needs explicit "no confirmation" directive | Agent mode runs automatically |
| Model | GPT-5 mini (smaller context) | Claude (larger context) |
