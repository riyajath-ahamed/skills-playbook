package agents

import (
	"context"
	"errors"
	"testing"
)

func TestUnimplemented(t *testing.T) {
	var executor Executor = Unimplemented{}
	result, err := executor.Execute(context.Background(), Task{Skill: "tdd"})
	if !errors.Is(err, ErrNotImplemented) {
		t.Fatalf("error = %v", err)
	}
	if result.Output != "" {
		t.Fatalf("result = %+v", result)
	}
}
