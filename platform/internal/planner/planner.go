// Package planner turns a workflow document into a sequential plan.
// It does not start agents or call tools.
package planner

import (
	"fmt"
	"strings"

	"engineering-intelligence/platform/internal/registry"
)

// Step is one skill invocation in order.
type Step struct {
	Title string
	Skill string
}

// Plan is the single-agent execution plan for a workflow.
type Plan struct {
	Workflow   string
	Mode       string
	MultiAgent string
	Steps      []Step
}

// Build reads the workflow steps. Multi-agent execution is recorded, not started.
func Build(workflow registry.Workflow) (Plan, error) {
	if workflow.Execution != "sequential" {
		return Plan{}, fmt.Errorf("%s: execution must be sequential", workflow.Name)
	}
	if workflow.MultiAgent == "required" {
		return Plan{}, fmt.Errorf("%s: multi-agent execution is not required by any supported workflow", workflow.Name)
	}
	var steps []Step
	var current string
	for _, line := range strings.Split(workflow.Body, "\n") {
		trimmed := strings.TrimSpace(line)
		if strings.HasPrefix(trimmed, "### ") {
			current = strings.TrimSpace(strings.TrimPrefix(trimmed, "### "))
			continue
		}
		if skill, ok := strings.CutPrefix(trimmed, "- Skill: "); ok {
			skill = strings.TrimSpace(skill)
			if skill == "" {
				return Plan{}, fmt.Errorf("%s: step %q has an empty skill", workflow.Name, current)
			}
			steps = append(steps, Step{Title: current, Skill: skill})
		}
	}
	if len(steps) == 0 {
		return Plan{}, fmt.Errorf("%s: workflow has no steps", workflow.Name)
	}
	return Plan{
		Workflow:   workflow.Name,
		Mode:       "sequential",
		MultiAgent: workflow.MultiAgent,
		Steps:      steps,
	}, nil
}
