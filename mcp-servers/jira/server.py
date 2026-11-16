"""Jira connector. stdio or streamable HTTP on 127.0.0.1:8102."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp.server import MCPServer

from common.runtime import serve
from jira import tools

PORT = 8102


def build() -> MCPServer:
    server = MCPServer("jira-mcp", instructions="Read Jira issues. Writes require confirmed=true and JIRA_WRITE_ENABLED.")
    server.tool()(tools.get_issue_details)
    server.tool()(tools.get_issue_comments)
    server.tool()(tools.create_issues_batch)
    return server


if __name__ == "__main__":
    serve(build(), PORT)
