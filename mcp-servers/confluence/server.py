"""Confluence connector. stdio or streamable HTTP on 127.0.0.1:8103."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp.server import MCPServer

from common.runtime import serve
from confluence import tools

PORT = 8103


def build() -> MCPServer:
    server = MCPServer("confluence-mcp", instructions="Read Confluence pages. This server does not publish pages.")
    server.tool()(tools.get_page)
    return server


if __name__ == "__main__":
    serve(build(), PORT)
