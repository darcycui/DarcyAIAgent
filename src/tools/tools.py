# ============================================================
# Tools 实现 — 4 个工具函数
# 这里主要实现四个工具函数: shell_exec, file_read, file_write, python_exec
# ============================================================
import os
import subprocess
import sys
import tempfile


def shell_exec(command: str) -> str:
    """执行 shell 命令并返回 stdout + stderr。"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout
        if result.stderr:
            output += "\n[stderr]\n" + result.stderr
        if result.returncode != 0:
            output += f"\n[exit code: {result.returncode}]"
        return output.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return "[error] command timed out after 30s"
    except Exception as e:
        return f"[error] {e}"


def file_read(path: str) -> str:
    """读取文件内容。"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"[error] {e}"


def file_write(path: str, content: str) -> str:
    """将内容写入文件（自动创建父目录）。"""
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"OK — wrote {len(content)} chars to {path}"
    except Exception as e:
        return f"[error] {e}"


def python_exec(code: str) -> str:
    """在子进程中执行 Python 代码并返回输出。"""
    try:
        with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout
        if result.stderr:
            output += "\n[stderr]\n" + result.stderr
        return output.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return "[error] execution timed out after 30s"
    except Exception as e:
        return f"[error] {e}"
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
