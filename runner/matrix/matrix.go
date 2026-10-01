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
}

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
	if m.MaxSteps <= 0 {
		return nil, fmt.Errorf("matrix: max_steps must be positive")
	}
	return &m, nil
}

// Expand returns jobs in a fixed order: scenarios, architectures, guards, planners, executors, seeds.
func (m *Matrix) Expand() []Job {
	var jobs []Job
	for _, sc := range m.Scenarios {
		for _, arch := range m.Architectures {
			for _, g := range m.Guards {
				for _, p := range m.Planners {
					for _, e := range m.Executors {
						for _, seed := range m.Seeds {
							j := Job{Matrix: m.Name, Scenarios: sc, Architecture: arch, Guard: g, Planner: p,
								Executor: e, Seed: seed, MaxSteps: m.MaxSteps}
							j.ID = jobID(j)
							jobs = append(jobs, j)
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
	key := fmt.Sprintf("%s|%s|%s|%s|%s|%d|%d", j.Scenarios, j.Architecture, j.Guard, j.Planner, j.Executor, j.Seed, j.MaxSteps)
	sum := sha256.Sum256([]byte(key))
	return hex.EncodeToString(sum[:])[:12]
}
