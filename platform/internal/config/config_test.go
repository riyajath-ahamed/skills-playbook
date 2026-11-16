package config

import (
	"os"
	"path/filepath"
	"testing"
)

func TestFindRootRequiresMarkers(t *testing.T) {
	if _, err := FindRoot(t.TempDir(), "", ""); err == nil {
		t.Fatal("expected missing root to fail")
	}
	root := t.TempDir()
	if err := os.WriteFile(filepath.Join(root, "AGENTS.md"), []byte("x\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.MkdirAll(filepath.Join(root, "mcp"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(root, "mcp", "catalog.yaml"), []byte("version: 1\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	found, err := FindRoot(root, "", t.TempDir())
	if err != nil {
		t.Fatal(err)
	}
	if found != root {
		t.Fatalf("root = %s", found)
	}
}
