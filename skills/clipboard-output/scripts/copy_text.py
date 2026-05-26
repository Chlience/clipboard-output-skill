#!/usr/bin/env python3
"""Copy text to the system clipboard across common Codex environments."""

from __future__ import annotations

import argparse
import ctypes
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


class ClipboardError(RuntimeError):
    pass


SENSITIVE_PATTERNS = [
    re.compile(
        r"(?i)\b(api[_-]?key|secret|token|password|passwd|pwd|access[_-]?token|"
        r"refresh[_-]?token|private[_-]?key)\b\s*[:=]\s*['\"]?[^'\"\s]{8,}"
    ),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
]


def is_wsl() -> bool:
    return bool(os.environ.get("WSL_DISTRO_NAME") or os.environ.get("WSL_INTEROP"))


def has_command(name: str) -> bool:
    return shutil.which(name) is not None


def run_with_stdin(command: list[str], text: str, encoding: str = "utf-8") -> None:
    completed = subprocess.run(
        command,
        input=text.encode(encoding),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.decode("utf-8", "replace").strip()
        raise ClipboardError(stderr or f"{command[0]} exited with {completed.returncode}")


def looks_sensitive(text: str) -> bool:
    return any(pattern.search(text) for pattern in SENSITIVE_PATTERNS)


def validate_text(text: str, allow_sensitive: bool = False) -> None:
    if looks_sensitive(text) and not allow_sensitive:
        raise ClipboardError("Refusing to copy likely sensitive content without --allow-sensitive")


def configure_windows_clipboard_api(user32, kernel32) -> None:
    kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = ctypes.c_void_p
    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalUnlock.restype = ctypes.c_int
    kernel32.GlobalFree.argtypes = [ctypes.c_void_p]
    kernel32.GlobalFree.restype = ctypes.c_void_p

    user32.OpenClipboard.argtypes = [ctypes.c_void_p]
    user32.OpenClipboard.restype = ctypes.c_int
    user32.EmptyClipboard.argtypes = []
    user32.EmptyClipboard.restype = ctypes.c_int
    user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
    user32.SetClipboardData.restype = ctypes.c_void_p
    user32.CloseClipboard.argtypes = []
    user32.CloseClipboard.restype = ctypes.c_int


def copy_windows_native(text: str) -> str:
    # CF_UNICODETEXT requires a NUL-terminated UTF-16LE buffer.
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    configure_windows_clipboard_api(user32, kernel32)

    cf_unicode_text = 13
    gmem_moveable = 0x0002

    data = (text + "\0").encode("utf-16le")
    handle = kernel32.GlobalAlloc(gmem_moveable, len(data))
    if not handle:
        raise ClipboardError("GlobalAlloc failed")

    locked = kernel32.GlobalLock(handle)
    if not locked:
        kernel32.GlobalFree(handle)
        raise ClipboardError("GlobalLock failed")

    ctypes.memmove(locked, data, len(data))
    kernel32.GlobalUnlock(handle)

    if not user32.OpenClipboard(None):
        kernel32.GlobalFree(handle)
        raise ClipboardError("OpenClipboard failed")

    try:
        if not user32.EmptyClipboard():
            raise ClipboardError("EmptyClipboard failed")
        if not user32.SetClipboardData(cf_unicode_text, handle):
            raise ClipboardError("SetClipboardData failed")
        handle = None
    finally:
        user32.CloseClipboard()
        if handle:
            kernel32.GlobalFree(handle)

    return "windows-native"


def copy_via_wsl_powershell(text: str) -> str:
    if not (has_command("powershell.exe") and has_command("wslpath")):
        raise ClipboardError("powershell.exe or wslpath not found")

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", delete=False) as f:
        f.write(text)
        temp_path = f.name

    try:
        win_path = subprocess.check_output(
            ["wslpath", "-w", temp_path],
            stderr=subprocess.PIPE,
            text=True,
        ).strip()
        command = [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            "Get-Content -Raw -Encoding UTF8 -LiteralPath $args[0] | Set-Clipboard",
            win_path,
        ]
        completed = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if completed.returncode != 0:
            stderr = completed.stderr.decode("utf-8", "replace").strip()
            raise ClipboardError(stderr or "powershell.exe Set-Clipboard failed")
    finally:
        try:
            os.unlink(temp_path)
        except FileNotFoundError:
            pass

    return "wsl-powershell"


def copy_with_command(text: str) -> str:
    if sys.platform == "darwin" and has_command("pbcopy"):
        run_with_stdin(["pbcopy"], text)
        return "pbcopy"

    if is_wsl():
        try:
            return copy_via_wsl_powershell(text)
        except ClipboardError:
            if has_command("clip.exe"):
                run_with_stdin(["clip.exe"], "\ufeff" + text, encoding="utf-16le")
                return "clip.exe"
            raise

    if has_command("wl-copy"):
        run_with_stdin(["wl-copy"], text)
        return "wl-copy"

    if has_command("xclip"):
        run_with_stdin(["xclip", "-selection", "clipboard"], text)
        return "xclip"

    if has_command("xsel"):
        run_with_stdin(["xsel", "--clipboard", "--input"], text)
        return "xsel"

    if has_command("termux-clipboard-set"):
        run_with_stdin(["termux-clipboard-set"], text)
        return "termux-clipboard-set"

    if has_command("powershell.exe"):
        run_with_stdin(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                "Set-Clipboard -Value ([Console]::In.ReadToEnd())",
            ],
            text,
        )
        return "powershell.exe"

    if has_command("powershell"):
        run_with_stdin(
            [
                "powershell",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                "Set-Clipboard -Value ([Console]::In.ReadToEnd())",
            ],
            text,
        )
        return "powershell"

    if has_command("pwsh"):
        run_with_stdin(
            [
                "pwsh",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                "Set-Clipboard -Value ([Console]::In.ReadToEnd())",
            ],
            text,
        )
        return "pwsh"

    raise ClipboardError("No clipboard backend found")


