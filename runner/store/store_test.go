package store

import (
	"path/filepath"
	"testing"

	"github.com/VivianSobers/StaleHand/runner/matrix"
)

func jobs(n int) []matrix.Job {
	out := make([]matrix.Job, n)
	for i := range out {
		out[i] = matrix.Job{ID: string(rune('a' + i)), Matrix: "m", Guard: "none", Seed: i, MaxSteps: 8}
	}
	return out
}

func open(t *testing.T) *Store {
	t.Helper()
	s, err := Open(filepath.Join(t.TempDir(), "runs.db"))
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { s.Close() })
	return s
}

func TestAddedJobsArePending(t *testing.T) {
	s := open(t)
	if err := s.Add(jobs(3)); err != nil {
		t.Fatal(err)
	}
	if c := mustCounts(t, s); c["pending"] != 3 {
		t.Fatalf("counts %v", c)
	}
}

func TestAddingAgainKeepsStatus(t *testing.T) {
	s := open(t)
	s.Add(jobs(2))
	claimed, _ := s.Claim("gpu1", 1)
	s.Finish(claimed[0].ID, 0, "")
	s.Add(jobs(2))
	if c := mustCounts(t, s); c["done"] != 1 || c["pending"] != 1 {
		t.Fatalf("counts %v", c)
	}
}

func TestClaimTakesAtMostN(t *testing.T) {
	s := open(t)
	s.Add(jobs(5))
	got, err := s.Claim("gpu1", 2)
	if err != nil || len(got) != 2 {
		t.Fatalf("got %d jobs, err %v", len(got), err)
	}
	more, _ := s.Claim("gpu2", 10)
	if len(more) != 3 {
		t.Fatalf("second claim got %d", len(more))
	}
}

func TestFailedJobsAreRetriedUntilLimit(t *testing.T) {
	s := open(t)
	s.MaxAttempts = 2
	s.Add(jobs(1))
	for attempt := 1; attempt <= 2; attempt++ {
		got, _ := s.Claim("gpu1", 1)
		if len(got) != 1 {
			t.Fatalf("attempt %d: nothing to claim", attempt)
		}
		s.Finish(got[0].ID, 1, "boom")
	}
	if got, _ := s.Claim("gpu1", 1); len(got) != 0 {
		t.Fatal("job retried past the attempt limit")
	}
}

func TestReleaseReturnsRunningJobsOfHost(t *testing.T) {
	s := open(t)
	s.Add(jobs(2))
	s.Claim("gpu1", 1)
	s.Claim("gpu2", 1)
	n, err := s.Release("gpu1")
	if err != nil || n != 1 {
		t.Fatalf("released %d, err %v", n, err)
	}
	if c := mustCounts(t, s); c["pending"] != 1 || c["running"] != 1 {
		t.Fatalf("counts %v", c)
	}
}

func TestClaimedJobKeepsItsSpec(t *testing.T) {
	s := open(t)
	s.Add(jobs(1))
	got, _ := s.Claim("gpu1", 1)
	if got[0].Guard != "none" || got[0].MaxSteps != 8 {
		t.Fatalf("spec lost: %+v", got[0])
	}
}

func mustCounts(t *testing.T, s *Store) map[string]int {
	t.Helper()
	c, err := s.Counts()
	if err != nil {
		t.Fatal(err)
	}
	return c
}
