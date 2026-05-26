<h1 align="center">Clipboard Output Skill</h1>

<p align="center">
  <strong>一个 Codex skill：把需要精确粘贴的生成内容直接放进剪贴板，避免从 TUI 复制时带上左侧空格。</strong>
</p>

<p align="center">
  <a href="./README.md">English</a> · <a href="#快速开始">快速开始</a> · <a href="#使用方式">使用方式</a> · <a href="#验证">验证</a>
</p>

<p align="center">
  <img alt="Codex Skill" src="https://img.shields.io/badge/Codex-skill-111827" />
  <img alt="Python" src="https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white" />
  <img alt="unittest" src="https://img.shields.io/badge/unittest-tested-2E7D32" />
  <img alt="License" src="https://img.shields.io/badge/License-MIT-blue" />
</p>

---

## 项目是什么？

Clipboard Output Skill 是一个面向 Codex 的个人 skill，用来处理“生成后需要粘贴到别处”的精确文本。典型场景包括脚本、配置片段、提示词、JSON、Markdown、命令、issue 正文、release note 和其他多行文本。

它的边界很明确：skill 负责判断什么内容适合放进剪贴板，附带的 Python helper 负责执行跨平台复制。它不是通用剪贴板管理器，也不会保存剪贴板历史。

## 功能

- 将精确生成物复制到系统剪贴板，减少终端 UI 选择文本时的格式污染。
- 多文件输出会先生成真实文件，再只复制最有用的入口文件、路径、命令或 manifest。
- 默认拒绝复制疑似敏感内容，包括 API key、token、密码和私钥。
- 支持 dry-run，用于检测剪贴板后端但不修改剪贴板。
- 提供单元测试，覆盖输入来源、敏感内容检测和 Windows 原生剪贴板 API 设置。

## 技术栈

| 层 | 选择 |
| --- | --- |
| Skill 格式 | Codex personal skill (`SKILL.md`) |
| Helper 运行时 | Python 3.12+ 标准库 |
| 剪贴板后端 | WSL/PowerShell、`clip.exe`、`pbcopy`、`wl-copy`、`xclip`、`xsel`、Termux、Windows 原生 API |
| 测试 | Python `unittest` |
| CI | GitHub Actions |

## 快速开始

安装为 Codex 个人 skill：

```bash
mkdir -p ~/.agents/skills
cp -R skills/clipboard-output ~/.agents/skills/clipboard-output
```

重启或重载 Codex，让新的 skill metadata 生效。

检查 helper 是否能读取 skill 文件并检测剪贴板后端：

```bash
python3 ~/.agents/skills/clipboard-output/scripts/copy_text.py \
  --file ~/.agents/skills/clipboard-output/SKILL.md \
  --dry-run
```

## 使用方式

从文件复制：

```bash
python3 ~/.agents/skills/clipboard-output/scripts/copy_text.py --file ./script.bat
```

复制短文本：

```bash
python3 ~/.agents/skills/clipboard-output/scripts/copy_text.py --text "hello"
```

从标准输入复制：

```bash
printf '%s\n' "hello" | python3 ~/.agents/skills/clipboard-output/scripts/copy_text.py --stdin
```

只有在明确决定需要复制敏感内容时，才使用：

```bash
python3 ~/.agents/skills/clipboard-output/scripts/copy_text.py --file ./.env --allow-sensitive
```

## 剪贴板后端

helper 会根据当前平台选择可用后端：

| 环境 | 后端 |
| --- | --- |
| WSL | PowerShell `Set-Clipboard`，失败后回退到 `clip.exe` |
| macOS | `pbcopy` |
| Linux Wayland | `wl-copy` |
| Linux X11 | `xclip` 或 `xsel` |
| Termux | `termux-clipboard-set` |
| Windows 原生 Python | 通过 `ctypes` 调用 Win32 剪贴板 API |

在受限沙箱、远程 SSH、无图形界面的 Linux、或没有 Windows interop 的 WSL 中，剪贴板访问可能失败。

## 输出规则

单个生成物会复制生成物本身。多个文件会先写入真实文件，再复制一个最有用的内容：入口文件、目录路径、压缩包路径、运行命令或简短 manifest。

只有用户明确要求“合并成一段可粘贴文本”时，skill 才会把多个文件合并到同一个剪贴板 payload。

## 安全

剪贴板是系统共享状态，默认不适合放 secrets。

helper 会拒绝疑似敏感内容，除非传入 `--allow-sensitive`。这个检测是启发式的，仍然应避免把 secret、私钥、生产日志、客户数据和其他机密材料放进剪贴板。

## 验证

在仓库根目录运行：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s skills/clipboard-output/tests \
  -p 'test_*.py'
```

解析 helper 脚本，并避免写入 `__pycache__`：

```bash
python3 -B -c "import ast, pathlib; ast.parse(pathlib.Path('skills/clipboard-output/scripts/copy_text.py').read_text())"
```

不修改剪贴板的 smoke check：

```bash
python3 skills/clipboard-output/scripts/copy_text.py \
  --file skills/clipboard-output/SKILL.md \
  --dry-run
```

## 文档

- [Skill 指令](skills/clipboard-output/SKILL.md)
- [剪贴板 helper](skills/clipboard-output/scripts/copy_text.py)
- [单元测试](skills/clipboard-output/tests/test_copy_text.py)
