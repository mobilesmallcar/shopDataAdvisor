# 运行 可在控制台查看当前项目的文件树

import os
from pathlib import Path

"""
功能：可在控制台查看当前项目的文件树
作者: Xsy
时间: 2025-11-29
"""


def extract_first_comment_line(filepath):
    """提取 Python 文件的第一行有效注释或模块 docstring 的第一行"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception:
        return ""

    i = 0
    # 跳过开头空行
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i >= len(lines):
        return ""

    first_line = lines[i].strip()

    # 情况1: 模块 docstring（单行）
    if first_line.startswith(('"""', "'''")):
        # 提取内容（去掉首尾引号）
        content = first_line[3:-3] if len(first_line) >= 6 and first_line.endswith(first_line[0:3]) else first_line[3:]
        content = content.strip()
        return content if content else ""

    # 情况2: 单行注释
    if first_line.startswith("#"):
        return first_line[1:].strip()

    # 情况3: 多行 docstring 的第一行（如 """ 开头但未结束）
    if first_line.startswith(('"""', "'''")):
        content = first_line[3:].strip()
        return content

    return ""


def print_tree_with_header(startpath, max_depth=3, exclude=None):
    exclude = set(exclude or ['.git', '__pycache__', '.idea', '.vscode', 'venv', 'env'])

    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d not in exclude]
        level = root.replace(startpath, '').count(os.sep)
        if level > max_depth:
            continue

        indent = '│   ' * level
        print(f'{indent}├── {os.path.basename(root)}/')

        subindent = '│   ' * (level + 1)
        for file in sorted(files):
            if file.startswith('.'):
                continue

            filepath = os.path.join(root, file)
            if file.endswith('.py'):
                comment = extract_first_comment_line(filepath)
                if comment:
                    print(f'{subindent}├── {file}  # {comment}')
                else:
                    print(f'{subindent}├── {file}')
            else:
                print(f'{subindent}├── {file}')


if __name__ == "__main__":
    startpath = str(Path(__file__).parents[1])
    exclude = ['.git', '__pycache__', '.idea', '.vscode', 'venv', 'env', '.venv']
    max_depth = 5

    print("Project Structure with First-Line Comments:\n")
    print_tree_with_header(startpath, max_depth=max_depth, exclude=exclude)
