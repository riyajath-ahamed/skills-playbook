package policy

import (
	"os"
	"path/filepath"
	"testing"
)

func TestEvaluateFailClosed(t *testing.T) {
	set := fixture()
	cases := []struct {
		name string
		req  Request
		want bool
	}{
		{name: "dev read", req: Request{Integration: "github", Environment: "development", Capability: "read"}, want: true},
		{name: "dev write", req: Request{Integration: "github", Environment: "development", Capability: "write"}, want: false},
		{name: "production read", req: Request{Integration: "github", Environment: "production", Capability: "read", Approval: true}, want: false},
		{name: "unknown env", req: Request{Integration: "github", Environment: "", Capability: "read"}, want: false},
		{name: "unknown integration", req: Request{Integration: "missing", Environment: "development", Capability: "read"}, want: false},
		{name: "escalation", req: Request{Integration: "github", Environment: "development", Capability: "write", Profile: "development-write"}, want: false},
		{name: "approved write", req: Request{Integration: "github", Environment: "development", Capability: "write", Profile: "development-write", Approval: true}, want: true},
		{name: "delete stays denied", req: Request{Integration: "github", Environment: "development", Capability: "delete", Profile: "development-write", Approval: true}, want: false},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			decision := Evaluate(set, tc.req)
			if decision.Allow != tc.want {
				t.Fatalf("allow = %v, reason = %s", decision.Allow, decision.Reason)
			}
		})
	}
}

func TestProductionRestrictedReadsNeedApproval(t *testing.T) {
	set := fixture()
	set.Integrations["db"] = Integration{ID: "db", PermissionProfile: "production-restricted", Production: "approval"}
	denied := Evaluate(set, Request{Integration: "db", Environment: "production", Capability: "read"})
	if denied.Allow {
		t.Fatal("production read without approval was allowed")
	}
	allowed := Evaluate(set, Request{Integration: "db", Environment: "production", Capability: "read", Approval: true})
	if !allowed.Allow {
		t.Fatalf("approved production read denied: %s", allowed.Reason)
	}
	write := Evaluate(set, Request{Integration: "db", Environment: "production", Capability: "write", Approval: true})
	if write.Allow {
		t.Fatal("production write was allowed")
	}
}

func TestLoadRealCatalogDeniesProduction(t *testing.T) {
	root := repoRoot(t)
	set, err := Load(root)
	if err != nil {
		t.Fatal(err)
	}
	decision := Evaluate(set, Request{Integration: "github", Environment: "production", Capability: "read", Approval: true})
	if decision.Allow {
		t.Fatalf("production read allowed: %s", decision.Reason)
	}
}

func fixture() Set {
	readOnly := Policy{
		ID:               "read-only",
		ProductionAccess: "deny",
		Allow:            map[string][]string{"development": {"read"}, "test": {"read"}},
		Deny:             []string{"delete", "deploy", "shell", "credential_admin"},
		ApprovalRequired: []string{"write", "delete", "deploy", "shell", "credential_admin", "production"},
		FailClosed:       true,
	}
	devWrite := readOnly
	devWrite.ID = "development-write"
	devWrite.Allow = map[string][]string{"development": {"read", "write"}, "test": {"read"}}
	restricted := devWrite
	restricted.ID = "production-restricted"
	restricted.ProductionAccess = "approval"
	restricted.Allow = map[string][]string{
		"development": {"read", "write"},
		"test":        {"read"},
		"production":  {"read"},
	}
	return Set{
		Integrations: map[string]Integration{
			"github": {ID: "github", PermissionProfile: "read-only", Production: "deny"},
		},
		Policies: map[string]Policy{
			"read-only":             readOnly,
			"development-write":     devWrite,
			"production-restricted": restricted,
		},
	}
}

func repoRoot(t *testing.T) string {
	t.Helper()
	dir, err := os.Getwd()
	if err != nil {
		t.Fatal(err)
	}
	for {
		if _, err := os.Stat(filepath.Join(dir, "mcp", "catalog.yaml")); err == nil {
			return dir
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			t.Fatal("repository root not found")
		}
		dir = parent
	}
}
