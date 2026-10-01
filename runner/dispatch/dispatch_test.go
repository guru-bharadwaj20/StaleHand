package dispatch

import (
	"context"
	"fmt"
	"io"
	"path/filepath"
	"sync"
	"sync/atomic"
	"testing"
	"time"

	"github.com/VivianSobers/StaleHand/runner/hosts"
	"github.com/VivianSobers/StaleHand/runner/matrix"
	"github.com/VivianSobers/StaleHand/runner/store"
)

type fakeRunner struct {
	mu        sync.Mutex
	running   map[string]int
	maxByHost map[string]int
	calls     atomic.Int64
	fail      func(job matrix.Job, attempt int64) bool
}

func (f *fakeRunner) Run(_ context.Context, h hosts.Host, j matrix.Job) (int, error) {
	n := f.calls.Add(1)
	f.mu.Lock()
	f.running[h.Name]++
	if f.running[h.Name] > f.maxByHost[h.Name] {
		f.maxByHost[h.Name] = f.running[h.Name]
	}
	f.mu.Unlock()
	time.Sleep(2 * time.Millisecond)
	f.mu.Lock()
	f.running[h.Name]--
	f.mu.Unlock()
	if f.fail != nil && f.fail(j, n) {
		return 1, nil
	}
	return 0, nil
}

func setup(t *testing.T, n int) *store.Store {
	t.Helper()
	st, err := store.Open(filepath.Join(t.TempDir(), "runs.db"))
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { st.Close() })
	jobs := make([]matrix.Job, n)
	for i := range jobs {
		jobs[i] = matrix.Job{ID: fmt.Sprintf("job%03d", i), Matrix: "m"}
	}
	st.Add(jobs)
	return st
}

var twoHosts = []hosts.Host{{Name: "a", Slots: 2}, {Name: "b", Slots: 1}}

func TestAllJobsFinish(t *testing.T) {
	st := setup(t, 20)
	f := &fakeRunner{running: map[string]int{}, maxByHost: map[string]int{}}
	sum, err := Dispatch(context.Background(), st, twoHosts, f, io.Discard)
	if err != nil || sum.Done != 20 || sum.Failed != 0 {
		t.Fatalf("summary %+v err %v", sum, err)
	}
}

func TestSlotsLimitConcurrencyPerHost(t *testing.T) {
	st := setup(t, 30)
	f := &fakeRunner{running: map[string]int{}, maxByHost: map[string]int{}}
	Dispatch(context.Background(), st, twoHosts, f, io.Discard)
	if f.maxByHost["a"] > 2 || f.maxByHost["b"] > 1 {
		t.Fatalf("concurrency exceeded slots: %v", f.maxByHost)
	}
}

func TestFailedJobsAreRetried(t *testing.T) {
	st := setup(t, 1)
	st.MaxAttempts = 3
	f := &fakeRunner{running: map[string]int{}, maxByHost: map[string]int{},
		fail: func(_ matrix.Job, attempt int64) bool { return attempt < 3 }}
	sum, _ := Dispatch(context.Background(), st, twoHosts, f, io.Discard)
	if sum.Done != 1 || f.calls.Load() != 3 {
		t.Fatalf("summary %+v calls %d", sum, f.calls.Load())
	}
}

func TestCancelStopsClaiming(t *testing.T) {
	st := setup(t, 50)
	ctx, cancel := context.WithCancel(context.Background())
	f := &fakeRunner{running: map[string]int{}, maxByHost: map[string]int{},
		fail: func(_ matrix.Job, n int64) bool {
			if n == 5 {
				cancel()
			}
			return false
		}}
	Dispatch(ctx, st, twoHosts, f, io.Discard)
	if f.calls.Load() >= 50 {
		t.Fatal("dispatch kept going after cancel")
	}
}
