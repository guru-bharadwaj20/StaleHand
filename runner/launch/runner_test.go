package launch

import (
	"context"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/VivianSobers/StaleHand/runner/hosts"
	"github.com/VivianSobers/StaleHand/runner/matrix"
)

func TestExecRunnerReportsExitCodeAndLogs(t *testing.T) {
	dir := t.TempDir()
	r := ExecRunner{LogDir: dir, Command: func(hosts.Host, matrix.Job) string { return "echo hello; exit 3" }}
	code, err := r.Run(context.Background(), hosts.Host{Name: "local"}, job)
	if err != nil || code != 3 {
		t.Fatalf("code %d err %v", code, err)
	}
	b, _ := os.ReadFile(filepath.Join(dir, "pilot", "abc123def456.log"))
	if !strings.Contains(string(b), "hello") {
		t.Fatalf("log: %q", b)
	}
}
