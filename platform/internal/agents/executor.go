// Package agents defines the execution port for a future agent runtime.
// Guard and ScreenResult enforce orchestration limits and do not start workers.
package agents

import (
	"context"
	"errors"
)

// ErrNotImplemented means this release has no agent runtime.
var ErrNotImplemented = errors.New("agent execution is not implemented")

// Task is the work an executor would receive.
type Task struct {
	Skill string
	Input string
}

// Result is the structured output of a task. No implementation produces one.
type Result struct {
	Output string
}

// Executor runs a task. The shipped implementation refuses.
type Executor interface {
	Execute(ctx context.Context, task Task) (Result, error)
}

// Unimplemented refuses every task.
type Unimplemented struct{}

// Execute returns ErrNotImplemented and an empty result.
func (Unimplemented) Execute(context.Context, Task) (Result, error) {
	return Result{}, ErrNotImplemented
}
