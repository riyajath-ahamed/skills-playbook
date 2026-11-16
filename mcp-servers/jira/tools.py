"""Jira Cloud reads, plus a gated bulk create. This module is the only Jira client."""

from __future__ import annotations

import base64
import os
from collections.abc import Callable
from typing import Any

from common.http_api import Api

_api: Api | None = None
_CARD_TYPES = {"inlineCard", "blockCard", "embedCard"}


def write_enabled() -> bool:
    return os.environ.get("JIRA_WRITE_ENABLED", "").strip().lower() in {"1", "true", "yes"}


def configure(api: Api | None = None) -> Api:
    global _api
    if api is not None:
        _api = api
    if _api is None:
        email = os.environ.get("JIRA_EMAIL", "")
        token = os.environ.get("JIRA_API_TOKEN", "")
        raw = base64.b64encode(f"{email}:{token}".encode()).decode()
        _api = Api({"Authorization": f"Basic {raw}", "Accept": "application/json"})
    return _api


def _base() -> str:
    return os.environ.get("JIRA_BASE_URL", "").rstrip("/")


def _adf_text(node: object) -> str:
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return " ".join(part for part in (_adf_text(item) for item in node) if part)
    if isinstance(node, dict):
        parts = []
        if isinstance(node.get("text"), str):
            parts.append(node["text"])
        card_url = _card_url(node)
        if card_url:
            parts.append(card_url)
        if node.get("content") is not None:
            parts.append(_adf_text(node["content"]))
        return " ".join(part for part in parts if part)
    return ""


def _card_url(node: dict[str, Any]) -> str:
    if node.get("type") not in _CARD_TYPES:
        return ""
    url = (node.get("attrs") or {}).get("url")
    return url if isinstance(url, str) else ""


def _mark_hrefs(node: dict[str, Any]) -> list[str]:
    hrefs = []
    for mark in node.get("marks") or []:
        if isinstance(mark, dict) and mark.get("type") == "link":
            href = (mark.get("attrs") or {}).get("href")
            if isinstance(href, str):
                hrefs.append(href)
    return hrefs


def _adf_urls(node: object) -> list[str]:
    if isinstance(node, list):
        return [url for item in node for url in _adf_urls(item)]
    if not isinstance(node, dict):
        return []
    found = [url for url in (_card_url(node), *_mark_hrefs(node)) if url]
    return found + _adf_urls(node.get("content"))


def _classify(url: str, buckets: dict[str, list[str]]) -> None:
    lowered = url.lower()
    if "lucid" in lowered:
        target = "lucid_refs"
    elif "docs.google.com" in lowered or "drive.google.com" in lowered:
        target = "google_workspace_refs"
    else:
        target = "links"
    if url not in buckets[target]:
        buckets[target].append(url)


def get_issue_details(issue_key: str) -> dict[str, Any]:
    """Read one Jira issue, including linked diagram and document URLs."""
    base = _base()
    if not base:
        return {"ok": False, "error": "JIRA_BASE_URL is not set"}
    status, body = configure().json("GET", f"{base}/rest/api/3/issue/{issue_key}")
    if status >= 400 or status == 0 or not isinstance(body, dict):
        detail = body.get("error") if isinstance(body, dict) else "request failed"
        return {"ok": False, "status": status, "error": detail}
    fields = body.get("fields") or {}
    buckets = {"links": [], "lucid_refs": [], "google_workspace_refs": []}
    description = _adf_text(fields.get("description"))
    for url in _adf_urls(fields.get("description")):
        _classify(url, buckets)
    for token in description.split():
        if token.startswith("http://") or token.startswith("https://"):
            _classify(token.strip(").,>"), buckets)
    remote_status, remote = configure().json("GET", f"{base}/rest/api/3/issue/{issue_key}/remotelink")
    if remote_status < 400 and isinstance(remote, list):
        for item in remote:
            url = ((item.get("object") or {}).get("url")) or ""
            if url:
                _classify(url, buckets)
    status_name = (fields.get("status") or {}).get("name")
    return {
        "ok": True,
        "key": body.get("key"),
        "summary": fields.get("summary"),
        "status": status_name,
        "description": description,
        **buckets,
    }


def get_issue_comments(issue_key: str) -> dict[str, Any]:
    """Read comments on one Jira issue."""
    base = _base()
    if not base:
        return {"ok": False, "error": "JIRA_BASE_URL is not set"}
    status, body = configure().json("GET", f"{base}/rest/api/3/issue/{issue_key}/comment")
    if status >= 400 or status == 0 or not isinstance(body, dict):
        detail = body.get("error") if isinstance(body, dict) else "request failed"
        return {"ok": False, "status": status, "error": detail}
    comments = []
    for item in body.get("comments") or []:
        comments.append(
            {
                "id": item.get("id"),
                "author": (item.get("author") or {}).get("displayName"),
                "body": _adf_text(item.get("body")),
            }
        )
    return {"ok": True, "comments": comments}


def _description_adf(text: str) -> dict[str, Any]:
    return {
        "type": "doc",
        "version": 1,
        "content": [{"type": "paragraph", "content": [{"type": "text", "text": text}]}],
    }


def plan_issue_batch(
    issues: list[dict[str, str]],
    *,
    confirmed: bool,
    enabled: bool,
    sender: Callable[[dict[str, Any]], tuple[int, object]],
) -> dict[str, Any]:
    if not confirmed or not enabled:
        return {
            "ok": True,
            "preview": True,
            "sent": False,
            "issues": issues,
            "reason": "Create stays a preview until confirmed is true and JIRA_WRITE_ENABLED is true.",
        }
    updates = []
    for item in issues:
        fields: dict[str, Any] = {
            "project": {"key": item.get("project", "")},
            "summary": item.get("summary", ""),
            "issuetype": {"name": item.get("issue_type", "Task")},
        }
        description = item.get("description", "").strip()
        if description:
            fields["description"] = _description_adf(description)
        updates.append({"fields": fields})
    payload = {"issueUpdates": updates}
    status, body = sender(payload)
    return {"ok": status < 400 and status != 0, "preview": False, "sent": True, "status": status, "result": body}


def create_issues_batch(issues: list[dict[str, str]], confirmed: bool = False) -> dict[str, Any]:
    """Preview a bulk create. Send it only when confirmed is true and JIRA_WRITE_ENABLED is true."""

    def sender(payload: dict[str, Any]) -> tuple[int, object]:
        base = _base()
        if not base:
            return 0, {"error": "JIRA_BASE_URL is not set"}
        return configure().json("POST", f"{base}/rest/api/3/issue/bulk", json=payload)

    return plan_issue_batch(issues, confirmed=confirmed, enabled=write_enabled(), sender=sender)
