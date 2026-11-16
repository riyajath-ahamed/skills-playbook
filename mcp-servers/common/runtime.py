"""Start one connector. mcp 2.3 renamed FastMCP to MCPServer."""

from __future__ import annotations

import os
import sys

from mcp.server import MCPServer

from common.env import load_env


def serve(server: MCPServer, port: int) -> None:
    load_env()
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport == "stdio":
        server.run(transport="stdio")
        return
    if transport == "streamable-http":
        server.run(transport="streamable-http", host="127.0.0.1", port=port)
        return
    print(f"unknown MCP_TRANSPORT {transport}", file=sys.stderr)
    raise SystemExit(2)
