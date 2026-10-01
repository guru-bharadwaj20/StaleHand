//go:build !windows

package launch

import (
	"os/exec"
	"syscall"
)

// setGroup starts the job in its own process group and makes cancelling signal the whole group.
func setGroup(cmd *exec.Cmd) {
	cmd.SysProcAttr = &syscall.SysProcAttr{Setpgid: true}
	cmd.Cancel = func() error { return syscall.Kill(-cmd.Process.Pid, syscall.SIGTERM) }
}
