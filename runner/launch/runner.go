package launch

import (
	"context"
	"errors"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/VivianSobers/StaleHand/runner/hosts"
	"github.com/VivianSobers/StaleHand/runner/matrix"
)

// ExecRunner runs jobs as child processes (sh locally, ssh remotely) and writes each job's output to
// LogDir/<matrix>/<id>.log. Each job runs in its own process group, and cancelling signals the whole group, so
// local jobs leave no orphaned run-job or browser processes. On a remote host only the ssh client is stopped; the
// job may keep running there and is found again through its result directory.
type ExecRunner struct {
	LogDir  string
	Command func(hosts.Host, matrix.Job) string // defaults to RemoteCommand
}

func (r ExecRunner) Run(ctx context.Context, h hosts.Host, j matrix.Job) (int, error) {
	build := r.Command
	if build == nil {
		build = RemoteCommand
	}
	dir := filepath.Join(r.LogDir, j.Matrix)
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return -1, err
	}
	logf, err := os.Create(filepath.Join(dir, j.ID+".log"))
	if err != nil {
		return -1, err
	}
	defer logf.Close()
	argv := Argv(h, build(h, j))
	cmd := exec.CommandContext(ctx, argv[0], argv[1:]...)
	cmd.Stdout, cmd.Stderr = logf, logf
	setGroup(cmd)
	err = cmd.Run()
	var exit *exec.ExitError
	switch {
	case err == nil:
		return 0, nil
	case errors.As(err, &exit) && ctx.Err() == nil:
		return exit.ExitCode(), nil
	case ctx.Err() != nil:
		return -1, fmt.Errorf("cancelled: %w", ctx.Err())
	default:
		return -1, err
	}
}
