package launch

import (
	"encoding/base64"
	"encoding/json"
	"strings"
	"testing"

	"github.com/VivianSobers/StaleHand/runner/hosts"
	"github.com/VivianSobers/StaleHand/runner/matrix"
)

var job = matrix.Job{ID: "abc123def456", Matrix: "pilot", Scenarios: "s.jsonl", Guard: "none", MaxSteps: 8}

func TestShellQuote(t *testing.T) {
	cases := map[string]string{"plain": "'plain'", "it's": `'it'\''s'`, "": "''"}
	for in, want := range cases {
		if got := shellQuote(in); got != want {
			t.Errorf("shellQuote(%q) = %s, want %s", in, got, want)
		}
	}
}

func TestRemoteCommandCarriesJobAndEnv(t *testing.T) {
	h := hosts.Host{Name: "gpu1", Workdir: "~/StaleHand", Python: ".venv/bin/python", Env: map[string]string{"CUDA_VISIBLE_DEVICES": "1"}}
	cmd := RemoteCommand(h, job)
	if !strings.HasPrefix(cmd, "cd ~/'StaleHand' && ") {
		t.Fatalf("workdir handling: %s", cmd)
	}
	if !strings.Contains(cmd, "CUDA_VISIBLE_DEVICES='1'") || !strings.Contains(cmd, "--out 'runs/pilot/abc123def456'") {
		t.Fatalf("command: %s", cmd)
	}
	i := strings.Index(cmd, "--job '") + len("--job '")
	raw, err := base64.StdEncoding.DecodeString(cmd[i : i+strings.Index(cmd[i:], "'")])
	if err != nil {
		t.Fatal(err)
	}
	var back matrix.Job
	if err := json.Unmarshal(raw, &back); err != nil || back != job {
		t.Fatalf("job did not survive: %+v %v", back, err)
	}
}

func TestEnvOrderIsStable(t *testing.T) {
	h := hosts.Host{Workdir: ".", Python: "p", Env: map[string]string{"B": "2", "A": "1", "C": "3"}}
	if !strings.Contains(RemoteCommand(h, job), "env A='1' B='2' C='3' ") {
		t.Fatal(RemoteCommand(h, job))
	}
}

func TestArgvUsesSSHOnlyForRemoteHosts(t *testing.T) {
	local := Argv(hosts.Host{Workdir: ".", Python: "p"}, "echo hi")
	if local[0] != "sh" {
		t.Fatalf("local argv %v", local)
	}
	remote := Argv(hosts.Host{SSH: "u@h", Workdir: ".", Python: "p"}, "echo hi")
	if remote[0] != "ssh" || remote[len(remote)-2] != "u@h" || remote[len(remote)-1] != "echo hi" {
		t.Fatalf("remote argv %v", remote)
	}
}
