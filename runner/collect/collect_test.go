package collect

import (
	"os"
	"path/filepath"
	"reflect"
	"testing"

	"github.com/VivianSobers/StaleHand/runner/hosts"
	"github.com/VivianSobers/StaleHand/runner/matrix"
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
