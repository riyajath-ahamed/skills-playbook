"""SonarQube connector. stdio or streamable HTTP on 127.0.0.1:8108."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp.server import MCPServer

from common.runtime import serve
from sonar import tools

PORT = 8108


def build() -> MCPServer:
    server = MCPServer("sonar-mcp", instructions="Read SonarQube quality gates and issues. The token is optional.")
    server.tool()(tools.get_quality_gate)
    server.tool()(tools.search_issues)
    return server


if __name__ == "__main__":
    serve(build(), PORT)
