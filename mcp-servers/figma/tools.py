"""Read-only Figma file and frame flatten. This module is the only Figma client."""

from __future__ import annotations

import os
import re
from typing import Any

from common.http_api import Api

API = "https://api.figma.com"
_FILE_KEY = re.compile(r"figma\.com/(?:file|design)/([A-Za-z0-9]+)")
_api: Api | None = None


def configure(api: Api | None = None) -> Api:
    global _api
    if api is not None:
        _api = api
    if _api is None:
        token = os.environ.get("FIGMA_ACCESS_TOKEN", "")
        _api = Api({"X-Figma-Token": token} if token else {})
    return _api


def file_key_from(value: str) -> str:
    match = _FILE_KEY.search(value)
    if match:
        return match.group(1)
    return value.strip()


def flatten_node(node: dict[str, Any], depth: int = 0, limit: list[int] | None = None) -> dict[str, Any]:
    remaining = limit if limit is not None else [200]
    item: dict[str, Any] = {"id": node.get("id"), "name": node.get("name"), "type": node.get("type")}
    children = node.get("children") or []
    if depth >= 6 or not children or remaining[0] <= 0:
        return item
    flat_children = []
    for child in children:
        if remaining[0] <= 0:
            break
        remaining[0] -= 1
        if isinstance(child, dict):
            flat_children.append(flatten_node(child, depth + 1, remaining))
    if flat_children:
        item["children"] = flat_children
    return item


def get_file(file_key: str) -> dict[str, Any]:
    """Flatten a Figma file by key or URL."""
    if not os.environ.get("FIGMA_ACCESS_TOKEN"):
        return {"ok": False, "configured": False, "error": "FIGMA_ACCESS_TOKEN is not set"}
    key = file_key_from(file_key)
    status, body = configure().json("GET", f"{API}/v1/files/{key}")
    if status >= 400 or status == 0 or not isinstance(body, dict):
        detail = body.get("error") if isinstance(body, dict) else "request failed"
        return {"ok": False, "status": status, "error": detail}
    document = body.get("document") or {}
    return {"ok": True, "file_key": key, "name": body.get("name"), "document": flatten_node(document)}


def get_frame(file_key: str, node_id: str) -> dict[str, Any]:
    """Flatten one Figma frame or node."""
    if not os.environ.get("FIGMA_ACCESS_TOKEN"):
        return {"ok": False, "configured": False, "error": "FIGMA_ACCESS_TOKEN is not set"}
    key = file_key_from(file_key)
    status, body = configure().json("GET", f"{API}/v1/files/{key}/nodes", params={"ids": node_id})
    if status >= 400 or status == 0 or not isinstance(body, dict):
        detail = body.get("error") if isinstance(body, dict) else "request failed"
        return {"ok": False, "status": status, "error": detail}
    nodes = body.get("nodes") or {}
    entry = nodes.get(node_id) or next(iter(nodes.values()), {})
    document = (entry or {}).get("document") or {}
    return {"ok": True, "file_key": key, "node_id": node_id, "document": flatten_node(document)}
