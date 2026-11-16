package runs

import "testing"

func TestLegalTransitions(t *testing.T) {
	legal := [][2]State{
		{Pending, Planning},
		{Pending, Cancelled},
		{Planning, AwaitingApproval},
		{Planning, Running},
		{Planning, Failed},
		{Planning, Cancelled},
		{AwaitingApproval, Running},
		{AwaitingApproval, Cancelled},
		{AwaitingApproval, Failed},
		{Running, Verifying},
		{Running, Failed},
		{Running, Cancelled},
		{Verifying, Succeeded},
		{Verifying, Failed},
		{Verifying, Cancelled},
		{Failed, Planning},
	}
	for _, pair := range legal {
		if err := Transition(pair[0], pair[1]); err != nil {
			t.Errorf("%s -> %s: %v", pair[0], pair[1], err)
		}
	}
}

func TestIllegalTransitions(t *testing.T) {
	illegal := [][2]State{
		{Pending, Succeeded},
		{Pending, Running},
		{Planning, Succeeded},
		{AwaitingApproval, Succeeded},
		{Running, Succeeded},
		{Verifying, Running},
		{Succeeded, Planning},
		{Cancelled, Failed},
		{Failed, Succeeded},
		{State("unknown"), Pending},
	}
	for _, pair := range illegal {
		if err := Transition(pair[0], pair[1]); err == nil {
			t.Errorf("%s -> %s was allowed", pair[0], pair[1])
		}
	}
}
