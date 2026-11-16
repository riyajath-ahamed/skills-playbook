"""SonarQube quality gate and issue reads. The token is optional."""

from __future__ import annotations

import os
from typing import Any

from common.http_api import Api

_api: Api | None = None


def configured() -> bool:
    return bool(os.environ.get("SONARQUBE_TOKEN", "").strip())


def configure(api: Api | None = None) -> Api:
    global _api
    if api is not None:
        _api = api
    if _api is None:
        token = os.environ.get("SONARQUBE_TOKEN", "")
        headers = {"Accept": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        _api = Api(headers)
    return _api


def _base() -> str:
    return os.environ.get("SONARQUBE_URL", "https://sonarcloud.io").rstrip("/")


def _params(extra: dict[str, str]) -> dict[str, str]:
    params = dict(extra)
    org = os.environ.get("SONARQUBE_ORG", "").strip()
    if org:
        params["organization"] = org
    return params


def _missing() -> dict[str, Any]:
    return {"ok": False, "configured": False, "error": "SONARQUBE_TOKEN is not set"}


def get_quality_gate(project_key: str) -> dict[str, Any]:
    """Read the quality gate for one SonarQube project."""
    if not configured():
        return _missing()
    status, body = configure().json(
        "GET",
        f"{_base()}/api/qualitygates/project_status",
        params=_params({"projectKey": project_key}),
    )
    if status >= 400 or status == 0 or not isinstance(body, dict):
        detail = body.get("error") if isinstance(body, dict) else "request failed"
        return {"ok": False, "configured": True, "status": status, "error": detail}
    project_status = body.get("projectStatus") or {}
    conditions = []
    for item in project_status.get("conditions") or []:
        conditions.append(
            {
                "metric": item.get("metricKey"),
                "status": item.get("status"),
                "actual": item.get("actualValue"),
            }
        )
    return {"ok": True, "configured": True, "status": project_status.get("status"), "conditions": conditions}


def search_issues(project_key: str) -> dict[str, Any]:
    """List unresolved issues for one SonarQube project."""
    if not configured():
        return _missing()
    status, body = configure().json(
        "GET",
        f"{_base()}/api/issues/search",
        params=_params({"componentKeys": project_key, "resolved": "false", "ps": "20"}),
    )
    if status >= 400 or status == 0 or not isinstance(body, dict):
        detail = body.get("error") if isinstance(body, dict) else "request failed"
        return {"ok": False, "configured": True, "status": status, "error": detail}
    issues = []
    for item in body.get("issues") or []:
        issues.append(
            {
                "key": item.get("key"),
                "severity": item.get("severity"),
                "message": item.get("message"),
                "component": item.get("component"),
                "line": item.get("line"),
            }
        )
    return {"ok": True, "configured": True, "total": body.get("total"), "issues": issues}
