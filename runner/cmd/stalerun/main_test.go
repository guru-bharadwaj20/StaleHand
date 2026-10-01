package main

import (
	"bytes"
	"os"
	"path/filepath"
	"strings"
	"testing"
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
