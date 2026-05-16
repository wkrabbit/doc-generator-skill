# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Claude Code skill (`doc-generator`) that scans a local code directory and calls any OpenAI Chat Completions-compatible API to generate a structured project documentation file (`GENERATED_DOC.md`). Published as a Claude Code plugin for marketplace installation.

## Repository Structure

```
.
├── .claude-plugin/plugin.json   # Plugin metadata for marketplace
├── skills/doc-generator/SKILL.md # Skill definition (YAML frontmatter + instructions)
├── scripts/doc_generator.py     # Core implementation (single-file, stdlib only)
├── docs/                        # Design specs and plans
└── README.md                    # User-facing install and usage guide
```

## Commands

```bash
# Set required environment variables (API_KEY is mandatory)
export API_KEY="your_key"
export API_BASE_URL="https://api.xiaomimimo.com/v1"  # default
export MODEL_NAME="mimo-v2.5-pro"                     # default

# Generate docs for current directory
python scripts/doc_generator.py --path .

# Generate docs with custom output and exclusions
python scripts/doc_generator.py --path /path/to/project --output ./docs/API.md --exclude tests,docs
```

## Architecture

Single-file design: `scripts/doc_generator.py` — no modules or packages.

```
main()
├── parse_args()           # --path, --output, --exclude
├── scan_files(path, ...)  # 7-step filtering (dirs → extension → size → binary → sort → cap → read)
├── build_prompt(snippets) # Embedded Chinese template, 12000-char auto-downgrade
├── call_api(prompt)       # urllib POST, 30s timeout, safe error logging
└── save_result(text, out) # mkdir + overwrite
```

## Technical Constraints

- **Python 3.10+**, standard library only (`os`, `sys`, `pathlib`, `argparse`, `json`, `urllib.request`, `time`)
- No third-party dependencies (no `requests`, no `openai` SDK)
- HTTP timeout: 30 seconds
- API errors (non-200 status, `error` field in response) are logged to `doc_gen_error.log` (append mode, timestamps)
- If `API_KEY` is unset, print a clear error and exit with code 1
- `API_BASE_URL` and `MODEL_NAME` fall back to defaults when unset
- Cross-platform compatible (Windows/Linux/macOS)
- No `.gitignore` parsing — uses built-in directory/extension/size rules only

## Skill Development

This is a Claude Code plugin skill. Key files to maintain:

- `skills/doc-generator/SKILL.md` — instructions Claude Code reads when the skill is invoked. Update the YAML frontmatter `description` when behavior changes.
- `.claude-plugin/plugin.json` — bump `version` on each release.
- `README.md` — keep in sync with SKILL.md and actual CLI behavior.

The `superpowers:brainstorming` skill is permitted in `.claude/settings.local.json` — use it before any creative or design work.

## Acceptance Criteria

- Setting `API_BASE_URL`, `API_KEY`, `MODEL_NAME` and running `python scripts/doc_generator.py --path .` produces a valid `GENERATED_DOC.md`
- The generated doc includes a project overview and at least one Markdown table
- Missing `API_KEY` produces a clear error message
- No hardcoded model names or API URLs beyond the documented defaults
