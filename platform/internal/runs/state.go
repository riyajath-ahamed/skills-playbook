// Package runs models the workflow run lifecycle.
// The machine is in memory. It does not execute a run.
package runs

import "fmt"

// State is a position in the run lifecycle.
type State string

const (
	Pending          State = "pending"
	Planning         State = "planning"
	AwaitingApproval State = "awaiting_approval"
	Running          State = "running"
	Verifying        State = "verifying"
	Succeeded        State = "succeeded"
	Failed           State = "failed"
	Cancelled        State = "cancelled"
)

var transitions = map[State][]State{
	Pending:          {Planning, Cancelled},
	Planning:         {AwaitingApproval, Running, Failed, Cancelled},
	AwaitingApproval: {Running, Cancelled, Failed},
	Running:          {Verifying, Failed, Cancelled},
	Verifying:        {Succeeded, Failed, Cancelled},
	Failed:           {Planning},
}

// Transition reports whether from may move to to.
// Succeeded and cancelled are terminal. Failed may return to planning only
// when the caller explicitly requests recovery.
func Transition(from, to State) error {
	allowed, known := transitions[from]
	if !known {
		if from == Succeeded || from == Cancelled {
			return fmt.Errorf("cannot transition from terminal state %s to %s", from, to)
		}
		return fmt.Errorf("unknown state %s", from)
	}
	for _, candidate := range allowed {
		if candidate == to {
			return nil
		}
	}
	return fmt.Errorf("cannot transition from %s to %s", from, to)
}
