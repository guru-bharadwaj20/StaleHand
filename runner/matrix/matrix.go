// Package matrix expands an experiment description into one job per combination of its axes.
package matrix

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
)

// Matrix is the experiment file: every list is an axis to cross.
type Matrix struct {
	Name          string   `json:"name"`
	Scenarios     []string `json:"scenarios"`
	Architectures []string `json:"architectures"`
	Guards        []string `json:"guards"`
	Planners      []string `json:"planners"`
	Executors     []string `json:"executors"`
	Seeds         []int    `json:"seeds"`
	MaxSteps      int      `json:"max_steps"`
	// Timings is optional; when absent every job uses before_observation.
	Timings []string `json:"timings,omitempty"`
}

// ChangeTimings are the moments a scheduled change can land (see stalehand/env/browser.py).
var ChangeTimings = map[string]bool{"before_observation": true, "mid_step": true}

// Job is one run of one scenario file under one configuration.
type Job struct {
	ID           string `json:"id"`
	Matrix       string `json:"matrix"`
	Scenarios    string `json:"scenarios"`
	Architecture string `json:"architecture"`
	Guard        string `json:"guard"`
	Planner      string `json:"planner"`
	Executor     string `json:"executor"`
	Seed         int    `json:"seed"`
	MaxSteps     int    `json:"max_steps"`
	ChangeTiming string `json:"change_timing"`
}

// Parse reads a matrix and rejects unknown fields and empty axes.
func Parse(r io.Reader) (*Matrix, error) {
	dec := json.NewDecoder(r)
	dec.DisallowUnknownFields()
	var m Matrix
	if err := dec.Decode(&m); err != nil {
		return nil, fmt.Errorf("matrix: %w", err)
	}
	axes := map[string]int{"scenarios": len(m.Scenarios), "architectures": len(m.Architectures),
		"guards": len(m.Guards), "planners": len(m.Planners), "executors": len(m.Executors), "seeds": len(m.Seeds)}
	for name, n := range axes {
		if n == 0 {
			return nil, fmt.Errorf("matrix: axis %q is empty", name)
		}
	}
	if len(m.Timings) == 0 {
		m.Timings = []string{"before_observation"}
	}
	for _, t := range m.Timings {
		if !ChangeTimings[t] {
			return nil, fmt.Errorf("matrix: unknown change timing %q", t)
		}
	}
	if m.MaxSteps <= 0 {
		return nil, fmt.Errorf("matrix: max_steps must be positive")
	}
	return &m, nil
}

// Expand returns jobs in a fixed order: scenarios, architectures, guards, planners, executors, seeds, timings.
func (m *Matrix) Expand() []Job {
	var jobs []Job
	for _, sc := range m.Scenarios {
		for _, arch := range m.Architectures {
			for _, g := range m.Guards {
				for _, p := range m.Planners {
					for _, e := range m.Executors {
						for _, seed := range m.Seeds {
							for _, timing := range m.Timings {
								j := Job{Matrix: m.Name, Scenarios: sc, Architecture: arch, Guard: g, Planner: p,
									Executor: e, Seed: seed, MaxSteps: m.MaxSteps, ChangeTiming: timing}
								j.ID = jobID(j)
								jobs = append(jobs, j)
							}
						}
					}
				}
			}
		}
	}
	return jobs
}

// jobID hashes everything that changes a job's result, and nothing else (not the matrix name).
func jobID(j Job) string {
	key := fmt.Sprintf("%s|%s|%s|%s|%s|%d|%d|%s", j.Scenarios, j.Architecture, j.Guard, j.Planner, j.Executor, j.Seed,
		j.MaxSteps, j.ChangeTiming)
	sum := sha256.Sum256([]byte(key))
	return hex.EncodeToString(sum[:])[:12]
}
