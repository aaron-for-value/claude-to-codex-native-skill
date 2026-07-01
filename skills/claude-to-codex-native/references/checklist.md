# Migration Checklist

## Inventory

- If any migrated artifact will be uploaded to GitHub or another remote, run a sensitive-information scan first.
- Read `~/.codex/config.toml` and `~/.codex/hooks.json`.
- List `~/.claude`, `~/.claude.json`, `~/claude-backup`, `~/.cache/claude`.
- Search shell startup files:
  - `~/.zshrc`
  - `~/.zprofile`
  - `~/.zshenv`
  - `~/.bashrc`
  - `~/.bash_profile`
  - `~/.profile`
- List project `.claude`, `.codex`, `.agents`, `AGENTS.md`, `CLAUDE.md`.

## Memory Mapping

Map Claude project memory by decoded project path.

Example:

```text
~/.claude/projects/-home-user-works-redNoteNew/memory/*.md
-> <home>/works/redNoteNew/.codex/memories/claude-import/*.md
```

For each target project:

- Create `.codex/memories/claude-import/`.
- Copy memory files.
- Write `.codex/memories/index.md`.
- Write `.codex/memories/manifest.json`.

Do not put project history into `AGENTS.md`.

## Skill Mapping

Map useful skills to project-level Codex skills:

```text
<project>/.claude/skills/<name> -> <project>/.codex/skills/<name>
<project>/.agents/skills/<name> -> <project>/.codex/skills/<name>
```

Patch visible docs:

- `.claude/skills` -> `.codex/skills`
- "Claude Code" -> "Codex" only when it describes the current runtime, not historical notes.

## Hook Mapping

Claude concepts to avoid:

- `.claude/settings.json`
- `statusLine`
- `CLAUDE_PLUGIN_ROOT`
- `CLAUDE_PLUGIN_DATA`
- Telegram bot as primary remote access

Codex-native target:

- `.codex/hooks.json`
- `.codex/token-saving-hooks/`
- `~/.codex/config.toml` only for global Codex config
- Codex remote/mobile/app features rather than Telegram unless explicitly requested

## Purge

Delete only after migration is verified and the user approves:

- `~/.claude`
- `~/.claude.json`
- `~/claude-backup`
- `~/.cache/claude`
- Project `.claude`
- `/Applications/Claude.app`
- Claude Code npm package
- Claude URL handler app

Keep Codex import artifacts unless the user asks to remove historical records:

- `~/.codex/claude-cowork-transcript-imports`
- `~/.codex/claude-cowork-import-history.json`
- `.codex/memories/claude-import/`

## Publishing Safety

Never upload:

- API keys, tokens, cookies, bearer strings, session IDs, OAuth credentials
- Personal absolute paths, usernames, local workspace names, private repository URLs
- Conversation transcripts, imported memories, shell history, cache files, test logs
- Machine-specific app paths unless they are generic examples

Prefer placeholders:

- `<home>` instead of a machine-specific home directory
- `<project>` instead of a private project name
- `<works-root>` instead of a personal workspace path
