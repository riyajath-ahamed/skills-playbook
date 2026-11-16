package registry

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestLoadAndFind(t *testing.T) {
	root := t.TempDir()
	writeSkill(t, root, "documentation", "alpha", "1.0.0")
	writeWorkflow(t, root, "alpha-flow", "alpha")

	lib, err := Load(root)
	if err != nil {
		t.Fatal(err)
	}
	if len(lib.Skills) != 1 || len(lib.Workflows) != 1 {
		t.Fatalf("library = %+v", lib)
	}
	skill, err := lib.FindSkill("alpha")
	if err != nil {
		t.Fatal(err)
	}
	if skill.Domain != "documentation" || skill.Version != "1.0.0" {
		t.Fatalf("skill = %+v", skill)
	}
	if _, err := lib.FindSkill("missing"); err == nil || !strings.Contains(err.Error(), "skill not found") {
		t.Fatalf("missing skill error = %v", err)
	}
	if _, err := lib.FindWorkflow("missing"); err == nil || !strings.Contains(err.Error(), "workflow not found") {
		t.Fatalf("missing workflow error = %v", err)
	}
}

func TestMalformedSkill(t *testing.T) {
	root := t.TempDir()
	path := filepath.Join(root, "skills", "documentation", "broken", "SKILL.md")
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, []byte("---\nname: [\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	if _, err := Load(root); err == nil || !strings.Contains(err.Error(), "SKILL.md") {
		t.Fatalf("expected malformed skill error, got %v", err)
	}
}

func writeSkill(t *testing.T, root, domain, name, version string) {
	t.Helper()
	path := filepath.Join(root, "skills", domain, name, "SKILL.md")
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		t.Fatal(err)
	}
	body := "---\nname: " + name + "\ndescription: Test skill.\nmetadata:\n  version: \"" + version + "\"\n  domain: " + domain + "\n  risk: low\n---\n\n# Body\n"
	if err := os.WriteFile(path, []byte(body), 0o644); err != nil {
		t.Fatal(err)
	}
}

func writeWorkflow(t *testing.T, root, name, skill string) {
	t.Helper()
	path := filepath.Join(root, "workflows", name, "WORKFLOW.md")
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		t.Fatal(err)
	}
	body := "---\nname: " + name + "\ndescription: Test workflow.\nexecution: sequential\nskills:\n  - " + skill + "\n---\n\n### 1. Do it\n- Skill: " + skill + "\n"
	if err := os.WriteFile(path, []byte(body), 0o644); err != nil {
		t.Fatal(err)
	}
}
