// Package hosts describes the machines jobs can run on. Keep real addresses in an untracked file.
package hosts

import (
	"encoding/json"
	"fmt"
	"io"
)

// Host is one machine. An empty SSH target means the local machine.
type Host struct {
	Name    string            `json:"name"`
	SSH     string            `json:"ssh,omitempty"`
	Slots   int               `json:"slots"`
	Workdir string            `json:"workdir"`
	Python  string            `json:"python"`
	Env     map[string]string `json:"env,omitempty"`
}

func Parse(r io.Reader) ([]Host, error) {
	dec := json.NewDecoder(r)
	dec.DisallowUnknownFields()
	var f struct {
		Hosts []Host `json:"hosts"`
	}
	if err := dec.Decode(&f); err != nil {
		return nil, fmt.Errorf("hosts: %w", err)
	}
	seen := map[string]bool{}
	for _, h := range f.Hosts {
		if h.Name == "" || h.Slots <= 0 || h.Workdir == "" || h.Python == "" {
			return nil, fmt.Errorf("hosts: %q needs a name, slots > 0, workdir and python", h.Name)
		}
		if seen[h.Name] {
			return nil, fmt.Errorf("hosts: duplicate name %q", h.Name)
		}
		seen[h.Name] = true
	}
	return f.Hosts, nil
}

func TotalSlots(hs []Host) int {
	n := 0
	for _, h := range hs {
		n += h.Slots
	}
	return n
}
