package cli

import (
	"bytes"
	"context"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"engineering-intelligence/platform/internal/registry"
)

func TestVersionAndUsage(t *testing.T) {
	stdout, stderr, code := run(t, nil, "version")
	if code != 0 || !strings.Contains(stdout, "ei 0.1.0") {
		t.Fatalf("code=%d stdout=%s stderr=%s", code, stdout, stderr)
	}
	stdout, stderr, code = run(t, nil, "nope")
	if code != 2 || !strings.Contains(stderr, "unknown command") {
		t.Fatalf("code=%d stderr=%s", code, stderr)
	}
	if _, _, code = run(t, nil); code != 0 || !strings.Contains(runText(t, nil), "ei skills list") {
		t.Fatalf("help code=%d", code)
	}
}

func TestSkillsWorkflowsAndSearch(t *testing.T) {
	root := fixtureRepo(t)
	stdout, stderr, code := run(t, &root, "skills", "list")
	if code != 0 || !strings.Contains(stdout, "Documentation (1)") || !strings.Contains(stdout, "│ alpha") || !strings.Contains(stdout, "Alpha test skill.") || !strings.Contains(stdout, "│ Skill") {
		t.Fatalf("code=%d stdout=%s stderr=%s", code, stdout, stderr)
	}
	stdout, stderr, code = run(t, &root, "skills", "show", "missing")
	if code != 1 || !strings.Contains(stderr, "skill not found") {
		t.Fatalf("code=%d stderr=%s", code, stderr)
	}
	stdout, stderr, code = run(t, &root, "skills", "show")
	if code != 2 {
		t.Fatalf("show without name code=%d stderr=%s", code, stderr)
	}
	stdout, _, code = run(t, &root, "workflows", "show", "alpha-flow")
	if code != 0 || !strings.Contains(stdout, "execution: sequential") {
		t.Fatalf("workflow show = %s", stdout)
	}
	stdout, stderr, code = run(t, &root, "knowledge", "search", "alpha-token")
	if code != 0 || !strings.Contains(stdout, "knowledge/note.md") {
		t.Fatalf("code=%d stdout=%s stderr=%s", code, stdout, stderr)
	}
	if _, _, code = run(t, &root, "knowledge", "search"); code != 2 {
		t.Fatal("empty search should be a usage error")
	}
}

func TestSkillListGroupsByDomain(t *testing.T) {
	var buf bytes.Buffer
	writeSkillList(&buf, []registry.Skill{
		{Name: "tdd", Domain: "software-engineering", Description: "Implement a behavior by writing a failing test."},
		{Name: "api-design", Domain: "architecture", Description: "Design an HTTP interface."},
		{Name: "adr-authoring", Domain: "architecture", Description: strings.Repeat("decision ", 20)},
	})
	out := buf.String()
	architecture := strings.Index(out, "Architecture (2)")
	software := strings.Index(out, "Software Engineering (1)")
	if architecture < 0 || software < architecture {
		t.Fatalf("domain order:\n%s", out)
	}
	if strings.Index(out, "adr-authoring") > strings.Index(out, "api-design") {
		t.Fatalf("skills are not sorted within the domain:\n%s", out)
	}
	if !strings.Contains(out, "│ Skill") || !strings.Contains(out, "│ Summary") || !strings.Contains(out, "decision") {
		t.Fatalf("table did not include wrapped summaries:\n%s", out)
	}
}