def detect_backend() -> str:
    if os.name == "nt":
        return "windows-native"
    if sys.platform == "darwin" and has_command("pbcopy"):
        return "pbcopy"
    if is_wsl() and has_command("powershell.exe") and has_command("wslpath"):
        return "wsl-powershell"
    if is_wsl() and has_command("clip.exe"):
        return "clip.exe"
    for command in ("wl-copy", "xclip", "xsel", "termux-clipboard-set", "powershell.exe", "powershell", "pwsh"):
        if has_command(command):
            return command
    return "none"


def read_text(args: argparse.Namespace) -> str:
    if args.file:
        return Path(args.file).read_text(encoding=args.encoding)
    if args.text is not None:
        return args.text
    if args.stdin:
        return sys.stdin.read()
    raise ClipboardError("Provide one input source: --file, --text, or --stdin")


def main() -> int:
    parser = argparse.ArgumentParser(description="Copy text to the system clipboard.")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--file", help="Read text from this file.")
    source.add_argument("--text", help="Copy this text directly.")
    source.add_argument("--stdin", action="store_true", help="Read text from standard input.")
    parser.add_argument("--encoding", default="utf-8", help="Encoding for --file. Default: utf-8.")
    parser.add_argument("--dry-run", action="store_true", help="Detect backend and validate input without copying.")
    parser.add_argument(
        "--allow-sensitive",
        action="store_true",
        help="Allow copying text that looks like a secret, token, password, or private key.",
    )
    args = parser.parse_args()

    try:
        text = read_text(args)
        validate_text(text, allow_sensitive=args.allow_sensitive)

        if args.dry_run:
            print(f"dry-run: {len(text)} chars, backend={detect_backend()}")
            return 0

        if os.name == "nt":
            backend = copy_windows_native(text)
        else:
            backend = copy_with_command(text)

        print(f"copied: {len(text)} chars via {backend}")
        return 0
    except Exception as exc:
        print(f"copy failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
