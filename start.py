"""校园二手交易与智能议价助手 - 一键启动脚本。

用法（在项目根目录执行）：
    python start.py                # 同时启动后端(8000)和前端(5173)
    python start.py --backend      # 只启动后端
    python start.py --frontend     # 只启动前端
    python start.py --seed         # 启动前先在后端执行种子数据脚本

环境要求：
    - Python 3.12（>=3.12, <3.14），后端依赖由 uv 管理（脚本会自动 uv sync）
    - Node.js >= 24.18，前端依赖用 npm 管理（首次会自动 npm install）
    - 本机 MySQL 已建库 campus_market（root/123456，可在 backend/config.yaml 修改）

按 Ctrl+C 可同时停止前后端两个服务。
"""
from __future__ import annotations

import argparse
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"

BACKEND_PORT = 8000
FRONTEND_PORT = 5173

# 子进程列表，便于统一收尾
_processes: list[subprocess.Popen] = []


def log(msg: str) -> None:
    print(f"[start] {msg}", flush=True)


def _npm_cmd() -> str:
    # Windows 下 npm 是 .cmd 脚本，shell=True 时才能解析
    return "npm"


def check_prerequisites() -> None:
    if sys.version_info < (3, 12) or sys.version_info >= (3, 14):
        log(f"警告：当前 Python {sys.version.split()[0]}，项目要求 3.12（>=3.12, <3.14）")
    if not BACKEND_DIR.exists():
        log("错误：未找到 backend 目录，请先克隆后端脚手架。")
        sys.exit(1)
    if not FRONTEND_DIR.exists():
        log("错误：未找到 frontend 目录，请先克隆前端脚手架。")
        sys.exit(1)


def ensure_backend_deps() -> None:
    if shutil.which("uv"):
        log("使用 uv sync 安装/校验后端依赖...")
        subprocess.run(["uv", "sync"], cwd=BACKEND_DIR, check=False)
    else:
        log("未检测到 uv，跳过 uv sync（假定 backend/.venv 依赖已就绪）。")


def ensure_frontend_deps() -> None:
    if (FRONTEND_DIR / "node_modules").exists():
        return
    log("首次运行，安装前端依赖 npm install（可能较慢）...")
    subprocess.run(f"{_npm_cmd()} install", cwd=FRONTEND_DIR, shell=True, check=False)


def run_seed() -> None:
    log("执行种子数据脚本 scripts/seed.py ...")
    if shutil.which("uv"):
        subprocess.run(["uv", "run", "python", "scripts/seed.py"], cwd=BACKEND_DIR, check=False)
    else:
        subprocess.run([sys.executable, "scripts/seed.py"], cwd=BACKEND_DIR, check=False)


def start_backend() -> subprocess.Popen:
    log(f"启动后端 http://127.0.0.1:{BACKEND_PORT} ...")
    if shutil.which("uv"):
        cmd = ["uv", "run", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(BACKEND_PORT)]
        use_shell = False
    else:
        python = BACKEND_DIR / ".venv" / "Scripts" / "python.exe"
        exe = str(python) if python.exists() else sys.executable
        cmd = [exe, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(BACKEND_PORT)]
        use_shell = False
    proc = subprocess.Popen(cmd, cwd=BACKEND_DIR, shell=use_shell)
    _processes.append(proc)
    return proc


def start_frontend() -> subprocess.Popen:
    log(f"启动前端 http://localhost:{FRONTEND_PORT} ...")
    # npm 需 shell=True（Windows）
    proc = subprocess.Popen(f"{_npm_cmd()} run dev", cwd=FRONTEND_DIR, shell=True)
    _processes.append(proc)
    return proc


def stop_all() -> None:
    log("正在停止前后端服务...")
    for proc in _processes:
        try:
            proc.terminate()
        except Exception:  # noqa: BLE001
            pass
    # 给一点时间优雅退出，再强杀残留
    time.sleep(1.5)
    for proc in _processes:
        try:
            if proc.poll() is None:
                proc.kill()
        except Exception:  # noqa: BLE001
            pass


def main() -> None:
    parser = argparse.ArgumentParser(description="一键启动校园二手交易项目")
    parser.add_argument("--backend", action="store_true", help="只启动后端")
    parser.add_argument("--frontend", action="store_true", help="只启动前端")
    parser.add_argument("--seed", action="store_true", help="启动前先执行种子数据脚本")
    args = parser.parse_args()

    # 默认两者都启动
    start_b = args.backend or not (args.backend or args.frontend)
    start_f = args.frontend or not (args.backend or args.frontend)

    check_prerequisites()

    if args.seed:
        run_seed()

    if start_b:
        ensure_backend_deps()
        start_backend()
    if start_f:
        ensure_frontend_deps()
        start_frontend()

    log("服务已启动。后端 http://127.0.0.1:8000/api/docs ，前台 http://localhost:5173 ，后台 http://localhost:5173/admin")
    log("按 Ctrl+C 停止全部服务。")

    def _handle_signal(signum, frame):  # noqa: ARG001
        stop_all()
        sys.exit(0)

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    # 主线程等待任一子进程退出
    try:
        while True:
            for proc in _processes:
                ret = proc.poll()
                if ret is not None:
                    log(f"检测到子进程退出（code={ret}），正在关闭其余服务...")
                    stop_all()
                    sys.exit(ret)
            time.sleep(1)
    except KeyboardInterrupt:
        stop_all()


if __name__ == "__main__":
    main()