func TestMCPList(t *testing.T) {
	root := fixtureRepo(t)
	stdout, stderr, code := run(t, &root, "mcp", "list")
	if code != 0 || !strings.Contains(stdout, "0 integrations") {
		t.Fatalf("empty catalog code=%d stdout=%s stderr=%s", code, stdout, stderr)
	}
	mustWrite(t, filepath.Join(root, "mcp", "catalog.yaml"), `
version: 1
integrations:
  - id: zeta
    purpose: Second entry.
    permission_profile: development-write
    installed: false
  - id: alpha
    provider: example/alpha
    purpose: Read a documented server description.
    permission_profile: read-only
    installed: false
`)
	stdout, stderr, code = run(t, &root, "mcp", "list")
	if code != 0 || strings.Index(stdout, "│ alpha") > strings.Index(stdout, "│ zeta") {
		t.Fatalf("order code=%d stdout=%s stderr=%s", code, stdout, stderr)
	}
	if !strings.Contains(stdout, "│ Integration") || !strings.Contains(stdout, "│ Vendor") || !strings.Contains(stdout, "example/alpha") || !strings.Contains(stdout, "│ Profile") || !strings.Contains(stdout, "false") || !strings.Contains(stdout, "Read a documented") {
		t.Fatalf("table stdout=%s", stdout)
	}
	if _, _, code = run(t, &root, "mcp"); code != 2 {
		t.Fatal("mcp without list should be a usage error")
	}
	mustWrite(t, filepath.Join(root, "mcp", "catalog.yaml"), "integrations: [\n")
	_, stderr, code = run(t, &root, "mcp", "list")
	if code != 1 || !strings.Contains(stderr, "parse catalog") {
		t.Fatalf("malformed catalog code=%d stderr=%s", code, stderr)
	}
}

func TestMCPHealth(t *testing.T) {
	auth := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Header.Get("Authorization") != "" {
			t.Errorf("health check sent credentials")
		}
		w.WriteHeader(http.StatusUnauthorized)
	}))
	defer auth.Close()
	ok := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusNoContent)
	}))
	defer ok.Close()
	items := []mcpIntegration{
		{ID: "remote-auth", Transport: "http", Endpoint: auth.URL, Status: "documented"},
		{ID: "remote-ok", Transport: "http", Endpoint: ok.URL, Status: "documented"},
		{ID: "local", Transport: "stdio", Status: "documented"},
		{ID: "planned", Transport: "none", Status: "planned"},
		{ID: "down", Transport: "http", Endpoint: "http://127.0.0.1:1", Status: "documented"},
		{ID: "private", Transport: "http", Endpoint: "https://10.1.1.1/mcp", Status: "documented"},
	}
	results := checkMCPHealth(context.Background(), items, mcpHealthClient())
	got := map[string]mcpHealthResult{}
	for _, result := range results {
		got[result.ID] = result
	}
	if got["remote-auth"].Result != "auth-required" || !strings.Contains(got["remote-auth"].Detail, "HTTP 401") {
		t.Fatalf("auth result: %+v", got["remote-auth"])
	}
	if got["remote-ok"].Result != "reachable" || !strings.Contains(got["remote-ok"].Detail, "HTTP 204") {
		t.Fatalf("ok result: %+v", got["remote-ok"])
	}
	if got["local"].Result != "skipped" || got["planned"].Result != "skipped" || got["private"].Result != "skipped" {
		t.Fatalf("skips: local=%+v planned=%+v private=%+v", got["local"], got["planned"], got["private"])
	}
	if got["down"].Result != "unreachable" {
		t.Fatalf("down result: %+v", got["down"])
	}
	var buf bytes.Buffer
	writeMCPHealth(&buf, results)
	if !strings.Contains(buf.String(), "│ Result") || !strings.Contains(buf.String(), "auth-required") {
		t.Fatalf("health table:\n%s", buf.String())
	}
}

