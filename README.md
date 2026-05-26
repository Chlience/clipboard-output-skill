# Clipboard Output Skill

`clipboard-output` is a Codex skill for avoiding broken copy/paste from terminal UIs. When an answer contains exact text the user is likely to paste elsewhere, the agent writes or copies the artifact directly instead of relying on chat selection.

The skill is useful for generated scripts, config files, prompts, JSON, Markdown, commands, issue bodies, release notes, and other multi-line artifacts.

## Status

Public beta.

Tested locally on WSL with the Windows clipboard. The helper includes support for macOS, Linux Wayland/X11, Termux, Windows PowerShell, and native Windows, but those platforms should be validated in their own environments before declaring a stable release.

## Repository Layout

```text
skills/
  clipboard-output/
    SKILL.md
    scripts/
      copy_text.py
    tests/
      test_copy_text.py
```

## Install

For Codex personal skills:

```bash
mkdir -p ~/.agents/skills
cp -R skills/clipboard-output ~/.agents/skills/clipboard-output
```

Restart or reload Codex so the new skill metadata is picked up.

## Usage

Copy from a file:

```bash
python3 ~/.agents/skills/clipboard-output/scripts/copy_text.py --file ./script.bat
```

Copy explicit short text:

```bash
python3 ~/.agents/skills/clipboard-output/scripts/copy_text.py --text "hello"
```

Copy from standard input:

```bash
printf '%s\n' "hello" | python3 ~/.agents/skills/clipboard-output/scripts/copy_text.py --stdin
```

Dry-run without touching the clipboard:

```bash
python3 ~/.agents/skills/clipboard-output/scripts/copy_text.py --file ./script.bat --dry-run
```

## Safety

The clipboard is shared system state. The helper refuses to copy content that looks like API keys, tokens, passwords, private keys, or similar secrets unless `--allow-sensitive` is provided.

Use `--allow-sensitive` only after intentionally deciding that the clipboard is the right place for that content:

```bash
python3 ~/.agents/skills/clipboard-output/scripts/copy_text.py --file ./.env --allow-sensitive
```

## Test

Run from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/clipboard-output/tests -p 'test_*.py'
python3 -B -c "import ast, pathlib; ast.parse(pathlib.Path('skills/clipboard-output/scripts/copy_text.py').read_text())"
```

## Known Limitations

- Clipboard access may fail in restricted sandboxes, remote SSH sessions, headless Linux, or WSL instances without access to Windows interop.
- Multi-file outputs still need judgment: the skill copies one payload and writes real files for the rest.
- Secret detection is heuristic. It can miss secrets or flag harmless text.
