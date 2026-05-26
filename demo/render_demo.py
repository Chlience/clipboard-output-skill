#!/usr/bin/env python3
"""Render the README demo GIF with ffmpeg.

The demo is intentionally generated, not hand-recorded, so repository users can
rebuild it without a GUI session.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = ROOT / "demo"
DEFAULT_OUTPUT = DEMO_DIR / "clipboard-output-demo.gif"
WIDTH = 1100
HEIGHT = 620
DURATION = 12
FPS = 15
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def escape_text(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace(":", "\\:")
        .replace(",", "\\,")
        .replace("%", "\\%")
    )


def drawbox(
    x: int,
    y: int,
    w: int,
    h: int,
    color: str,
    thickness: str | int = "fill",
    *,
    enable: str | None = None,
) -> str:
    options = [f"x={x}", f"y={y}", f"w={w}", f"h={h}", f"color={color}", f"t={thickness}"]
    if enable:
        options.append(f"enable='{enable}'")
    return "drawbox=" + ":".join(options)


def drawtext(
    text: str,
    x: int,
    y: int,
    *,
    size: int = 24,
    color: str = "F8FAFC",
    font: str = FONT_MONO,
    enable: str | None = None,
) -> str:
    options = [
        f"fontfile={font}",
        f"text='{escape_text(text)}'",
        f"x={x}",
        f"y={y}",
        f"fontsize={size}",
        f"fontcolor={color}",
    ]
    if enable:
        options.append(f"enable='{enable}'")
    return "drawtext=" + ":".join(options)


def lines(
    texts: list[str],
    x: int,
    y: int,
    *,
    size: int = 22,
    color: str = "CBD5E1",
    enable: str | None = None,
) -> list[str]:
    return [
        drawtext(text, x, y + index * int(size * 1.45), size=size, color=color, enable=enable)
        for index, text in enumerate(texts)
    ]


def build_filter_graph() -> str:
    script_lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "npm ci",
        "npm run build",
    ]
    gutter_lines = [f"·   {line:<34}" for line in script_lines]
    origin_tui = [
        "$ codex \"create build.sh\"",
        "",
        "codex",
        "  created build.sh",
        "",
        *gutter_lines,
    ]
    manual_copy = [
        *gutter_lines,
    ]
    clean_paste = [
        *script_lines,
    ]

    filters: list[str] = [
        drawbox(0, 0, WIDTH, HEIGHT, "0D1117"),
        drawtext("TUI output to clipboard", 56, 34, size=25, color="F0F6FC", font=FONT_SANS),
        drawtext("manual selection keeps gutters, direct paste keeps only the artifact", 58, 67, size=15, color="8B949E", font=FONT_SANS),
        drawtext("1 Select", 58, 104, size=13, color="F6C177", font=FONT_SANS, enable="between(t,0,3.2)"),
        drawtext("2 Manual copy", 151, 104, size=13, color="F2A08D", font=FONT_SANS, enable="between(t,2.6,6.4)"),
        drawtext("3 Direct paste", 288, 104, size=13, color="9BE7D8", font=FONT_SANS, enable="gte(t,6.2)"),
        drawbox(56, 126, 988, 222, "0B0F14"),
        drawbox(56, 126, 988, 222, "30363D", thickness=1),
        drawtext("Original Codex-style output", 76, 145, size=14, color="C9D1D9", font=FONT_SANS),
        *lines(
            origin_tui,
            78,
            170,
            size=14,
            color="C9D1D9",
        ),
        drawbox(70, 262, 520, 84, "B45309@0.30", enable="between(t,0.7,3.6)"),
        drawbox(70, 262, 520, 84, "F59E0B", thickness=2, enable="between(t,0.7,3.6)"),
        drawtext("selected text includes gutter dots and padding", 626, 286, size=15, color="F6C177", font=FONT_SANS, enable="between(t,0.7,3.6)"),
        drawbox(108, 361, 382, 4, "F59E0B", enable="between(t,2.8,5.4)"),
        drawbox(490, 354, 9, 18, "F59E0B", enable="between(t,2.8,5.4)"),
        drawtext("Ctrl+C, Ctrl+V", 215, 374, size=13, color="F6C177", font=FONT_SANS, enable="between(t,2.8,5.4)"),
        drawbox(618, 361, 326, 4, "38D9A9", enable="between(t,6.0,8.2)"),
        drawbox(944, 354, 9, 18, "38D9A9", enable="between(t,6.0,8.2)"),
        drawtext("paste exact artifact", 718, 374, size=13, color="9BE7D8", font=FONT_SANS, enable="between(t,6.0,8.2)"),
        drawbox(56, 406, 486, 154, "141922"),
        drawbox(56, 406, 486, 154, "6B2F37", thickness=1),
        drawbox(56, 406, 486, 30, "2A181D"),
        drawtext("manual paste result", 76, 414, size=14, color="F2A08D", font=FONT_SANS),
        drawtext("waiting for selected text...", 78, 462, size=12, color="6E7681", enable="between(t,0,3.9)"),
        *lines(
            manual_copy,
            78,
            456,
            size=12,
            color="F2A08D",
            enable="gte(t,4.0)",
        ),
        drawtext("polluted: gutter dots + padding", 76, 570, size=13, color="F2A08D", font=FONT_SANS, enable="gte(t,4.0)"),
        drawbox(558, 406, 486, 154, "101B1F"),
        drawbox(558, 406, 486, 154, "2D7F8C", thickness=1),
        drawbox(558, 406, 486, 30, "12343B"),
        drawtext("direct paste result", 578, 414, size=14, color="9BE7D8", font=FONT_SANS),
        drawtext("waiting for direct paste...", 580, 462, size=12, color="6E7681", enable="between(t,0,7.1)"),
        *lines(
            clean_paste,
            582,
            456,
            size=13,
            color="9BE7D8",
            enable="gte(t,7.2)",
        ),
        drawtext("clean: runnable script only", 578, 570, size=13, color="9BE7D8", font=FONT_SANS, enable="gte(t,7.2)"),
    ]

    return ",".join(filters) + ",split[s0][s1];[s0]palettegen=max_colors=96[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3"


def build_ffmpeg_command(output: Path) -> list[str]:
    return [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"color=c=0B1020:s={WIDTH}x{HEIGHT}:r={FPS}:d={DURATION}",
        "-filter_complex",
        build_filter_graph(),
        "-loop",
        "0",
        str(output),
    ]


def render(output: Path = DEFAULT_OUTPUT) -> None:
    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg is required to render the demo GIF")

    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(build_ffmpeg_command(output), check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the Clipboard Output Skill demo GIF.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help=f"Output GIF path. Default: {DEFAULT_OUTPUT}")
    args = parser.parse_args()

    render(args.output)
    print(f"rendered {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
