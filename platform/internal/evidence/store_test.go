package evidence

import (
	"strings"
	"testing"
)

func TestAddRedactsSecrets(t *testing.T) {
	token := "ghp_" + strings.Repeat("a", 36)
	store := Store{}
	store.Add(Item{Path: "notes.md", Kind: "log", Note: "saw " + token})
	if len(store.Items) != 1 {
		t.Fatalf("items = %+v", store.Items)
	}
	if strings.Contains(store.Items[0].Note, token) || !strings.Contains(store.Items[0].Note, "[REDACTED]") {
		t.Fatalf("note = %q", store.Items[0].Note)
	}
}
