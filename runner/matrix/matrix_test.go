package matrix

import (
	"strings"
	"testing"
)

const sample = `{
  "name": "pilot",
  "scenarios": ["inbox.jsonl", "shop.jsonl"],
  "architectures": ["hierarchical"],
  "guards": ["none", "replan_every_step", "rule_subtask"],
  "planners": ["qwen3-vl-8b"],
  "executors": ["ui-tars-1.5-7b"],
  "seeds": [0, 1],
  "max_steps": 8
}`

func TestExpandCrossesEveryAxis(t *testing.T) {
	m, err := Parse(strings.NewReader(sample))
	if err != nil {
		t.Fatal(err)
	}
	jobs := m.Expand()
	if len(jobs) != 2*1*3*1*1*2 {
		t.Fatalf("got %d jobs", len(jobs))
	}
}

func TestJobIDsAreUniqueAndStable(t *testing.T) {
	m, _ := Parse(strings.NewReader(sample))
	a, b := m.Expand(), m.Expand()
	seen := map[string]bool{}
	for i := range a {
		if a[i].ID != b[i].ID {
			t.Fatalf("id changed between expansions: %s vs %s", a[i].ID, b[i].ID)
		}
		if seen[a[i].ID] {
			t.Fatalf("duplicate id %s", a[i].ID)
		}
		seen[a[i].ID] = true
		if len(a[i].ID) != 12 {
			t.Fatalf("id %q should be 12 hex characters", a[i].ID)
		}
	}
}

func TestJobIDIgnoresMatrixName(t *testing.T) {
	m1, _ := Parse(strings.NewReader(sample))
	m2, _ := Parse(strings.NewReader(strings.Replace(sample, `"pilot"`, `"renamed"`, 1)))
	if m1.Expand()[0].ID != m2.Expand()[0].ID {
		t.Fatal("renaming the matrix must not change job ids, or finished jobs would rerun")
	}
}

func TestEmptyAxisIsAnError(t *testing.T) {
	_, err := Parse(strings.NewReader(strings.Replace(sample, `"seeds": [0, 1]`, `"seeds": []`, 1)))
	if err == nil {
		t.Fatal("expected an error for an empty axis")
	}
}

func TestUnknownFieldIsAnError(t *testing.T) {
	_, err := Parse(strings.NewReader(strings.Replace(sample, `"max_steps"`, `"max_stepz"`, 1)))
	if err == nil {
		t.Fatal("expected an error for a misspelt field")
	}
}

func TestTimingsDefaultAndExpand(t *testing.T) {
	m, _ := Parse(strings.NewReader(sample))
	if got := m.Expand()[0].ChangeTiming; got != "before_observation" {
		t.Fatalf("default timing %q", got)
	}
	both := strings.Replace(sample, `"max_steps": 8`, `"max_steps": 8, "timings": ["before_observation", "mid_step"]`, 1)
	m2, err := Parse(strings.NewReader(both))
	if err != nil {
		t.Fatal(err)
	}
	jobs := m2.Expand()
	if len(jobs) != 2*len(m.Expand()) || jobs[0].ID == jobs[1].ID {
		t.Fatalf("timing must be an axis that changes the id: %d jobs", len(jobs))
	}
}

func TestUnknownTimingIsAnError(t *testing.T) {
	bad := strings.Replace(sample, `"max_steps": 8`, `"max_steps": 8, "timings": ["after_lunch"]`, 1)
	if _, err := Parse(strings.NewReader(bad)); err == nil {
		t.Fatal("expected an error for an unknown timing")
	}
}
