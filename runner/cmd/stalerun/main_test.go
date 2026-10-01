package main

import (
	"bytes"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/VivianSobers/StaleHand/runner/store"
)

func TestPlanThenStatus(t *testing.T) {
	dir := t.TempDir()
	m := filepath.Join(dir, "m.json")
	os.WriteFile(m, []byte(`{"name": "t", "scenarios": ["a.jsonl"], "architectures": ["hierarchical"],
		"guards": ["none", "rule_subtask"], "planners": ["p"], "executors": ["e"], "seeds": [0], "max_steps": 4}`), 0o644)
	db := filepath.Join(dir, "runs.db")
	var out bytes.Buffer
	if err := run([]string{"plan", "-matrix", m, "-db", db}, &out); err != nil {
		t.Fatal(err)
	}
	out.Reset()
	if err := run([]string{"status", "-db", db}, &out); err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(out.String(), "pending  2") {
		t.Fatalf("status output %q", out.String())
	}
}

func TestUnknownCommand(t *testing.T) {
	if err := run([]string{"fly", "-db", filepath.Join(t.TempDir(), "x.db")}, &bytes.Buffer{}); err == nil {
		t.Fatal("expected error")
	}
}

func TestCollectCopiesDoneJobs(t *testing.T) {
	dir := t.TempDir()
	m := filepath.Join(dir, "m.json")
	os.WriteFile(m, []byte(`{"name": "t", "scenarios": ["a.jsonl"], "architectures": ["hierarchical"],
		"guards": ["none"], "planners": ["p"], "executors": ["e"], "seeds": [0], "max_steps": 4}`), 0o644)
	db := filepath.Join(dir, "runs.db")
	if err := run([]string{"plan", "-matrix", m, "-db", db}, &bytes.Buffer{}); err != nil {
		t.Fatal(err)
	}
	st, _ := store.Open(db)
	jobs, _ := st.Claim("local", 1)
	st.Finish(jobs[0].ID, 0, "")
	st.Close()
	work := filepath.Join(dir, "work")
	runDir := filepath.Join(work, "runs", "t", jobs[0].ID)
	os.MkdirAll(runDir, 0o755)
	os.WriteFile(filepath.Join(runDir, "config.json"), []byte("{}"), 0o644)
	os.WriteFile(filepath.Join(runDir, "results.jsonl"), []byte("{}\n"), 0o644)
	hostsFile := filepath.Join(dir, "hosts.json")
	os.WriteFile(hostsFile, []byte(`{"hosts": [{"name": "local", "slots": 1, "workdir": "`+work+`", "python": "python3"}]}`), 0o644)
	dest := filepath.Join(dir, "results")
	var out bytes.Buffer
	if err := run([]string{"collect", "-db", db, "-hosts", hostsFile, "-dest", dest}, &out); err != nil {
		t.Fatal(err, out.String())
	}
	if !strings.Contains(out.String(), "copied 1") {
		t.Fatalf("output %q", out.String())
	}
	if _, err := os.Stat(filepath.Join(dest, "t", jobs[0].ID, "results.jsonl")); err != nil {
		t.Fatal(err)
	}
}
