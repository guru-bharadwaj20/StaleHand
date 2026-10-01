// Package collect copies finished run directories from the hosts that ran them into one results tree.
package collect

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/VivianSobers/StaleHand/runner/hosts"
	"github.com/VivianSobers/StaleHand/runner/matrix"
)

// RunDir is where stalehand run-job writes a job, relative to the host's workdir (see launch.RemoteCommand).
func RunDir(j matrix.Job) string { return filepath.Join("runs", j.Matrix, j.ID) }

// Argv is the rsync command that copies one job's run directory to dest/<matrix>/<id>/.
func Argv(h hosts.Host, j matrix.Job, dest string) []string {
	to := filepath.Join(dest, j.Matrix, j.ID) + "/"
	if h.SSH == "" {
		return []string{"rsync", "-a", filepath.Join(h.Workdir, RunDir(j)) + "/", to}
	}
	// rsync resolves a relative remote path against the remote home, which is what a leading ~/ means
	from := filepath.Join(strings.TrimPrefix(h.Workdir, "~/"), RunDir(j)) + "/"
	return []string{"rsync", "-a", "-e", "ssh -o BatchMode=yes -o ConnectTimeout=15", h.SSH + ":" + from, to}
}

// Check reports whether a copied run directory has the files every report reads.
func Check(dir string) error {
	for _, f := range []string{"config.json", "results.jsonl"} {
		if _, err := os.Stat(filepath.Join(dir, f)); err != nil {
			return fmt.Errorf("%s: missing %s", dir, f)
		}
	}
	return nil
}
