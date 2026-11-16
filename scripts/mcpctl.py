#!/usr/bin/env python3
"""Start, stop, and check the local MCP connectors."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mcp-servers"))

from common.env import find_root, read_env
from common.manifest import load_servers, missing_optional, missing_required, venv_python


def runtime_dir(root: Path) -> Path:
    path = root / ".eit" / "mcpctl"
    path.mkdir(parents=True, exist_ok=True)
    return path


def doctor(root: Path) -> int:
    env = read_env(root)
    failed = False
    for server in load_servers(root):
        missing = missing_required(server, env)
        optional = missing_optional(server, env)
        if missing:
            failed = True
            print(f"[missing] {server['id']}: {', '.join(missing)}")
        else:
            print(f"[ok] {server['id']}")
        if optional:
            print(f"[optional] {server['id']}: {', '.join(optional)}")
    if failed:
        print("doctor found missing required environment names", file=sys.stderr)
        return 1
    return 0


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _selected(servers: list[dict], names: list[str]) -> list[dict]:
    if not names:
        return servers
    wanted = set(names)
    return [server for server in servers if server["id"] in wanted]


def start(root: Path, names: list[str]) -> int:
    python = venv_python(root)
    if not python.is_file():
        print("missing .venv/bin/python", file=sys.stderr)
        return 1
    env_values = read_env(root)
    code = 0
    run_dir = runtime_dir(root)
    for server in _selected(load_servers(root), names):
        missing = missing_required(server, env_values)
        if missing:
            print(f"[missing] {server['id']}: {', '.join(missing)}", file=sys.stderr)
            code = 1
            continue
        pid_path = run_dir / f"{server['id']}.pid"
        if pid_path.is_file():
            try:
                existing = int(pid_path.read_text().strip())
            except ValueError:
                existing = 0
            if existing and _alive(existing):
                print(f"[ok] {server['id']} already running")
                continue
        child_env = os.environ.copy()
        for key, value in env_values.items():
            if key not in child_env or not child_env[key]:
                child_env[key] = value
        child_env["MCP_TRANSPORT"] = "streamable-http"
        child_env["PYTHONPATH"] = str((root / "mcp-servers").resolve())
        script = root / server["directory"] / server["entry"]
        log_path = run_dir / f"{server['id']}.log"
        with log_path.open("a", encoding="utf-8") as log:
            proc = subprocess.Popen(
                [str(python), str(script)],
                cwd=root,
                env=child_env,
                stdout=log,
                stderr=log,
                start_new_session=True,
            )
        pid_path.write_text(f"{proc.pid}\n", encoding="utf-8")
        print(f"[ok] {server['id']} pid {proc.pid} port {server['port']}")
    return code


def stop(root: Path, names: list[str]) -> int:
    run_dir = runtime_dir(root)
    for server in _selected(load_servers(root), names):
        pid_path = run_dir / f"{server['id']}.pid"
        if not pid_path.is_file():
            print(f"[ok] {server['id']} not running")
            continue
        try:
            pid = int(pid_path.read_text().strip())
        except ValueError:
            pid_path.unlink(missing_ok=True)
            continue
        if _alive(pid):
            os.kill(pid, signal.SIGTERM)
            for _ in range(20):
                if not _alive(pid):
                    break
                time.sleep(0.1)
            if _alive(pid):
                os.kill(pid, signal.SIGKILL)
        pid_path.unlink(missing_ok=True)
        print(f"[ok] {server['id']} stopped")
    return 0


def status(root: Path) -> int:
    run_dir = root / ".eit" / "mcpctl"
    for server in load_servers(root):
        pid_path = run_dir / f"{server['id']}.pid"
        state = "stopped"
        if pid_path.is_file():
            try:
                pid = int(pid_path.read_text().strip())
            except ValueError:
                pid = 0
            if pid and _alive(pid):
                state = f"running pid {pid}"
        print(f"{server['id']}\t{server['port']}\t{state}")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in {"-h", "--help"}:
        print("usage: python scripts/mcpctl.py doctor|start|stop|status [server-id...]")
        return 0 if len(argv) > 1 else 2
    root = find_root()
    command = argv[1]
    names = argv[2:]
    if command == "doctor":
        return doctor(root)
    if command == "start":
        return start(root, names)
    if command == "stop":
        return stop(root, names)
    if command == "status":
        return status(root)
    print(f"unknown command {command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
