#!/usr/bin/env python3
"""通用代码库文档生成器 — 扫描代码目录，调用 AI 生成项目文档。"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.error
from pathlib import Path

# 内置过滤目录
SKIP_DIRS = {
    '.git', 'node_modules', '__pycache__', '.venv', 'venv', 'env',
    'dist', 'build', '.idea', '.vscode', '.coverage',
    'htmlcov', '.tox', '.mypy_cache', '.pytest_cache'
}

# 文件扩展名白名单
ALLOWED_EXTENSIONS = {
    '.py', '.pyi', '.js', '.mjs', '.ts', '.tsx', '.java',
    '.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.go', '.rs',
    '.sh', '.bash', '.rb', '.php', '.swift', '.kt'
}

# 二进制文件扩展名（不用读内容直接跳过）
BINARY_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.bmp', '.svg',
    '.mp3', '.mp4', '.avi', '.mov', '.mkv', '.wav',
    '.pdf', '.zip', '.tar', '.gz', '.bz2', '.7z', '.rar',
    '.exe', '.dll', '.so', '.dylib', '.bin',
    '.ttf', '.otf', '.woff', '.woff2', '.eot',
    '.o', '.a', '.lib', '.obj', '.class', '.pyc', '.pyo'
}

MAX_FILE_SIZE = 1_048_576       # 1MB
MAX_FILES = 10
READ_CHARS = 2000
READ_CHARS_REDUCED = 1000
PROMPT_MAX_CHARS = 12000
API_TIMEOUT = 30


def parse_args():
    parser = argparse.ArgumentParser(
        description='通用代码库文档生成器 — 扫描代码目录并生成 GENERATED_DOC.md'
    )
    parser.add_argument(
        '--path', required=True,
        help='要扫描的代码目录路径'
    )
    parser.add_argument(
        '--output', default=None,
        help='输出文件路径（默认当前工作目录下的 GENERATED_DOC.md）'
    )
    parser.add_argument(
        '--exclude', default='',
        help='额外排除的目录名，逗号分隔（如 tests,docs）'
    )
    return parser.parse_args()


def is_binary(filepath):
    """快速判断文件是否为二进制：先查扩展名，再读前512字节检测空字节。"""
    suffix = Path(filepath).suffix.lower()
    if suffix in BINARY_EXTENSIONS:
        return True
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(512)
        return b'\x00' in chunk
    except OSError:
        return True


def scan_files(root_path, extra_exclude_str=''):
    """
    扫描目录，返回 [(relative_path, content), ...]。
    按7步规则过滤：目录→扩展名白名单→大小→二进制→候选排序截取→读取内容。
    """
    root = Path(root_path).resolve()
    if not root.is_dir():
        print(f"错误: 路径不存在或不是目录: {root_path}", file=sys.stderr)
        sys.exit(1)
    extra_exclude = {d.strip() for d in extra_exclude_str.split(',') if d.strip()}
    all_skip_dirs = SKIP_DIRS | extra_exclude

    candidates = []

    for dirpath, dirnames, filenames in os.walk(root):
        # 修改 dirnames 原地过滤目录（同时过滤 *.egg-info 等 glob 模式）
        dirnames[:] = [d for d in dirnames if d not in all_skip_dirs and not d.endswith('.egg-info')]

        for fname in filenames:
            fpath = Path(dirpath) / fname
            suffix = fpath.suffix.lower()

            # 扩展名白名单
            if suffix not in ALLOWED_EXTENSIONS:
                continue

            # 文件大小检查
            try:
                fsize = fpath.stat().st_size
            except OSError:
                continue
            if fsize > MAX_FILE_SIZE:
                continue

            # 二进制检查
            if is_binary(str(fpath)):
                continue

            candidates.append((fpath, fsize))

    # 候选 > MAX_FILES 时按大小升序取前 MAX_FILES
    candidates.sort(key=lambda x: x[1])
    if len(candidates) > MAX_FILES:
        candidates = candidates[:MAX_FILES]

    # 读取文件内容（前 READ_CHARS 字符）
    snippets = []
    for fpath, _ in candidates:
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(READ_CHARS)
        except OSError:
            continue
        rel_path = os.path.relpath(fpath, root).replace('\\', '/')
        snippets.append((rel_path, content))

    return snippets


def build_prompt(snippets, read_chars=READ_CHARS):
    """构建发送给 API 的 prompt 字符串。超过 PROMPT_MAX_CHARS 时自动降级重试。"""
    sections = []
    for path, code in snippets:
        sections.append(f"=== {path} ===\n{code}\n")
    code_block = "\n".join(sections)

    prompt_template = (
        "你是一个专业的技术文档撰写助手。请根据以下多个代码片段，生成一份项目的技术文档。\n"
        "\n"
        "输出格式要求为 Markdown，必须严格按照以下三个部分输出：\n"
        "\n"
        "## 1. 项目概述\n"
        "用一句话概括该项目的目的，根据代码内容推测。\n"
        "\n"
        "## 2. 文件列表及功能表\n"
        "使用 Markdown 表格，包含三列：\n"
        "| 文件名 | 功能简述 | 主要函数/类 |\n"
        "|--------|----------|-------------|\n"
        "对于每个代码文件，填写一行。功能简述不超过20个字。主要函数/类列出最重要的2个名称（若没有则填\"无\"）。\n"
        "\n"
        "## 3. 快速开始\n"
        "提供如何运行/使用这个项目的命令或步骤。\n"
        "- 如果存在明显的入口文件（如 main.py、index.js、Main.java），说明运行命令。\n"
        "- 如果看不出主入口，给出通用建议（如\"请参考各文件内的函数定义\"）。\n"
        "\n"
        "不要输出任何额外解释、对话或注释，仅输出 Markdown 文档内容。\n"
        "\n"
        "以下是各个代码文件的内容：\n"
        "\n"
        "{code_block}"
    )

    prompt = prompt_template.format(code_block=code_block)

    # 长度自动降级
    if len(prompt) > PROMPT_MAX_CHARS and read_chars > READ_CHARS_REDUCED:
        reduced_snippets = [(p, c[:READ_CHARS_REDUCED]) for p, c in snippets]
        return build_prompt(reduced_snippets, read_chars=READ_CHARS_REDUCED)

    return prompt


def call_api(prompt):
    """调用 OpenAI 兼容 Chat Completions API，成功返回文本，失败返回 None。"""
    api_base_url = os.environ.get('API_BASE_URL', 'https://api.xiaomimimo.com/v1')
    api_key = os.environ.get('API_KEY')
    model_name = os.environ.get('MODEL_NAME', 'mimo-v2.5-pro')

    if not api_key:
        print("错误：环境变量 API_KEY 未设置。请先设置 API_KEY 后重试。", file=sys.stderr)
        sys.exit(1)

    url = f"{api_base_url.rstrip('/')}/chat/completions"
    body = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    data = json.dumps(body).encode('utf-8')

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        },
        method='POST'
    )

    try:
        with urllib.request.urlopen(req, timeout=API_TIMEOUT) as resp:
            raw = resp.read().decode('utf-8')
            result = json.loads(raw)

            # 检查响应是否包含 error 字段
            if 'error' in result:
                log_error(f"API 返回错误: {result['error']}")
                return None

            # 安全提取响应内容
            try:
                choice = result['choices'][0]
                finish_reason = choice.get('finish_reason')
                if finish_reason == 'length':
                    log_error("API 响应被截断：达到令牌长度限制")
                return choice['message']['content']
            except (KeyError, IndexError, TypeError) as e:
                log_error(f"意外的 API 响应结构: {e}")
                return None

    except urllib.error.HTTPError as e:
        body_text = ''
        try:
            body_text = e.read().decode('utf-8')[:500]
        except Exception:
            pass
        log_error(f"HTTP {e.code}: {e.reason} | body: {body_text}")
        return None
    except urllib.error.URLError as e:
        log_error(f"网络错误: {e.reason}")
        return None
    except Exception as e:
        log_error(f"未预期的错误: {e}")
        return None


def log_error(message):
    """追加错误日志到当前工作目录的 doc_gen_error.log（失败时静默忽略）。"""
    try:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        with open('doc_gen_error.log', 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass


def save_result(text, output_path):
    """保存文档到指定路径，自动创建父目录。"""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"文档已生成: {out.resolve()}")


def main():
    args = parse_args()

    # 检查 API_KEY
    api_key = os.environ.get('API_KEY')
    if not api_key:
        print("错误：环境变量 API_KEY 未设置。请先设置 API_KEY 后重试。", file=sys.stderr)
        print("示例: export API_KEY=\"your_key_here\"", file=sys.stderr)
        sys.exit(1)

    try:
        # 扫描文件
        extra_exclude = args.exclude
        snippets = scan_files(args.path, extra_exclude)

        if not snippets:
            print("未找到可处理的代码文件。请检查目录或文件扩展名。")
            sys.exit(0)

        print(f"已扫描 {len(snippets)} 个代码文件，正在生成文档...")

        # 构建 prompt
        prompt = build_prompt(snippets)
        print(f"Prompt 长度: {len(prompt)} 字符")

        # 调用 API
        result = call_api(prompt)
        if result is None:
            print("文档生成失败，请查看 doc_gen_error.log 了解详情。", file=sys.stderr)
            sys.exit(1)

        # 保存结果
        output_path = args.output or 'GENERATED_DOC.md'
        save_result(result, output_path)

    except Exception as e:
        log_error(f"程序异常: {e}")
        print(f"程序运行出错: {e}", file=sys.stderr)
        print("详情请查看 doc_gen_error.log", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
