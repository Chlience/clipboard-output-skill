<h1 align="center">Clipboard Output Skill</h1>

<p align="center">
  <strong>把 agent 生成的精确文本直接复制到剪贴板，不再和终端 UI 选区较劲。</strong>
</p>

<p align="center">
  <a href="./README.md">English</a> ·
  <a href="#快速开始">快速开始</a> ·
  <a href="#使用方式">使用方式</a> ·
  <a href="#验证">验证</a> ·
  <a href="#文档">文档</a>
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

## 项目是什么？

Clipboard Output Skill 是一个面向 Codex 的个人 skill，用来处理那些必须原样粘贴到别处的生成文本。典型场景包括脚本、提示词、JSON、Markdown、Shell 命令、issue 正文、release note 和其他多行生成物；这些内容如果从终端 UI 手动选中，容易带上左侧空格、边框、项目符号，或者漏复制一段。

这个 skill 不是通用剪贴板管理器，也不会保存剪贴板历史。它给 agent 一条清晰规则：当精确复制很重要时，先判断或生成正确的内容，再把最终生成物直接放进系统剪贴板。

## 适合谁使用？

- 经常把 agent 生成的命令、脚本、配置或提示词粘贴到其他工具的人。
- 遇到 TUI 复制时带上左侧空格、边框、项目符号等格式污染的人。
- 需要生成多个文件，但只想复制一个入口文件、路径或运行命令的人。
- 希望复制前对疑似 secrets 做安全拦截的人。

## 功能

- 将精确生成物复制到系统剪贴板。
- 对单文件和多文件任务提供明确的复制规则。
- 默认拒绝复制疑似敏感内容，包括 API key、token、密码、cookie 和私钥。
- 支持 dry-run，用于检测输入和剪贴板后端，但不修改剪贴板。
- 在有可用剪贴板后端时，支持 WSL、Windows、macOS、Linux 桌面会话和 Termux。

## 技术栈

| 层 | 选择 |
| --- | --- |
| Skill 格式 | Codex personal skill (`SKILL.md`) |
| Helper 运行时 | Python 3.12+ 标准库 |
| 剪贴板后端 | PowerShell、`clip.exe`、`pbcopy`、`wl-copy`、`xclip`、`xsel`、Termux、Win32 API |
| 测试 | Python `unittest` |
| Demo | Python renderer + `ffmpeg` |
| CI | GitHub Actions |

## 快速开始

### 1. 让 agent 安装

如果你的 coding agent 支持从 GitHub URL 安装 skill，直接把这个仓库地址发给它：

```text
https://github.com/Chlience/clipboard-output-skill
```

示例提示：

```text
请从 https://github.com/Chlience/clipboard-output-skill 安装这个 Codex skill
```

### 2. 或者手动安装

```bash
git clone https://github.com/Chlience/clipboard-output-skill.git
cd clipboard-output-skill

mkdir -p ~/.agents/skills
cp -R skills/clipboard-output ~/.agents/skills/clipboard-output
```

重启或重载 Codex，让它重新发现新的 skill metadata。

### 3. 验证 helper

```bash
python3 ~/.agents/skills/clipboard-output/scripts/copy_text.py \
  --file ~/.agents/skills/clipboard-output/SKILL.md \
  --dry-run
```

dry-run 成功说明 helper 可以读取输入并检测剪贴板后端，而且不会修改当前剪贴板。

## 使用方式

安装后，可以直接用自然语言让 agent 输出到剪贴板：

```text
生成这个 PowerShell 脚本，并放到我的剪贴板。
```

```text
写一份 release notes，并复制最终 Markdown。
```

```text
创建这些配置文件，然后复制我应该先打开的路径。
```

也可以直接调用 helper。

复制文件内容：

```bash
python3 ~/.agents/skills/clipboard-output/scripts/copy_text.py --file ./script.bat
```

复制短文本：

```bash
python3 ~/.agents/skills/clipboard-output/scripts/copy_text.py --text "hello"
```

复制标准输入：

```bash
printf '%s\n' "hello" | python3 ~/.agents/skills/clipboard-output/scripts/copy_text.py --stdin
```

只有在明确决定需要复制疑似敏感内容时，才使用：

```bash
python3 ~/.agents/skills/clipboard-output/scripts/copy_text.py --file ./.env --allow-sensitive
```

## 输出模型

| 场景 | 剪贴板内容 |
| --- | --- |
| 单个生成物 | 生成物本身 |
| 多个生成文件 | 最有用的入口文件、路径、命令、压缩包路径或简短 manifest |
| 疑似敏感内容 | 默认拒绝，除非显式允许 |
| 剪贴板后端不可用 | 保留生成文件，并由 agent 报告 fallback |

只有用户明确要求“合并成一个可粘贴块”时，skill 才会把多个文件合并到同一个剪贴板 payload。

## 配置说明

项目没有全局配置文件。运行行为由命令参数控制：

| 参数 | 用途 |
| --- | --- |
| `--file` | 从文件复制内容 |
| `--text` | 复制短文本 |
| `--stdin` | 复制标准输入 |
| `--dry-run` | 检测输入和剪贴板后端，但不复制 |
| `--allow-sensitive` | 覆盖疑似 secret 的启发式拦截 |

## 数据、存储和输出

helper 不保存剪贴板历史。它只读取选定输入，完成检查，然后通过第一个可用后端写入系统剪贴板。

对于需要长期保留的生成物，agent 应先创建真实文件，再只复制最终有用的内容。一次性复制内容可以先写到 `/tmp` 下的临时文件，再执行复制。

## 安全

剪贴板是系统共享状态，默认不适合放 secrets。

helper 会拒绝疑似敏感内容，除非传入 `--allow-sensitive`。这个检测是启发式的，仍然应避免把凭证、私钥、生产日志、客户数据和其他机密材料放进剪贴板。

## 验证

在仓库根目录运行：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s skills/clipboard-output/tests \
  -p 'test_*.py'

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s tests \
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
- [Skill 单元测试](skills/clipboard-output/tests/test_copy_text.py)
- [Demo 生成器](demo/README.md)
