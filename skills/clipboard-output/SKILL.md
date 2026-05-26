---
name: clipboard-output
description: Use when the user needs to copy or paste generated text, scripts, prompts, config, JSON, Markdown, commands, or any exact multi-line output; especially when they mention clipboard, copy, paste, TUI spacing, left padding, or avoiding chat selection problems.
---

# Clipboard Output

## Core Rule

When the user is likely to copy exact generated content, put the final copyable text on the clipboard instead of relying on a chat code block.

This applies to scripts, config files, prompts, JSON, Markdown, commands, patches, issue text, PR bodies, release notes, and any multi-line artifact the user will paste elsewhere.

## Workflow

1. Decide what exact text the user needs to paste.
2. Check whether the content may contain secrets, credentials, private keys, production logs, personal data, or other sensitive material. If it does, do not copy it automatically; write it to a file or ask for explicit approval.
3. If the content is a durable artifact, write it to a file first using the normal file-editing rules.
4. Copy the exact final text with the bundled helper:

```bash
python3 ~/.agents/skills/clipboard-output/scripts/copy_text.py --file path/to/file
```

For one-off content that should not become a project file, use a temporary file under `/tmp`, then copy that file.

5. In the final response, say what was copied and include the file path if one exists. Do not also paste the full long content unless the user explicitly asks to see it in chat.

## What To Copy

- Copy only the artifact, not explanatory text around it.
- Preserve exact line endings and indentation.
- If the user asks for several separate snippets, copy the most immediately useful one and state which one was copied.
- If multiple files were created, follow the multi-file rules below.

## Sensitive Content

The clipboard is shared system state. Treat it as unsuitable for secrets by default.

Do not automatically copy:

- API keys, tokens, passwords, cookies, private keys, SSH keys, certificates, or `.env` files.
- Production logs, customer data, personal data, or proprietary records.
- Anything the user labels confidential, private, secret, sensitive, or internal-only.

If copying sensitive content is truly required, ask for explicit approval first. Then use:

```bash
python3 ~/.agents/skills/clipboard-output/scripts/copy_text.py --file path/to/file --allow-sensitive
```

If unsure, write the content to a file and report the path instead of copying it.

## Multiple Files

The clipboard reliably holds one text payload. For multiple files, do not copy each file one after another; the last copy wins and hides the earlier files.

Default behavior:

1. Create the real files in a directory.
2. Copy the most useful entrypoint, path, or run command to the clipboard.
3. In the final response, list the generated files and state exactly what was copied.

Choose the clipboard payload by intent:

- If one file is the normal user entrypoint, copy that file's content. Example: copy `.bat` when `.bat` and `.ps1` variants both exist.
- If the user needs to locate or share the generated set, copy the directory path, archive path, or a short manifest.
- If the user needs to run the set, copy the exact run command.
- If the user needs to send files elsewhere, create an archive and copy the archive path.
- If the user explicitly asks for one pasteable combined text, concatenate with clear file markers:

```text
--- file: path/to/a.txt ---
...

--- file: path/to/b.txt ---
...
```

Do not combine multiple files into one clipboard payload unless the user asked for a single combined paste or the receiving tool only accepts one text field.

## Commands

Copy from a file:

```bash
python3 ~/.agents/skills/clipboard-output/scripts/copy_text.py --file ./script.bat
```

Copy explicit short text:

```bash
python3 ~/.agents/skills/clipboard-output/scripts/copy_text.py --text "hello"
```

Copy from standard input only when explicitly requested:

```bash
printf '%s\n' "hello" | python3 ~/.agents/skills/clipboard-output/scripts/copy_text.py --stdin
```

Dry-run backend detection without touching the clipboard:

```bash
python3 ~/.agents/skills/clipboard-output/scripts/copy_text.py --file ./script.bat --dry-run
```

If an environment uses a shell wrapper, sandbox prefix, or approval command, apply that wrapper according to local instructions.

## Failure Handling

If clipboard copy fails:

- Keep the generated content in a file when possible.
- Report the failure and the file path.
- Give the shortest practical fallback command, for example `clip.exe < path` on WSL/Windows.
- Do not retry with broader permissions unless the clipboard update is necessary for the user's request.

Do not claim the clipboard was updated unless the helper reports success.
