"""Confluence page reads. Publishing is not a tool on this server."""

from __future__ import annotations

import base64
import os
import re
from typing import Any

from common.http_api import Api

_api: Api | None = None
_PAGE_ID = re.compile(r"/pages/(\d+)")


def configure(api: Api | None = None) -> Api:
    global _api
    if api is not None:
        _api = api
    if _api is None:
        email = os.environ.get("CONFLUENCE_EMAIL", "")
        token = os.environ.get("CONFLUENCE_API_TOKEN", "")
        raw = base64.b64encode(f"{email}:{token}".encode()).decode()
        _api = Api({"Authorization": f"Basic {raw}", "Accept": "application/json"})
    return _api


def page_id_from(value: str) -> str:
    match = _PAGE_ID.search(value)
    if match:
        return match.group(1)
    return value.strip()


def get_page(page_id: str) -> dict[str, Any]:
    """Read one Confluence page by id or page URL."""
    base = os.environ.get("CONFLUENCE_BASE_URL", "").rstrip("/")
    if not base:
        return {"ok": False, "error": "CONFLUENCE_BASE_URL is not set"}
    ident = page_id_from(page_id)
    status, body = configure().json(
        "GET",
        f"{base}/wiki/api/v2/pages/{ident}",
        params={"body-format": "storage"},
    )
    if status >= 400 or status == 0 or not isinstance(body, dict):
        detail = body.get("error") if isinstance(body, dict) else "request failed"
        return {"ok": False, "status": status, "error": detail}
    storage = ((body.get("body") or {}).get("storage") or {}).get("value") or ""
    return {
        "ok": True,
        "id": body.get("id"),
        "title": body.get("title"),
        "space_id": body.get("spaceId"),
        "body": storage,
    }
