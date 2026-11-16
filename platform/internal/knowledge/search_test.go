package knowledge

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestSearchRanksAndRequiresEveryTerm(t *testing.T) {
	root := t.TempDir()
	writeDoc(t, root, "knowledge/one.md", "# Alpha guide\n\nalpha appears here\n")
	writeDoc(t, root, "knowledge/two.md", "# Alpha beta\n\nalpha and beta together\n")
	hits, err := Search(root, "alpha beta", 10)
	if err != nil {
		t.Fatal(err)
	}
	if len(hits) != 1 || hits[0].Path != "knowledge/two.md" {
		t.Fatalf("hits = %+v", hits)
	}
	if hits[0].Path == "" {
		t.Fatal("hit missing path")
	}
	if _, err := Search(root, "   ", 10); err == nil {
		t.Fatal("empty query was accepted")
	}
}

func TestSearchSkipsMissingTerm(t *testing.T) {
	root := t.TempDir()
	writeDoc(t, root, "note.md", "# Note\n\nnothing relevant\n")
	hits, err := Search(root, "absent-term", 10)
	if err != nil {
		t.Fatal(err)
	}
	if len(hits) != 0 {
		t.Fatalf("hits = %+v", hits)
	}
}

func writeDoc(t *testing.T, root, rel, body string) {
	t.Helper()
	path := filepath.Join(root, filepath.FromSlash(rel))
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, []byte(body), 0o644); err != nil {
		t.Fatal(err)
	}
}

func TestSnippetDoesNotInventPath(t *testing.T) {
	root := t.TempDir()
	writeDoc(t, root, "knowledge/named.md", "# Named\n\ncatalog-token is here\n")
	hits, err := Search(root, "catalog-token", 5)
	if err != nil {
		t.Fatal(err)
	}
	if len(hits) != 1 || !strings.Contains(hits[0].Snippet, "catalog-token") {
		t.Fatalf("hits = %+v", hits)
	}
}
