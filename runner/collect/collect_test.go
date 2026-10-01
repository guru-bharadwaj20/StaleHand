package collect

import (
	"os"
	"path/filepath"
	"reflect"
	"testing"

	"github.com/VivianSobers/StaleHand/runner/hosts"
	"github.com/VivianSobers/StaleHand/runner/matrix"
	"github.com/VivianSobers/StaleHand/runner/store"
)

var job = matrix.Job{ID: "abc123def456", Matrix: "pilot"}

func TestRemoteArgvStripsHomePrefix(t *testing.T) {
	h := hosts.Host{Name: "w1", SSH: "ccbd@10.0.0.1", Workdir: "~/stalehand"}
	got := Argv(h, job, "results/vivian-4090")
	want := []string{"rsync", "-a", "-e", "ssh -o BatchMode=yes -o ConnectTimeout=15",
		"ccbd@10.0.0.1:stalehand/runs/pilot/abc123def456/", "results/vivian-4090/pilot/abc123def456/"}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("got  %q\nwant %q", got, want)
	}
}

func TestLocalArgvCopiesFromWorkdir(t *testing.T) {
	got := Argv(hosts.Host{Name: "local", Workdir: "/srv/sh"}, job, "out")
	want := []string{"rsync", "-a", "/srv/sh/runs/pilot/abc123def456/", "out/pilot/abc123def456/"}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("got %q", got)
	}
}

func TestCheckNeedsConfigAndResults(t *testing.T) {
	dir := t.TempDir()
	if err := Check(dir); err == nil {
		t.Fatal("empty directory passed")
	}
	os.WriteFile(filepath.Join(dir, "config.json"), []byte("{}"), 0o644)
	if err := Check(dir); err == nil {
		t.Fatal("directory without results passed")
	}
	os.WriteFile(filepath.Join(dir, "results.jsonl"), []byte("{}\n"), 0o644)
	if err := Check(dir); err != nil {
		t.Fatal(err)
	}
}

func writeRun(t *testing.T, workdir string, j matrix.Job, rows string) {
	t.Helper()
	dir := filepath.Join(workdir, RunDir(j))
	os.MkdirAll(dir, 0o755)
	os.WriteFile(filepath.Join(dir, "config.json"), []byte("{}"), 0o644)
	if rows != "" {
		os.WriteFile(filepath.Join(dir, "results.jsonl"), []byte(rows), 0o644)
	}
}

func TestAllCopiesFinishedRunsAndReportsProblems(t *testing.T) {
	work, dest := t.TempDir(), t.TempDir()
	good := matrix.Job{ID: "aaaaaaaaaaaa", Matrix: "pilot"}
	broken := matrix.Job{ID: "bbbbbbbbbbbb", Matrix: "pilot"}
	orphan := matrix.Job{ID: "cccccccccccc", Matrix: "pilot"}
	writeRun(t, work, good, "{}\n")
	writeRun(t, work, broken, "")
	hs := []hosts.Host{{Name: "local", Workdir: work}}
	placed := []store.Placed{{Job: good, Host: "local"}, {Job: broken, Host: "local"}, {Job: orphan, Host: "gone"}}
	sum := All(placed, hs, dest, RunCommand)
	if sum.Copied != 1 || len(sum.Problems) != 2 {
		t.Fatalf("summary %+v", sum)
	}
	if _, err := os.Stat(filepath.Join(dest, "pilot", good.ID, "results.jsonl")); err != nil {
		t.Fatal(err)
	}
}
