"""Read the connector manifest and build the Cursor stdio config."""

from __future__ import annotations

from pathlib import Path

import yaml


def load_servers(root: Path) -> list[dict]:
    path = root / "config" / "mcpctl-manifest.yaml"
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    servers = loaded.get("servers") if isinstance(loaded, dict) else None
    if not isinstance(servers, list):
        raise ValueError(f"{path}: servers must be a list")
    return servers


def venv_python(root: Path) -> Path:
    return root / ".venv" / "bin" / "python"


def cursor_config(root: Path, python: Path) -> dict:
    servers: dict[str, dict] = {}
    for server in load_servers(root):
        script = (root / server["directory"] / server["entry"]).resolve()
        servers[server["id"]] = {
            "type": "stdio",
            "command": str(python),
            "args": [str(script)],
            "env": {
                "PYTHONPATH": str((root / "mcp-servers").resolve()),
                "MCP_TRANSPORT": "stdio",
            },
        }
    return {"mcpServers": servers}


def missing_required(server: dict, env: dict[str, str]) -> list[str]:
    missing = []
    for key in server.get("required_env") or []:
        if not str(env.get(key, "")).strip():
            missing.append(key)
    return missing


def missing_optional(server: dict, env: dict[str, str]) -> list[str]:
    missing = []
    for key in server.get("optional_env") or []:
        if not str(env.get(key, "")).strip():
            missing.append(key)
    return missing
