//go:build !windows

package launch

import (
	"context"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"syscall"
	"testing"
	"time"

	"github.com/VivianSobers/StaleHand/runner/hosts"
	"github.com/VivianSobers/StaleHand/runner/matrix"
)

func TestExecRunnerStopsOnCancel(t *testing.T) {
	r := ExecRunner{LogDir: t.TempDir(), Command: func(hosts.Host, matrix.Job) string { return "sleep 30" }}
	ctx, cancel := context.WithTimeout(context.Background(), 100*time.Millisecond)
	defer cancel()
	start := time.Now()
	r.Run(ctx, hosts.Host{Name: "local"}, job)
	if time.Since(start) > 5*time.Second {
		t.Fatal("cancel did not stop the command")
	}
}

func TestCancelStopsGrandchildren(t *testing.T) {
	pidFile := filepath.Join(t.TempDir(), "pid")
	// like run-job under sh -c: the long-lived process is a grandchild of the runner
	r := ExecRunner{LogDir: t.TempDir(), Command: func(hosts.Host, matrix.Job) string {
		return "sleep 30 & echo $! > " + pidFile + "; wait"
	}}
	ctx, cancel := context.WithCancel(context.Background())
	done := make(chan struct{})
	go func() { r.Run(ctx, hosts.Host{Name: "local"}, job); close(done) }()
	var pid int
	for i := 0; i < 50 && pid == 0; i++ {
		time.Sleep(50 * time.Millisecond)
		b, _ := os.ReadFile(pidFile)
		pid, _ = strconv.Atoi(strings.TrimSpace(string(b)))
	}
	if pid == 0 {
		t.Fatal("grandchild never started")
	}
	cancel()
	<-done
	time.Sleep(200 * time.Millisecond)
	if err := syscall.Kill(pid, 0); err == nil {
		syscall.Kill(pid, syscall.SIGKILL)
		t.Fatal("grandchild survived cancel")
	}
}
