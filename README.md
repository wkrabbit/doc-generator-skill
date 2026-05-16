# Doc Generator Skill

一个 Claude Code 技能，通过扫描代码目录并调用任意兼容 OpenAI Chat Completions 接口的大模型，自动生成结构化的项目文档 `GENERATED_DOC.md`。

## 特性

- **零依赖** — 仅使用 Python 3.10+ 标准库
- **通用接口** — 支持任意兼容 OpenAI 的 API（MiMo、GPT、Claude、DeepSeek、Ollama 等）
- **20+ 语言** — 识别 Python、JavaScript、TypeScript、Java、C/C++、Go、Rust 等
- **智能过滤** — 自动跳过二进制文件、构建产物、大型文件
- **生成内容** — 项目概述 + 文件功能表 + 快速开始指南

## 快速开始

### 1. 设置 API 凭证

```bash
# 必填
export API_KEY="your_api_key"

# 可选（以下为默认值）
export API_BASE_URL="https://api.xiaomimimo.com/v1"
export MODEL_NAME="mimo-v2.5-pro"
```

### 2. 运行

```bash
python scripts/doc_generator.py --path /path/to/your/project
```

### 3. 结果

当前目录下生成 `GENERATED_DOC.md`，包含三个部分：

- **项目概述** — 一句话概括项目目的
- **文件列表及功能表** — 文件名 | 功能简述 | 主要函数/类
- **快速开始** — 运行/使用项目的命令或步骤

## 安装方式

**Plugin Marketplace（推荐）**

在 Claude Code 中执行：

```
/plugin marketplace add wkrabbit/doc-generator-skill
/plugin install doc-generator@wkrabbit-doc-generator-skill
```

**手动安装**

```bash
# 全局安装（所有项目可用）
git clone https://github.com/wkrabbit/doc-generator-skill.git ~/.claude/skills/doc-generator

# 项目级安装（仅当前项目）
git clone https://github.com/wkrabbit/doc-generator-skill.git .claude/skills/doc-generator
```

## 重新配置 API

在 Claude Code 中直接说 **"重新配置API"** 或 **"reconfigure API"** 即可触发重新配置流程，Skill 会引导你逐步选择 API 提供商、输入密钥和模型名称。

## 命令行选项

| 选项 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `--path` | 是 | — | 要扫描的目录路径 |
| `--output` | 否 | `./GENERATED_DOC.md` | 输出文件路径 |
| `--exclude` | 否 | — | 额外排除的目录，逗号分隔（如 `tests,docs`） |

## 环境变量

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `API_KEY` | **是** | — | API 密钥 |
| `API_BASE_URL` | 否 | `https://api.xiaomimimo.com/v1` | API 基础地址 |
| `MODEL_NAME` | 否 | `mimo-v2.5-pro` | 模型名称 |

## 支持的编程语言

Python（`.py`、`.pyi`）、JavaScript（`.js`、`.mjs`）、TypeScript（`.ts`、`.tsx`）、Java（`.java`）、C/C++（`.c`、`.cpp`、`.cc`、`.cxx`、`.h`、`.hpp`）、Go（`.go`）、Rust（`.rs`）、Shell（`.sh`、`.bash`）、Ruby（`.rb`）、PHP（`.php`）、Swift（`.swift`）、Kotlin（`.kt`）

## 工作流程

1. **扫描** — 遍历目录树，过滤构建产物、二进制文件和超过 1MB 的文件
2. **选取** — 按文件大小升序排列，取前 10 个代码文件
3. **构建** — 将文件内容拼接成结构化 Prompt（总长度超过 12000 字符时自动截短）
4. **调用** — 发送 POST 请求到 OpenAI 兼容的 Chat Completions 接口
5. **保存** — 将 AI 生成的 Markdown 写入磁盘

## 错误处理

- 未设置 `API_KEY` → 打印清晰错误信息，退出码 1
- 未找到代码文件 → 打印提示信息，退出码 0
- API 调用失败 → 记录到 `doc_gen_error.log`（带时间戳，追加模式）
- 程序异常 → 记录日志并输出到 stderr

## API 兼容性

已测试的 API 提供商：

- 小米 MiMo API
- OpenAI API
- DeepSeek API
- Ollama（本地部署，需开启 OpenAI 兼容模式）

任何遵循 OpenAI Chat Completions 格式的 API 均可使用。

## 环境要求

- Python 3.10 或更高版本
- 无需安装任何第三方包（仅使用 Python 标准库）

## 许可证

MIT
