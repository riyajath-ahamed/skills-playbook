"""GitHub connector. stdio or streamable HTTP on 127.0.0.1:8101."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp.server import MCPServer

from common.runtime import serve
from github import tools

PORT = 8101


def build() -> MCPServer:
    server = MCPServer("github-mcp", instructions="Read GitHub pull requests, their changed files and diffs, files, commits, and issues.")
    server.tool()(tools.get_pull_request)
    server.tool()(tools.get_pull_request_files)
    server.tool()(tools.get_file)
    server.tool()(tools.list_commits)
    server.tool()(tools.search_issues)
    return server


if __name__ == "__main__":
    serve(build(), PORT)
