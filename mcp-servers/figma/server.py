"""Figma connector. stdio or streamable HTTP on 127.0.0.1:8106."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp.server import MCPServer

from common.runtime import serve
from figma import tools

PORT = 8106


def build() -> MCPServer:
    server = MCPServer("figma-mcp", instructions="Read and flatten Figma files. This server does not write to Figma.")
    server.tool()(tools.get_file)
    server.tool()(tools.get_frame)
    return server


if __name__ == "__main__":
    serve(build(), PORT)
