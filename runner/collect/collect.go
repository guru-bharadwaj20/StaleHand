// Package collect copies finished run directories from the hosts that ran them into one results tree.
package collect

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/VivianSobers/StaleHand/runner/hosts"
	"github.com/VivianSobers/StaleHand/runner/matrix"
	"github.com/VivianSobers/StaleHand/runner/store"
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

// Summary counts copied runs and lists the ones that could not be copied or are incomplete.
type Summary struct {
	Copied   int
	Problems []string
}

// RunCommand runs argv and returns its combined output on failure.
func RunCommand(argv []string) error {
	if err := os.MkdirAll(argv[len(argv)-1], 0o755); err != nil {
		return err
	}
	out, err := exec.Command(argv[0], argv[1:]...).CombinedOutput()
	if err != nil {
		return fmt.Errorf("%v: %s", err, strings.TrimSpace(string(out)))
	}
	return nil
}

// All copies every placed job into dest and checks each copy. It keeps going past failures.
func All(placed []store.Placed, hs []hosts.Host, dest string, run func([]string) error) Summary {
	byName := map[string]hosts.Host{}
	for _, h := range hs {
		byName[h.Name] = h
	}
	var sum Summary
	for _, p := range placed {
		h, ok := byName[p.Host]
		if !ok {
			sum.Problems = append(sum.Problems, fmt.Sprintf("%s: host %q is not in the hosts file", p.Job.ID, p.Host))
			continue
		}
		if err := run(Argv(h, p.Job, dest)); err != nil {
			sum.Problems = append(sum.Problems, fmt.Sprintf("%s: %v", p.Job.ID, err))
			continue
		}
		if err := Check(filepath.Join(dest, p.Job.Matrix, p.Job.ID)); err != nil {
			sum.Problems = append(sum.Problems, err.Error())
			continue
		}
		sum.Copied++
	}
	return sum
}
