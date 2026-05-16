# Doc Generator Skill

A Claude Code skill that scans code directories and calls any OpenAI Chat Completions-compatible API to automatically generate structured project documentation (`GENERATED_DOC.md`).

## Features

- **Zero dependencies** — Python 3.10+ standard library only
- **Universal API** — Supports any OpenAI-compatible API (MiMo, GPT, Claude, DeepSeek, Ollama, etc.)
- **20+ languages** — Recognizes Python, JavaScript, TypeScript, Java, C/C++, Go, Rust, and more
- **Smart filtering** — Automatically skips binary files, build artifacts, and large files
- **Output** — Project overview + file function table + quick start guide

## Quick Start

### 1. Set API credentials

```bash
# Required
export API_KEY="your_api_key"

# Optional (defaults shown below)
export API_BASE_URL="https://api.xiaomimimo.com/v1"
export MODEL_NAME="mimo-v2.5-pro"
```

### 2. Run

```bash
python scripts/doc_generator.py --path /path/to/your/project
```

### 3. Result

A `GENERATED_DOC.md` is created in the current directory with three sections:

- **Project Overview** — One-line summary of the project's purpose
- **File List & Function Table** — File name | Description | Main functions/classes
- **Quick Start** — Commands or steps to run/use the project

## Installation

**Plugin Marketplace (recommended)**

In Claude Code, run:

```
/plugin marketplace add wkrabbit/doc-generator-skill
/plugin install doc-generator@wkrabbit-doc-generator-skill
```

**Manual Installation**

```bash
# Global installation (available in all projects)
git clone https://github.com/wkrabbit/doc-generator-skill.git ~/.claude/skills/doc-generator

# Project-level installation (current project only)
git clone https://github.com/wkrabbit/doc-generator-skill.git .claude/skills/doc-generator
```

## Reconfiguring API

In Claude Code, simply say **"reconfigure API"** (or **"重新配置API"**) to trigger the reconfiguration flow. The skill will guide you through selecting an API provider, entering your API key, and choosing a model name.

## Command-Line Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--path` | Yes | — | Directory to scan |
| `--output` | No | `./GENERATED_DOC.md` | Output file path |
| `--exclude` | No | — | Additional directories to exclude, comma-separated (e.g., `tests,docs`) |

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_KEY` | **Yes** | — | API key |
| `API_BASE_URL` | No | `https://api.xiaomimimo.com/v1` | API base URL |
| `MODEL_NAME` | No | `mimo-v2.5-pro` | Model name |

## Supported Languages

Python (`.py`, `.pyi`), JavaScript (`.js`, `.mjs`), TypeScript (`.ts`, `.tsx`), Java (`.java`), C/C++ (`.c`, `.cpp`, `.cc`, `.cxx`, `.h`, `.hpp`), Go (`.go`), Rust (`.rs`), Shell (`.sh`, `.bash`), Ruby (`.rb`), PHP (`.php`), Swift (`.swift`), Kotlin (`.kt`)

## How It Works

1. **Scan** — Walk the directory tree, filtering out build artifacts, binary files, and files over 1 MB
2. **Select** — Sort by file size ascending, take the first 10 code files
3. **Build** — Concatenate file contents into a structured prompt (auto-truncate when exceeding 12,000 characters)
4. **Call** — Send a POST request to an OpenAI-compatible Chat Completions endpoint
5. **Save** — Write the AI-generated Markdown to disk

## Error Handling

- `API_KEY` not set → prints a clear error message, exit code 1
- No code files found → prints an informational message, exit code 0
- API call failure → logged to `doc_gen_error.log` (timestamped, append mode)
- Program exceptions → logged and output to stderr

## API Compatibility

Tested API providers:

- Xiaomi MiMo API
- OpenAI API
- DeepSeek API
- Ollama (local deployment, OpenAI-compatible mode required)

Any API that follows the OpenAI Chat Completions format is supported.

## Requirements

- Python 3.10 or higher
- No third-party packages required (Python standard library only)

## License

MIT
