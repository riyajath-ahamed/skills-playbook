"""GitHub REST reads. This module is the only GitHub client in the repository."""

from __future__ import annotations

import os
from typing import Any

from common.http_api import Api

API = "https://api.github.com"
FILES_PER_PAGE = 100
# GitHub stops listing pull request files after 3000 entries.
MAX_FILE_PAGES = 30
DEFAULT_PATCH_BUDGET = 60000
_api: Api | None = None


def configure(api: Api | None = None) -> Api:
    global _api
    if api is not None:
        _api = api
    if _api is None:
        token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", "")
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "engineering-intelligence-mcp",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        _api = Api(headers)
    return _api


def _error(status: int, body: object) -> dict[str, Any]:
    detail = body.get("error") if isinstance(body, dict) else "request failed"
    return {"ok": False, "status": status, "error": detail}


def get_pull_request(owner: str, repo: str, number: int) -> dict[str, Any]:
    """Read one pull request."""
    status, body = configure().json("GET", f"{API}/repos/{owner}/{repo}/pulls/{number}")
    if status >= 400 or status == 0 or not isinstance(body, dict):
        return _error(status, body)
    return {
        "ok": True,
        "number": body.get("number"),
        "title": body.get("title"),
        "state": body.get("state"),
        "html_url": body.get("html_url"),
        "body": body.get("body") or "",
        "user": (body.get("user") or {}).get("login"),
        "head": (body.get("head") or {}).get("ref"),
        "base": (body.get("base") or {}).get("ref"),
    }


def _list_pull_request_files(owner: str, repo: str, number: int) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    url = f"{API}/repos/{owner}/{repo}/pulls/{number}/files"
    files: list[dict[str, Any]] = []
    for page in range(1, MAX_FILE_PAGES + 1):
        status, body = configure().json("GET", url, params={"per_page": FILES_PER_PAGE, "page": page})
        if status >= 400 or status == 0 or not isinstance(body, list):
            return files, _error(status, body)
        files.extend(item for item in body if isinstance(item, dict))
        if len(body) < FILES_PER_PAGE:
            break
    return files, None


def _shape_file(item: dict[str, Any], budget: int) -> tuple[dict[str, Any], int]:
    entry: dict[str, Any] = {
        "filename": item.get("filename"),
        "status": item.get("status"),
        "additions": item.get("additions"),
        "deletions": item.get("deletions"),
    }
    if item.get("previous_filename"):
        entry["previous_filename"] = item["previous_filename"]
    patch = item.get("patch")
    if not isinstance(patch, str):
        entry["patch_omitted"] = "GitHub returned no patch (binary or too large)"
    elif len(patch) > budget:
        entry["patch_omitted"] = "max_patch_chars reached; read the file with get_file"
    else:
        entry["patch"] = patch
        budget -= len(patch)
    return entry, budget


def get_pull_request_files(
    owner: str, repo: str, number: int, max_patch_chars: int = DEFAULT_PATCH_BUDGET
) -> dict[str, Any]:
    """List the files a pull request changes, with each file's unified diff until max_patch_chars is spent."""
    files, failure = _list_pull_request_files(owner, repo, number)
    if failure is not None:
        return failure
    budget = max(0, max_patch_chars)
    shaped = []
    for item in files:
        entry, budget = _shape_file(item, budget)
        shaped.append(entry)
    return {
        "ok": True,
        "count": len(shaped),
        "additions": sum(item.get("additions") or 0 for item in files),
        "deletions": sum(item.get("deletions") or 0 for item in files),
        "patches_omitted": sum(1 for item in shaped if "patch_omitted" in item),
        "files": shaped,
    }


def get_file(owner: str, repo: str, path: str, ref: str = "") -> dict[str, Any]:
    """Read one file from a repository."""
    url = f"{API}/repos/{owner}/{repo}/contents/{path}"
    params = {"ref": ref} if ref else None
    status, body = configure().json("GET", url, params=params)
    if status >= 400 or status == 0 or not isinstance(body, dict):
        return _error(status, body)
    return {
        "ok": True,
        "path": body.get("path"),
        "sha": body.get("sha"),
        "encoding": body.get("encoding"),
        "content": body.get("content"),
        "html_url": body.get("html_url"),
    }


def list_commits(owner: str, repo: str, sha: str = "") -> dict[str, Any]:
    """List commits on a branch or pull request head."""
    params = {"sha": sha, "per_page": 20} if sha else {"per_page": 20}
    status, body = configure().json("GET", f"{API}/repos/{owner}/{repo}/commits", params=params)
    if status >= 400 or status == 0 or not isinstance(body, list):
        return _error(status, body)
    commits = []
    for item in body:
        commit = item.get("commit") or {}
        commits.append(
            {
                "sha": item.get("sha"),
                "message": (commit.get("message") or "").split("\n", 1)[0],
                "html_url": item.get("html_url"),
            }
        )
    return {"ok": True, "commits": commits}


def search_issues(query: str) -> dict[str, Any]:
    """Search issues and pull requests."""
    status, body = configure().json("GET", f"{API}/search/issues", params={"q": query, "per_page": 20})
    if status >= 400 or status == 0 or not isinstance(body, dict):
        return _error(status, body)
    items = []
    for item in body.get("items") or []:
        items.append(
            {
                "number": item.get("number"),
                "title": item.get("title"),
                "state": item.get("state"),
                "html_url": item.get("html_url"),
            }
        )
    return {"ok": True, "total": body.get("total_count"), "items": items}
