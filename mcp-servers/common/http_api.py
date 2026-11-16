"""Small HTTP helper. Callers pass a transport in tests."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx

from common.env import redact


class Api:
    def __init__(self, headers: Mapping[str, str], transport: httpx.BaseTransport | None = None) -> None:
        self._headers = dict(headers)
        self._transport = transport

    def json(self, method: str, url: str, **kwargs: Any) -> tuple[int, object]:
        try:
            with httpx.Client(headers=self._headers, transport=self._transport, timeout=30.0) as client:
                response = client.request(method, url, **kwargs)
        except httpx.HTTPError as exc:
            return 0, {"error": redact(str(exc))}
        text = response.text[:2000]
        try:
            body: object = response.json()
        except ValueError:
            body = {"text": redact(text)}
        if response.status_code >= 400:
            return response.status_code, {"error": redact(text)}
        return response.status_code, body
