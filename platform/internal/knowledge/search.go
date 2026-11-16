// Package knowledge searches the canonical Markdown corpus.
// Results always include a repository path. The package does not create citations.
package knowledge

import (
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

// Hit is one matching document.
type Hit struct {
	Path    string
	Title   string
	Score   int
	Snippet string
}

// Search returns documents that contain every query term.
func Search(root, query string, limit int) ([]Hit, error) {
	terms := strings.Fields(strings.ToLower(query))
	if len(terms) == 0 {
		return nil, fmt.Errorf("search query is required")
	}
	if limit <= 0 {
		limit = 20
	}
	var hits []Hit
	err := filepath.WalkDir(root, func(path string, entry fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		if entry.IsDir() {
			switch entry.Name() {
			case ".git", ".eit", "node_modules":
				return fs.SkipDir
			}
			return nil
		}
		if !strings.HasSuffix(strings.ToLower(entry.Name()), ".md") {
			return nil
		}
		rel, err := filepath.Rel(root, path)
		if err != nil {
			return err
		}
		body, err := os.ReadFile(path)
		if err != nil {
			return err
		}
		text := string(body)
		title := titleOf(text, entry.Name())
		haystack := strings.ToLower(title + "\n" + text)
		score := 0
		for _, term := range terms {
			if !strings.Contains(haystack, term) {
				return nil
			}
			score += strings.Count(strings.ToLower(title), term)*5 + strings.Count(strings.ToLower(text), term)
		}
		hits = append(hits, Hit{
			Path:    filepath.ToSlash(rel),
			Title:   title,
			Score:   score,
			Snippet: snippet(text, terms),
		})
		return nil
	})
	if err != nil {
		return nil, err
	}
	sort.Slice(hits, func(i, j int) bool {
		if hits[i].Score == hits[j].Score {
			return hits[i].Path < hits[j].Path
		}
		return hits[i].Score > hits[j].Score
	})
	if len(hits) > limit {
		hits = hits[:limit]
	}
	return hits, nil
}

func titleOf(text, name string) string {
	for _, line := range strings.Split(text, "\n") {
		if strings.HasPrefix(line, "# ") {
			return strings.TrimSpace(strings.TrimPrefix(line, "# "))
		}
	}
	return strings.TrimSuffix(name, filepath.Ext(name))
}

func snippet(text string, terms []string) string {
	for _, line := range strings.Split(text, "\n") {
		lower := strings.ToLower(line)
		for _, term := range terms {
			if strings.Contains(lower, term) {
				line = strings.TrimSpace(line)
				if len(line) > 160 {
					return line[:160]
				}
				return line
			}
		}
	}
	return ""
}
