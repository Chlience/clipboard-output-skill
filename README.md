<h1 align="center">Clipboard Output Skill</h1>

<p align="center">
  <strong>Copy exact agent-generated text to your clipboard instead of fighting terminal UI selection.</strong>
</p>

<p align="center">
  <a href="./README_zh.md">中文</a> ·
  <a href="#quick-start">Quick Start</a> ·
  <a href="#usage">Usage</a> ·
  <a href="#verification">Verification</a> ·
  <a href="#documentation">Documentation</a>
</p>

<p align="center">
  <img alt="Codex Skill" src="https://img.shields.io/badge/Codex-skill-111827" />
  <img alt="Python" src="https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white" />
  <img alt="unittest" src="https://img.shields.io/badge/unittest-tested-2E7D32" />
  <img alt="Clipboard" src="https://img.shields.io/badge/Clipboard-cross--platform-0F766E" />
  <img alt="License" src="https://img.shields.io/badge/License-MIT-blue" />
</p>

<p align="center">
  <img alt="Clipboard Output Skill demo" src="./demo/clipboard-output-demo.gif" />
</p>

---

## What is Clipboard Output Skill?

Clipboard Output Skill is a Codex personal skill for generated text that must be pasted somewhere else exactly as written. It is designed for scripts, prompts, JSON, Markdown, shell commands, issue bodies, release notes, and other multi-line artifacts where terminal UI selection can add padding, lose indentation, or copy the wrong block.

The skill does not replace your clipboard manager and does not keep clipboard history. It gives the agent a clear rule: when exact copy/paste matters, write or choose the right artifact and place that artifact directly on the system clipboard.

## Who is it for?

- Codex users who often paste generated commands, scripts, configs, or prompts into other tools.
- Agent workflows where copying from a TUI adds left padding, bullets, borders, or other formatting noise.
- Multi-file generation tasks where only one useful entrypoint should be copied.
- Users who want clipboard safety checks before copying likely secrets.

## Features

- Copies exact generated artifacts to the system clipboard.
- Handles single-output and multi-file tasks with explicit copy rules.
- Refuses likely secrets by default, including API keys, tokens, passwords, cookies, and private keys.
- Supports dry-run backend detection without modifying the clipboard.
- Works across WSL, Windows, macOS, Linux desktop sessions, and Termux when a clipboard backend is available.

## Tech Stack

| Layer | Choice |
| --- | --- |
| Skill format | Codex personal skill (`SKILL.md`) |
| Helper runtime | Python 3.12+ standard library |
| Clipboard backends | PowerShell, `clip.exe`, `pbcopy`, `wl-copy`, `xclip`, `xsel`, Termux, Win32 API |
| Tests | Python `unittest` |
| Demo | Python renderer plus `ffmpeg` |
| CI | GitHub Actions |

## Quick Start

### 1. Install with an agent

If your coding agent supports installing skills from a GitHub URL, give it this repository URL:

```text
https://github.com/Chlience/clipboard-output-skill
```

Example prompt:

```text
Install the Codex skill from https://github.com/Chlience/clipboard-output-skill
```

### 2. Or install manually

```bash
git clone https://github.com/Chlience/clipboard-output-skill.git
cd clipboard-output-skill

mkdir -p ~/.agents/skills
cp -R skills/clipboard-output ~/.agents/skills/clipboard-output
```

Restart or reload Codex so it can discover the new skill metadata.

### 3. Verify the helper

```bash
python3 ~/.agents/skills/clipboard-output/scripts/copy_text.py \
  --file ~/.agents/skills/clipboard-output/SKILL.md \
  --dry-run
```

A successful dry run confirms that the helper can read input and detect a clipboard backend without changing the clipboard.

## Usage

After installation, ask the agent for copy-ready output in natural language:

```text
Generate the PowerShell script and put it on my clipboard.
```

```text
Write the release notes and copy the final Markdown.
```

```text
Create the config files, then copy the path I should open first.
```

You can also call the helper directly.

Copy a file:

```bash
python3 ~/.agents/skills/clipboard-output/scripts/copy_text.py --file ./script.bat
```

Copy short text:

```bash
python3 ~/.agents/skills/clipboard-output/scripts/copy_text.py --text "hello"
```

Copy standard input:

```bash
printf '%s\n' "hello" | python3 ~/.agents/skills/clipboard-output/scripts/copy_text.py --stdin
```

Allow copying sensitive-looking content only after an explicit decision:

```bash
python3 ~/.agents/skills/clipboard-output/scripts/copy_text.py --file ./.env --allow-sensitive
```

## Output Model

| Situation | Clipboard payload |
| --- | --- |
| One generated artifact | The artifact itself |
| Multiple generated files | The most useful entrypoint, path, command, archive path, or short manifest |
| Sensitive-looking content | Refused unless explicitly allowed |
| Clipboard backend unavailable | The artifact remains in a file and the agent reports a fallback |

The skill only combines multiple files into one pasteable block when the user explicitly asks for a single combined payload.

## Configuration

There is no project-level configuration file. Runtime behavior is controlled by command flags:

| Flag | Purpose |
| --- | --- |
| `--file` | Copy content from a file |
| `--text` | Copy a short string |
| `--stdin` | Copy standard input |
| `--dry-run` | Detect input and clipboard backend without copying |
| `--allow-sensitive` | Override the heuristic secret check |

## Data, Storage, and Output

The helper does not store clipboard history. It reads the selected input, checks it, and writes to the system clipboard through the first available backend.

For durable generated artifacts, the agent should create real files first and copy only the useful final payload. Temporary one-off clipboard payloads can be written under `/tmp` before copying.

## Safety

The clipboard is shared system state. Treat it as unsuitable for secrets by default.

The helper refuses likely sensitive content unless `--allow-sensitive` is provided. Detection is heuristic, so users should still avoid putting credentials, private keys, production logs, customer data, or other confidential material on the clipboard.

## Verification

Run from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s skills/clipboard-output/tests \
  -p 'test_*.py'

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s tests \
  -p 'test_*.py'
```

Parse the helper without writing `__pycache__` files:

```bash
python3 -B -c "import ast, pathlib; ast.parse(pathlib.Path('skills/clipboard-output/scripts/copy_text.py').read_text())"
```

Run a smoke check without touching the clipboard:

```bash
python3 skills/clipboard-output/scripts/copy_text.py \
  --file skills/clipboard-output/SKILL.md \
  --dry-run
```

## Documentation

- [Skill instructions](skills/clipboard-output/SKILL.md)
- [Clipboard helper](skills/clipboard-output/scripts/copy_text.py)
- [Skill unit tests](skills/clipboard-output/tests/test_copy_text.py)
- [Demo renderer](demo/README.md)
