package tools

import (
	"context"
	"errors"
	"testing"

	"engineering-intelligence/platform/internal/policy"
)

type recordingAdapter struct {
	calls int
}

func (a *recordingAdapter) Invoke(context.Context, policy.Request) (string, error) {
	a.calls++
	return "", ErrNotImplemented
}

func TestDeniedCallDoesNotReachAdapter(t *testing.T) {
	adapter := &recordingAdapter{}
	gateway := Gateway{Set: set(), Adapter: adapter}
	_, err := gateway.Call(context.Background(), policy.Request{
		Integration: "github",
		Environment: "production",
		Capability:  "write",
		Approval:    true,
	})
	var denied ErrDenied
	if !errors.As(err, &denied) {
		t.Fatalf("error = %v", err)
	}
	if adapter.calls != 0 || gateway.Calls != 0 {
		t.Fatalf("adapter calls = %d, gateway calls = %d", adapter.calls, gateway.Calls)
	}
}

func TestAllowedCallStopsAtUnimplementedAdapter(t *testing.T) {
	adapter := &recordingAdapter{}
	gateway := Gateway{Set: set(), Adapter: adapter}
	_, err := gateway.Call(context.Background(), policy.Request{
		Integration: "github",
		Environment: "development",
		Capability:  "read",
	})
	if !errors.Is(err, ErrNotImplemented) {
		t.Fatalf("error = %v", err)
	}
	if adapter.calls != 1 || gateway.Calls != 1 {
		t.Fatalf("adapter calls = %d, gateway calls = %d", adapter.calls, gateway.Calls)
	}
}

func set() policy.Set {
	return policy.Set{
		Integrations: map[string]policy.Integration{
			"github": {ID: "github", PermissionProfile: "read-only", Production: "deny"},
		},
		Policies: map[string]policy.Policy{
			"read-only": {
				ID:               "read-only",
				ProductionAccess: "deny",
				Allow:            map[string][]string{"development": {"read"}},
				Deny:             []string{"delete", "deploy", "shell", "credential_admin"},
				ApprovalRequired: []string{"write", "production"},
				FailClosed:       true,
			},
		},
	}
}
