package hosts

import (
	"strings"
	"testing"
)

const sample = `{"hosts": [
  {"name": "gpu1", "ssh": "user@gpu1.lab", "slots": 2, "workdir": "~/stalehand", "python": ".venv/bin/python",
   "env": {"CUDA_VISIBLE_DEVICES": "0"}},
  {"name": "local", "slots": 1, "workdir": ".", "python": "python3"}
]}`

func TestParseHosts(t *testing.T) {
	hs, err := Parse(strings.NewReader(sample))
	if err != nil {
		t.Fatal(err)
	}
	if len(hs) != 2 || hs[0].Slots != 2 || hs[1].SSH != "" {
		t.Fatalf("parsed %+v", hs)
	}
}

func TestZeroSlotsIsAnError(t *testing.T) {
	_, err := Parse(strings.NewReader(`{"hosts": [{"name": "x", "slots": 0, "workdir": ".", "python": "p"}]}`))
	if err == nil {
		t.Fatal("expected error")
	}
}

func TestDuplicateNamesAreAnError(t *testing.T) {
	_, err := Parse(strings.NewReader(`{"hosts": [{"name": "x", "slots": 1, "workdir": ".", "python": "p"},
		{"name": "x", "slots": 1, "workdir": ".", "python": "p"}]}`))
	if err == nil {
		t.Fatal("expected error")
	}
}

func TestTotalSlots(t *testing.T) {
	hs, _ := Parse(strings.NewReader(sample))
	if TotalSlots(hs) != 3 {
		t.Fatal("wrong slot total")
	}
}
