package planner

import (
	"strings"
	"testing"

	"engineering-intelligence/platform/internal/registry"
)

func TestBuildSequentialPlan(t *testing.T) {
	plan, err := Build(registry.Workflow{
		Name:       "example",
		Execution:  "sequential",
		MultiAgent: "optional",
		Body:       "### 1. First\n- Skill: technical-scouting\n### 2. Second\n- Skill: source-verification\n",
	})
	if err != nil {
		t.Fatal(err)
	}
	if plan.Mode != "sequential" || len(plan.Steps) != 2 {
		t.Fatalf("plan = %+v", plan)
	}
	if plan.Steps[0].Skill != "technical-scouting" || plan.Steps[1].Title != "2. Second" {
		t.Fatalf("steps = %+v", plan.Steps)
	}
}

func TestRejectRequiredMultiAgent(t *testing.T) {
	_, err := Build(registry.Workflow{Name: "example", Execution: "sequential", MultiAgent: "required", Body: "- Skill: tdd\n"})
	if err == nil || !strings.Contains(err.Error(), "multi-agent") {
		t.Fatalf("error = %v", err)
	}
}
