// Package dispatch runs pending jobs on every host slot until none are left or the context is cancelled.
package dispatch

import (
	"context"
	"fmt"
	"io"
	"sync"

	"github.com/VivianSobers/StaleHand/runner/hosts"
	"github.com/VivianSobers/StaleHand/runner/matrix"
	"github.com/VivianSobers/StaleHand/runner/store"
)

// Runner executes one job on one host and returns its exit code.
type Runner interface {
	Run(ctx context.Context, h hosts.Host, j matrix.Job) (int, error)
}

// Summary counts attempts: a job that failed twice and then passed adds 2 to Failed and 1 to Done.
type Summary struct {
	Done   int
	Failed int
}

// Dispatch starts Slots workers per host. Each claims one job at a time from the store.
func Dispatch(ctx context.Context, st *store.Store, hs []hosts.Host, r Runner, log io.Writer) (Summary, error) {
	var (
		mu       sync.Mutex
		sum      Summary
		firstErr error
		wg       sync.WaitGroup
	)
	note := func(format string, a ...any) {
		mu.Lock()
		defer mu.Unlock()
		fmt.Fprintf(log, format+"\n", a...)
	}
	for _, h := range hs {
		for slot := 0; slot < h.Slots; slot++ {
			wg.Add(1)
			go func(h hosts.Host) {
				defer wg.Done()
				for ctx.Err() == nil {
					jobs, err := st.Claim(h.Name, 1)
					if err != nil {
						mu.Lock()
						if firstErr == nil {
							firstErr = err
						}
						mu.Unlock()
						return
					}
					if len(jobs) == 0 {
						return
					}
					j := jobs[0]
					code, runErr := r.Run(ctx, h, j)
					msg := ""
					if runErr != nil {
						code, msg = -1, runErr.Error()
					}
					if err := st.Finish(j.ID, code, msg); err != nil {
						note("store: %v", err)
					}
					mu.Lock()
					if code == 0 {
						sum.Done++
					} else {
						sum.Failed++
					}
					mu.Unlock()
					note("%s %s exit=%d %s", h.Name, j.ID, code, msg)
				}
			}(h)
		}
	}
	wg.Wait()
	return sum, firstErr
}
