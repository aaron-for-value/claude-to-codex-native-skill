#!/usr/bin/env python3
"""Migrate Claude Code assets to Codex-native project structures.

Default mode is dry-run. Use --apply to write. Use --purge-claude in addition
to --apply for destructive cleanup.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path


SHELL_FILES = [
    ".zshrc",
    ".zprofile",
    ".zshenv",
    ".bashrc",
    ".bash_profile",
    ".profile",
]


def log(actions: list[str], message: str) -> None:
    actions.append(message)


def copy_tree(src: Path, dst: Path, apply: bool, actions: list[str]) -> None:
    if not src.exists():
        return
    log(actions, f"copy_tree {src} -> {dst}")
    if apply:
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)


def copy_file(src: Path, dst: Path, apply: bool, actions: list[str]) -> None:
    if not src.exists():
        return
    log(actions, f"copy_file {src} -> {dst}")
    if apply:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def rm_path(path: Path, apply: bool, actions: list[str]) -> None:
    if not path.exists() and not path.is_symlink():
        return
    log(actions, f"remove {path}")
    if apply:
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        else:
            path.unlink()


def project_from_claude_dir(project_dir: Path, works_root: Path) -> Path | None:
    name = project_dir.name
    prefix = "-"
    if not name.startswith(prefix):
        return None
    parts = [p for p in name.split("-") if p]
    candidate = Path("/" + "/".join(parts))
    try:
        candidate.relative_to(works_root)
    except ValueError:
        return None
    return candidate


def title_from_md(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    in_frontmatter = False
    for i, raw in enumerate(text.splitlines()):
        line = raw.strip()
        if i == 0 and line == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if line == "---":
                in_frontmatter = False
            elif line.lower().startswith(("title:", "summary:", "name:")):
                return line.split(":", 1)[1].strip().strip('"') or path.stem
            continue
        if line.startswith("#"):
            return line.lstrip("#").strip() or path.stem
        if line:
            return line[:80]
    return path.stem


def migrate_memories(home: Path, works_root: Path, apply: bool, actions: list[str]) -> None:
    projects_root = home / ".claude/projects"
    if not projects_root.exists():
        return
    for project_dir in sorted(projects_root.iterdir()):
        memory_dir = project_dir / "memory"
        if not memory_dir.is_dir():
            continue
        target_project = project_from_claude_dir(project_dir, works_root)
        if target_project is None:
            log(actions, f"skip_memory not_under_works {memory_dir}")
            continue
        if not target_project.exists():
            log(actions, f"skip_memory missing_target {memory_dir} -> {target_project}")
            continue
        md_files = sorted(memory_dir.glob("*.md"))
        if not md_files:
            continue
        memory_root = target_project / ".codex/memories"
        import_dir = memory_root / "claude-import"
        manifest = {
            "source_memory_dir": str(memory_dir),
            "target_project": str(target_project),
            "files": [],
        }
        index = [
            f"# {target_project.name} Project Memories",
            "",
            "Imported historical project memories. Read this index first, then open only the specific memory file needed for the task.",
            "",
            "## Files",
            "",
        ]
        for src in md_files:
            dst = import_dir / src.name
            copy_file(src, dst, apply, actions)
            title = title_from_md(src)
            rel = f"claude-import/{src.name}"
            index.append(f"- [`{rel}`]({rel}) - {title}")
            manifest["files"].append({"source": str(src), "dest": str(dst), "title": title})
        if apply:
            memory_root.mkdir(parents=True, exist_ok=True)
            (memory_root / "index.md").write_text("\n".join(index) + "\n", encoding="utf-8")
            (memory_root / "manifest.json").write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        log(actions, f"write {memory_root / 'index.md'}")
        log(actions, f"write {memory_root / 'manifest.json'}")


def migrate_project_skills(project: Path, apply: bool, actions: list[str]) -> None:
    for source_base in [project / ".claude/skills", project / ".agents/skills"]:
        if not source_base.is_dir():
            continue
        for skill_dir in sorted(p for p in source_base.iterdir() if p.is_dir()):
            dst = project / ".codex/skills" / skill_dir.name
            copy_tree(skill_dir, dst, apply, actions)
            if apply:
                for md in dst.rglob("*.md"):
                    text = md.read_text(encoding="utf-8", errors="replace")
                    text = text.replace("`.claude/skills/`", "`.codex/skills/`")
                    text = text.replace(".claude/skills/", ".codex/skills/")
                    md.write_text(text, encoding="utf-8")


def install_token_hooks(project: Path, source: Path, apply: bool, actions: list[str]) -> None:
    hooks_src = source / "hooks"
    scripts_src = source / "scripts"
    if not hooks_src.is_dir():
        log(actions, f"skip_token_hooks missing {hooks_src}")
        return
    root = project / ".codex/token-saving-hooks"
    copy_tree(hooks_src, root / "hooks", apply, actions)
    copy_tree(scripts_src, root / "scripts", apply, actions)
    hooks_dir = root / "hooks"
    config = {
        "hooks": {
            "UserPromptSubmit": [{"hooks": [{"type": "command", "command": f"python3 {hooks_dir / 'user-prompt-submit.py'}", "timeout": 5}]}],
            "PreToolUse": [
                {"matcher": "Read", "hooks": [{"type": "command", "command": f"bash {hooks_dir / 'pre-tool-dedup.sh'}"}]},
                {"matcher": "Bash", "hooks": [
                    {"type": "command", "command": f"bash {hooks_dir / 'pre-bash-diff-guard.sh'}"},
                    {"type": "command", "command": f"bash {hooks_dir / 'pre-bash-dedup.sh'}"},
                ]},
            ],
            "PostToolUse": [{"matcher": "Read", "hooks": [{"type": "command", "command": f"bash {hooks_dir / 'post-tool-dedup.sh'}"}]}],
            "PreCompact": [{"hooks": [{"type": "command", "command": f"bash {hooks_dir / 'precompact-snapshot.sh'}", "timeout": 15}]}],
            "SessionStart": [{"hooks": [{"type": "command", "command": f"bash {hooks_dir / 'session-start-restore.sh'}", "timeout": 5}]}],
            "Stop": [{"hooks": [{"type": "command", "command": f"bash {hooks_dir / 'stop-quality-gate.sh'}"}]}],
        }
    }
    log(actions, f"write {project / '.codex/hooks.json'}")
    if apply:
        (project / ".codex").mkdir(parents=True, exist_ok=True)
        (project / ".codex/hooks.json").write_text(
            json.dumps(config, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def clean_shell(home: Path, apply: bool, actions: list[str]) -> None:
    pattern = re.compile(
        r"\n# .*?(?:Claude|CLAUDE|Anthropic|ANTHROPIC).*?\n(?=\n?# |\n?[A-Za-z_]+=|\Z)",
        re.S,
    )
    for name in SHELL_FILES:
        path = home / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        original = text
        text = pattern.sub("\n", text)
        lines = []
        for line in text.splitlines():
            if re.search(r"\b(CLAUDE|ANTHROPIC|claude|anthropic)\b", line):
                continue
            lines.append(line)
        new_text = "\n".join(lines) + "\n"
        if new_text != original:
            log(actions, f"clean_shell {path}")
            if apply:
                path.write_text(new_text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--home", default=str(Path.home()))
    parser.add_argument("--works-root", default=str(Path.home() / "works"))
    parser.add_argument("--extra-project", action="append", default=[])
    parser.add_argument("--token-hooks-source")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--purge-claude", action="store_true")
    parser.add_argument("--clean-shell", action="store_true", default=True)
    args = parser.parse_args()

    home = Path(args.home).expanduser()
    works_root = Path(args.works_root).expanduser()
    actions: list[str] = []

    migrate_memories(home, works_root, args.apply, actions)

    projects = [p for p in works_root.iterdir() if p.is_dir()] if works_root.exists() else []
    projects += [Path(p).expanduser() for p in args.extra_project]
    for project in sorted(set(projects)):
        migrate_project_skills(project, args.apply, actions)
        if args.token_hooks_source:
            install_token_hooks(project, Path(args.token_hooks_source).expanduser(), args.apply, actions)

    if args.clean_shell:
        clean_shell(home, args.apply, actions)

    if args.purge_claude:
        for path in [
            home / ".claude",
            home / ".claude.json",
            home / "claude-backup",
            home / ".cache/claude",
            home / "Applications/Claude Code URL Handler.app",
        ]:
            rm_path(path, args.apply, actions)
        for project in projects:
            rm_path(project / ".claude", args.apply, actions)

    print(json.dumps({"apply": args.apply, "purge_claude": args.purge_claude, "actions": actions}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
