package launch

import "os/exec"

// setGroup kills the job's shell on cancel. Windows has no process groups to signal, so a cancelled local job
// can leave its run-job and browser running; it is found again through its result directory.
func setGroup(cmd *exec.Cmd) {
	cmd.Cancel = func() error { return cmd.Process.Kill() }
}
