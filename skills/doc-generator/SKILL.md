---
name: doc-generator
description: >-
  Generate structured project documentation by scanning code and calling AI. Use when users ask to "generate docs", "create documentation", "document this project", "generate project doc", "写文档", "生成文档", "生成项目文档", "帮我写项目文档", "分析代码生成文档", or ask "这个项目是干什么的", "介绍一下这个项目", "帮我分析这个代码库", "what does this project do", "explain this codebase". Also use when users want an AI-generated README or project overview of a code directory.
  
  Also trigger for API configuration: "重新配置API", "reconfigure API", "修改API配置", "更改API配置", "切换模型", "switch model", "change API key", "重置API配置", "reset API config", "配置API", "configure API", "设置API", "setup API".
---

# Documentation Generator

Automatically scan a code directory and generate `GENERATED_DOC.md` using any OpenAI-compatible API.

## When to Use

**Trigger immediately** when the user's request matches any of these patterns:
- 生成文档 / 写文档 / 项目文档
- 介绍/分析这个项目 / 代码库
- "what does this project do" / "document this"
- 想要一份项目概览

If unsure whether to use this skill, use it. False positives are harmless.

## Instructions

### Step 1: Check API configuration

First, determine if the user is asking to **reconfigure** their API. Reconfigure triggers include: "重新配置", "reconfigure", "修改配置", "更改配置", "切换模型", "switch model", "change API", "重置配置", "reset config", "配置API", "configure API", "设置API", "setup API".

Run this to check if `API_KEY` is already set:

```bash
echo "${API_KEY:-NOT_SET}"
```

**If user is asking to reconfigure:** Go to Step 2 regardless of current API_KEY state. Tell the user: "好的，我来帮你重新配置 API。"

**If API_KEY is set AND user is NOT asking to reconfigure:** Go directly to Step 3.

**If API_KEY is NOT set AND user is NOT asking to reconfigure:** Go to Step 2 for setup.

### Step 2: Interactive API setup

Help the user configure their API. Ask these questions **one by one**, not all at once:

**Question 1 — Which API provider?**

Present these options:

| # | Provider | API_BASE_URL | Example models |
|---|----------|-------------|----------------|
| 1 | 小米 MiMo | `https://api.xiaomimimo.com/v1` | mimo-v2.5-pro |
| 2 | OpenAI | `https://api.openai.com/v1` | (用户输入) |
| 3 | DeepSeek | `https://api.deepseek.com/v1` | deepseek-v4-flash, deepseek-v4-pro |
| 4 | Ollama (本地) | `http://localhost:11434/v1` | (用户输入) |
| 5 | 其他（自定义） | (用户输入) | (用户输入) |

Let the user choose by number.

**Question 2 — API Key?**

Ask for their API key. If they chose Ollama, tell them any non-empty value works (e.g., `ollama`).

**Question 3 — Model name?**

If the chosen provider has example models listed, show them and let the user pick or press Enter for the first one as default.

If the chosen provider has `(用户输入)` in the model column, ask the user to enter the model name directly (no default).

**Then set the environment variables:**

For each confirmed value, run:

```bash
export API_BASE_URL="<value>"
export API_KEY="<value>"
export MODEL_NAME="<value>"
```

Tell the user: "配置完成。以后使用时如果切换了终端，需要重新设置，或者把以下内容加到 `~/.bashrc` / `~/.zshrc` 中："

```bash
export API_BASE_URL="<value>"
export API_KEY="<value>"
export MODEL_NAME="<value>"
```

### Step 3: Determine scan path

- User specified a directory → use it
- User didn't specify → default to `--path .`
- Suggest `--exclude tests,docs,node_modules` for better results

### Step 4: Run the generator

```bash
python <skill-root>/scripts/doc_generator.py --path <target> --exclude tests,docs,node_modules
```

### Step 5: Report result

After generation, tell the user:
- Number of files scanned
- Where `GENERATED_DOC.md` was saved
- Brief content summary

**Edge cases:**
- No code files found → suggest checking the path or file types
- API error → tell user to check `doc_gen_error.log` and verify their API key

## Supported Languages

Python, JavaScript, TypeScript, Java, C/C++, Go, Rust, Shell, Ruby, PHP, Swift, Kotlin, and more.
