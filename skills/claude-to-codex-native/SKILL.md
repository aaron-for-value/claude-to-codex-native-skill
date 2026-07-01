---
name: claude-to-codex-native
description: Migrate a heavy Claude Code or Claude desktop power-user setup to a Codex-native setup. Use when the user wants to uninstall Claude Code, remove Claude-flavored project/global config, convert Claude project memories into Codex project memories, migrate Claude skills/hooks/plugins into Codex-native .codex structures, remove Telegram/Claude marketplace integrations, clean shell startup files, or audit whether future Codex project chats will avoid redundant memory loading.
---

# Claude To Codex Native

## Goal

Convert a user's Claude Code environment into a Codex-native environment without carrying Claude assumptions forward.

Prefer Codex-native project files:

- Project skills: `<project>/.codex/skills/`
- Project memories: `<project>/.codex/memories/`
- Project hooks: `<project>/.codex/hooks.json`
- Global personal plugin source only when explicitly useful: `~/token-saving-hooks` or another Codex marketplace source

Do not convert Claude project memory into `AGENTS.md`. Keep `AGENTS.md` for rules; keep recallable history under `.codex/memories/`.

## Workflow

1. Inventory before editing.
   - Search shell startup files for `claude`, `CLAUDE`, `anthropic`, `ANTHROPIC`.
   - List global Claude config: `~/.claude`, `~/.claude.json`, `~/claude-backup`, `~/.cache/claude`.
   - List project `.claude` directories.
   - List Codex plugins and marketplaces; remove `claude-plugins-official`, Telegram, and other Claude-origin plugins when the user wants Codex-native only.
2. Migrate useful data.
   - Copy `~/.claude/projects/*/memory/*.md` into the matching project’s `.codex/memories/claude-import/`.
   - Generate `.codex/memories/index.md` and `.codex/memories/manifest.json`.
   - Copy useful `.claude/skills/<skill>` or `.agents/skills/<skill>` into `.codex/skills/<skill>`.
   - Rewrite visible skill docs that say `.claude/skills` to `.codex/skills`.
3. Install Codex-native hooks.
   - Use Codex hook config, not Claude statusLine or `.claude/settings.json`.
   - For token-saving hooks, place runnable scripts in `.codex/token-saving-hooks/` and register them in `.codex/hooks.json`.
4. Clean Claude live config only after migration is verified.
   - Remove project `.claude` directories.
   - Remove global Claude config/cache/app/CLI after explicit user approval.
   - Clean shell startup files.
5. Explain remaining "Claude" strings.
   - A path like `.codex/memories/claude-import/` is historical provenance, not active Claude config.
   - Imported memories may mention `.claude`; do not rewrite history unless the user asks.

## Script

Use `scripts/migrate_claude_to_codex.py` for repeatable dry-runs and applies.

Dry-run:

```bash
python3 <skill>/scripts/migrate_claude_to_codex.py \
  --home "$HOME" \
  --works-root "$HOME/works"
```

Apply migration without deletion:

```bash
python3 <skill>/scripts/migrate_claude_to_codex.py \
  --home "$HOME" \
  --works-root "$HOME/works" \
  --apply
```

Apply migration and remove Claude config:

```bash
python3 <skill>/scripts/migrate_claude_to_codex.py \
  --home "$HOME" \
  --works-root "$HOME/works" \
  --apply \
  --purge-claude
```

Install token-saving hooks from a Codex-only source:

```bash
python3 <skill>/scripts/migrate_claude_to_codex.py \
  --home "$HOME" \
  --works-root "$HOME/works" \
  --token-hooks-source "$HOME/token-saving-hooks" \
  --apply
```

## Safety Rules

- Before uploading any migrated artifact to GitHub or another remote, scan for API keys, tokens, cookies, session IDs, OAuth credentials, personal absolute paths, usernames, private repository URLs, conversation transcripts, cache files, and imported memories. Do not upload them.
- Never delete with only `--apply`; require `--purge-claude` for Claude deletion.
- Ask for approval before destructive commands or writes outside the workspace.
- Treat `learn/study`, `redNoteForAi`, and similar nonstandard paths as user-confirmed deletions only.
- If a project has both `.claude/skills` and `.codex/skills`, copy into `.codex/skills` and preserve the existing Codex version unless overwriting is necessary.
- Keep Telegram out unless the user explicitly asks for Telegram.

## Verification

After applying, verify:

```bash
command -v claude || true
npm list -g --depth=0 2>/dev/null | rg -n '@anthropic-ai/claude-code|claude' || true
find "$HOME/works" -maxdepth 3 -type d -name .claude -print
rg -n 'claude-plugins-official|telegram@claude|ANTHROPIC|CLAUDE' "$HOME/.codex/config.toml" "$HOME/.zshrc" 2>/dev/null
```

Expect no active CLI/app/plugin/shell hits. Imported memories may still contain historical references.
