# Claude to Codex Native Skill

A Codex skill for migrating a serious Claude Code or Claude desktop setup into a Codex-native workflow.

It is designed for users who want to fully leave Claude Code behind rather than keep a compatibility layer. The skill focuses on converting useful project memory, skills, hooks, and shell/app configuration into Codex-native locations.

## What It Migrates

- Claude project memories into `.codex/memories/`
- Claude or `.agents` skills into project-level `.codex/skills/`
- Token-saving hooks into `.codex/token-saving-hooks/` plus `.codex/hooks.json`
- Shell startup files by removing Claude/Anthropic environment leftovers
- Global and project Claude config after explicit approval

It intentionally does not copy project memory into `AGENTS.md`. `AGENTS.md` should stay focused on rules and workflow; historical recall should live in `.codex/memories/`.

## Install

Copy the skill folder into your project:

```bash
mkdir -p .codex/skills
cp -R skills/claude-to-codex-native .codex/skills/
```

Or install it into your Codex skills directory if you intentionally want it globally:

```bash
mkdir -p ~/.codex/skills
cp -R skills/claude-to-codex-native ~/.codex/skills/
```

## Use

Ask Codex:

```text
Use claude-to-codex-native to migrate this Claude Code setup to Codex-native form.
```

The bundled script defaults to dry-run:

```bash
python3 skills/claude-to-codex-native/scripts/migrate_claude_to_codex.py
```

Apply writes:

```bash
python3 skills/claude-to-codex-native/scripts/migrate_claude_to_codex.py --apply
```

Destructive cleanup requires both flags:

```bash
python3 skills/claude-to-codex-native/scripts/migrate_claude_to_codex.py --apply --purge-claude
```

## Safety

Run the dry-run first and inspect the planned actions. The script does not delete Claude files unless `--purge-claude` is passed together with `--apply`.