func TestMalformedSkillFailsList(t *testing.T) {
	root := fixtureRepo(t)
	path := filepath.Join(root, "skills", "documentation", "bad", "SKILL.md")
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, []byte("---\nname: [\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	_, stderr, code := run(t, &root, "skills", "list")
	if code != 1 || !strings.Contains(stderr, "SKILL.md") {
		t.Fatalf("code=%d stderr=%s", code, stderr)
	}
}

func TestDoctorAndValidateFixture(t *testing.T) {
	root := fixtureRepo(t)
	stdout, stderr, code := run(t, &root, "doctor")
	if code != 0 || !strings.Contains(stdout, "[ok] repository root") {
		t.Fatalf("code=%d stdout=%s stderr=%s", code, stdout, stderr)
	}
	if !strings.Contains(stdout, "opentelemetry-export") || !strings.Contains(stdout, "optional") {
		t.Fatalf("doctor should report optional telemetry, stdout=%s", stdout)
	}
	_, stderr, code = run(t, &root, "validate")
	if code != 1 || !strings.Contains(stderr, "validator not found") {
		t.Fatalf("fixture validate code=%d stderr=%s", code, stderr)
	}
}

func TestRepositoryCommands(t *testing.T) {
	root := repositoryRoot(t)
	stdout, stderr, code := run(t, &root, "skills", "list")
	if code != 0 || !strings.Contains(stdout, "system-design") {
		t.Fatalf("code=%d stderr=%s", code, stderr)
	}
	stdout, stderr, code = run(t, &root, "workflows", "list")
	if code != 0 || !strings.Contains(stdout, "research-to-decision") {
		t.Fatalf("workflows code=%d stdout=%s stderr=%s", code, stdout, stderr)
	}
	stdout, stderr, code = run(t, &root, "mcp", "list")
	if code != 0 || !strings.Contains(stdout, "│ github") || !strings.Contains(stdout, "│ GitHub") || !strings.Contains(stdout, "│ Vendor") || !strings.Contains(stdout, "read-only") || !strings.Contains(stdout, "Source: mcp/catalog.yaml") {
		t.Fatalf("mcp list code=%d stdout=%s stderr=%s", code, stdout, stderr)
	}
	stdout, stderr, code = run(t, &root, "knowledge", "search", "canonical-source-revision")
	if code != 0 || !strings.Contains(stdout, "knowledge/glossaries/engineering-intelligence.md") {
		t.Fatalf("search code=%d stdout=%s stderr=%s", code, stdout, stderr)
	}
	stdout, stderr, code = run(t, &root, "validate")
	if code != 0 {
		t.Fatalf("validate failed: %s\n%s", stdout, stderr)
	}
}

func run(t *testing.T, root *string, args ...string) (string, string, int) {
	t.Helper()
	var stdout, stderr bytes.Buffer
	if root != nil {
		args = append([]string{"--root", *root}, args...)
	}
	code := Main(args, &stdout, &stderr, func(string) string { return "" })
	return stdout.String(), stderr.String(), code
}

func runText(t *testing.T, root *string, args ...string) string {
	t.Helper()
	stdout, _, _ := run(t, root, args...)
	return stdout
}

func fixtureRepo(t *testing.T) string {
	t.Helper()
	root := t.TempDir()
	mustWrite(t, filepath.Join(root, "AGENTS.md"), "agent\n")
	mustWrite(t, filepath.Join(root, "mcp", "catalog.yaml"), "version: 1\n")
	mustWrite(t, filepath.Join(root, "skills", "documentation", "alpha", "SKILL.md"), `---
name: alpha
description: Alpha test skill.
metadata:
  version: "1.0.0"
  domain: documentation
  risk: low
---

# Alpha

Procedure.
`)
	mustWrite(t, filepath.Join(root, "workflows", "alpha-flow", "WORKFLOW.md"), `---
name: alpha-flow
description: Alpha flow.
execution: sequential
skills:
  - alpha
---

### 1. Use alpha
- Skill: alpha
`)
	mustWrite(t, filepath.Join(root, "knowledge", "note.md"), "# Note\n\nalpha-token lives here\n")
	return root
}

func mustWrite(t *testing.T, path, body string) {
	t.Helper()
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, []byte(body), 0o644); err != nil {
		t.Fatal(err)
	}
}

func repositoryRoot(t *testing.T) string {
	t.Helper()
	dir, err := os.Getwd()
	if err != nil {
		t.Fatal(err)
	}
	for {
		if _, err := os.Stat(filepath.Join(dir, "AGENTS.md")); err == nil {
			return dir
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			t.Fatal("repository root not found")
		}
		dir = parent
	}
}
