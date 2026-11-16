// Package tools is the gateway in front of MCP or other tool adapters.
// The shipped adapter does not open a connection.
package tools

import (
	"context"
	"errors"

	"engineering-intelligence/platform/internal/policy"
)

// ErrNotImplemented means the allow decision had no live adapter.
var ErrNotImplemented = errors.New("tool adapter is not implemented")

// ErrDenied means policy rejected the call before any adapter ran.
type ErrDenied struct {
	Reason string
}

func (e ErrDenied) Error() string {
	return "tool call denied: " + e.Reason
}

// Adapter would invoke an external tool. NotImplementedAdapter does not.
type Adapter interface {
	Invoke(ctx context.Context, req policy.Request) (string, error)
}

// NotImplementedAdapter refuses live calls.
type NotImplementedAdapter struct{}

// Invoke returns ErrNotImplemented.
func (NotImplementedAdapter) Invoke(context.Context, policy.Request) (string, error) {
	return "", ErrNotImplemented
}

// Gateway checks policy before calling an adapter.
type Gateway struct {
	Set     policy.Set
	Adapter Adapter
	Calls   int
}

// Call denies failed policy checks without incrementing Calls.
func (g *Gateway) Call(ctx context.Context, req policy.Request) (string, error) {
	decision := policy.Evaluate(g.Set, req)
	if !decision.Allow {
		return "", ErrDenied{Reason: decision.Reason}
	}
	adapter := g.Adapter
	if adapter == nil {
		adapter = NotImplementedAdapter{}
	}
	g.Calls++
	return adapter.Invoke(ctx, req)
}
