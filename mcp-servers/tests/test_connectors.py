"""Connector tests. They mock HTTP and do not call vendor APIs."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import httpx

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "mcp-servers"))

from common.env import parse_env, redact
from common.http_api import Api
from common.manifest import cursor_config, load_servers, missing_required
from confluence.tools import get_page, page_id_from
from figma.tools import file_key_from, flatten_node, get_file
from github.tools import get_pull_request, get_pull_request_files
from jira.tools import get_issue_details, plan_issue_batch
from sonar.tools import get_quality_gate


def client(handler) -> Api:
    return Api({}, transport=httpx.MockTransport(handler))


class ToolTests(unittest.TestCase):
    def test_github_read_uses_the_mock(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.url.path, "/repos/acme/app/pulls/7")
            return httpx.Response(200, json={"number": 7, "title": "Fix", "state": "open", "user": {"login": "a"}})

        from github import tools

        tools.configure(client(handler))
        result = get_pull_request("acme", "app", 7)
        self.assertEqual(result["title"], "Fix")
        tools.configure(None)
        tools._api = None

    def test_github_pull_request_files_pages_and_budgets_patches(self) -> None:
        first_page = [
            {"filename": f"src/f{index}.py", "status": "modified", "additions": 1, "deletions": 0, "patch": "@@ -1 +1 @@\n+x"}
            for index in range(100)
        ]
        second_page = [
            {"filename": "img/logo.png", "status": "added", "additions": 0, "deletions": 0},
            {"filename": "src/new.py", "status": "renamed", "previous_filename": "src/old.py", "additions": 2, "deletions": 1, "patch": "@@ -1 +1,2 @@\n+y\n+z"},
        ]
        pages: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.url.path, "/repos/acme/app/pulls/7/files")
            pages.append(request.url.params["page"])
            return httpx.Response(200, json=first_page if request.url.params["page"] == "1" else second_page)

        from github import tools

        tools.configure(client(handler))
        result = get_pull_request_files("acme", "app", 7, max_patch_chars=len(first_page[0]["patch"]) * 100)
        tools._api = None
        self.assertEqual(pages, ["1", "2"])
        self.assertEqual(result["count"], 102)
        self.assertEqual(result["additions"], 102)
        self.assertEqual(result["deletions"], 1)
        self.assertIn("patch", result["files"][0])
        binary, renamed = result["files"][100], result["files"][101]
        self.assertIn("no patch", binary["patch_omitted"])
        self.assertEqual(renamed["previous_filename"], "src/old.py")
        self.assertIn("max_patch_chars", renamed["patch_omitted"])
        self.assertEqual(result["patches_omitted"], 2)

    def test_github_pull_request_files_reports_errors(self) -> None:
        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(404, json={"message": "Not Found"})

        from github import tools

        tools.configure(client(handler))
        result = get_pull_request_files("acme", "app", 404)
        tools._api = None
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], 404)

    def test_jira_preview_does_not_send(self) -> None:
        def sender(_payload: dict) -> tuple[int, object]:
            raise AssertionError("create was sent")

        preview = plan_issue_batch(
            [{"project": "ETI", "summary": "Add", "issue_type": "Task"}],
            confirmed=False,
            enabled=True,
            sender=sender,
        )
        self.assertFalse(preview["sent"])
        preview = plan_issue_batch(
            [{"project": "ETI", "summary": "Add"}],
            confirmed=True,
            enabled=False,
            sender=sender,
        )
        self.assertFalse(preview["sent"])

    def test_jira_send_uses_the_gate(self) -> None:
        sent: list[dict] = []

        def sender(payload: dict) -> tuple[int, object]:
            sent.append(payload)
            return 201, {"issues": []}

        result = plan_issue_batch(
            [{"project": "ETI", "summary": "Add", "issue_type": "Task", "description": "note"}],
            confirmed=True,
            enabled=True,
            sender=sender,
        )
        self.assertTrue(result["sent"])
        fields = sent[0]["issueUpdates"][0]["fields"]
        self.assertEqual(fields["summary"], "Add")
        self.assertEqual(fields["description"]["type"], "doc")

    def test_jira_details_classify_links(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path.endswith("/remotelink"):
                return httpx.Response(200, json=[{"object": {"url": "https://lucid.app/diagram/1"}}])
            return httpx.Response(
                200,
                json={
                    "key": "ETI-1",
                    "fields": {
                        "summary": "Read",
                        "status": {"name": "Open"},
                        "description": {
                            "type": "doc",
                            "content": [{"type": "text", "text": "See https://docs.google.com/document/d/abc"}],
                        },
                    },
                },
            )

        from jira import tools

        tools.configure(client(handler))
        with mock.patch.dict("os.environ", {"JIRA_BASE_URL": "https://example.atlassian.net"}):
            result = get_issue_details("ETI-1")
        self.assertEqual(result["google_workspace_refs"], ["https://docs.google.com/document/d/abc"])
        self.assertEqual(result["lucid_refs"], ["https://lucid.app/diagram/1"])
        tools._api = None

    def test_jira_details_read_smart_links_and_hyperlinks(self) -> None:
        description = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "inlineCard", "attrs": {"url": "https://lucid.app/lucidchart/abc/edit"}},
                        {
                            "type": "text",
                            "text": "design doc",
                            "marks": [{"type": "link", "attrs": {"href": "https://docs.google.com/document/d/xyz"}}],
                        },
                    ],
                },
                {"type": "blockCard", "attrs": {"url": "https://example.com/runbook"}},
            ],
        }

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path.endswith("/remotelink"):
                return httpx.Response(200, json=[])
            return httpx.Response(200, json={"key": "ETI-2", "fields": {"summary": "s", "status": {"name": "Open"}, "description": description}})

        from jira import tools

        tools.configure(client(handler))
        with mock.patch.dict("os.environ", {"JIRA_BASE_URL": "https://example.atlassian.net"}):
            result = get_issue_details("ETI-2")
        tools._api = None
        self.assertEqual(result["lucid_refs"], ["https://lucid.app/lucidchart/abc/edit"])
        self.assertEqual(result["google_workspace_refs"], ["https://docs.google.com/document/d/xyz"])
        self.assertEqual(result["links"], ["https://example.com/runbook"])
        self.assertIn("https://lucid.app/lucidchart/abc/edit", result["description"])
        self.assertIn("design doc", result["description"])

    def test_confluence_page_id(self) -> None:
        self.assertEqual(page_id_from("https://example.atlassian.net/wiki/spaces/ENG/pages/42/Title"), "42")

        def handler(request: httpx.Request) -> httpx.Response:
            self.assertIn("/wiki/api/v2/pages/42", request.url.path)
            return httpx.Response(200, json={"id": "42", "title": "Notes", "body": {"storage": {"value": "body"}}})

        from confluence import tools

        tools.configure(client(handler))
        with mock.patch.dict("os.environ", {"CONFLUENCE_BASE_URL": "https://example.atlassian.net"}):
            result = get_page("42")
        self.assertEqual(result["title"], "Notes")
        tools._api = None

    def test_figma_flatten_and_key(self) -> None:
        self.assertEqual(file_key_from("https://www.figma.com/design/AbC123/Name"), "AbC123")
        flat = flatten_node({"id": "0", "name": "File", "type": "DOCUMENT", "children": [{"id": "1", "name": "Frame", "type": "FRAME"}]})
        self.assertEqual(flat["children"][0]["name"], "Frame")

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"name": "Design", "document": {"id": "0", "name": "File", "type": "DOCUMENT"}})

        from figma import tools

        tools.configure(client(handler))
        with mock.patch.dict("os.environ", {"FIGMA_ACCESS_TOKEN": "figma-test-token"}):
            result = get_file("AbC123")
        self.assertEqual(result["name"], "Design")
        tools._api = None

    def test_sonar_missing_token_does_not_call(self) -> None:
        def handler(_request: httpx.Request) -> httpx.Response:
            raise AssertionError("sonar was called")

        from sonar import tools

        tools.configure(client(handler))
        with mock.patch.dict("os.environ", {"SONARQUBE_TOKEN": ""}):
            result = get_quality_gate("proj")
        self.assertFalse(result["configured"])
        tools._api = None

    def test_redact_hides_token(self) -> None:
        text = redact("failed with supersecretvalue", {"GITHUB_PERSONAL_ACCESS_TOKEN": "supersecretvalue"})
        self.assertNotIn("supersecretvalue", text)


class ControlTests(unittest.TestCase):
    def test_generator_has_stdio_and_no_secret(self) -> None:
        secret = "ghp_" + ("a" * 36)
        with tempfile.TemporaryDirectory() as tmp:
            python = Path(tmp) / "python"
            python.write_text("", encoding="utf-8")
            config = cursor_config(ROOT, python)
        raw = json.dumps(config)
        self.assertNotIn(secret, raw)
        self.assertNotIn("Bearer", raw)
        github = config["mcpServers"]["github-mcp"]
        self.assertEqual(github["env"]["MCP_TRANSPORT"], "stdio")
        self.assertTrue(github["args"][0].endswith("mcp-servers/github/server.py"))

    def test_generator_keeps_the_venv_interpreter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "config").mkdir()
            (root / "config" / "mcpctl-manifest.yaml").write_text(
                (ROOT / "config" / "mcpctl-manifest.yaml").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            link = root / ".venv" / "bin" / "python"
            link.parent.mkdir(parents=True)
            link.symlink_to(Path(sys.executable).resolve())
            sys.path.insert(0, str(ROOT / "scripts"))
            from generate_cursor_mcp import generate

            destination = generate(root)
            command = json.loads(destination.read_text(encoding="utf-8"))["mcpServers"]["github-mcp"]["command"]
        self.assertTrue(command.endswith("/.venv/bin/python"))

    def test_doctor_reports_names_not_values(self) -> None:
        servers = load_servers(ROOT)
        github = next(item for item in servers if item["id"] == "github-mcp")
        self.assertEqual(missing_required(github, {}), ["GITHUB_PERSONAL_ACCESS_TOKEN"])
        self.assertEqual(missing_required(github, {"GITHUB_PERSONAL_ACCESS_TOKEN": "supersecretvalue"}), [])
        sonar = next(item for item in servers if item["id"] == "sonar-mcp")
        self.assertEqual(missing_required(sonar, {}), [])

    def test_ports_match_server_files(self) -> None:
        for server in load_servers(ROOT):
            text = (ROOT / server["directory"] / server["entry"]).read_text(encoding="utf-8")
            self.assertIn(f"PORT = {server['port']}", text)

    def test_parse_env_ignores_comments(self) -> None:
        self.assertEqual(parse_env("# note\nTOKEN=value\n"), {"TOKEN": "value"})

    def test_servers_register_every_tool_their_skills_name(self) -> None:
        import asyncio
        import importlib

        import yaml

        registered: set[str] = set()
        for server in load_servers(ROOT):
            module = importlib.import_module(f"{Path(server['directory']).name}.server")
            registered.update(tool.name for tool in asyncio.run(module.build().list_tools()))
        for path in sorted((ROOT / "skills").glob("*/*/SKILL.md")):
            front = yaml.safe_load(path.read_text(encoding="utf-8").split("---\n", 2)[1])
            for tool in (front.get("metadata") or {}).get("tools") or []:
                self.assertIn(tool, registered, f"{path.relative_to(ROOT)} names unregistered tool {tool}")


if __name__ == "__main__":
    unittest.main()
